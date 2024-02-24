#Pitcher class. Child to Player class to handle everything regarding a pitcher.

from Endpoints import Endpoints
from Player import Player

class Pitcher(Player):
    #CONSTRUCTOR - default pitcher ID is Gerrit Cole from the NYY.
    #Assistance: https://www.geeksforgeeks.org/calling-a-super-class-constructor-in-python/
    def __init__(self, a_pitcherID = 543037):
        super().__init__(a_pitcherID) 
        
    #Gets the general pitching statistics of a player within a certain date range.
    def GetPitchingStatistics(self, a_season, a_startDate, a_endDate):
        #Create the pitching statistics endpoint for an individual pitcher.
        individualPitchingEndpoint = self.m_endpointObj.GetIndividualPitchingEndpoint(self.m_playerID, a_season, a_startDate, a_endDate)
        
        #Access the created endpoint and store the data.
        individualPitchingData = self.m_endpointObj.AccessEndpointData(individualPitchingEndpoint)

        #Making sure the player ID being used actually exists and stats were returned by the API.
        if 'people' not in individualPitchingData or 'stats' not in individualPitchingData['people'][0]:
            return 0
        
        #Making sure the player has played within the given timeframe.
        splits = individualPitchingData['people'][0]['stats'][0]['splits']    
        if not splits:
            return 0

        #Sometimes a player may play on multiple teams due to in season trades, so there are splits for each individual team. The last split provided is cumulative stats (that's why -1).
        cumulativeStats = splits[-1]['stat']
        
        #Gather all of the necessary pitching statistics.
        fullName = individualPitchingData['people'][0]['fullName']
        gamesStarted = cumulativeStats['gamesPlayed']
        inningsPitched = cumulativeStats['inningsPitched']
        wins = cumulativeStats['wins']
        losses = cumulativeStats['losses']
        #Note: ERA = Earned Run Average and WHIP = Walks and Hits per Innings Pitched. The lower these values, the better the pitcher.
        ERA = cumulativeStats['era']          
        WHIP = cumulativeStats['whip']         
        #Note: The stats below represent the average number strikeouts and homeruns if the pitcher were to pitch a full 9 innings. Higher strikeout rates are better, and lower homerun rates are better.
        strikeoutsPer9Inn = cumulativeStats['strikeoutsPer9Inn']
        homeRunsPer9Inn = cumulativeStats['homeRunsPer9']
        
        return { 'fullName': fullName,
                 'gamesStarted': gamesStarted,
                 'inningsPitched': inningsPitched,
                 'wins': wins,
                 'losses': losses,
                 'ERA': ERA,
                 'WHIP': WHIP,
                 'strikeoutsPer9': strikeoutsPer9Inn,
                 'homeRunsPer9': homeRunsPer9Inn }



