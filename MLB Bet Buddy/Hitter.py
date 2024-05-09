#********************************************************************************************************************************
# Author: Ian Pluchino                                                                                                          *
# Class: Hitter class                                                                                                           *
# Description: Handles everything regarding an MLB hitter. Child to the Player class.                                           *
# Date: 5/2/24                                                                                                                  *
#********************************************************************************************************************************

from Endpoints import Endpoints
from Player import Player
import math
from datetime import datetime, timedelta

class Hitter(Player):
    #CONSTANTS
    #Minimum batting average required for each classification of hitting.
    ON_FIRE_BA_MINIMUM = 'Omitted'
    HOT_BA_MINIMUM = 'Omitted'
    AVERAGE_BA_MINIMUM = 'Omitted'
    COOL_BA_MINIMUM = 'Omitted'
    ICE_COLD_BA_MINIMUM = 'Omitted'

    #Weights for each classification of hitting.
    ON_FIRE_WEIGHT = 'Omitted'
    HOT_WEIGHT = 'Omitted'
    AVERAGE_WEIGHT = 'Omitted'
    COOL_WEIGHT = 'Omitted'
    ICE_COLD_WEIGHT = 'Omitted'

    #CONSTRUCTOR - default hitter ID is Aaron Judge from the NYY.
    def __init__(self, a_hitterID = 592450):
        """Constructor for the Hitter class.

        This constructor is used to create and initialize and Hitter object. The hitter ID provided to the constructor
        is set as a member variable. If a hitter ID is not provided, Aaron Judge's player ID is used by default.

        Args:
            a_hitterID (int): The ID used by the MLB API to represent a hitter.
            
        Returns:
            Nothing.
        """
        super().__init__(a_hitterID) 
        
    #Data gathering functions.
    #Gets the general offensive statistics of a player within a certain date range.
    def GetOffensiveStatistics(self, a_season, a_startDate, a_endDate):
        """Gets the general offensive statistics for a hitter within a date range.

        This method is used to extract offensive statistics for a hitter within a date range from the MLB API. If 
        there are any errors with the date range, or the stats could not be found, an empty dictionary is returned.

        Args:
            a_season (int): The season to get the offensive statistics for.
            a_startDate (datetime): The date representing the start of the date range to consider.
            a_endDate (datetime): The date representing the end of the date range to consider.

        Returns:
            A dictionary, representing the offensive statistics of a hitter from within the provided date range. Stats
            such as the number of hits, batting average, OBP, OPS, and the number of home runs are included.
        """
        #Create the offensive statistics endpoint for an individual hitter.
        individualHittingEndpoint = self.m_endpointObj.GetIndividualHittingEndpoint(self.m_playerID, a_season, a_startDate, a_endDate)
        
        #Access the created endpoint and store the data.
        individualHittingData = self.m_endpointObj.AccessEndpointData(individualHittingEndpoint)    

        #Making sure the player ID being used actually exists and stats were returned by the API.
        if 'people' not in individualHittingData or 'stats' not in individualHittingData['people'][0]:
            return {}
        
        #Making sure the player has played within the given timeframe.
        splits = individualHittingData['people'][0]['stats'][0]['splits']    
        if not splits:
            return {}
        
        #Sometimes a player may play on multiple teams due to in season trades, so there are splits for each individual team. The last split provided is cumulative stats (that's why -1).
        cumulativeStats = splits[-1]['stat']
        
        #Gather all of the offensive statistics.
        fullName = individualHittingData['people'][0]['fullName']
        gamesPlayed = int(cumulativeStats['gamesPlayed'])
        plateAppearances = int(cumulativeStats['plateAppearances'])
        hits = int(cumulativeStats['hits'])
        battingAverage = float(cumulativeStats['avg'])
        OBP = float(cumulativeStats['obp'])
        OPS = float(cumulativeStats['ops'])
        homeRuns = int(cumulativeStats['homeRuns'])

        return { 'fullName': fullName,
                 'gamesPlayed': gamesPlayed,
                 'plateAppearances': plateAppearances,
                 'hits': hits,
                 'battingAverage': battingAverage,
                 'OBP': OBP,
                 'OPS': OPS,
                 'homeRuns': homeRuns }
    
    #Gets the career offensive statistics off a specific provided pitcher.
    def GetCareerStatsOffPitcher(self, a_pitcherID):
        """Gets a hitter's career statistics off of a pitcher.

        This method is used to get a hitter's career statistics off of a specific pitcher. If the pitcher could not 
        be found in the MLB API, an empty dictionary is returned. It is also checked to make sure that the hitter has 
        faced the pitcher at least once. If they haven't, an empty dictionary is returned since the statistics do not 
        exist.

        Args:
            a_pitcherID (int): The ID used by the MLB API to represent the opposing pitcher.

        Returns:
            A dictionary, representing the hitter's career numbers when facing the provided pitcher. Stats such  as the
            number of plate appearances, hits, batting average, OBP, OPS, and the number of home runs are included.
        """
        #Create the endpoint to find the career statistics.
        careerHittingStatisticsEndpoint = self.m_endpointObj.GetCareerHittingNumbersEndpoint(self.m_playerID, a_pitcherID)
        
        #Access the created endpoint and store the data.
        careerHittingStatistics = self.m_endpointObj.AccessEndpointData(careerHittingStatisticsEndpoint)
        
        #Make sure the hitter ID provided is valid and could be found. 0 is returned to indicate no career stats could be found.
        if 'people' not in careerHittingStatistics:
            return {}
        
        #Also make sure that the pitcher ID provided is valid and the hitter has career statistics against them. 0 is returned to indicate no career stats could be found.
        splits = careerHittingStatistics['people'][0]['stats'][0]['splits']
        if not splits:
            #Either the pitcher ID is invalid, or the hitter has never faced the pitcher so there will be no statistics returned from the MLB API.
            return {}
        
        #If both the hitter and pitcher exists, extract the career hitting statistics the hitter has against the pitcher.
        stats = splits[0]
        hitterFullName = stats['batter']['fullName']
        pitcherFullName = stats['pitcher']['fullName']
        
        #Gather the offensive statistics and return them. Note: OBP stands for on base percentage, OPS stands for on base plus slugging.
        gamesPlayed = int(stats['stat']['gamesPlayed'])
        plateAppearances = int(stats['stat']['plateAppearances'])
        hits = int(stats['stat']['hits'])
        battingAverage = float(stats['stat']['avg'])
        OBP = float(stats['stat']['obp'])
        OPS = float(stats['stat']['ops'])
        homeRuns = int(stats['stat']['homeRuns'])
        
        #Stats are returned as a dictionary containing all of the information.
        return { 'hitterName': hitterFullName,
                 'pitcherName': pitcherFullName,
                 'gamesPlayed': gamesPlayed,
                 'plateAppearances': plateAppearances,
                 'hits': hits,
                 'battingAverage': battingAverage,
                 'OBP': OBP,
                 'OPS': OPS,
                 'homeRuns': homeRuns }
    
    #Determines the offensive statistics against left handed-pitchers and right-handed pitchers in a specified season.
    def GetLRHittingSplits(self, a_season):
        """Gets the lefty-righty splits for a hitter.

        This method retrieves lefty-righty splits for a hitter, meaning their stats against left-handed and
        right-handed pitchers. If there are any errors with the date range, or if any stats are missing for a
        specific split, that split is omitted from the return dictionary. Sometimes a player can have multiple splits
        returned by the MLB API if they were traded to another team mid-season, but this method ensures that only the
        season long combined splits are returned.

        Args:
            a_season (int): The season to get the hitting splits for.

        Returns:
            A dictionary containing the batting average against, strikeouts per 9 innings, and home runs per 9
            innings for each split, vs. left-handed hitters and vs. right-handed hitters.
        """
        #Create the lefty/righty splits endpoint for hitters.
        LRSplitsEndpoint = self.m_endpointObj.GetLRHitterSplitsEndpoint(self.m_playerID, a_season)
        
        #Access the created endpoint and store the data.
        LRSplitsData = self.m_endpointObj.AccessEndpointData(LRSplitsEndpoint)
        
        #Make sure the player ID provided is valid and could be found. 0 is returned to indicate the player could not be found, and therefore it was not possible to find the lefty/righty splits.
        if 'people' not in LRSplitsData:
            return {}
        
        #Important note: Not every player may have faced both types of pitchers yet at specific points in the provided season, or they may not have played at all in the provided season.
        splits = LRSplitsData['people'][0]['stats'][0]['splits']
        
        #Loop through the possible splits. There can be 0, 1, or 2 depending on the player and season.
        resultDictionary = {'fullName': LRSplitsData['people'][0]['fullName']}
        for index in range(len(splits)):
            splitName = splits[index]['split']['description']
            
            #Extracting the actual statistics for the individual split.
            splitStats = splits[index]['stat']
            plateAppearances = int(splitStats['plateAppearances'])
            hits = int(splitStats['hits'])
            battingAverage = float(splitStats['avg'])
            OBP = float(splitStats['obp'])
            OPS = float(splitStats['ops'])
            homeRuns = float(splitStats['homeRuns'])
            
            #Building a dictionary for the individual split.
            splitDictionary = { splitName: { 'plateAppearances': plateAppearances,
                                             'hits': hits,
                                             'battingAverage': battingAverage,
                                             'OBP': OBP,
                                             'OPS': OPS,
                                             'homeRuns': homeRuns }
                              }
            
            #Adding the individual split to the final result dictionary.
            resultDictionary.update(splitDictionary)
             
        return resultDictionary
    
    #Finds and returns a hitter's last 10 games offensive statistics, given a starting date to search from.
    def Last10Stats(self, a_season, a_date):
        """Gets a hitter's offensive statistics in their last 10 games.

        This method is used to get a hitter's offensive statistics considering only their last 10 games. First, 
        the hitter's entire game log is extracted from the MLB API, starting from the date provided. Then, 
        starting from a week back, the hitter's stats are extracted. This range is incremented by 1 day and the 
        process is repeated until the player has a total of at least 10 games played in the range (example: last 7 
        days --> last 8 days --> last 9 days...). Once the games played requirement has been met, the offensive stats 
        are extracted and returned (see GetOffensiveStatistics()). If the hitter has not played in 10 games within 3 
        weeks of the starting date, an empty dictionary is returned as the hitter does not have recent offensive 
        statistics.

        Args:
            a_season (int): The season to get the hitter's last 10 games stats from.
            a_date (datetime): The starting date to get the hitter's last 10 game stats from.

        Returns:
            A dictionary, representing the offensive statistics of a hitter from their last 10 games. Stats such
            as the number of hits, batting average, OBP, OPS, and the number of home runs are included.
        """
        #Will act as the ending date for the date range.
        endDate = a_date

        #The starting date of the search will be a week away from the end just in case of double headers (which are rare, but occur when two games are played on the same day).
        startDate = a_date - timedelta(days=7)

        #If the player has not played 10 games in the last 3 weeks from the date, the data isn't recent enough and shouldn't be used.
        maximumDate = a_date - timedelta(days=21)
        
        #Loop through each range of dates, decrementing the end date by 1 day each time until the closing date is reached.
        while startDate > maximumDate:
            hittingStatistics = self.GetOffensiveStatistics(a_season, startDate, endDate)
            
            #Make sure hitting statistics were found in the date range to avoid crashing.
            if hittingStatistics == {}:
                startDate -= timedelta(days=1)
                continue

            gamesPlayed = hittingStatistics['gamesPlayed']
            if gamesPlayed >= 10:
                #If 10 games played was found, add the date range used to the return dictionary and return it.
                hittingStatistics['startDateRange'] = startDate.strftime('%m/%d/%Y')
                hittingStatistics['endDateRange'] = endDate.strftime('%m/%d/%Y')
                
                return hittingStatistics

            #Expand the range of dates to keep searching for the player's last 10 games.
            startDate -= timedelta(days=1)
            
        #If the maximum date range was reached and the player hasn't played 10 games, return an empty dictionary to represent there was not enough data from the starting date.
        return {}
    
    #Classify a batting average into one of five categories and assign its weight (used for creating hitting predictions).
    def ClassifyHitting(self, a_BA):
        """Classify a batting average into one of five categories and assign its weight.

        This method is used to determine how well a hitter is doing, based on their batting average. One of five
        categories is determined, and the respective weight for that category is returned from this function.

        Args:
            a_BA (float): The batting average of the hitter in question.

        Returns:
            A tuple, containing a string representing the hot/cold description and a float representing the 
            hot/cold factor for a hitter which is used for creating hitting bet predictions.
        """
        #Determine the classification for the hitter based on their batting average.
        if a_BA >= self.ON_FIRE_BA_MINIMUM:
            return 'On Fire', self.ON_FIRE_WEIGHT
        elif a_BA >= self.HOT_BA_MINIMUM:
            return 'Hot', self.HOT_WEIGHT
        elif a_BA >= self.AVERAGE_BA_MINIMUM:
            return 'Average', self.AVERAGE_WEIGHT
        elif a_BA >= self.COOL_BA_MINIMUM:
            return 'Cool', self.COOL_WEIGHT
        else:
            return 'Ice Cold', self.ICE_COLD_WEIGHT
        
    #Checks to see if a game was played on the provided date, and returns whether or not a hitter achieved certain beting goals during that game.
    def HittingBetReview(self, a_gameDate):
        """Determines the betting benchmarks a hitter achieved, on a specific day for bet accuracy checking.

        This method first checks to see if the hitter played on the given date. If they have, the number of hits,
        runs, and RBIs are extracted from the game for the hitter. Then, it is checked if the hitter has achieved at
        least 1 hit, at least 2 hits, at least 2 hits + runs + RBIs, and at least 3 hits + runs + RBIs. The results
        are recorded in a dictionary.

        Args:
            a_gameDate (string): The date of the game being reviewed as a string (ex: 05/15/2024).

        Returns:
            A dictionary containing several betting benchmarks, and whether the hitter reached them. The
            benchmarks included are at least 1 hit, at least 2 hits, at least 2 hits + runs + RBIs, and at least 3
            hits + runs + RBIs. If the player did not play on the given date, an empty dictionary is returned.
        """
        #Extract the season year from the game date.
        gameDatetimeObj = datetime.strptime(a_gameDate, '%m/%d/%Y')
        season = gameDatetimeObj.year
        
        #Create the endpoint to access a hitter's game log, and access the data from that endpoint.
        hitterGameLogEndpoint = self.m_endpointObj.GetHittingGameLogEndpoint(self.m_playerID, season, gameDatetimeObj)
        hitterGameLogData = self.m_endpointObj.AccessEndpointData(hitterGameLogEndpoint)
        
        #Make sure the game log exists for the hitter.
        if 'stats' not in hitterGameLogData or not hitterGameLogData['stats'] or not hitterGameLogData['stats'][0]['splits']:
            return {}
        
        #Extract the first game in the hitter's game log. This will always be the game closest to the provided date to this function.
        gameLog = hitterGameLogData['stats'][0]['splits']
        firstGame = gameLog[0]
        
        #Check the date of the closest game.
        firstGameDate = datetime.strptime(firstGame['date'], '%Y-%m-%d').strftime('%m/%d/%Y')
        
        #If the dates do not match with what is provided to this function, then the player did not play that day (the player may have had an off-day).
        if firstGameDate != a_gameDate:
            return {}
        
        #Otherwise, the player did play on the specified date. Extract their stats from that day. 
        stats = firstGame['stat']
        summary = stats['summary']
        hits = int(stats['hits'])
        runsScored = int(stats['runs'])
        RBIs = int(stats['rbi'])
        HitsPlusRunsPlusRBIs = hits + runsScored + RBIs
        
        #Check to see if the hitter accomplished certain bet goals on that day. Note: HRR = Hits, Runs, and RBIs combined.
        atLeast1Hit = hits >= 1
        atLeast2Hits = hits >= 2
        atLeast2HHR = HitsPlusRunsPlusRBIs >= 2
        atLeast3HHR = HitsPlusRunsPlusRBIs >= 3
        
        #Compile all results into a single dictionary, and return it.
        betReviewDictionary = { 'summary': summary,
                                'hits': hits,
                                'runsScored': runsScored,
                                'RBIs': RBIs,
                                'atLeast1Hit': atLeast1Hit,
                                'atLeast2Hits': atLeast2Hits,
                                'atLeast2HRR': atLeast2HHR,
                                'atLeast3HRR': atLeast3HHR }

        return betReviewDictionary        

    #Static method to return a list of all the qualified hitters of a season.
    @staticmethod
    def GetAllHitters(a_season):
        """Gets a list of all qualified hitters for a season.

        This method is used to get all "qualified" hitters for a provided season. A qualified hitter is a hitter that 
        has at least 3.1 plate appearances per game played. To get all the qualified hitters, this method repeatedly 
        calls the qualified hitter endpoint with different offsets. This is because the MLB API can only return 50 
        players at a time, so an offset is used to get the entire list of qualified hitters. Each player is then 
        appended to a return list.

        Args:
            a_season (int): The season to get the qualified hitters for.

        Returns:
            A list of dictionaries where each dictionary represents a qualified hitter. Information such as the
            player's full name, player ID, team name and ID, games played, and total plate appearances on the season
            are included.
        """
        #Create a temporary endpoint object.
        tempEndpointObj = Endpoints()
        
        #Create the endpoint to obtain a list of all hitters and access the data from the endpoint.
        allHittersEndpoint = tempEndpointObj.GetAllHittersEndpoint(a_season, 0)
        allHittersData = tempEndpointObj.AccessEndpointData(allHittersEndpoint)
        
        #Obtain the total number of players that need to be recorded. 
        #Note: Only 50 players are returned from the API at a time, and those 50 determined by an offset. The number of API calls is found by taking the total number of players and dividing by 50.
        totalPlayers = allHittersData['stats'][0]['totalSplits']
        totalAPICalls = math.ceil(totalPlayers/50)
        
        #Continue calling the API until all qualified players have been collected.
        hittersList = []
        for APICallNumber in range(totalAPICalls):
            currentOffset = APICallNumber * 50
            
            #For each offset, create a new endpoint and access the data from that endpoint.
            currentHittersEndpoint = tempEndpointObj.GetAllHittersEndpoint(a_season, currentOffset)
            currentHittersData = tempEndpointObj.AccessEndpointData(currentHittersEndpoint)
            
            #Extract the list of all 50 players returned by the API.
            hitters = currentHittersData['stats'][0]['splits']
            
            #Loop through each of the hitters to make sure they are qualified. If they are, add them to the result list.
            for hitter in hitters:
                gamesPlayed = int(hitter['stat']['gamesPlayed'])
                plateAppearances = int(hitter['stat']['plateAppearances'])
                
                #Note: Qualified hitters have 3.1 plate appearances per game played. Ensure that the hitter has reached that mark.
                qualifiedPlateAppearances = gamesPlayed * 3.1
                if plateAppearances >= qualifiedPlateAppearances:
                    #If the hitter is qualified and has played a minimum of 30 games, add them to the result list.
                    playerName = hitter['player']['fullName']
                    playerID = hitter['player']['id']
                    teamName = hitter['team']['name']
                    teamID = hitter['team']['id']
                    
                    playerInfo = { 'playerName': playerName, 
                                   'playerID': playerID,
                                   'teamName': teamName,
                                   'teamID': teamID,
                                   'gamesPlayed': gamesPlayed,
                                   'plateAppearances': plateAppearances }
                    
                    hittersList.append(playerInfo)

        return hittersList