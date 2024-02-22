#Game CLASS. Handles everything regarding an MLB game. Takes a game ID as its constructor, so that it can quickly scan the data for that game.

from Endpoints import Endpoints
from datetime import datetime

class Game():
    #CONSTRUCTOR - default game is opening day for the Yankees (2023 for now).
    def __init__(self, a_gameID = 718781):
        #Endpoint object from the Endpoints class to handle MLB API access.
        self.m_endpointObj = Endpoints()
        
        #Passed game ID that represents a single game.
        self.m_gameID = a_gameID
        
        #Access and store the information from the MLB API's game endpoint.
        self.SetGameEndpointInformation()
        
        #Store all basic information about the game that can quickly be determined.
        self.SetBasicInformation()
        
    #Accesses the endpoint for the game and stores the data returned. This minimalizes the number of API calls required.
    def SetGameEndpointInformation(self):
        #Create the individual game analysis endpoint.
        gameEndpoint = self.m_endpointObj.GetGameAnalysisEndpoint(self.m_gameID)
        
        #Access the created endpoint and store the data.
        gameData = self.m_endpointObj.AccessEndpointData(gameEndpoint)
        
        #It needs to be made sure that the actual game entered as the game_id exists and can be scanned before other information can be gathered.
        if 'gamePk' in gameData:
            if int(gameData['gamePk']) != 0:
                self.m_gameData = gameData
            else:
                #By default set the game ID to the Yankees opening day game and reset the game data.
                self.m_gameID = 718781
                self.SetGameEndpointInformation()
        #If this else block si reached, the provided game ID was completely invalid and the API returned an error. 
        else:
            #By default set the game ID to the Yankees opening day game and reset the game data.
            self.m_gameID = 718781
            self.SetGameEndpointInformation() 
        
    #Gathers basic information and sets them as class variables.
    def SetBasicInformation(self):
        gameInformation = self.m_gameData['gameData']
        
        #Setting the exact date and time of the game. Note: The time of game is LOCAL time.
        self.m_date = datetime.strptime(gameInformation['datetime']['dateTime'], '%Y-%m-%dT%H:%M:%SZ')
        self.m_time = gameInformation['datetime']['time'] + ' ' + gameInformation['datetime']['ampm']

        #Setting the state of the game - whether the game is final or not (sometimes games can be postponed or cancelled due to rain - this is important for game tracking).
        gameState = gameInformation['status']['detailedState']
        if gameState != 'Final':
            self.m_isFinal = False
        else:
            self.m_isFinal = True
        
        #Setting the home and away team information.
        self.m_homeTeamName = gameInformation['teams']['home']['name']
        self.m_homeTeamID = gameInformation['teams']['home']['id']
        self.m_awayTeamName = gameInformation['teams']['away']['name']
        self.m_awayTeamID = gameInformation['teams']['away']['id']

        #Setting the stadium the game is being played at.
        self.m_stadium = gameInformation['venue']['name']
        
        #Contains data regarding the probable starting pitchers of the game.
        probablePitchersData = gameInformation['probablePitchers']
        
        #Set the probable pitchers, if they exist. If the starting pitcher hasn't be announced or determined yet, the data will not exist. T.B.D. stands for to be determined.
        if not probablePitchersData:
            self.m_homePitcherName = 'T.B.D.'
            self.m_homePitcherID = 0
            self.m_awayPitcherName = 'T.B.D.'
            self.m_awayPitcherID = 0
        else:
            homeProbablePitcherData = probablePitchersData['home']
            awayProbablePitcherData = probablePitchersData['away']
            
            #Setting the home team's starting pitcher, if it exists.
            if not homeProbablePitcherData:
                self.m_homePitcherName = 'T.B.D.'
                self.m_homePitcherID = 0
            else:
                self.m_homePitcherName = homeProbablePitcherData['fullName']
                self.m_homePitcherID = homeProbablePitcherData['id']
            
            #Setting the away team's starting pitcher, if it exists.
            if not awayProbablePitcherData:
                self.m_awayPitcherName = 'T.B.D.'
                self.m_awayPitcherID = 0
            else:
                self.m_awayPitcherName = awayProbablePitcherData['fullName']
                self.m_awayPitcherID = awayProbablePitcherData['id']

    #Getter functions.
    #Gets the ID of the game.
    def GetGameID(self):
        return self.m_gameID

    #Gets the date the game was played on.
    def GetGameDate(self):
        return self.m_date
    
    #Gets the time the game was played at (ex: 1:05 PM).
    def GetGameTime(self):
        return self.m_time

    #Determines whether or not the game is final, meaning it has ended.
    def IsGameFinal(self):
        return self.m_isFinal

    #Gets the name of the home team in the game.
    def GetHomeTeamName(self):
        return self.m_homeTeamName
    
    #Gets the team ID for the home team.
    def GetHomeTeamID(self):
        return self.m_homeTeamID

    #Gets the name of the away team in the game.
    def GetAwayTeamName(self):
        return self.m_awayTeamName

    #Gets the team ID for the away team.
    def GetAwayTeamID(self):
        return self.m_awayTeamID

    #Gets the stadium the game is being played at.
    def GetStadium(self):
        return self.m_stadium

    #Gets the name of the starting pitcher for the home team.
    def GetHomeStartingPitcherName(self):
        return self.m_homePitcherName
    
    #Gets the ID of the starting pitcher for the home team.
    def GetHomeStartingPitcherID(self):
        return self.m_homePitcherID

    #Gets the name of the starting pitcher the away team.
    def GetAwayStartingPitcherName(self):
        return self.m_awayPitcherName
    
    #Gets the ID of the starting pitcher for the away team.
    def GetAwayStartingPitcherID(self):
        return self.m_awayPitcherID
    
    #Gets all of the individual plays from a game (every at-bat result).
    def GetAllPlays(self):
        return self.m_gameData['liveData']['plays']['allPlays']
    
    #Gets all of the indices of plays in which a run was scored. Ex: [4, 14, 24, ...]
    def GetScoringPlayIndices(self):
        return self.m_gameData['liveData']['plays']['scoringPlays']
    
    #NRFI Functions
    #Determines whether or not a run was scored in the first run of the inning.
    def DidYRFIOccur(self):
        allPlays = self.GetAllPlays()
        scoringPlays = self.GetScoringPlayIndices()
        
        #Make sure the play data actually exists before doing any calculations.
        if not allPlays or not scoringPlays:
            return False
        
        #Loop through each scoring play that happened in the game.
        for scoringIndex in scoringPlays:
            #Extract the information about that specific play in which a run was scored.
            play = allPlays[scoringIndex]
            
            #If the scoring play occurred in the first inning, return True. Otherwise, return false.
            inning = int(play['about']['inning'])
            if inning == 1:
                return True
            elif inning > 1:
                return False
    
        return False
    
    #Determines if a specific team scored in the first inning of a game - used to calculate how often a team scores in the first inning.
    def DidTeamScoreFirstInning(self, a_teamID):
        allPlays = self.GetAllPlays()
        scoringPlays = self.GetScoringPlayIndices()
        
        #Make sure the play data actually exists before doing any calculations.
        if not allPlays or not scoringPlays:
            return False

        #Loop through each scoring play that happened in the game.
        for scoringIndex in scoringPlays:
            #Extract the information about that specific play in which a run was scored.
            play = allPlays[scoringIndex]
            
            #Check to see if a run was scored in the first inning.
            inning = int(play['about']['inning'])
            if inning == 1:
                #Check to see which team scored, and if it matches the team ID that it being searched for.
                halfInning = play['about']['halfInning']
                
                #The run scored was in the top of the first inning, by the away team.
                if halfInning == 'top':
                    awayTeamID = self.GetAwayTeamID()
                    if awayTeamID == a_teamID:
                        return True
                #The run scored was in the bottom of the first inning, by the home team.
                else:
                    homeTeamID = self.GetHomeTeamID()
                    if homeTeamID == a_teamID:
                        return True
            elif inning > 1:
                return False
    
        return False
    
    #Determines if a specific pitcher let up a run in the first inning of a game - used to calculate how often a pitcher lets up a run in the first inning.
    def DidPitcherLetUpRunFirstInning(self, a_pitcherID):
        allPlays = self.GetAllPlays()
        scoringPlays = self.GetScoringPlayIndices()
        
        #Make sure the play data actually exists before doing any calculations.
        if not allPlays or not scoringPlays:
            return False
        
        #Loop through each scoring play that happened in the game.
        for scoringIndex in scoringPlays:
            #Extract the information about that specific play in which a run was scored.
            play = allPlays[scoringIndex]
            
            #If the scoring play occurred in the first inning, check to see if the pitcher that let it up matches the pitcher ID being searched for.
            inning = int(play['about']['inning'])
            if inning == 1:
                pitcherID = play['matchup']['pitcher']['id']
                if pitcherID == a_pitcherID:
                    return True
            elif inning > 1:
                return False
    
        return False