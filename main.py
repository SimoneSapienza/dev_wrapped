import os
import sys
from dotenv import load_dotenv
from providers.gitlab_provider import GitLabProvider
from providers.github_provider import GitHubProvider
from utils.visualizer import Visualizer

load_dotenv()
TARGET_YEAR = int(os.getenv('TARGET_YEAR', 2024))


def merge_stats(all_stats):
    merged = {
        'total_commits': 0,
        'projects_count': 0,
        'lines_added': 0,
        'lines_deleted': 0,
        'commits_by_month': {},
        'commits_by_hour': {},
        'languages': {},
        'dates': set(),
        'punch_card': {},
        'extensions': {},
        'weekly_activity': {},
        'commit_types': {},
        'daily_projects': {},
        'daily_commits': {}
    }

    for stat in all_stats:
        merged['total_commits'] += stat.get('total_commits', 0)
        merged['projects_count'] += stat.get('projects_count', 0)
        merged['lines_added'] += stat.get('lines_added', 0)
        merged['lines_deleted'] += stat.get('lines_deleted', 0)

        # Merge numeric dictionaries
        for field in ['commits_by_month', 'commits_by_hour', 'languages',
                      'punch_card', 'extensions', 'weekly_activity', 'commit_types']:
            for k, v in stat.get(field, {}).items():
                merged[field][k] = merged[field].get(k, 0) + v

        # Merge Sets
        merged['dates'].update(stat.get('dates', set()))

        # Merge Daily Projects (Set union)
        for date, projs in stat.get('daily_projects', {}).items():
            if date not in merged['daily_projects']:
                merged['daily_projects'][date] = set()
            merged['daily_projects'][date].update(projs)

        # Merge Daily Commits (Integer sum)
        for date, count in stat.get('daily_commits', {}).items():
            merged['daily_commits'][date] = merged['daily_commits'].get(date, 0) + count

    return merged


if __name__ == "__main__":
    viz = Visualizer()
    active_providers = []

    if os.getenv('GITLAB_TOKEN'):
        active_providers.append(GitLabProvider(os.getenv('GITLAB_URL'), os.getenv('GITLAB_TOKEN')))
    if os.getenv('GITHUB_TOKEN'):
        active_providers.append(GitHubProvider(os.getenv('GITHUB_TOKEN')))

    if not active_providers:
        viz.console.print("[bold red]No provider configured.[/bold red]")
        sys.exit(1)

    with viz.console.status("[bold green]Processing data...[/bold green]") as status:
        collected_stats = []
        user_names = []
        for provider in active_providers:
            try:
                provider.connect()
                user_names.append(provider.get_user_info())
                stats = provider.get_year_stats(TARGET_YEAR)
                collected_stats.append(stats)
            except Exception as e:
                viz.console.print(f"[red]Provider error:[/red] {e}")

    if collected_stats:
        final_stats = merge_stats(collected_stats)
        display_name = user_names[0].split('(')[0].strip() if user_names else "Dev"

        viz.print_terminal_report(final_stats, display_name, TARGET_YEAR)
        img_path = viz.generate_shareable_image(final_stats, display_name, TARGET_YEAR)

        viz.console.print(
            f"\n[bold green]Image saved:[/bold green] [link=file://{os.getcwd()}/{img_path}]{img_path}[/link]")