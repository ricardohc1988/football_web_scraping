from ids import leagues_id
import requests
import pandas as pd
import bs4
from bs4 import BeautifulSoup
import json

def check_content(url: str) -> bytes:
    """
    This function attempts to retrieve the content of a webpage at the specified URL.
    It raises an exception if any error occurs during the request, and returns the
    content of the response if successful.
    Args:
        url (str): The URL of the webpage to fetch.

    Returns:
        bytes: The content of the response if the request is successful.
    """
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status() 
        return response.content
    except requests.exceptions.RequestException as e:
        print(f'Error connecting: {e}')
    
def check_league(league: str) -> str:
    """
    Validate if the provided league exists in the leagues_id dictionary.

    Parameters:
        league (str): The name of the football league to check.

    Returns:
        str: The validated league name.

    Raises:
        ValueError: If the league is not found in the leagues_id dictionary.
    """
    validated_league = leagues_id.get(league)
    if not validated_league:
        raise ValueError(f"Error: {league} not found.")
    return league
    
def player_data(content: bytes) -> pd.DataFrame:
    """
    This function parses HTML content (in bytes format) and extracts player data into a Pandas DataFrame.

    Args:
        content (bytes): The HTML content in bytes format containing player information.

    Returns:
        pd.DataFrame: A DataFrame containing player data with columns for name, position, etc.
    """
    try:
        soup = BeautifulSoup(content, 'html.parser')
        meta_div = soup.find('div', id='meta')

        headers = ['Name:', 'Position:', 'Footed:', 'Height:', 'Weight:', 'Born:', 'Nation:', 'Club:']

        player_name = meta_div.find('span').get_text() if len(meta_div.find('span').get_text()) > 1 else 'Unknown'
        player_position = meta_div.find('strong', text='Position:').next_sibling.split('\xa0▪')[0].strip() if meta_div.find('strong', text='Position:') else 'Unknown'
        player_foot = meta_div.find('strong', text='Footed:').next_sibling.strip() if meta_div.find('strong', text='Footed:') else 'Unknown'
        player_height = next((span.get_text()[:-2] for span in meta_div.find_all('span') if span.get_text().endswith('cm')), 'Unknown')
        player_weight = next((span.get_text()[:-2] for span in meta_div.find_all('span') if span.get_text().endswith('kg')), 'Unknown')
        player_birth_date = meta_div.find('span', id='necro-birth').get_text().strip() if meta_div.find('span', id='necro-birth') else 'Unknown'
        player_club = meta_div.find('strong', text='Club:').find_next_sibling('a').get_text()
        player_nation = ''
        for field in ['National Team:', 'Citizenship:', 'Youth National Team:']:
            field_element = meta_div.find('strong', text=field)
            if field_element:
                player_nation = field_element.find_next_sibling('a').get_text()
                break
        else:
            player_nation = 'Unknown'

        data = [
            [player_name, player_position, player_foot, player_height, player_weight, player_birth_date, player_nation, player_club]
        ]

        df = pd.DataFrame(data, columns=headers)

        return df
    
    except Exception as e:
            print(f"An error occurred while parsing player data: {str(e)}")
            return pd.DataFrame(columns=headers)

def match_data(content: bytes, team: str) -> pd.DataFrame:
    soup = BeautifulSoup(content, 'html.parser')
    content_div = soup.find('div', id='content')
    
    # Check if the specified team is mentioned in the header (h1) of the content
    if team in content_div.find('h1').get_text():
        # Find team_stats div and team_stats_extra div
        team_stats = content_div.find('div', id='team_stats')
        team_stats_extra = content_div.find('div', id='team_stats_extra')

        team_stats_extra_divs = team_stats_extra.find_all('div')
        numbers = [element.get_text() for element in team_stats_extra_divs if element.get_text().isdigit()]
        grouped_numbers = [[int(number) for number in numbers[i:i+2]] for i in range(0, len(numbers), 2)]

        # Get all rows from team_stats
        rows = [tr.get_text() for tr in team_stats.find_all('tr') if tr.get_text() != 'Cards']

         # Extract team names from the first row, splitting and joining to clean up extra spaces
        teams = [' '.join(element.split()) for element in rows[0].split('\t')]

         # Extract headers from rows, skipping the first and last row and taking every second row
        team_stats_headers = rows[1:-1:2]
        # Insert 'Team' as the first header
        team_stats_headers.insert(0, 'Team')

        team_stats_extra_headers = ['Fouls', 'Corners', 'Crosses', 'Touches', 'Tackles', 'Interceptions', 'Aerials Won', 'Clearances', 'Offsides', 'Goal Kicks', 'Throw Ins', 'Long Balls']

        headers = team_stats_headers + team_stats_extra_headers
        
        match_data = []
        # Iterate through each row in the stats table
        for row in team_stats.find_all('tr'):
            cells = row.find_all('td')
            row_data = []
            # Extract the text from the <strong> tag within each cell
            for cell in cells:
                strong_tag = cell.find('strong')
                if strong_tag:
                    row_data.append(strong_tag.text)
            # If row_data is not empty, add it to match_data
            if row_data:
                match_data.append(row_data)

        # Insert team names as the first row of match_data
        match_data.insert(0, teams)

        for group in grouped_numbers:
            match_data.append(group)
        
        # Create a DataFrame from match_data and transpose it
        df = pd.DataFrame(match_data)
        df = df.transpose()
        
        # Set headers as the column names of the DataFrame
        df.columns = headers

        return df

    # Print error
    else:
        print('Team not involved in this match')

def available_stats_tables(content: bytes) -> pd.DataFrame:
  """
  Parses HTML content to identify tables containing league statistics.

  Args:
      content: The HTML content to be parsed.

  Returns:
      pd.DataFrame: A DataFrame containing information about available statistics tables, 
                    or an empty DataFrame if there's an error parsing the content.
  """
  try:
    soup = BeautifulSoup(content, 'html.parser')
    tables = soup.find_all('table')
    exclude_data = {'similar_GK', 'similar_DF', 'similar_FB', 'similar_MF', 'similar_AM', 'similar_FW', 'scout_summary_GK', 'scout_summary_DF', 'scout_summary_FB', 'scout_summary_MF', 'scout_summary_AM', 'scout_summary_FW', }
    data = []

    for table in tables:
      caption = table.find('caption')
      if caption:
        main_text = caption.get_text()
        if main_text not in data:
          table_id = table.get('id')
          if table_id and table_id not in exclude_data:
            data.append((main_text, table_id))

    df = pd.DataFrame(data, columns=['Statistic', 'Table_ID'])
    return df
  except Exception as e:
    print(f"Error parsing HTML content: {e}")
    return pd.DataFrame()
    
def extract_table(content: bytes, table_id: str) -> bs4.element.Tag:
    """
    Extract a table from the provided HTML content using its ID.

    Parameters:
    content (str): The HTML content to parse.
    table_id (str): The ID of the table to extract.

    Returns:
    bs4.element.Tag: The extracted table element, or raises ValueError if not found.

    Raises:
    ValueError: If the content is empty or invalid.
    """
    try:
        soup = BeautifulSoup(content, 'html.parser')
        table = soup.find('table', id=table_id)
        if table is None:
            raise ValueError(f"Error: Table with id '{table_id}' not found.")
        return table
    
    except Exception as e:
        raise ValueError(f"Error: An error occurred while extracting the table. {str(e)}")

def table_to_df(table: bs4.element.Tag) -> pd.DataFrame:
    """
    Convert an HTML table element to a pandas DataFrame.

    Parameters:
    table (bs4.element.Tag): The HTML table element to convert.

    Returns:
    pd.DataFrame: A DataFrame containing the table data.
    """ 
    try:
        if not table.thead or not table.tbody:
            return pd.DataFrame()
        
        exclude_columns = {'Rank', 'Notes', 'Day', 'Attendance', 'Matches'}
        exclude_cells = {'rank', 'notes', 'dayofweek', 'attendance', 'matches'}    

        headers = [th.get('aria-label') for th in table.thead.select('th:not(.over_header)') if th.get('aria-label') not in exclude_columns and th.text.strip()]     
        valid_rows = table.tbody.select('tr:not(.spacer):not(.blank_table)')        
        rows = []

        for tr in valid_rows:
            cells = []
            for element in tr.select('td, th'):
                data_stat = element.get('data-stat')
                if data_stat not in exclude_cells:
                    if data_stat in {'match_report', 'nationality'}:
                        href = element.find('a', href=True)
                        if href and href['href']:
                            href_value = href['href'].split('/')
                            cells.append(href_value[3] if len(href_value) > 3 else 'Unknown')
                    else:
                        cells.append(element.text.strip())
            if cells:
                rows.append(cells)

        table_df = pd.DataFrame(rows, columns=headers)

        if 'Match Report' in table_df.columns:
            table_df.rename(columns={'Match Report': 'Match ID'}, inplace=True)

        return table_df
    
    except Exception as e:
        print(f"An error occurred while converting the table to DataFrame: {str(e)}")
        return pd.DataFrame()

def find_team_id(team_name: str, teams_ids: json) -> str:
    """
    Find the ID of a team given its name and a dictionary of teams.

    Parameters:
    team_name (str): The name of the team to find.
    teams_dict (dict): A dictionary where keys are league names and values are dictionaries
                       of team names and their corresponding IDs.

    Returns:
    str: The ID of the team if found, or None if not found.

    Raises:
    ValueError: If the team_name or teams_dict is invalid.
    """
    try:
        with open(teams_ids, 'r', encoding='utf-8') as json_file:
            teams_ids = json.load(json_file)

        for league, teams in teams_ids.items():
            team_id = teams.get(team_name)
            if team_id:
                return team_id
            
    except Exception as e:
        print(f"An unexpected error occurred: {str(e)}")
        return None
    
def find_league(team_name: str, teams_ids: json) -> str:
    """
    Find the league for a given team name.

    Parameters:
    team_name (str): The name of the team to search for.
    teams_dict (dict): A dictionary mapping leagues to their teams.

    Returns:
    str: The league in which the team plays, or None if the team is not found.
    """
    try:
        with open(teams_ids, 'r', encoding='utf-8') as json_file:
            teams_ids = json.load(json_file)

        for league, teams in teams_ids.items():
            if team_name in teams:
                return league

    except Exception as e:
        print(f"An error occurred while finding the league: {str(e)}")
        return None
    
def find_player_id(player_name: str) -> str:
    """
    Find the player ID for a given player name.

    Parameters:
    player_name (str): The name of the player to search for.

    Returns:
    str: The player ID, or None if the player is not found.
    """
    try:
        with open('players_ids.json', 'r', encoding='utf-8') as json_file:
            players_ids = json.load(json_file)
        
        for team, players in players_ids.items():
            if player_name in players:
                return players[player_name]
        return None
    except FileNotFoundError:
        print("Error: File not found")
        return None
    except Exception as e:
        print(f"An unexpected error occurred: {str(e)}")
        return None

def extract_player_ids(squad_table: bs4.element.Tag) -> dict:
    """
    Extract player names and their corresponding IDs from a squad table.

    Parameters:
    squad_table (bs4.element.Tag): The HTML table element containing player information.

    Returns:
    dict: A dictionary mapping player names to their IDs.
    """
    players_dict = {}
    try:
        for a_tag in squad_table.find_all('a', href=True):
            if '/en/players/' in a_tag['href']:
                player_id = a_tag['href'].split('/')[3]
                if a_tag.text != 'matches':
                    player_name = a_tag.text
                    players_dict[player_name] = player_id
                else:
                    continue
        return players_dict
    
    except Exception as e:
        print(f"An error occurred while extracting player IDs: {str(e)}")
        return {}