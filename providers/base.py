from abc import ABC, abstractmethod
from typing import Dict, Any

class GitProvider(ABC):
    @abstractmethod
    def connect(self):
        """Authenticates with the provider."""
        pass

    @abstractmethod
    def get_user_info(self) -> str:
        """Returns the formatted user name."""
        pass

    @abstractmethod
    def get_year_stats(self, year: int) -> Dict[str, Any]:
        """
        Retrieves statistics for the specified year.
        Expected output structure:
        {
            'total_commits': int,
            'projects_count': int,
            'lines_added': int,
            'lines_deleted': int,
            'commits_by_month': {1: x...},
            'commits_by_hour': {0: x...},
            'languages': {'Python': x...},
            'dates': set(),
            'punch_card': {(weekday, hour): count},
            'extensions': {'.py': 100, '.md': 20},
            'weekly_activity': {1: 50, ... 52: 10},
            'daily_projects': {'2024-01-01': {'projA', 'projB'}},
            'daily_commits': {'2024-01-01': int}
        }
        """
        pass