#Game CLASS. Handles everything regarding an MLB game. Takes a game ID as its constructor, so that it can quickly scan the data for that game.

from Endpoints import Endpoints

class Game():
    #CONSTRUCTOR - default game is opening day for the Yankees (2024 for now).
    def __init__(self, a_gameID = 746418):
        """Constructor for the Game class.

        This constructor is used to create and initialize a Game object. The game ID provided to this constructor is
        set as a member variable. If a game ID is not provided, the opening day game in 2024 for the Yankees is used
        by default. Next, the game's endpoint information is set as a member variable (see
        InitializeGameEndpointInformation()), to minimize the total number of MLB API calls required when extracting
        information about the game. Finally, the basic information regarding the game is stored as member variables (
        see InitializeBasicInformation()). This includes the records of the teams, starting pitchers, stadium the
        game is being played at, and more.

        Args:
            a_gameID (int): The ID used by the MLB API to represent a game.

        Returns:
            Nothing.
        """
        #Endpoint object from the Endpoints class to handle MLB API access.
        self.m_endpointObj = Endpoints()
        
        #Passed game ID that represents a single game.
        self.m_gameID = a_gameID
        
        #Access and store the information from the MLB API's game endpoint.
        self.InitializeGameEndpointInformation()
        
        #Store all basic information about the game that can quickly be determined.
        self.InitializeBasicInformation()
        
    #Accesses the endpoint for the game and stores the data returned. This minimalizes the number of API calls required.
    def InitializeGameEndpointInformation(self):
        """Sets the game endpoint information.

        This method accesses the MLB API to retrieve all the information about a specific game. The information
        returned by the MLB API is stored as a class member variable to minimize the total number of API calls when
        using an object of this class, since the information only needs to be retrieved once. If the game ID is
        invalid or the game cannot be found in the MLB API, the default ID used is the Yankees opening day game.

        Returns:
            Nothing.
        """
        #Create the individual game analysis endpoint.
        gameEndpoint = self.m_endpointObj.GetGameAnalysisEndpoint(self.m_gameID)
        
        #Access the created endpoint and store the data.
        gameData = self.m_endpointObj.AccessEndpointData(gameEndpoint)
        
        #It needs to be made sure that the actual game entered as the game id exists and can be scanned before other information can be gathered.
        if 'gamePk' in gameData:
            if int(gameData['gamePk']) != 0:
                self.m_gameData = gameData
            else:
                #By default set the game ID to the Yankees opening day game and reset the game data.
                self.m_gameID = 746418
                self.InitializeGameEndpointInformation()
        #If this else block is reached, the provided game ID was completely invalid and the API returned an error. 
        else:
            #By default set the game ID to the Yankees opening day game and reset the game data.
            self.m_gameID = 746418
            self.InitializeGameEndpointInformation() 
        
    #Gathers basic information and sets them as class variables.
    def InitializeBasicInformation(self):
        """Parses the game information returned by the MLB API and stores them as class member variables.

        This method is used to automatically parse the game information that is returned by the MLB API (see
        InitializeGameEndpointInformation). All parsed fields are stored as class member variables for easy access.
        If any field is missing, default values are used. For example, if a starting pitcher has not yet been named
        for an upcoming game, the starting pitcher will be "T.B.D.".

        Returns:
            Nothing.
        """
        gameInformation = self.m_gameData['gameData']
        
        #Setting the exact date and time of the game. Note: The time of game is LOCAL time.
        self.m_date = gameInformation['datetime']['officialDate']
        self.m_time = gameInformation['datetime']['time'] + ' ' + gameInformation['datetime']['ampm']
        self.m_dateTimeString = gameInformation['datetime']['dateTime']

        #Setting the state of the game - whether the game is final or not (sometimes games can be postponed or cancelled due to rain - this is important for game tracking).
        gameState = gameInformation['status']['detailedState']
        if gameState != 'Final' and gameState != 'Completed Early':
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
        #Handling the case where neither starting pitcher has been announced yet.
        if not probablePitchersData:
            self.m_homePitcherName = 'T.B.D.'
            self.m_homePitcherID = 0
            self.m_awayPitcherName = 'T.B.D.'
            self.m_awayPitcherID = 0
        else:
            #Setting the home team's starting pitcher, if it exists.
            if not 'home' in probablePitchersData or not 'fullName' in probablePitchersData['home'] or not 'id' in probablePitchersData['home']:
                self.m_homePitcherName = 'T.B.D.'
                self.m_homePitcherID = 0
            else:
                homeProbablePitcherData = probablePitchersData['home']
                self.m_homePitcherName = homeProbablePitcherData['fullName']
                self.m_homePitcherID = homeProbablePitcherData['id']
            
            #Setting the away team's starting pitcher, if it exists.
            if not 'away' in probablePitchersData or not 'fullName' in probablePitchersData['away'] or not 'id' in probablePitchersData['away']:
                self.m_awayPitcherName = 'T.B.D.'
                self.m_awayPitcherID = 0
            else:
                awayProbablePitcherData = probablePitchersData['away']
                self.m_awayPitcherName = awayProbablePitcherData['fullName']
                self.m_awayPitcherID = awayProbablePitcherData['id']

    #Basic Getter functions.
    #Gets the ID of the game.
    def GetGameID(self):
        """Gets the ID used by the MLB API to identify a specific game.

        Returns:
            An integer, representing the ID of the game.
        """
        return self.m_gameID

    #Gets the date the game was played on.
    def GetGameDate(self):
        """Gets the date the game was played on.

        Returns:
            A string, representing the date the game occured (example: 05/15/2024).
        """
        return self.m_date
    
    #Gets the local time the game was played at (ex: 1:05 PM).
    def GetGameTime(self):
        """Gets the time the game began, local to the stadium it was played at.

        Returns:
            A string, representing the local time the game started (example: 1:05 PM).
        """
        return self.m_time
    
    #Gets the dateTime string of when the game was played, in the UTC timezone.
    def GetGameDateTimeString(self):
        """Gets the dateTime string representation of when the game began.

        Returns:
            A string, representing when the game started in dateTime format in the UTC timezone
            (example: 2022-06-03T00:40:00Z).
        """
        return self.m_dateTimeString

    #Determines whether or not the game is final, meaning it has ended.
    def IsGameFinal(self):
        """Gets whether the game is finished or not.

        Returns:
            A boolean, which is true if the game is officially completed, false otherwise.
        """
        return self.m_isFinal

    #Gets the name of the home team in the game.
    def GetHomeTeamName(self):
        """Gets the name of the home team of the game.

        Returns:
            A string, representing the name of the home team of the game.
        """
        return self.m_homeTeamName
    
    #Gets the team ID for the home team.
    def GetHomeTeamID(self):
        """Gets the ID used by the MLB API to represent the home team of the game.

        Returns:
            An integer, representing the ID of the home team of the game.
        """
        return self.m_homeTeamID

    #Gets the name of the away team in the game.
    def GetAwayTeamName(self):
        """Gets the name of the away team of the game.

        Returns:
            A string, representing the name of the away team of the game.
        """
        return self.m_awayTeamName

    #Gets the team ID for the away team.
    def GetAwayTeamID(self):
        """Gets the ID used by the MLB API to represent the away team of the game.

        Returns:
            An integer, representing the ID of the away team of the game.
        """
        return self.m_awayTeamID

    #Gets the stadium the game is being played at.
    def GetStadium(self):
        """Gets the name of the stadium that game is being played at.

        Returns:
            A string, representing the name of the stadium the game is/was played at.
        """
        return self.m_stadium

    #Gets the name of the starting pitcher for the home team.
    def GetHomeStartingPitcherName(self):
        """Gets the name of the starting pitcher for the home team of the game.

        Returns:
            A string, representing the name of the starting pitcher for the home team of the game.
        """
        return self.m_homePitcherName
    
    #Gets the ID of the starting pitcher for the home team.
    def GetHomeStartingPitcherID(self):
        """Gets the ID used by the MLB API to represent the starting pitcher for the home team of the game.

        Returns:
            An integer, representing the ID of the starting pitcher for the home team of the game.
        """
        return self.m_homePitcherID

    #Gets the name of the starting pitcher the away team.
    def GetAwayStartingPitcherName(self):
        """Gets the name of the starting pitcher for the away team of the game.

        Returns:
            A string, representing the name of the starting pitcher for the away team of the game.
        """
        return self.m_awayPitcherName
    
    #Gets the ID of the starting pitcher for the away team.
    def GetAwayStartingPitcherID(self):
        """Gets the ID used by the MLB API to represent the starting pitcher for the away team of the game.

        Returns:
            An integer, representing the ID of the starting pitcher for the away team of the game.
        """
        return self.m_awayPitcherID
    
    #Basic Setters
    def SetNewGame(self, a_gameID):
        """Sets the instance of the class to represent a new game.

        Args:
            a_gameID (int): The ID used by the MLB API to represent the new game.

        Returns:
            Nothing.
        """
        self.m_gameID = a_gameID
        
        #Re-update the member variables to represent the new game.
        self.InitializeGameEndpointInformation()
        self.InitializeBasicInformation()
    
    #Gets all of the individual plays from a game (every at-bat result).
    def GetAllPlays(self):
        """Helper method to extract all the plays that have occurred within a game so far.

        Returns:
            A list, containing individual dictionaries with each dictionary representing a play in the game.
        """
        return self.m_gameData['liveData']['plays']['allPlays']
    
    #Gets all of the indices of plays in which a run was scored. Ex: [4, 14, 24, ...]
    def GetScoringPlayIndices(self):
        """Helper method to extract all the plays that have resulted in a run being scored within a game so far.

        Returns:
            A list, containing individual dictionaries with each dictionary representing a play where a run has scored
            in the game so far.
        """
        return self.m_gameData['liveData']['plays']['scoringPlays']
    
    #Displays all the information about the game in a neat format.
    def PrintGameInfo(self):
        """Displays all the information about the game in a neat format to the console.

        Returns:
            Nothing.
        """
        #Basic game ID and time information.
        print('Game ID:', self.m_gameID)
        print('Date:', self.m_date)
        print('Game Time:', self.m_time, '\n')

        #Teams and probable pitchers.
        print('Home Team:', self.m_homeTeamName)
        print('Home Starting Pitcher:', self.m_homePitcherName)
        print('Away Team:', self.m_awayTeamName)
        print('Away Starting Pitcher:', self.m_awayPitcherName, '\n')

        #Stadium information and game status.
        print('Stadium:', self.m_stadium)
        print('Game final?', self.m_isFinal, '\n')

        #NRFI/YRFI information.
        print('Was a run scored in the first inning?', self.DidYRFIOccur())
        print('Did the home team score in the first inning?', self.DidTeamScoreFirstInning(self.m_homeTeamID))
        print('Did the away team score in the first inning?', self.DidTeamScoreFirstInning(self.m_awayTeamID))
        print('Did the home pitcher, ' + self.m_homePitcherName + ', let up a run in the first inning?', self.DidPitcherLetUpRunFirstInning(self.m_homePitcherID))
        print('Did the away pitcher, ' + self.m_awayPitcherName + ', let up a run in the first inning?', self.DidPitcherLetUpRunFirstInning(self.m_awayPitcherID), '\n')

    #NRFI Functions
    def ExtractFirstInningScoringPlays(self):
        """Extracts the plays from the game where a run was scored in the first innings.

        This method is used to gather all the plays of the game where a run was scored in the first inning. First,
        every play from the game as well as the indices of those plays where a run was scored is extracted. For each
        play, it is checked which inning the run was scored. If it was scored in the first inning, it is added to the
        return list, otherwise the search is continued for the rest of the scoring plays.

        Returns:
            A list, containing individual dictionaries with each dictionary representing a 1st inning play where a run
            scored. An empty list is returned if no first inning runs were scored in the game.
        """
        #Gather all the plays from the game, as well as the specific indices of those plays that resulted in a run being scored.
        allPlays = self.GetAllPlays()
        scoringPlays = self.GetScoringPlayIndices()
        
        #Make sure the play data actually exists.
        if not allPlays or not scoringPlays:
            return []
        
        #Loop through each scoring play that occurred in the game.
        firstInningScoringPlays = []
        for scoringIndex in scoringPlays:
            #Extract the information about that specific play in which a run was scored.
            play = allPlays[scoringIndex]
            
            #If the scoring play occurred in the first inning, append it to the result list.
            inning = int(play['about']['inning'])
            if inning == 1:
                firstInningScoringPlays.append(play)
            #No need to continue searching after the first inning.
            elif inning > 1:
                break
    
        return firstInningScoringPlays

    #Determines whether or not a run was scored in the first run of the inning.
    def DidYRFIOccur(self):
        """Determines whether a run was scored in the first inning of the game or not.

        This method is used to determine if a YRFI occurred in the game. First, the plays from the game where a run 
        was scored in the first inning is extracted (see ExtractFirstInningScoringPlays()). If there is at least one 
        play from the returned list, a YRFI occurred and true is returned, otherwise false is returned.

        Returns:
            A boolean, which his true if a run was scored in the first inning of the game, false otherwise.
        """
        firstInningScoringPlays = self.ExtractFirstInningScoringPlays()
        return len(firstInningScoringPlays) > 0
    
    #Determines if a specific team scored in the first inning of a game - used to calculate how often a team scores in the first inning.
    def DidTeamScoreFirstInning(self, a_teamID):
        """Determines whether a specific team has scored in the first inning of the game.

        This method is used to determine if a specific team has scored in the first inning of the game. First, 
        the plays from the game where a run was scored in the first inning is extracted (see 
        ExtractFirstInningScoringPlays()). For each of these scoring plays, it is determined which half of the inning 
        the play occurred. If the inning is in the top half then the away team scored, otherwise if the inning is in 
        the bottom half the home team scored. The team ID of the scoring team (home or away) is then compared with 
        the team ID provided to this method. If they match, true is returned. If no scoring play occurred in the 
        first inning for the requested team, false is returned.

        Args:
            a_teamID (int): The ID used by the MLB API to represent a team.

        Returns:
            A boolean, which is true if the provided team scored a run in the first inning of the game, false otherwise.
        """
        #Extract all the plays that resulted in a run being scored in the first inning, if any exist.
        firstInningScoringPlays = self.ExtractFirstInningScoringPlays()
        
        #Loop through each play where a run was scored in the first inning.
        for scoringPlay in firstInningScoringPlays:
            #Check to see which team scored, and if it matches the team ID that it being searched for.
            halfInning = scoringPlay['about']['halfInning']
                
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
                
        return False
    
    #Determines if a specific pitcher let up a run in the first inning of a game - used to calculate how often a pitcher lets up a run in the first inning.
    def DidPitcherLetUpRunFirstInning(self, a_pitcherID):
        """Determines whether a specific pitcher  has let up a run in the first inning of the game.

        This method is used to determine if a specific pitcher has let up a run in the first inning of the game. 
        first, the plays from the game where a run was scored in the first inning is extracted (see 
        ExtractFirstInningScoringPlays()). For each scoring play, the ID of the pitcher who let up the run(s) is 
        extracted. This ID is then compared with the pitcher ID that was provided to this method. If they match, 
        true is returned. If no scoring play occurred in the first inning and the requested pitcher was pitching at 
        the time, false is returned.

        Args:
            a_pitcherID (int): The ID used by the MLB API to represent a pitcher.

        Returns:
            A boolean, which is true if the provided pitcher let up a run in the first inning of the game, false
            otherwise.
        """
        #Extract all the plays that resulted in a run being scored in the first inning, if any exist.
        firstInningScoringPlays = self.ExtractFirstInningScoringPlays()
        
        #Loop through each play where a run was scored in the first inning.
        for scoringPlay in firstInningScoringPlays:
            pitcherID = scoringPlay['matchup']['pitcher']['id']
            if pitcherID == a_pitcherID:
                return True
            
        return False