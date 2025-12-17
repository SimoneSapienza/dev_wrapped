# DevWrapped

DevWrapped is a Python-based tool designed to generate a "Spotify Wrapped"-style infographic visualizing a developer's coding activity over the past year. It aggregates data from both **GitLab** and **GitHub**, analyzing commit history to produce detailed insights into coding habits, productivity patterns, and technology stack usage.

## Features

- **Multi-Provider Support**: Seamlessly fetches data from GitLab (SaaS or self-hosted) and GitHub.
- **Privacy First**: Runs entirely on your local machine. No tokens or data are sent to third-party servers.
- **Advanced Analytics**:
  - **Weekly Velocity**: Visualizes commit volume distribution throughout the year.
  - **Punch Card Heatmap**: Identifies peak productivity hours and days.
  - **Language Breakdown**: Calculates technology usage percentages based on commit volume.
  - **Productivity Metrics**: Tracks longest streaks, daily records, and multitasking indices.
- **High-Quality Output**: Generates a shareable, dark-mode PNG poster.

## Prerequisites

- Python 3.8+
- pip package manager

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/your-username/dev-wrapped.git
   cd dev-wrapped
   ```

2. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Configuration

Create a `.env` file in the root directory of the project. You can use the example below as a template:

```ini
# Year to analyze
TARGET_YEAR=2025

# GitLab Configuration (Optional)
# Defaults to https://gitlab.com if GITLAB_URL is not provided
GITLAB_URL=https://gitlab.com
GITLAB_TOKEN=glpat-your-personal-access-token

# GitHub Configuration (Optional)
GITHUB_TOKEN=ghp_your-personal-access-token
```

### Obtaining Access Tokens

- **GitLab**:
  1. Go to User Profile -> Preferences -> Access Tokens.
  2. Create a new token with the `read_api` scope.

- **GitHub**:
  1. Go to Settings -> Developer settings -> Personal access tokens (Tokens classic).
  2. Generate a new token with `repo` and `read:user` scopes.

## Usage

Run the main script from your terminal:

```bash
python main.py
```

The application will authenticate with the configured providers, fetch the activity data for the target year, and generate a file named `wrapped_2024.png` in the project root.

## Project Structure

- `main.py`: Application entry point and data aggregation logic.
- `providers/`: Connection logic for Git platforms (GitLab/GitHub).
- `utils/`: Helper functions and visualization logic (Matplotlib).
- `requirements.txt`: Python dependencies.

## License

This project is licensed under the MIT License.