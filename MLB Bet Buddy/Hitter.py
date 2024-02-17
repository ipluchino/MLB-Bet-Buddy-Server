#HITTER CLASS. Child to Player class to handle everything regarding a hitter.

from Endpoints import Endpoints
from Player import Player

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
        totalHits = int(stats['stat']['hits'])
        battingAverage = float(stats['stat']['avg'])
        OBP = float(stats['stat']['obp'])
        OPS = float(stats['stat']['ops'])
        homeRuns = float(stats['stat']['homeRuns'])
        
        #Stats are returned as a dictionary containing all of the information.
        return { 'hitterName': hitterFullName,
                 'pitcherName': pitcherFullName,
                 'gamesPlayed': gamesPlayed,
                 'plateAppearances': plateAppearances,
                 'totalHits': totalHits,
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
        
        #Making sure the hitter ID being used actually exists.
        if 'people' not in individualHittingData:
            return 0
        
        #Validate that the data could be found (in case an invalid date range is entered or the player did not play during a date range).
        splits = individualHittingData['people'][0]['stats'][0]['splits']    
        if not splits:
            return 0
        
        #Sometimes a player may play on multiple teams due to in season trades, so there are splits for each individual team. The last split provided is cumulative stats (that's why -1).
        cumulativeStats = splits[-1]['stat']
        
        #Gather all of the offensive statistics.
        fullName = individualHittingData['people'][0]['fullName']
        battingAverage = cumulativeStats['avg']
        OBP = cumulativeStats['obp']
        OPS = cumulativeStats['ops']
        homeRuns = cumulativeStats['homeRuns']

        return { 'fullName': fullName,
                 'battingAverage': battingAverage,
                 'OBP': OBP,
                 'OPS': OPS,
                 'homeRuns': homeRuns }
        



        





