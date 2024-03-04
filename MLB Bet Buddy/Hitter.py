#HITTER CLASS. Child to Player class to handle everything regarding a hitter.

from Endpoints import Endpoints
from Player import Player
import math
from datetime import datetime, timedelta

class Hitter(Player):
    #CONSTRUCTOR - default hitter ID is Aaron Judge from the NYY.
    #Assistance: https://www.geeksforgeeks.org/calling-a-super-class-constructor-in-python/
    def __init__(self, a_hitterID = 592450):
        super().__init__(a_hitterID) 
        
    #Data gathering functions.
    #Gets the career offensive statistics off a specific provided pitcher.
    def GetCareerStatsOffPitcher(self, a_pitcherID):
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
        
    #Gets the general offensive statistics of a player within a certain date range.
    def GetOffensiveStatistics(self, a_season, a_startDate, a_endDate):
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
    
    #Determines the offensive statistics against left handed pitchers and right handed pitchers in a specified season.
    def GetLRHittingSplits(self, a_season):
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
        #Will act as the ending date for the date range.
        endDate = a_date       

        #The starting date of the search will be a week away from the end just in case of double headers (which are rare, but occur when two games are played on the same day).
        startDate = a_date - timedelta(days=7)

        #If the player has not played 10 games in the last 3 weeks from the date, the data isn't recent enough and shouldn't be used.
        maximumDate = a_date - timedelta(days=21)
        
        #Loop through each range of dates, decrementing the end date by 1 day each time until the closing date is reached.
        while startDate > maximumDate:
            hittingStatistics = self.GetOffensiveStatistics(a_season, startDate, endDate)
            
            #Make sure hitting statistics were found in the date range to avoid crashihng.
            if hittingStatistics == 0:
                startDate -= timedelta(days=1)
                continue

            gamesPlayed = hittingStatistics['gamesPlayed']
            if gamesPlayed == 10:
                #If 10 games played was found, add the date range used to the return dictionary and return it.
                hittingStatistics['startDateRange'] = startDate.strftime('%m/%d/%Y')
                hittingStatistics['endDateRange'] = endDate.strftime('%m/%d/%Y')
                
                return hittingStatistics

            #Expand the range of dates to keep searching for the player's last 10 games.
            startDate -= timedelta(days=1)
            
        #If the maximum date range was reached and the player hasn't played 10 games, return an empty dictionary to represent there was not enough data from the starting date.
        return {}

    #Static method to return a list of all the qualified hitters of a season.
    @staticmethod
    def GetAllHitters(a_season):
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
                
                #Note: Qualified hitters have 3.1 plate appearances per game played. Also, ensure that the player has played at least 30 games so there are valid statistics.
                qualifiedPlateAppearances = gamesPlayed * 3.1
                if gamesPlayed >= 30 and plateAppearances >= qualifiedPlateAppearances:
                    #If the hitter is qualified and has played a minimum of 30 games, add them to the result list.
                    playerName = hitter['player']['fullName']
                    playerID = hitter['player']['id']
                    
                    playerInfo = { 'playerName': playerName, 
                                   'playerID': playerID,
                                   'gamesPlayed': gamesPlayed,
                                   'plateAppearances': plateAppearances }
                    
                    hittersList.append(playerInfo)

        return hittersList
        

        

        



        





