#HITTER CLASS. Child to Player class to handle everything regarding a hitter.

from Endpoints import Endpoints
from Player import Player
import math

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
            return 0
        
        #Also make sure that the pitcher ID provided is valid and the hitter has career statistics against them. 0 is returned to indicate no career stats could be found.
        splits = careerHittingStatistics['people'][0]['stats'][0]['splits']
        if not splits:
            #Either the pitcher ID is invalid, or the hitter has never faced the pitcher so there will be no statistics returned from the MLB API.
            return 0
        
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
        #Create the team offensive statistics endpoint for an individual hitter.
        individualHittingEndpoint = self.m_endpointObj.GetIndividualHittingEndpoint(self.m_playerID, a_season, a_startDate, a_endDate)
        
        #Access the created endpoint and store the data.
        individualHittingData = self.m_endpointObj.AccessEndpointData(individualHittingEndpoint)    

        #Making sure the hitter ID being used actually exists and stats were returned by the API.
        if 'people' not in individualHittingData or 'stats' not in individualHittingData['people'][0]:
            return 0
        
        #Making sure the player has played within the given timeframe.
        splits = individualHittingData['people'][0]['stats'][0]['splits']    
        if not splits:
            return 0
        
        #Sometimes a player may play on multiple teams due to in season trades, so there are splits for each individual team. The last split provided is cumulative stats (that's why -1).
        cumulativeStats = splits[-1]['stat']
        
        #Gather all of the offensive statistics.
        fullName = individualHittingData['people'][0]['fullName']
        plateAppearances = cumulativeStats['plateAppearances']
        hits = cumulativeStats['hits']
        battingAverage = cumulativeStats['avg']
        OBP = cumulativeStats['obp']
        OPS = cumulativeStats['ops']
        homeRuns = cumulativeStats['homeRuns']

        return { 'fullName': fullName,
                 'plateAppearances': plateAppearances,
                 'hits': hits,
                 'battingAverage': battingAverage,
                 'OBP': OBP,
                 'OPS': OPS,
                 'homeRuns': homeRuns }
    
    #Determines the offensive statistics against left handed pitchers and right handed pitchers in a specified season.
    def GetLRSplits(self, a_season):
        #Create the lefty/righty splits endpoint for hitters.
        LRSplitsEndpoint = self.m_endpointObj.GetLRHitterSplitsEndpoint(self.m_playerID, a_season)
        
        #Access the created endpoint and store the data.
        LRSplitsData = self.m_endpointObj.AccessEndpointData(LRSplitsEndpoint)
        
        #Make sure the hitter ID provided is valid and could be found. 0 is returned to indicate the player could not be found, and therefore it was not possible to find the lefty/righty splits.
        if 'people' not in LRSplitsData:
            return 0
        
        #Extract the split data as well as the number of splits that were returned by the endpoint.
        #Important note: Not every player may have faced both types of pitchers yet at specific points in the provided season, or they may not have played at all in the provided season.
        splits = LRSplitsData['people'][0]['stats'][0]['splits']
        
        #Loop through the possible splits. There can be 0, 1, or 2 depending on the player and season.
        resultDictionary = {'fullName': LRSplitsData['people'][0]['fullName']}
        for index in range(len(splits)):
            splitName = splits[index]['split']['description']
            
            #Extracting the actual statistics for the split.
            splitStats = splits[index]['stat']
            plateAppearances = splitStats['plateAppearances']
            hits = splitStats['hits']
            battingAverage = splitStats['avg']
            OBP = splitStats['obp']
            OPS = splitStats['ops']
            homeRuns = splitStats['homeRuns']
            
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
        

        

        



        





