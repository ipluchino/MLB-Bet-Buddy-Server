#********************************************************************************************************************************
# Author: Ian Pluchino                                                                                                          *
# Class: Endpoints class                                                                                                        *
# Description: Handles everything regarding the I/O with the endpoints for the MLB and Weather APIs.                            *
# Date: 5/2/24                                                                                                                  *
#********************************************************************************************************************************

import requests
import time

class Endpoints():
    #All API endpoint links that will be used in the project. Variable portions of the URL are within curly braces {}. 
    #Endpoint to analyze an individual game. Note: v1.1 is used for live game data.
    GAME_ANALYSIS_URL = 'https://statsapi.mlb.com/api/v1.1/game/{game_id}/feed/live'
    
    #Endpoint to find the offensive statistics for a team.
    TEAM_OFFENSE_URL = 'https://statsapi.mlb.com/api/v1/teams/{team_id}/stats?group=hitting&season={season}&sportIds=1&stats=byDateRange&startDate={start_date}&endDate={end_date}'

    #Endpoint to get basic player information (such as batting hand and pitching hand).
    GENERAL_PLAYER_INFO_URL = 'https://statsapi.mlb.com/api/v1/people/{player_id}'

    #Endpoint to find the offensive statistics for an individual player.
    INDIVIDUAL_HITTING_URL = 'https://statsapi.mlb.com/api/v1/people/{player_id}?sportId=1&hydrate=stats(group=[hitting],type=[byDateRange],startDate={start_date},endDate={end_date},season={season})' 
    
    #Endpoint to find the pitching statistics for an individual player.
    INDIVIDUAL_PITCHING_URL = 'https://statsapi.mlb.com/api/v1/people/{player_id}?sportId=1&hydrate=stats(group=[pitching],type=[byDateRange],startDate={start_date},endDate={end_date},season={season})' 
    
    #Endpoint to get the schedule of games for a specific date, along with the probable pitchers.
    TODAY_SCHEDULE_URL = 'https://statsapi.mlb.com/api/v1/schedule?sportId=1&hydrate=probablePitcher&startDate={start_date}&endDate={end_date}'
    
    #Endpoint to get a team's game log in a specified date range.
    TEAM_GAME_LOG_URL='https://statsapi.mlb.com/api/v1/schedule?&sportId=1&teamId={team_id}&startDate={start_date}&endDate={end_date}&season={season}'
    
    #Endpoint to get MLB standings.
    STANDINGS_URL = 'https://statsapi.mlb.com/api/v1/standings?standingsTypes=regularSeason&leagueId=103,104&date={date}&season={season}'

    #Endpoint to get the game log of a hitter.
    HITTING_GAME_LOG_URL = 'https://statsapi.mlb.com/api/v1/people/{player_id}/stats?stats=gameLog&group=hitting&season={season}&startDate={start_date}'

    #Endpoint to get the game log of a pitcher.
    PITCHING_GAME_LOG_URL = 'https://statsapi.mlb.com/api/v1/people/{player_id}/stats?stats=gameLog&group=pitching&season={season}&startDate={start_date}&endDate={end_date}'
    
    #Endpoint to get a hitter's career numbers off a specific pitcher.
    CAREER_HITTING_NUMBERS_URL = 'https://statsapi.mlb.com/api/v1/people?personIds={hitter_id}&hydrate=stats(group=[hitting],type=[vsPlayerTotal],opposingPlayerId={pitcher_id},sportId=1)'
    
    #Endpoint to get the player ID of a player based on their name.
    ID_LOOKUP_URL = 'https://statsapi.mlb.com/api/v1/people/search?names={player_name}'
    
    #Endpoint to get the lefty/righty splits for a hitter.
    LEFTY_RIGHTY_SPLITS_HITTER_URL = 'https://statsapi.mlb.com/api/v1/people/{player_id}?hydrate=stats(group=[hitting],type=[statSplits],sitCodes=[vr,vl],season={season})'
    
    #Endpoint to get the lefty/righty splits for a pitcher.
    LEFTY_RIGHTY_SPLITS_PITCHER_URL = 'https://statsapi.mlb.com/api/v1/people/{player_id}?hydrate=stats(group=[pitching],type=[statSplits],sitCodes=[vr,vl],season={season})'
    
    #Endpoint to get the hourly forecast for a city. Note: Weather API is used, not MLB API.
    WEATHER_URL = 'https://api.weatherapi.com/v1/forecast.json?key={API_key}&q={city}' 
    
    #Endpoint to get a list of all hitters in a specified season.
    ALL_HITTERS_URL = 'https://statsapi.mlb.com/api/v1/stats?stats=season&group=hitting&season={season}&playerPool=QUALIFIED&offset={offset}'        

    #CONSTRUCTOR
    def __init__(self):
        """Constructor for the Endpoints class.

        Returns:
            Nothing.
        """
        #Create a session object to increase API lookup speed.
        self.session = requests.Session()
    
    #UTILITY METHODS
    def AccessEndpointData(self, a_URL):
        """Sends a get request to the provided endpoint URL and returns the JSON data in the response.

        This method is used throughout the entire project to retrieve data from both the MLB API and Weather API. All 
        data is returned in a JSON format. Before returning, this function makes sure that the data was successfully 
        retrieved. If there are any errors, the function sleeps for 10 seconds and tries to access the API again.

        Args:
            a_URL (string): The URL to send a get request to.

        Returns:
            A dictionary representing the JSON data returned from accessing the provided endpoint URL.
        """    
        #Attempt to make a request to the endpoint.
        try:
            response = self.session.get(a_URL)
            data = response.json()
            return data
        #Occasionally the data may be missing or the API may not respond. It is fixed by simply waiting a short time, then trying again.
        except Exception as e:
            print(e, '\n\n', a_URL)
            time.sleep(10)
            return self.AccessEndpointData(a_URL)
            
    def FormatDate(self, a_dateObj):
        """Converts a datetime object into the correct string format.

        Args:
            a_dateObj (datetime): The datetime object to convert to a string. 

        Returns:
            A string representing the formatted date in the format mm/dd/yyyy.
        """
        return a_dateObj.strftime('%m/%d/%Y')
    
    def GetGameAnalysisEndpoint(self, a_gameID):
        """Gets the endpoint URL to analyze a specific game.

        Args:
            a_gameID (int): The game ID used by the MLB API to represent an individual game.

        Returns:
            A string representing the URL endpoint required to retrieve an MLB game's information.
        """
        return self.GAME_ANALYSIS_URL.format(game_id=a_gameID)
    
    def GetTeamOffensiveEndpoint(self, a_teamID, a_season, a_startDate, a_endDate):
        """Gets the endpoint URL to analyze team offensive statistics.

        Args:
            a_teamID (int): The team ID used by the MLB API to represent the team.
            a_season (int): The season to get the statistics from.
            a_startDate (datetime): The date representing the start of the date range to extract the stats from.
            a_endDate (datetime): The date representing the end of the date range to extract the stats from.

        Returns:
            A string representing the URL endpoint required to retrieve the team's offensive statistics.
        """
        #Format the dates into the correct format before creating the endpoint.
        return self.TEAM_OFFENSE_URL.format(team_id=a_teamID, season=a_season, start_date=self.FormatDate(a_startDate), 
                                            end_date=self.FormatDate(a_endDate))
    
    def GetGeneralPlayerInfoEndpoint(self, a_playerID):
        """Gets the endpoint URL to get basic player information.

        Args:
            a_playerID (int): The player ID used by the MLB API to represent the player.

        Returns:
            A string representing the URL endpoint required to retrieve the player information.
        """
        return self.GENERAL_PLAYER_INFO_URL.format(player_id=a_playerID)
    
    def GetIndividualHittingEndpoint(self, a_playerID, a_season, a_startDate, a_endDate):
        """Gets the endpoint URL to analyze individual hitting statistics.

        Args:
            a_playerID (int): The player ID used by the MLB API to represent the hitter. 
            a_season (int): The season to get the statistics from.
            a_startDate (datetime): The date representing the start of the date range to extract the stats from.
            a_endDate (datetime): The date representing the end of the date range to extract the stats from.

        Returns:
            A string representing the URL endpoint required to retrieve the hitting statistics.
        """
        #Format the dates into the correct format before creating the endpoint.
        return self.INDIVIDUAL_HITTING_URL.format(player_id=a_playerID, season=a_season, start_date=self.FormatDate(a_startDate), 
                                                  end_date=self.FormatDate(a_endDate))

    def GetIndividualPitchingEndpoint(self, a_playerID, a_season, a_startDate, a_endDate):
        """Gets the endpoint URL to analyze individual pitching statistics.
      
        Args:
            a_playerID (int): The player ID used by the MLB API to represent the pitcher. 
            a_season (int): The season to get the statistics from.
            a_startDate (datetime): The date representing the start of the date range to extract the stats from.
            a_endDate (datetime): The date representing the end of the date range to extract the stats from.

        Returns:
            A string representing the URL endpoint required to retrieve the pitching statistics.
        """
        #Format the dates into the correct format before creating the endpoint.
        return self.INDIVIDUAL_PITCHING_URL.format(player_id=a_playerID, season=a_season, start_date=self.FormatDate(a_startDate), 
                                                   end_date=self.FormatDate(a_endDate))
    
    def GetTodayScheduleEndpoint(self, a_startDate, a_endDate):
        """Gets the endpoint URL to analyze the schedule for a given day(s).

        If the start date is not the same as the end date, the schedule of every day in that date range is returned. If the dates are the same, 
        the schedule for that day only is returned.
        
        Args:
            a_startDate (datetime): The date representing the start of the schedules to be returned.
            a_endDate (datetime): The date representing the end of the schedules to be returned.

        Returns:
            A string representing the URL endpoint required to retrieve a single or multiple schedules. 
        """
        return self.TODAY_SCHEDULE_URL.format(start_date=self.FormatDate(a_startDate), end_date=self.FormatDate(a_endDate))
    
    def GetTeamGameLogEndpoint(self, a_teamID, a_season, a_startDate, a_endDate):
        """Gets the endpoint URL to analyze a game log for a team in a specific date range.

        Args:
            a_teamID (int): The team ID used by the MLB API to represent the team.
            a_season (int): The season to get the game log from.
            a_startDate (datetime): The date representing the start of game log.
            a_endDate (datetime): The date representing the end of the game log.

        Returns:
            A string representing the URL endpoint required to retrieve a team's game log.
        """
        return self.TEAM_GAME_LOG_URL.format(team_id=a_teamID, season=a_season, start_date=self.FormatDate(a_startDate),
                                             end_date=self.FormatDate(a_endDate))
        
    def GetStandingsEndpoint(self, a_date, a_season):
        """Gets the endpoint URL to analyze the standings on a specific date (used for obtaining team records).

        Args:
            a_date (datetime): The specific date to get the standings from.
            a_season (int): The season to get the standings from.

        Returns:
            A string representing the URL endpoint required to retrieve the standings.
        """
        return self.STANDINGS_URL.format(date=self.FormatDate(a_date), season=a_season)
    
    def GetHittingGameLogEndpoint(self, a_playerID, a_season, a_startDate):
        """Gets the endpoint URL to analyze the game log for a specific hitter.

        Args:
            a_playerID (int): The player ID used by the MLB API to represent the hitter. 
            a_season (int): The season to get the game log from.
            a_startDate (datetime): The date representing the start of game log.

        Returns:
            A string representing the URL endpoint required to retrieve a hitter's game log.
        """
        #Format the dates into the correct format before creating the endpoint.
        return self.HITTING_GAME_LOG_URL.format(player_id=a_playerID, season=a_season, start_date=self.FormatDate(a_startDate))
    
    def GetPitchingGameLogEndpoint(self, a_playerID, a_season, a_startDate, a_endDate):
        """Gets the endpoint URL to analyze the game log for a specific pitcher.

        Args:
            a_playerID (int): The player ID used by the MLB API to represent the pitcher. 
            a_season (int): The season to get the game log from.
            a_startDate (datetime): The date representing the start of game log.
            a_endDate (datetime): The date representing the end of the game log.

        Returns:
            A string representing the URL endpoint required to retrieve a pitcher's game log.
        """
        #Format the dates into the correct format before creating the endpoint.
        return self.PITCHING_GAME_LOG_URL.format(player_id=a_playerID, season=a_season, start_date=self.FormatDate(a_startDate), 
                                                 end_date=self.FormatDate(a_endDate))

    def GetCareerHittingNumbersEndpoint(self, a_hitterID, a_pitcherID):
        """Gets the endpoint URL to analyze a hitter's career numbers off a specific pitcher.

        Args:
            a_hitterID (int): The player ID used by the MLB API to represent the hitter. 
            a_pitcherID (int): The player ID used by the MLB API to represent the pitcher.

        Returns:
            A string representing the URL endpoint required to retrieve a hitter's career numbers off a specific pitcher. 
        """
        return self.CAREER_HITTING_NUMBERS_URL.format(hitter_id=a_hitterID, pitcher_id=a_pitcherID)
    
    def GetPlayerIDLookupEndpoint(self, a_playerName):
        """Gets the endpoint URL to look up a player ID, given a player's name.

        Args:
            a_playerName (string): The name of a player being searched for.

        Returns:
            A string representing the URL endpoint required to search for a player's MLB API player ID.
        """
        return self.ID_LOOKUP_URL.format(player_name=a_playerName)
    
    def GetLRHitterSplitsEndpoint(self, a_playerID, a_season):
        """Gets the endpoint URL to look up a hitter's lefty/righty splits for a season.

        Args:
            a_playerID (int): The player ID used by the MLB API to represent the hitter.
            a_season (int): The season to get the splits from.

        Returns:
            A string representing the URL endpoint required to retrieve the L/R hitting splits.
        """
        return self.LEFTY_RIGHTY_SPLITS_HITTER_URL.format(player_id=a_playerID, season=a_season)
    
    def GetLRPitcherSplitsEndpoint(self, a_playerID, a_season):
        """Gets the endpoint URL to look up a hitter's lefty/righty splits for a season.
        
        Args:
            a_playerID (int): The player ID used by the MLB API to represent the pitcher.
            a_season (int): The season to get the splits from.

        Returns:
            A string representing the URL endpoint required to retrieve the L/R pitching splits.
        """
        return self.LEFTY_RIGHTY_SPLITS_PITCHER_URL.format(player_id=a_playerID, season=a_season)
    
    def GetWeatherEndpoint(self, a_APIKey, a_city):
        """Gets the endpoint URL to look up get the hourly forecast of a city.
        
        Args:
            a_APIKey (string): The API key used to access the Weather API.
            a_city (string): The city to get the weather forecast for.

        Returns:
            A string representing the URL endpoint required to retrieve the weather forecast.
        """
        return self.WEATHER_URL.format(API_key=a_APIKey, city=a_city)
    
    def GetAllHittersEndpoint(self, a_season, a_offset):
        """Gets the endpoint URL to get a full list of qualified hitters for a specific season.

        An offset is required to this method because the data returned from the MLB API can only contain a maximum of 50 
        qualified players at a time, and there will almost always be more than 50 qualified hitters in any season.
        
        Args:
            a_season (int): The season to get qualified hitters from.
            a_offset (int): The offset related to which index to start the list from.

        Returns:
            A string representing the URL endpoint required to retrieve the qualified hitter list.
        """
        return self.ALL_HITTERS_URL.format(season=a_season, offset=a_offset)