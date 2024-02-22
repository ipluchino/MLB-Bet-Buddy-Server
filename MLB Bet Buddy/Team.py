#TEAM CLASS. Handles everything regarding an MLB team.

from Endpoints import Endpoints

class Team():
    #All MLB teams and their respective IDs associated with the MLB API.
    MLB_TEAM_IDS = [
        { 'id': 109, 'name': 'Arizona Diamondbacks' },
        { 'id': 144, 'name': 'Atlanta Braves' },
        { 'id': 110, 'name': 'Baltimore Orioles' },
        { 'id': 111, 'name': 'Boston Red Sox' },
        { 'id': 112, 'name': 'Chicago Cubs' },
        { 'id': 145, 'name': 'Chicago White Sox' },
        { 'id': 113, 'name': 'Cincinnati Reds' },
        { 'id': 114, 'name': 'Cleveland Guardians' },
        { 'id': 115, 'name': 'Colorado Rockies' },
        { 'id': 116, 'name': 'Detroit Tigers' },
        { 'id': 117, 'name': 'Houston Astros' },
        { 'id': 118, 'name': 'Kansas City Royals' },
        { 'id': 108, 'name': 'Los Angeles Angels' },
        { 'id': 119, 'name': 'Los Angeles Dodgers' },
        { 'id': 146, 'name': 'Miami Marlins' },
        { 'id': 158, 'name': 'Milwaukee Brewers' },
        { 'id': 142, 'name': 'Minnesota Twins' },
        { 'id': 121, 'name': 'New York Mets' },
        { 'id': 147, 'name': 'New York Yankees' },
        { 'id': 133, 'name': 'Oakland Athletics' },
        { 'id': 143, 'name': 'Philadelphia Phillies' },
        { 'id': 134, 'name': 'Pittsburgh Pirates' },
        { 'id': 135, 'name': 'San Diego Padres' },
        { 'id': 137, 'name': 'San Francisco Giants' },
        { 'id': 136, 'name': 'Seattle Mariners' },
        { 'id': 138, 'name': 'St. Louis Cardinals' },
        { 'id': 139, 'name': 'Tampa Bay Rays' },
        { 'id': 140, 'name': 'Texas Rangers' },
        { 'id': 141, 'name': 'Toronto Blue Jays' },
        { 'id': 120, 'name': 'Washington Nationals' }
    ]
    
    #CONSTRUCTOR - default team is the NYY.
    def __init__(self, a_teamID = 147):
        #Endpoint object from the Endpoints class to handle MLB API access.
        self.m_endpointObj = Endpoints()
        
        #If the ID provided is valid, set the name and ID of the team as class variables.
        if self.ValidateTeamID(a_teamID):
            self.m_teamID = a_teamID
            self.m_teamName = self.NameFromID(a_teamID)
        #Otherwise, default to the New York Yankees information.
        else:
            self.m_teamID = 147
            self.m_teamName = 'New York Yankees'
            
    #Validates that a provided ID is legitimate.
    def ValidateTeamID(self, a_teamID):
        #Loop through each team and check if the ID matches one of the teams in the list.
        for team in self.MLB_TEAM_IDS:
            if team['id'] == a_teamID:
                return True
            
        #If all of the teams are checked and the ID hasn't been found, it is not valid.
        return False

    #Gets the name of a team given its ID.
    def NameFromID(self, a_teamID):
        #Loop through each team and check if the ID matches one of the teams in the list. If it does, extract its name.
        for team in self.MLB_TEAM_IDS:
            if team['id'] == a_teamID:
                return team['name']
            
        #Otherwise, the ID is not valid, and there is no name.
        return 'Unknown'

    #Getters
    def GetTeamID(self):
        return self.m_teamID

    def GetTeamName(self):
        return self.m_teamName
    
    #Setters
    def SetTeam(self, a_teamID):
        #Make sure that the team ID is valid in terms of the MLB API. If the team ID is not valid, nothing needs to be changed.
        if self.ValidateTeamID(a_teamID):
            self.m_teamID = a_teamID
            self.m_teamName = self.NameFromID(a_teamID)

    #Gets the record information for a team and returns it as a tuple in the format (wins, losses). Example: (33, 22).
    def GetRecord(self, a_date, a_season):
        #Create the standings endpoint.
        standingsEndpoint = self.m_endpointObj.GetStandingsEndpoint(a_date, a_season)
        
        #Access the created endpoint and store the date.
        endpointData = self.m_endpointObj.AccessEndpointData(standingsEndpoint)
        
        #Access the standings.
        standingsData = endpointData['records']
        
        #If there are no standings present (such as if the date or season entered is not valid, default to 0-0 record).
        if not standingsData:
            return (0, 0)
        
        #Otherwise, find the standings for the specified team.
        record = self.FindRecord(standingsData)
        return record
        
    #Sifts through record data to find the correct team.
    def FindRecord(self, a_recordData):
        #Note: The layout of the data is split into 6 total divisions, each with 5 teams (30 total MLB teams).
        
        #Search through each division in the provided data.
        for division in a_recordData:
            #Extract the division's standings.
            allRecords = division['teamRecords']
            
            #Search through each team in the specific division.
            for teamRecord in allRecords:
                #Extract the team name so that it can be compared with the class instance's team ID.
                teamID = teamRecord['team']['id']
                
                #If the team ID matches, return the record. Otherwise, keep searching. 
                if teamID == self.m_teamID:
                    wins = teamRecord['leagueRecord']['wins']
                    losses = teamRecord['leagueRecord']['losses']
                    
                    return (wins, losses)
                    
        #At this point, a record could not be found, so return a default record of 0 wins and 0 losses.
        return (0, 0)

    def GetTeamOffensiveStatistics(self, a_season, a_startDate, a_endDate):
        #Create the team offensive statistics endpoint.
        teamOffenseEndpoint = self.m_endpointObj.GetTeamOffensiveEndpoint(self.m_teamID, a_season, a_startDate, a_endDate)
        
        #Access the created endpoint and store the data.
        teamOffenseData = self.m_endpointObj.AccessEndpointData(teamOffenseEndpoint)
       
        teamSplits = teamOffenseData['stats'][0]['splits']
        
        #If the splits containing the statistics could not be found (such as the user entered an incorrect date or season) simply return all 0s for the requested statistics.
        if not teamSplits:
            return { 'battingAverage': 0.000, 'OPS': 0.000, 'RPG': 0.000, 'strikeoutPercentage': 0.000, 'homerunPercentage': 0.000 }
        
        #teamStats contains all of the actual statistics.
        teamStats = teamSplits[0]['stat']
        
        #Extract the total number of games played as well as the total number of runs scored to find overall runs per game.
        totalGamesPlayed = float(teamStats['gamesPlayed'])
        totalRunsScored = float(teamStats['runs'])
        teamRunsPerGame = totalRunsScored / totalGamesPlayed

        #Extract the other commonly used team offensive statistics. OPS = On Base Plus Slugging.
        teamBattingAverage = float(teamStats['avg'])
        teamOPS = float(teamStats['ops'])
        
        #Calculate the strikeout rate of the team. High strikeout rate is good for NRFI since the ball is never put into play.
        totalPlateAppearances = float(teamStats['plateAppearances'])
        totalStrikeouts = float(teamStats['strikeOuts'])
        teamStrikeoutPercentage = totalStrikeouts / totalPlateAppearances
        
        #Extract homerun rate of the team. Since homeruns instantly end a NRFI, a low team homerun rate is desired for NRFI.
        totalHomeruns = float(teamStats['homeRuns'])
        teamHomerunPercentage = totalHomeruns / totalPlateAppearances
        
        return { 'teamName': self.m_teamName,
                 'battingAverage': teamBattingAverage, 
                 'OPS': teamOPS,
                 'RPG': teamRunsPerGame,
                 'strikeoutPercentage': teamStrikeoutPercentage,
                 'homerunPercentage': teamHomerunPercentage }
        
        
        

        

