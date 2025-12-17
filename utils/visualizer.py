import matplotlib.pyplot as plt
import seaborn as sns
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich import box
from datetime import datetime

class Visualizer:
    def __init__(self):
        self.console = Console()
        plt.style.use('dark_background')
        self.colors_pie = sns.color_palette("pastel")

    def determine_persona(self, hourly_stats):
        morning = sum(hourly_stats.get(h, 0) for h in range(5, 12))
        night = sum(hourly_stats.get(h, 0) for h in [23, 0, 1, 2, 3, 4])
        total = sum(hourly_stats.values())
        if total == 0: return "The Ghost 👻"
        if night > total * 0.3: return "Vampire Coder 🧛"
        if morning > total * 0.45: return "Early Bird ☕"
        return "9-to-5 Pro 👔"

    def calculate_streak(self, date_set):
        if not date_set: return 0
        sorted_dates = sorted([datetime.strptime(d, "%Y-%m-%d") for d in date_set])
        longest = 1
        current = 1
        for i in range(1, len(sorted_dates)):
            delta = sorted_dates[i] - sorted_dates[i - 1]
            if delta.days == 1:
                current += 1
            elif delta.days > 1:
                longest = max(longest, current)
                current = 1
        return max(longest, current)

    def print_terminal_report(self, stats, user_name, year):
        self.console.print(Panel.fit(f"[bold magenta]DEV WRAPPED {year}[/bold magenta]\n[cyan]{user_name}[/cyan]"))
        table = Table(box=box.SIMPLE_HEAVY, show_header=True)
        table.add_column("Metric")
        table.add_column("Value")

        table.add_row("Commits", str(stats['total_commits']))

        added = stats.get('lines_added', 0)
        deleted = stats.get('lines_deleted', 0)
        if added > 0:
            table.add_row("Lines Added", f"+{added:,}", style="green")
            table.add_row("Lines Deleted", f"-{deleted:,}", style="red")

        # Context Switcher Calculation
        daily = stats.get('daily_projects', {})
        active_days = len(daily)
        switches = sum(len(p) for p in daily.values())
        avg = (switches / active_days) if active_days else 0
        table.add_row("Avg Projects/Day", f"{avg:.2f}")

        self.console.print(table)

    def generate_shareable_image(self, stats, user_name, year):
        # 1. Prepare Data
        streak = self.calculate_streak(stats.get('dates', set()))

        # Record Max Projects
        d_projs = stats.get('daily_projects', {})
        max_p = 0
        date_p = "-"
        if d_projs:
            max_p = max(len(x) for x in d_projs.values())
            date_iso = max(d_projs, key=lambda k: len(d_projs[k]))
            try:
                date_p = datetime.strptime(date_iso, "%Y-%m-%d").strftime("%d %b")
            except:
                pass

        # Record Max Commits
        d_comms = stats.get('daily_commits', {})
        max_c = 0
        date_c = "-"
        if d_comms:
            max_c = max(d_comms.values())
            date_iso = max(d_comms, key=d_comms.get)
            try:
                date_c = datetime.strptime(date_iso, "%Y-%m-%d").strftime("%d %b")
            except:
                pass

        # 2. Setup Figure (Standard 10x15 Poster format)
        fig = plt.figure(figsize=(10, 15))
        fig.patch.set_facecolor('#0f0f0f')

        # Grid Layout: 5 Rows
        gs = fig.add_gridspec(5, 1, height_ratios=[0.1, 0.15, 0.25, 0.25, 0.25], hspace=0.4)

        # --- ROW 0: HEADER ---
        ax_head = fig.add_subplot(gs[0])
        ax_head.axis('off')
        ax_head.text(0.5, 0.7, f"DEV WRAPPED {year}", ha='center', fontsize=30, color='#00ff41', weight='bold', fontname='monospace')
        ax_head.text(0.5, 0.3, f"@{user_name}", ha='center', fontsize=18, color='white', fontname='monospace')

        # --- ROW 1: STATS GRID ---
        gs_stats = gs[1].subgridspec(1, 4)

        def print_stat(idx, val, label, color='white', sublabel=None):
            ax = fig.add_subplot(gs_stats[idx])
            ax.axis('off')
            ax.text(0.5, 0.6, str(val), ha='center', fontsize=24, color=color, weight='bold')
            ax.text(0.5, 0.3, label, ha='center', fontsize=9, color='#888')
            if sublabel:
                ax.text(0.5, 0.15, sublabel, ha='center', fontsize=7, color='#555', style='italic')

        print_stat(0, stats['total_commits'], "COMMITS")
        print_stat(1, streak, "DAY STREAK", "#f1c40f")
        print_stat(2, max_p, "MAX PROJ/DAY", "#3498db", f"on {date_p}")
        print_stat(3, max_c, "MAX COMM/DAY", "#e74c3c", f"on {date_c}")

        # --- ROW 2: VELOCITY ---
        ax_vel = fig.add_subplot(gs[2])
        weeks = list(range(1, 53))
        counts = [stats['weekly_activity'].get(w, 0) for w in weeks]
        ax_vel.plot(weeks, counts, color='#00ff41', linewidth=2, marker='o', markersize=3)
        ax_vel.fill_between(weeks, counts, color='#00ff41', alpha=0.1)
        ax_vel.set_title("WEEKLY VELOCITY", color='white', weight='bold', fontsize=12)

        ax_vel.set_facecolor('#0f0f0f')
        ax_vel.spines['top'].set_visible(False)
        ax_vel.spines['right'].set_visible(False)
        ax_vel.spines['left'].set_visible(False)
        ax_vel.spines['bottom'].set_color('#333')
        ax_vel.set_xlim(1, 52)
        ax_vel.set_xticks([1, 13, 26, 39, 52])
        ax_vel.set_xticklabels(['W1', 'W13', 'W26', 'W39', 'W52'], color='#666')
        ax_vel.set_yticks([])

        # --- ROW 3: PUNCH CARD ---
        ax_punch = fig.add_subplot(gs[3])
        pc = stats.get('punch_card', {})
        X, Y, S = [], [], []
        max_val = max(pc.values()) if pc else 1
        for (d, h), c in pc.items():
            X.append(d)
            Y.append(h)
            S.append((c / max_val) * 300 + 20)

        ax_punch.scatter(X, Y, s=S, color='#e91e63', alpha=0.7, edgecolors='none')
        ax_punch.set_title("ACTIVITY HEATMAP", color='white', weight='bold', fontsize=12)

        ax_punch.set_facecolor('#0f0f0f')
        ax_punch.set_xticks(range(7))
        ax_punch.set_xticklabels(['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'], color='#aaa')
        ax_punch.set_yticks([0, 6, 12, 18, 23])
        ax_punch.set_yticklabels(['00:00', '06:00', '12:00', '18:00', '23:00'], color='#aaa')
        ax_punch.invert_yaxis()
        ax_punch.spines['top'].set_visible(False)
        ax_punch.spines['right'].set_visible(False)
        ax_punch.spines['bottom'].set_color('#333')
        ax_punch.spines['left'].set_color('#333')

        # --- ROW 4: PIE CHART ---
        ax_pie = fig.add_subplot(gs[4])
        langs = stats.get('languages', {})
        if langs:
            s_langs = sorted(langs.items(), key=lambda x: x[1], reverse=True)[:5]
            others = sum(langs.values()) - sum(v for k, v in s_langs)
            L = [k for k, v in s_langs]
            V = [v for k, v in s_langs]
            if others > 0:
                L.append("Other")
                V.append(others)

            ax_pie.pie(V, labels=L, autopct='%1.0f%%', colors=self.colors_pie,
                       textprops={'color': 'white', 'fontsize': 10})
            ax_pie.add_artist(plt.Circle((0, 0), 0.7, fc='#0f0f0f'))
        else:
            ax_pie.text(0.5, 0.5, "NO DATA", ha='center', color='#555')
            ax_pie.axis('off')

        ax_pie.set_title("TOP LANGUAGES", color='white', weight='bold', fontsize=12)

        # Footer
        fig.text(0.5, 0.02, "Generated with DevWrapped Python", ha='center', color='#444', fontsize=8)

        output_file = f"wrapped_{year}.png"
        plt.savefig(output_file, facecolor=fig.get_facecolor(), dpi=150, bbox_inches='tight')
        plt.close(fig)
        return output_file