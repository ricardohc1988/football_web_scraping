# Football web scraping

## Description
Football Scraper is a Python project designed to extract and analyze football statistics from the FBref website. 
This project provides classes and methods to retrieve data for leagues, teams, players, and matches, offering comprehensive insights into various aspects of football performance.

## Features

- **League Statistics**: Retrieve available statistics for different leagues and specific seasons.
- **Team Statistics**: Get detailed stats for football teams, including season-specific data.
- **Player Statistics**: Extract individual player statistics and biographical information.
- **Match Statistics**: Access match-specific data and team match logs.

## Installation

To install the necessary dependencies, use Pipenv:

```sh
git clone https://github.com/yourusername/football-scraper.git
cd football-scraper
pipenv install
```

## Getting Started

# Check Available Leagues: Before diving into specific statistics, you can see which football leagues are available:

```python
from football_scraper import FootballScraper
scraper = FootballScraper()
available_leagues = scraper.get_available_leagues()
```

# Retrieve League Statistics: Once you've identified the league of interest from the available options, you can retrieve statistics for that league:

```
league_name = 'Premier League'  # Replace with the desired league name
league_stats = FootballScraper.LeagueStats(league_name)
```

# Example: Retrieve statistics for the current season
df_league_stats = league_stats.get_league_stats()

-Explore Team and Player Statistics: Use similar methods to explore team and player statistics:

# Example: Retrieve team statistics
team_name = 'Manchester United'  # Replace with the desired team name
team_stats = FootballScraper.TeamStats(team_name)
df_team_stats = team_stats.get_team_stats()

# Example: Retrieve player statistics
player_name = 'Lionel Messi'  # Replace with the desired player name
player_stats = FootballScraper.PlayerStats(player_name)
df_player_stats = player_stats.get_player_stats()
