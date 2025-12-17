from github import Github
from datetime import datetime
import os
from .base import GitProvider


class GitHubProvider(GitProvider):
    def __init__(self, token: str):
        self.token = token
        self.client = None
        self.user = None
        self._lang_cache = {}

    def connect(self):
        try:
            self.client = Github(self.token)
            self.user = self.client.get_user()
            print(f"[GitHub] Connected as: {self.user.login}")
        except Exception as e:
            raise ConnectionError(f"GitHub connection error: {e}")

    def get_user_info(self) -> str:
        display_name = self.user.name if self.user.name else self.user.login
        return f"{display_name} (@{self.user.login})"

    def _get_repo_languages(self, repo):
        repo_name = repo.full_name
        if repo_name in self._lang_cache:
            return self._lang_cache[repo_name]
        try:
            raw = repo.get_languages()
            total = sum(raw.values())
            if total == 0:
                return {repo.language or "Unknown": 1.0}

            res = {k: v / total for k, v in raw.items()}
            self._lang_cache[repo_name] = res
            return res
        except:
            return {"Unknown": 1.0}

    def get_year_stats(self, year: int) -> dict:
        if not self.client:
            self.connect()

        print(f"[GitHub] Querying data for {year}...")
        start_date = f"{year}-01-01"
        end_date = f"{year}-12-31"
        query = f"author:{self.user.login} committer-date:{start_date}..{end_date}"

        commits = self.client.search_commits(query)

        stats = {
            'total_commits': commits.totalCount,
            'projects_count': 0,
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

        for commit in commits:
            raw_date = commit.commit.author.date
            local_date = raw_date.astimezone()

            date_str = local_date.strftime('%Y-%m-%d')
            week_num = local_date.isocalendar()[1]
            weekday = local_date.weekday()
            hour = local_date.hour

            # 1. Base Stats
            stats['commits_by_month'][local_date.month] += 1
            stats['commits_by_hour'][hour] += 1
            stats['dates'].add(date_str)

            # 2. Punch Card
            pc_key = (weekday, hour)
            stats['punch_card'][pc_key] = stats['punch_card'].get(pc_key, 0) + 1

            # 3. Weekly Velocity
            stats['weekly_activity'][week_num] = stats['weekly_activity'].get(week_num, 0) + 1

            # 4. Project & Context Switcher
            repo = commit.repository
            stats['_temp_projects'].add(repo.full_name)
            if date_str not in stats['daily_projects']:
                stats['daily_projects'][date_str] = set()
            stats['daily_projects'][date_str].add(repo.full_name)
            stats['daily_commits'][date_str] = stats['daily_commits'].get(date_str, 0) + 1

            # 5. Lines & Extensions
            if commit.stats:
                stats['lines_added'] += commit.stats.additions
                stats['lines_deleted'] += commit.stats.deletions

            try:
                for f in commit.files[:5]:
                    filename = f.filename
                    ext = os.path.splitext(filename)[1].lower()
                    if ext and len(ext) < 10:
                        stats['extensions'][ext] = stats['extensions'].get(ext, 0) + 1
            except:
                pass

            # 6. Languages
            breakdown = self._get_repo_languages(repo)
            for lang, ratio in breakdown.items():
                stats['languages'][lang] = stats['languages'].get(lang, 0) + (1 * ratio)

        stats['projects_count'] = len(stats['_temp_projects'])
        del stats['_temp_projects']
        return stats