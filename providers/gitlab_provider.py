import gitlab
from datetime import datetime, timezone
from .base import GitProvider
from utils.classify import classify_commit

class GitLabProvider(GitProvider):
    def __init__(self, url: str, token: str):
        self.url = url
        self.token = token
        self.client = None
        self.user = None
        self._lang_cache = {}

    def connect(self):
        try:
            self.client = gitlab.Gitlab(self.url, private_token=self.token)
            self.client.auth()
            self.user = self.client.user
            print(f"[GitLab] Connected as: {self.user.username}")
        except Exception as e:
            raise ConnectionError(f"GitLab connection error: {e}")

    def get_user_info(self) -> str:
        return f"{self.user.name} (@{self.user.username})"

    def _get_language_breakdown(self, project_id):
        if project_id in self._lang_cache:
            return self._lang_cache[project_id]

        try:
            p = self.client.projects.get(project_id)
            langs = p.languages()
            total = sum(langs.values())

            if total == 0:
                return {"Unknown": 1.0}

            breakdown = {k: v / total for k, v in langs.items()}
            self._lang_cache[project_id] = breakdown
            return breakdown
        except:
            self._lang_cache[project_id] = {"Unknown": 1.0}
            return {"Unknown": 1.0}

    def get_year_stats(self, year: int) -> dict:
        if not self.client:
            self.connect()

        print(f"[GitLab] Querying data for {year} (Fast Mode)...")
        start_date = datetime(year, 1, 1).isoformat()
        end_date = datetime(year, 12, 31).isoformat()

        stats = {
            'total_commits': 0,
            'projects_count': 0,
            # GitLab Events API does not support line diffs efficiently
            'lines_added': 0,
            'lines_deleted': 0,
            'commits_by_month': {i: 0 for i in range(1, 13)},
            'commits_by_hour': {i: 0 for i in range(24)},
            'languages': {},
            'dates': set(),
            'punch_card': {},
            'extensions': {},
            'weekly_activity': {i: 0 for i in range(1, 54)},
            'daily_projects': {},
            'daily_commits': {},
            'commit_types': {},
            '_temp_projects': set()
        }

        # Retrieve Push events only
        events = self.client.events.list(
            after=start_date, before=end_date, action='pushed', all=True
        )

        print(f"[GitLab] Analyzing {len(events)} push events...")

        for event in events:
            project_id = event.project_id
            stats['_temp_projects'].add(project_id)

            if not hasattr(event, 'push_data'):
                continue

            commit_count = event.push_data['commit_count']
            stats['total_commits'] += commit_count

            dt_utc = datetime.strptime(event.created_at, '%Y-%m-%dT%H:%M:%S.%fZ').replace(tzinfo=timezone.utc)
            dt_local = dt_utc.astimezone()

            date_str = dt_local.strftime('%Y-%m-%d')
            week_num = dt_local.isocalendar()[1]

            # Heuristic: Cap daily contribution for massive pushes to avoid
            # skewing daily statistics (e.g., initial imports or merges).
            effective_daily_count = commit_count
            if commit_count > 20:
                effective_daily_count = 1

            # Populate Stats
            stats['dates'].add(date_str)
            stats['commits_by_month'][dt_local.month] += effective_daily_count
            stats['commits_by_hour'][dt_local.hour] += effective_daily_count
            stats['weekly_activity'][week_num] = stats['weekly_activity'].get(week_num, 0) + effective_daily_count

            # Punch Card
            pc_key = (dt_local.weekday(), dt_local.hour)
            stats['punch_card'][pc_key] = stats['punch_card'].get(pc_key, 0) + effective_daily_count

            # Record Daily Commits
            stats['daily_commits'][date_str] = stats['daily_commits'].get(date_str, 0) + effective_daily_count

            # Context Switcher
            if date_str not in stats['daily_projects']:
                stats['daily_projects'][date_str] = set()
            stats['daily_projects'][date_str].add(project_id)

            # Commit Types
            title = event.push_data.get('commit_title')
            ctype = classify_commit(title)
            stats['commit_types'][ctype] = stats['commit_types'].get(ctype, 0) + commit_count

            # Languages
            breakdown = self._get_language_breakdown(project_id)
            for lang, ratio in breakdown.items():
                stats['languages'][lang] = stats['languages'].get(lang, 0) + (commit_count * ratio)

        stats['projects_count'] = len(stats['_temp_projects'])
        del stats['_temp_projects']

        return stats