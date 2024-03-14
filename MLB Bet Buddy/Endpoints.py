#ENDPOINTS CLASS. Contains everything regarding endpoints to the MLB API.

from datetime import datetime
import requests
import time

class Endpoints():
    #All API endpoint links that will be used in the project. Variable portions of the URL are within curly brackets {}. 
    #Base endpoint of the API.
    BASE_URL = 'https://statsapi.mlb.com/api/'
    
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
    
    #Endpoint to get current MLB standings.
    STANDINGS_URL = 'https://statsapi.mlb.com/api/v1/standings?standingsTypes=regularSeason&leagueId=103,104&date={date}&season={season}'

    #Endpoint to gather the game log of a hitter.
    HITTING_GAME_LOG_URL = 'https://statsapi.mlb.com/api/v1/people/{player_id}/stats?stats=gameLog&group=hitting&season={season}&startDate={start_date}&endDate={end_date}'

    #Endpoint to gather the game log of a pitcher.
    PITCHING_GAME_LOG_URL = 'https://statsapi.mlb.com/api/v1/people/{player_id}/stats?stats=gameLog&group=pitching&season={season}&startDate={start_date}&endDate={end_date}'
    
    #Endpoint to get a hitter's career numbers off of a specific pitcher.
    CAREER_HITTING_NUMBERS_URL = 'https://statsapi.mlb.com/api/v1/people?personIds={hitter_id}&hydrate=stats(group=[hitting],type=[vsPlayerTotal],opposingPlayerId={pitcher_id},sportId=1)'
    
    #Endpoint to get the player ID of a player based on their name.
    ID_LOOKUP_URL = 'https://statsapi.mlb.com/api/v1/people/search?names={player_name}'
    
    #Endpoint to get the lefty/righty splits for a hitter.
    LEFTY_RIGHTY_SPLITS_HITTTER_URL = 'https://statsapi.mlb.com/api/v1/people/{player_id}?hydrate=stats(group=[hitting],type=[statSplits],sitCodes=[vr,vl],season={season})'
    
    #Endpoint to get the lefty/righty splits for a pitcher.
    LEFTY_RIGHTY_SPLITS_PITCHER_URL = 'https://statsapi.mlb.com/api/v1/people/{player_id}?hydrate=stats(group=[pitching],type=[statSplits],sitCodes=[vr,vl],season={season})'
    
    #Endpoint to get the hourly weather of a city. Note: Uses Weather API not MLB API.
    WEATHER_URL = 'https://api.weatherapi.com/v1/forecast.json?key={API_key}&q={city}' 
    
    #Endpoint to get a list of all hitters in a specified season.
    ALL_HITTERS_URL = 'https://statsapi.mlb.com/api/v1/stats?stats=season&group=hitting&season={season}&playerPool=QUALIFIED&offset={offset}'        

    #CONSTRUCTOR
    def __init__(self):
        #Create a session object to increase API lookup speed.
        self.session = requests.Session()
    
    #Sends a request to the endpoint and simply returns the data.
    def AccessEndpointData(self, a_URL):
        response = self.session.get(a_URL)
        
        #Occassionaly there is a rare error by the MLB API. It is fixed by simply waiting a short time, then trying again.
        try:
            data = response.json()
            return data
        except:
            print(response.text)
            time.sleep(10)
            return self.AccessEndpoint(a_URL)
            
    
    #Converts a datetime object into the correct string format.
    def FormatDate(self, a_dateObj):
        return a_dateObj.strftime('%m/%d/%Y')

    #Gets the endpoint URL to analyze a specific game.
    def GetGameAnalysisEndpoint(self, a_gameID):
        return self.GAME_ANALYSIS_URL.format(game_id=a_gameID)
    
    #Gets the endpoint URL to analyze team offensive statistics.
    def GetTeamOffensiveEndpoint(self, a_teamID, a_season, a_startDate, a_endDate):
        #Format the dates into the correct format before creating the endpoin
        return self.TEAM_OFFENSE_URL.format(team_id=a_teamID, season=a_season, start_date=self.FormatDate(a_startDate), end_date=self.FormatDate(a_endDate))
    
    #Gets the endpoint URL to get basic player information.
    def GetGeneralPlayerInfoEndpoint(self, a_playerID):
        return self.GENERAL_PLAYER_INFO_URL.format(player_id=a_playerID)
    
    #Gets the endpoint URL to analyze individual hitting statistics.
    def GetIndividualHittingEndpoint(self, a_playerID, a_season, a_startDate, a_endDate):
        #Format the dates into the correct format before creating the endpoint.
        return self.INDIVIDUAL_HITTING_URL.format(player_id=a_playerID, season=a_season, start_date=self.FormatDate(a_startDate), end_date=self.FormatDate(a_endDate))

    #Gets the endpoint URL to analyze individual pitching statistics.
    def GetIndividualPitchingEndpoint(self, a_playerID, a_season, a_startDate, a_endDate):
        #Format the dates into the correct format before creating the endpoint.
        return self.INDIVIDUAL_PITCHING_URL.format(player_id=a_playerID, season=a_season, start_date=self.FormatDate(a_startDate), end_date=self.FormatDate(a_endDate))
    
    #Gets the endpoint URL to analyze the schedule for a given day(s).
    def GetTodayScheduleEndpoint(self, a_startDate, a_endDate):
        return self.TODAY_SCHEDULE_URL.format(start_date=self.FormatDate(a_startDate), end_date=self.FormatDate(a_endDate))
    
    #Gets the endpoint URL to analyze a game log for a team in a specific date range.
    def GetTeamGameLogEndpoint(self, a_teamID, a_season, a_startDate, a_endDate):
        return self.TEAM_GAME_LOG_URL.format(team_id=a_teamID, season=a_season, start_date=self.FormatDate(a_startDate), end_date=self.FormatDate(a_endDate))
        
    #Gets the endpoint URL to analyze the standings on a specific date (used for obtaining team records).
    def GetStandingsEndpoint(self, a_date, a_season):
        return self.STANDINGS_URL.format(date=self.FormatDate(a_date), season=a_season)
    
    #Gets the endpoint URL to analyze the game log for a specific pitcher.
    def GetPitchingGameLogEndpoint(self, a_playerID, a_season, a_startDate, a_endDate):
        #Format the dates into the correct format before creating the endpoint.
        return self.PITCHING_GAME_LOG_URL.format(player_id=a_playerID, season=a_season, start_date=self.FormatDate(a_startDate), end_date=self.FormatDate(a_endDate))
    
    #Gets the endpoint URL to analyze the game log for a specific hitter.
    def GetHittingGameLogEndpoint(self, a_playerID, a_season, a_startDate, a_endDate):
        #Format the dates into the correct format before creating the endpoint.
        return self.HITTING_GAME_LOG_URL.format(player_id=a_playerID, season=a_season, start_date=self.FormatDate(a_startDate), end_date=self.FormatDate(a_endDate))

    #Gets the endpoint URL to analyze a hitter's career numbers off of a certain pitcher.
    def GetCareerHittingNumbersEndpoint(self, a_hitterID, a_pitcherID):
        return self.CAREER_HITTING_NUMBERS_URL.format(hitter_id=a_hitterID, pitcher_id=a_pitcherID)
    
    #Gets the endpoint URL to look up a player ID, given a player's name.f
    def GetPlayerIDLookupEndpoint(self, a_playerName):
        return self.ID_LOOKUP_URL.format(player_name=a_playerName)
    
    #Gets the endpoint URL to look up a hitter's lefty/righty splits for a season.
    def GetLRHitterSplitsEndpoint(self, a_playerID, a_season):
        return self.LEFTY_RIGHTY_SPLITS_HITTTER_URL.format(player_id=a_playerID, season=a_season)
    
    #Gets the endpoint URL to look up a hitter's lefty/righty splits for a season.
    def GetLRPitcherSplitsEndpoint(self, a_playerID, a_season):
        return self.LEFTY_RIGHTY_SPLITS_PITCHER_URL.format(player_id=a_playerID, season=a_season)
    
    #Gets the endpoint URL to look up the weather at a specific city and time.
    def GetWeatherEndpoint(self, a_APIKey, a_city):
        return self.WEATHER_URL.format(API_key=a_APIKey, city=a_city)
    
    #Gets the endpoint URL to get a full list of qualified hitters for a specified season.
    def GetAllHittersEndpoint(self, a_season, a_offset):
        return self.ALL_HITTERS_URL.format(season=a_season, offset=a_offset)

    
    
    
    
    


    




