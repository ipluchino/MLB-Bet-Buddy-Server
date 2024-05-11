#********************************************************************************************************************************
# Author: Ian Pluchino                                                                                                          *
# Class: Pitcher class                                                                                                          *
# Description: Handles everything regarding an MLB pitcher. Child of the Player class.                                          *
# Date: 5/2/24                                                                                                                  *
#********************************************************************************************************************************

from Player import Player
from Game import Game

class Pitcher(Player):
    #CONSTRUCTOR
    def __init__(self, a_pitcherID = 543037):
        """Constructor for the Pitcher class.

        This constructor is used to create and initialize and Pitcher object. The pitcher ID provided to the constructor
        is set as a member variable. If a pitcher ID is not provided, Gerrit Cole's player ID is used by default.

        Args:
            a_pitcherID (int): The ID used by the MLB API to represent a pitcher.
            
        Returns:
            Nothing.
        """
        super().__init__(a_pitcherID) 
        
    #UTILITY METHODS
    def GetPitchingStatistics(self, a_season, a_startDate, a_endDate):
        """Gets general pitching statistics for a player within a date range.

        This method retrieves several basic pitching statistics for a pitcher, and returns them in the form of a 
        dictionary. If there are any errors with the date range, or the stats could not be found, an empty dictionary 
        is returned.

        Args:
            a_season (int): The season to get the pitching statistics for.
            a_startDate (datetime): The date representing the start of the date range to consider.
            a_endDate (datetime): The date representing the end of the date range to consider.

        Returns:
            A dictionary containing the pitcher's innings pitched, wins, losses, ERA, WHIP, strikeouts per 9 innings and
            home runs per 9 innings.
        """
        #Create the pitching statistics endpoint for an individual pitcher.
        individualPitchingEndpoint = self.m_endpointObj.GetIndividualPitchingEndpoint(self.m_playerID, a_season, a_startDate, a_endDate)
        
        #Access the created endpoint and store the data.
        individualPitchingData = self.m_endpointObj.AccessEndpointData(individualPitchingEndpoint)

        #Making sure the player ID being used exists and stats were returned by the API.
        if 'people' not in individualPitchingData or 'stats' not in individualPitchingData['people'][0]:
            return {}
        
        #Making sure the player has played within the given timeframe.
        splits = individualPitchingData['people'][0]['stats'][0]['splits']    
        if not splits:
            return {}

        #Sometimes a player may play on multiple teams due to in season trades, so there are splits for each individual team. The last split 
        #provided is cumulative stats (that's why -1 is used as the index).
        cumulativeStats = splits[-1]['stat']
        
        #Gather all of the necessary pitching statistics.
        fullName = individualPitchingData['people'][0]['fullName']
        gamesStarted = int(cumulativeStats['gamesStarted'])
        inningsPitched = float(cumulativeStats['inningsPitched'])
        wins = int(cumulativeStats['wins'])
        losses = int(cumulativeStats['losses'])
        #Note: ERA = Earned Run Average and WHIP = Walks and Hits per Innings Pitched. The lower these values, the better the pitcher.
        era = float(cumulativeStats['era'])       
        whip = float(cumulativeStats['whip'])         
        #Note: The stats below represent the average number strikeouts and home runs if the pitcher were to pitch a full 9 innings. Higher 
        #strikeout rates are better, and lower home run rates are better.
        strikeoutsPer9Inn = float(cumulativeStats['strikeoutsPer9Inn'])
        homeRunsPer9Inn = float(cumulativeStats['homeRunsPer9'])
        
        return { 'fullName': fullName,
                 'gamesStarted': gamesStarted,
                 'inningsPitched': inningsPitched,
                 'wins': wins,
                 'losses': losses,
                 'ERA': era,
                 'WHIP': whip,
                 'strikeoutsPer9': strikeoutsPer9Inn,
                 'homeRunsPer9': homeRunsPer9Inn }
    
    def GetLRPitchingSplits(self, a_season):
        """Gets the lefty-righty splits for a pitcher.

        This method retrieves lefty-righty splits for a pitcher, meaning their stats against left-handed and 
        right-handed hitters. If there are any errors with the date range, or if any stats are missing for a specific 
        split, that split is omitted from the return dictionary. Sometimes a player can have multiple splits returned 
        by the MLB API if they were traded to another team mid-season, but this method ensures that only the season 
        long combined splits are returned.

        Args:
            a_season (int): The season to get the pitching splits for.

        Returns: 
            A dictionary containing the batting average against, strikeouts per 9 innings, and home runs per 9
            innings for each split, vs. left-handed hitters and vs. right-handed hitters.
        """
        #Create the lefty/righty splits endpoint for pitchers.
        lrSplitsEndpoint = self.m_endpointObj.GetLRPitcherSplitsEndpoint(self.m_playerID, a_season)
        
        #Access the created endpoint and store the data.
        lrSplitsData = self.m_endpointObj.AccessEndpointData(lrSplitsEndpoint)
        
        #Make sure the player ID provided is valid and can be found. 0 is returned to indicate the player could not be found.
        if 'people' not in lrSplitsData:
            return {}
        
        #Extract the split data.
        splits = lrSplitsData['people'][0]['stats'][0]['splits']
        
        #Loop through the possible splits. There can be 0, 1, or 2 depending on the player and season but practically all pitchers will have 2.
        resultDictionary = {'fullName': lrSplitsData['people'][0]['fullName']}
        for index in range(len(splits)):
            splitName = splits[index]['split']['description']
            
            #Extracting the actual statistics for the individual split.
            splitStats = splits[index]['stat']
            
            battersFaced = int(splitStats['battersFaced'])
            BAA = float(splitStats['avg'])
            
            #The following stats may be missing in very limited sample sizes.
            if splitStats['strikeoutsPer9Inn'] == '-.--':
                strikeoutsPer9Inn = 0.00
            else:
                strikeoutsPer9Inn = float(splitStats['strikeoutsPer9Inn'])
                
            if splitStats['homeRunsPer9'] == '-.--':
                homeRunsPer9Inn = 0.00
            else:
                homeRunsPer9Inn = float(splitStats['homeRunsPer9'])
            
            #Building a dictionary for the individual split.
            splitDictionary = { splitName: { 'battersFaced': battersFaced,
                                             'battingAverageAgainst': BAA,
                                             'strikeoutsPer9': strikeoutsPer9Inn,
                                             'homeRunsPer9': homeRunsPer9Inn }
                              }
            
            #Adding the individual split to the result dictionary.
            resultDictionary.update(splitDictionary)
        
        return resultDictionary

    def CalculateYRFIPercentage(self, a_season, a_startDate, a_endDate):
        """Calculates the percentage of games a pitcher lets up a run in the first inning.

        This method is used to calculate the YRFI percentage for a pitcher. First, all the pitcher's starts within 
        the provided date range is extracted from the MLB API. Then, a Game object is created for each of their 
        starts, and the total number of games where the pitcher lets up a run in the first inning is tallied. The 
        YRFI percentage is calculated by taking this total and dividing it by their total number of starts in the 
        date range.

        Args:
            a_season (int): The season to get the YRFI percentage for.
            a_startDate (datetime): The date representing the start of the date range to consider.
            a_endDate (datetime): The date representing the end of the date range to consider.

        Returns: A float, representing the percentage of games a pitcher lets up a run in the first inning (between
                 0 and 1).
        """
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
        yrfiCount = 0
        
        #Loop through each game the pitcher has started within the date range.
        for game in gameLog:
            #Ensure the pitcher started the game (and didn't appear as a relief pitcher).
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
            
            #Determine if the pitcher lets up a run in the 1st inning for that game.
            if gameObj.DidPitcherLetUpRunFirstInning(self.m_playerID):
                yrfiCount += 1
        
        #Make sure a game has been played to avoid division by 0 error.
        if totalGamesStarted == 0:
            return 0
        
        #The YRFI rate represents the percentage of games a pitcher let up a run in the 1st inning in their starts. 
        #Lower YRFI rates are better for NRFI, while higher YRFI rates are better for YRFI.
        yrfiRate = yrfiCount / totalGamesStarted

        return yrfiRate