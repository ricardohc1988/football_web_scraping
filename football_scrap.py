from ids import leagues_id
from aux_functions import check_league, match_data, player_data, check_content, extract_table, table_to_df, extract_player_ids, find_league, find_team_id, find_player_id, available_stats_tables
import pandas as pd
import json
import os

fbref_url = 'https://fbref.com/en/'
actual_season = '2023-2024'
teams_ids = 'teams_ids.json'

class FootballScraper:

    class LeagueStats:
        """
        Used to represent statistics for a specific league.
        """
        def __init__(self, league_name: str):
            """
            Initialize the LeagueStats with a league name.

            Parameters:
            league_name (str): The name of the football league.
            """
            self.url = fbref_url
            self.league = league_name

        def get_available_league_stats(self) -> pd.DataFrame:
            """
            Retrieve the available statistics for the specified league.

            Returns:
            pd.DataFrame: A DataFrame containing the available statistics tables for the league.
            """
            try:
                league = check_league(self.league)
                league_url = f'{self.url}/comps/{leagues_id[league]}/{league}-Stats'
                content = check_content(league_url)
                available_stats_df = available_stats_tables(content)
                return available_stats_df
            except Exception as e:
                print(f"An unexpected error occurred: {str(e)}")
                return pd.DataFrame()           
            
        def get_league_stats(self, season: str = actual_season, table_id: str = 'stats_squads_standard_for') -> pd.DataFrame:
            """
            Retrieve the statistics for a specific season of the league.

            Parameters:
            season (str): The season for which the statistics are needed (default is actual_season).
            table_id (str): The ID of the specific statistics table to fetch (default is None).

            Returns:
            pd.DataFrame: A DataFrame containing the statistics table data.
            """
            try:
                league = check_league(self.league)
                league_season_url = f'{self.url}/comps/{leagues_id[league]}/{season}/{season}-{league}-Stats'
                content = check_content(league_season_url)
                league_table = extract_table(content, table_id)
                league_table_df = table_to_df(league_table)
                return league_table_df
            except Exception as e:
                print(f"An unexpected error occurred: {str(e)}")
                return pd.DataFrame()           
        
    class TeamStats:
        """
        Used to represent statistics for a specific football team.
        """
        def __init__(self, team_name: str):
            """
            Initialize the TeamStats with a team name.

            Parameters:
            team_name (str): The name of the football team.
            """
            self.url = fbref_url
            self.team = team_name
        
        def get_available_team_stats(self) -> pd.DataFrame:
            """
            Get available statistics for the current team.

            Returns:
            pd.DataFrame: A DataFrame containing available team statistics.
            """
            try:
                team_id = find_team_id(self.team, teams_ids)
                team_url = f'{self.url}/squads/{team_id}/{self.team}-Stats'
                content = check_content(team_url)
                available_stats_df = available_stats_tables(content)
                return available_stats_df
            except Exception as e:
                print(f"An unexpected error occurred: {str(e)}")
                return pd.DataFrame()               

        def get_team_stats(self, table_id: str, season: str = actual_season) -> pd.DataFrame:
            """
            Get team statistics for the specified season and table ID.

            Parameters:
            table_id (str): ID of the specific table to extract.
            season (str): The season for which statistics are requested (default: actual_season).

            Returns:
            pd.DataFrame: A DataFrame containing team statistics for the specified season and table ID
            """
            try:
                team_id = find_team_id(self.team, teams_ids)
                team_season_url = f'{self.url}/squads/{team_id}/{season}/{self.team}-Stats'
                content = check_content(team_season_url)
                team_table = extract_table(content, table_id)
                team_table_df = table_to_df(team_table)
                return team_table_df
            except Exception as e:
                print(f"An unexpected error occurred: {str(e)}")
                return pd.DataFrame()
        
    class PlayerStats:
        """
        Used to represent statistics for a specific player.
        """
        def __init__(self, player_name):
            """
            Initialize the PlayerStats with a player name.

            Parameters:
            player_name (str): The name of the player.
            """
            self.url = fbref_url
            self.player = player_name

        def get_available_player_stats(self) -> pd.DataFrame:
            """
            Retrieve available statistics for the specified player.

            Returns:
            pd.DataFrame: A DataFrame containing available statistics for the player,
                        or an empty DataFrame if no statistics are found.
            """
            try:
                player_id = find_player_id(self.player)
                player_url = f'{self.url}/players/{player_id}/{self.player}'
                content = check_content(player_url)
                available_stats = available_stats_tables(content)
                return available_stats
            except Exception as e:
                print(f"An unexpected error occurred: {str(e)}")
                return pd.DataFrame()
        
        def get_player_stats(self, season: str = actual_season, table_id: str = 'stats_standard_dom_lg') -> pd.DataFrame:
            """
            Retrieve statistics for the specified player and season.

            Parameters:
            season (str): The season for which statistics are requested (default: actual_season).
            table_id (str): ID of the specific table to extract (default: 'stats_standard_dom_lg').

            Returns:
            pd.DataFrame: A DataFrame containing player statistics for the specified season and table ID.
            """
            try:
                player_id = find_player_id(self.player)
                player_url = f'{self.url}/players/{player_id}/{self.player}'
                content = check_content(player_url)
                player_table = extract_table(content, table_id)
                player_table_df = table_to_df(player_table)
                player_table_df = player_table_df.loc[player_table_df['Season'] == season].reset_index(drop=True)
                return player_table_df
            except Exception as e:
                print(f"An unexpected error occurred: {str(e)}")
                return pd.DataFrame()
        
        def get_player_bio(self) -> pd.DataFrame:
            """
            Retrieve the biography information for the specified player.

            Returns:
            pd.DataFrame: A DataFrame containing player biography information.
            """
            try:
                player_id = find_player_id(self.player)
                player_url = f'{self.url}/players/{player_id}/{self.player}'
                self.content = check_content(player_url)
                if self.content:
                    bio = player_data(self.content)
                return bio
            except Exception as e:
                print(f"An unexpected error occurred: {str(e)}")
                return pd.DataFrame() 

    class Matches:
        """
        Used to represent statistics for a specific team matches.
        """
        def __init__(self, team_name: str):
            """
            Initializes Matches with a team name.

            Parameters:
            team_name (str): The name of the football team.
            """
            self.url = fbref_url
            self.team = team_name
        
        def get_team_matches(self, season: str = actual_season) -> pd.DataFrame:
            """
            Retrieves matches for the current team in a specified season.

            Parameters:
            season (str): The season for which matches are requested (default: actual_season).

            Returns:
            pd.DataFrame: DataFrame containing team matches for the specified season
            """
            try:
                team_id = find_team_id(self.team, teams_ids)
                team_matches_url = f'{self.url}/squads/{team_id}/{season}/matchlogs/'
                content = check_content(team_matches_url)
                matches_table = extract_table(content, 'matchlogs_for')
                matches_table_df = table_to_df(matches_table)
                return matches_table_df
            except Exception as e:
                print(f"An unexpected error occurred: {str(e)}")
        
        def get_match_stats(self, match_id: str) -> pd.DataFrame:
            """
            Retrieves match statistics for a specific match ID.

            Parameters:
            match_id (str): The ID of the match.

            Returns:
            pd.DataFrame: DataFrame containing match statistics
            """
            try: 
                match_url = f'{self.url}/matches/{match_id}'
                content = check_content(match_url)
                match_table = match_data(content, self.team)
                return match_table
            except Exception as e:
                print(f"An unexpected error occurred: {str(e)}")

    def get_teams_ids(self, league_name: str, season: str = actual_season) -> None:
        """
        Retrieve team IDs for a specific league and season.

        Parameters:
        league (str): The name of the league.
        season (str): The season for which to retrieve team IDs.

        Returns:
        None: The function updates a JSON file with the teams IDs.
        """
        try:
            league_season_url = f'{fbref_url}/comps/{leagues_id[league_name]}/{season}/{season}-{league_name}-Stats'
            print(f"Fetching URL: {league_season_url}")
            content = check_content(league_season_url)
            league_table_id = f'results{season}{leagues_id[league_name]}1_overall'
            table = extract_table(content, league_table_id)
            
            teams_ids = {}
            
            for tr in table.tbody.find_all('tr'):
                first_td = tr.find('td')
                if first_td:
                    a_tag = first_td.find('a')
                    if a_tag:
                        team_name = a_tag.text.strip()
                        team_id = a_tag['href'].split('/')[-2] if season == actual_season else a_tag['href'].split('/')[-3]
                        teams_ids[team_name] = team_id
            
            teams_ids_file = 'teams_ids.json'
            
            if os.path.exists(teams_ids_file):
                with open(teams_ids_file, 'r', encoding='utf-8') as json_file:
                    existing_teams_ids = json.load(json_file)
            else:
                existing_teams_ids = {}

            if league_name not in existing_teams_ids:
                existing_teams_ids[league_name] = {}
            existing_teams_ids[league_name].update(teams_ids)

            with open(teams_ids_file, 'w', encoding='utf-8') as json_file:
                json.dump(existing_teams_ids, json_file, ensure_ascii=False, indent=4)
            
            print(f'Got {league_name} teams IDs from {season} season successfully')

        except Exception as e:
            print(f"An unexpected error occurred: {str(e)}")
            return {}

    def get_players_ids(self, team_name: str, season: str = actual_season) -> None:
        """
        Retrieve player IDs for a specific team and season.

        Parameters:
        team_name (str): The name of the team.
        season (str): The season for which to retrieve player IDs (default: actual_season).

        Returns:
        None: The function updates a JSON file with the player IDs.
        """
        try:
            team_id = find_team_id(team_name, teams_ids)
            if team_id:
                team_season_url = f'{fbref_url}/squads/{team_id}/{season}/{team_name}-Stats'
                print(f"Fetching URL: {team_season_url}")
                content = check_content(team_season_url)
                players_ids_file = 'players_ids.json'

                if os.path.exists(players_ids_file):
                    with open(players_ids_file, 'r', encoding='utf-8') as json_file:
                        players_ids = json.load(json_file)
                else:
                    players_ids = {}
                league = find_league(team_name, teams_ids)
                table_id = f'stats_standard_{leagues_id[league]}'
                squad_table = extract_table(content, table_id)

                if squad_table:
                    players_ids[team_name] = extract_player_ids(squad_table)

                with open(players_ids_file, 'w', encoding='utf-8') as json_file:
                    json.dump(players_ids, json_file, ensure_ascii=False, indent=4)

                print(f'Got {team_name} players IDs from {season} season successfully')

            else:
                print('Could not find team id')
        except Exception as e:
            print(f"An error occurred: {str(e)}")
            return {}

    def get_available_leagues(self) -> pd.DataFrame:
        """
        Retrieve a DataFrame containing available football leagues and their corresponding countries.

        Returns:
        pd.DataFrame: A DataFrame with columns 'Country' and 'League Name' listing available football leagues.
        """
        available_leagues = {
            'Austria': 'Austrian Bundesliga', 
            'Belgium': 'Belgian Pro League', 
            'Croatia': 'Hrvatska NL',
            'Czech Republic': 'Czech First League',
            'Denmark': 'Superliga', 
            'England': 'Premier League',
            'France': 'Ligue 1',
            'Germany': 'Bundesliga',
            'Greece': 'Super League Greece',
            'Hungary': 'NB-I',
            'Italy': 'Serie A',
            'Netherlands': 'Eredivisie', 
            'Poland': 'Ekstraklasa',
            'Portugal': 'Primeira Liga',
            'Russia': 'Russian Premier League',
            'Spain': 'La Liga',
            'Switzerland': 'Swiss-Super-League',
            'Turkey': 'Super Lig',
        }

        countries = list(available_leagues.keys())
        league_names = list(available_leagues.values())

        df = pd.DataFrame({'Country': countries, 'League Name': league_names})

        return df

# scraper = FootballScraper()
# tables = scraper.LeagueStats(league_name='Primeira Liga').get_available_league_stats()
# print(tables)
# league = scraper.LeagueStats(league_name='Primeira Liga').get_league_stats()
# print(league)
# team = scraper.TeamStats('Bayern Munich').get_team_stats(table_id='stats_shooting_20', season='2021-2022')
# print(team)
# team_tables = scraper.TeamStats('Bayern Munich').get_available_team_stats()
# print(team_tables)
# player_tables = scraper.PlayerStats("Denis Odoi").get_available_player_stats()
# print(player_tables)
# player_stats = scraper.PlayerStats("Denis Odoi").get_player_stats()
# print(player_stats)
# player = scraper.PlayerStats("Mathias Kjølø").get_player_bio()
# print(player)
# teams = scraper.get_teams_ids('Primeira-Liga', '2023-2024')
# players = scraper.get_players_ids('Greuther Fürth')
# matches = scraper.Matches(team='Ajax').get_team_matches()
# print(matches)
# match = scraper.Matches(team='Ajax').get_match_stats('d45aec45')
# print(match.transpose())