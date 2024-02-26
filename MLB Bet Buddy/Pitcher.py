#Pitcher class. Child to Player class to handle everything regarding a pitcher.

from Endpoints import Endpoints
from Player import Player
from Game import Game

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

    #Calculates the percentage of a pitcher's game where they let up a run in the 1st inning.
    def CalculateYRFIPercentage(self, a_season, a_startDate, a_endDate):
        #Create the pitching game log endpoint.
        pitchingGameLogEndpoint = self.m_endpointObj.GetPitchingGameLogEndpoint(self.m_playerID, a_season, a_startDate, a_endDate)
        
        #Access the data from the endpoint.
        pitchingGameLogData = self.m_endpointObj.AccessEndpointData(pitchingGameLogEndpoint)
        
        #Make sure the player ID was valid, to ensure no errors occur. If 'stats' don't exist in the returned dictionary from the API, an error occurred.
        if 'stats' not in pitchingGameLogData or not pitchingGameLogData['stats']:
            return 0
        
        #Make sure that the date and season provided to the API is valid, and the pitcher has starts within the time range.
        gameLog = pitchingGameLogData['stats'][0]['splits']
        if not gameLog:
            return 0
        
        totalGamesStarted = 0
        YRFIcount = 0
        
        #Loop through each game the pitcher has started within the date range.
        for game in gameLog:
            #Ensure the pitcher actually started the game (and didn't appear as a relief pitcher since some pitchers start games and are bullpen pitchers as well).
            if int(game['stat']['gamesStarted']) == 0:
                continue
            else:
                totalGamesStarted += 1
            
            #Extract the game's ID and create a Game object from that ID.
            gameID = game['game']['gamePk']
            gameObj = Game(gameID)
            
            #Ensure the game has ended. If it hasn't, continue looping through all the games.
            if not gameObj.IsGameFinal():
                continue
            
            #Determine if the pitcher let up a run in the 1st inning for that game.
            if gameObj.DidPitcherLetUpRunFirstInning(self.m_playerID):
                print('Yes', gameObj.GetGameDate())
                YRFIcount += 1
            else:
                print('No', gameObj.GetGameDate())

        #The YRFI rate represents the percentage of games a pitcher let up a run in the 1st inning in their starts. Lower YRFI rates are better.            
        YRFIrate = YRFIcount / totalGamesStarted
        print(totalGamesStarted)
        
        return YRFIrate
        

            
        
        

