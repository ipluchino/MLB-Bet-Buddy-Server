#********************************************************************************************************************************
# Author: Ian Pluchino                                                                                                          *
# Class: BetPredictor class                                                                                                     *
# Description: Handles everything regarding the schedule information as well as the creation of the bet predictions.            *
# Date: 5/2/24                                                                                                                  *
#********************************************************************************************************************************
 
from Endpoints import Endpoints
from datetime import datetime
from Team import Team
from Game import Game
from Hitter import Hitter
from Pitcher import Pitcher
from LocalFactors import LocalFactors
import pandas as pd
import os
from bayes_opt import BayesianOptimization

class BetPredictor():
    #CONSTANTS
    #Pitching Score for NRFI Constants.
    #OMITTED.
    
    #Team Score for NRFI Constants.
    #OMITTED.
    
    #Minimum starts required for a pitcher to consider them for bet predictions.
    MINIMUM_GAMES_STARTED = 3
    
    #Minimum PA for hot/cold factor for a hitter.
    MINIMUM_PA_FOR_HOT_COLD_FACTOR = 20

    #Minimum plate appearances for career stats factor for a hitter.
    MINIMUM_PA_FOR_CAREER_FACTOR = 7

    #Minimum number of bets for accuracy testing.
    MINIMUM_PREDICTIONS_FOR_NRFIYRFI = 7
    MINIMUM_PREDICTIONS_FOR_HITTING = 40
    
    #Column constants for bet prediction tables.
    SCHEDULE_COLUMNS = ['Game ID', 'Date', 'DateTime String', 'Time', 'Home Team Name', 'Home Team ID', 'Home Team Record', 
                        'Home Team Probable Pitcher Name', 'Home Team Probable Pitcher ID', 'Away Team Name', 'Away Team ID', 
                        'Away Team Record', 'Away Team Probable Pitcher Name', 'Away Team Probable Pitcher ID', 'Stadium', 
                        'Ballpark Factor', 'Weather Description', 'Weather Code', 'Temperature', 'Wind Speed']
    
    NRFI_COLUMNS =  [] #OMITTED.
    
    HITTING_COLUMNS = [] #OMITTED.

    #CONSTRUCTOR
    def __init__(self):
        """Constructor for the BetPredictor class.

        Returns:
            Nothing.
        """
        #Endpoint object from the Endpoints class to handle MLB API access.
        self.m_endpointObj = Endpoints()
        
    #SCHEDULE AND BET PREDICTION CREATION METHODS
    def CreateSchedule(self, a_date, a_season):
        """Creates a pandas DataFrame representing the schedule on the provided date.

        This method is used to create the schedule DataFrame that holds information about all the games that will be
        played on the provided date. All the games being played are first extracted from the schedule endpoint of the
        MLB API. Then, the game ID for each game is parsed (see ExtractGameIDsFromSchedule()). A Game object is
        created for each game using its ID so that information about that game such as the probable starting
        pitchers, team records, etc. can be retrieved. Finally, the local factors about the game are extracted using
        the LocalFactors class (ballpark factors and weather), and the game is added as a row into the DataFrame.
        Once all games have been processed, the completed DataFrame is returned.

        Args:
            a_date (datetime): The date to get the schedule for.
            a_season (int): The season to get the schedule from.

        Returns:
            A pandas DataFrame containing schedule information for the provided date and season.
        
        Assistance Received:
            https://stackoverflow.com/questions/71565413/adding-a-dictionary-to-a-row-in-a-pandas-dataframe-using-concat-in-pandas-1-4
        """
        #Create the endpoint to obtain the schedule information and access the data from it.
        scheduleEndpoint = self.m_endpointObj.GetTodayScheduleEndpoint(a_date, a_date)
        scheduleData = self.m_endpointObj.AccessEndpointData(scheduleEndpoint)
        
        allGameIDs = self.ExtractGameIDsFromSchedule(scheduleData)
        
        #Create the base pandas DataFrame that will hold the schedule information.
        scheduleDataFrame = pd.DataFrame(columns=self.SCHEDULE_COLUMNS)
        
        #If there are no games to add to the schedule, return the empty DataFrame.
        if len(allGameIDs) == 0:
            return scheduleDataFrame

        #Loop through each game that is being played on the provided date and extract all the required information from them.
        for gameID in allGameIDs:
            #Create a Game object with the game ID to easily obtain all information about that game.
            gameObj = Game(gameID)
            
            #Get the basic game information.
            todayDate = a_date.strftime('%m/%d/%Y')
            gameDateTimeString = gameObj.GetGameDateTimeString() 
            gameTime = gameObj.GetGameTime()
            homeTeamName = gameObj.GetHomeTeamName()
            homeTeamID = gameObj.GetHomeTeamID()
            awayTeamName = gameObj.GetAwayTeamName()
            awayTeamID = gameObj.GetAwayTeamID()
            stadium = gameObj.GetStadium()
            
            #Get the records of the two teams.
            homeTeam = Team(homeTeamID)
            awayTeam = Team(awayTeamID)
            homeTeamRecord = homeTeam.GetRecord(a_date, a_season)
            awayTeamRecord = awayTeam.GetRecord(a_date, a_season)
            
            #Get the probable pitcher information.
            homeProbablePitcherName = gameObj.GetHomeStartingPitcherName()
            homeProbablePitcherID = gameObj.GetHomeStartingPitcherID()
            awayProbablePitcherName = gameObj.GetAwayStartingPitcherName()
            awayProbablePitcherID = gameObj.GetAwayStartingPitcherID()
            
            #Get the local factors of the game.
            localFactors = LocalFactors()
            ballparkFactor = localFactors.GetBallparkFactor(stadium)
            weatherInformation = localFactors.GetWeather(stadium, gameTime)
            
            #Make sure the stadium was found.
            if weatherInformation == 'Unknown':
                weatherDescription = 'Unknown'
                weatherCode = 'Unknown'
                temperature = 'Unknown'
                windSpeed = 'Unknown'
            else:
                weatherDescription = weatherInformation['weatherCondition']
                weatherCode = weatherInformation['weatherCode']
                temperature = str(weatherInformation['temperatureF']) + ' \u00b0F'      #Note: The unicode is the degree symbol for Fahrenheit.
                windSpeed = str(weatherInformation['windSpeed']) + ' mph'
            
            
            #Create a row, representing a game, to be inserted into the table.
            gameRow = { 'Game ID': gameID, 'Date': todayDate, 'DateTime String': gameDateTimeString, 'Time': gameTime, 
                        'Home Team Name': homeTeamName, 'Home Team ID': homeTeamID, 'Home Team Record': homeTeamRecord, 
                        'Home Team Probable Pitcher Name': homeProbablePitcherName, 'Home Team Probable Pitcher ID': homeProbablePitcherID, 
                        'Away Team Name': awayTeamName, 'Away Team ID': awayTeamID, 'Away Team Record': awayTeamRecord, 
                        'Away Team Probable Pitcher Name': awayProbablePitcherName, 'Away Team Probable Pitcher ID': awayProbablePitcherID, 
                        'Stadium': stadium, 'Ballpark Factor': ballparkFactor, 'Weather Description': weatherDescription, 
                        'Weather Code': weatherCode, 'Temperature': temperature, 'Wind Speed': windSpeed }
            
            #Add the created game row into the DataFrame.
            scheduleDataFrame = pd.concat([scheduleDataFrame, pd.DataFrame([gameRow])], ignore_index=True)

        return scheduleDataFrame

    def ExtractGameIDsFromSchedule(self, a_scheduleData):
        """Helper method that extracts only the game IDs from a dictionary containing the entire schedule information.

        This method is a simple helper method to help extract only the game IDs from a schedule dictionary. First,
        a list of the games occurring in the schedule is extracted. Then, only the game ID is added to a return list
        for each of those games.

        Args: a_scheduleData (list): A dictionary that contains information about a schedule returned from the MLB API.

        Returns:
            A list of integers, where each integer represents a game ID.
        """
        #Make sure the schedule data has games to extract.
        if 'totalGames' not in a_scheduleData or int(a_scheduleData['totalGames']) == 0:
            return []
        
        resultList = []
        allGames = a_scheduleData['dates'][0]['games']
        
        #Loop through each game and extract only the game ID. Data gathering will be handled by the Game and Team classes.
        for game in allGames:
            gameID = game['gamePk']
            resultList.append(gameID)
            
        return resultList

    def CreateNRFIPredictions(self, a_scheduleDataFrame, a_openingDayDate, a_season):
        """Creates the NRFI predictions and processes them into a pandas DataFrame.

        This method is used to create the NRFI predictions and return them as a pandas DataFrame. A prediction is
        created for every game (row) in the schedule DataFrame provided to this method. First, basic information
        about each game is pulled directly from the schedule DataFrame. Then, the pitching statistics and team
        offense statistics are generated from the MLB API for each game (see GatherPitcherNRFIData() and
        GatherTeamNRFIData()). Finally, the NRFI prediction is created (see CalculatePitchingScore(),
        CalculateTeamHittingScore(), and CalculateOverallNRFIScore()) and added to the result DataFrame. Each row in
        the DataFrame also contains the statistics as well as other helpful information that were used in the bet
        prediction creation. If any important statistics are missing from either of the pitchers or either of the
        team playing, or either of the starting pitchers have not pitched a set minimum of games, the game is skipped
        and a prediction for that game is not added to the final DataFrame.

        Args:
            a_scheduleDataFrame (pandas.DataFrame): A pandas DataFrame containing the schedule information.
            a_openingDayDate (datetime): The date of opening day of the season the schedule was generated for.
            a_season (int): The season the schedule was generated for.

        Returns:
            A pandas DataFrame containing the NRFI bet predictions. The DataFrame is sorted by the Overall NRFI Score
            column, with the best NRFI bet predictions at the top. A lower Overall NRFI Score is better.

        Assistance Received:
            https://stackoverflow.com/questions/16476924/how-to-iterate-over-rows-in-a-pandas-dataframe
            https://stackoverflow.com/questions/71565413/adding-a-dictionary-to-a-row-in-a-pandas-dataframe-using-concat-in-pandas-1-4
        """
        #Create the base pandas DataFrame that will hold all the NRFI prediction data.   
        nrfiDataFrame = pd.DataFrame(columns=self.NRFI_COLUMNS)
        
        #Loop through each game in the schedule and fill in the information for each column. 
        #NOTE: Lots of the general information is pulled directly from the schedule DataFrame.
        for _, game in a_scheduleDataFrame.iterrows():
            #Games that do not have pitchers announced for both teams will be skipped - due to lack of data.
            if game['Home Team Probable Pitcher Name']  == 'T.B.D.' or game['Away Team Probable Pitcher Name'] == 'T.B.D.':
                continue
            
            #Basic information about the game.
            gameID = game['Game ID']
            gameDate = game['Date']
            gameDateTimeString = game['DateTime String']
            gameDatetimeObj = datetime.strptime(gameDate, '%m/%d/%Y')
            stadium = game['Stadium']
            
            #Gather and fill in information about the home starting pitcher. 
            '''
            The stat extraction portion of this method has been omitted for privacy reasons.
            If you wish to know more about how the NRFI/YRFI bet predictions are created, reach out to me.
            '''

            #Calculate all the NRFI/YRFI factors and scores for the game.
            '''
            The calculation portion of this method has been omitted for privacy reasons.
            If you wish to know more about how the NRFI/YRFI bet predictions are created, reach out to me.
            '''
            
            #Create a row, representing a game, to be inserted into the table.
            gameRow = {} #OMITTED.
            
            #Add on the individual pitching and team hitting statistics to the row.
            #OMITTED.

            #Add the created game row into the DataFrame. Sort by overall NRFI Score.
            nrfiDataFrame = pd.concat([nrfiDataFrame, pd.DataFrame([gameRow])], ignore_index=True)
            
        #Sort by overall NRFI Score.
        sortedNRFIDataFrame = nrfiDataFrame.sort_values(by='Overall NRFI Score')
        return sortedNRFIDataFrame
    
    def GatherPitcherNRFIData(self, a_pitcherID, a_season, a_startDate, a_endDate, a_homeOrAway):
        """Helper method to gather pitching statistics for NRFI bet predictions.

        This method is a helper method to CreateNRFIPredictions() and used to gather the pitching statistics from the
        MLB API that is used in NRFI bet prediction creation. The YRFI percentage for the pitcher is also calculated
        (see CalculateYRFIPercentage() in the Pitcher class). The gathered data is returned as a dictionary.

        Args:
            a_pitcherID (int): The ID used by the MLB API of the pitcher to get the stats for.
            a_season (int): The season to get the stats from.
            a_startDate (datetime): The date representing the start of the date range to consider.
            a_endDate (datetime): The date representing the end of the date range to consider.
            a_homeOrAway (string): A string indicating if the pitcher passed to this method is the home or away pitcher.

        Returns:
            A dictionary containing all the pitching statistics that are necessary to make the NRFI betting
            predictions.
        """
        pitcherObj = Pitcher(a_pitcherID)
        pitcherStats = pitcherObj.GetPitchingStatistics(a_season, a_startDate, a_endDate)
        
        if not pitcherStats:
            return {}

        #Extract the pitcher statistics from the MLB API.
        '''
        The calculation portion of this method has been omitted for privacy reasons.
        If you wish to know more about how the NRFI/YRFI bet predictions are created, reach out to me.
        '''
        
        #Format the statistics into a neat dictionary.
        formattedDictionary = {} #Omitted. 

        return formattedDictionary
        
    def GatherTeamNRFIData(self, a_teamID, a_season, a_startDate, a_endDate, a_homeOrAway):
        """Helper method to gather team offense statistics for NRFI bet predictions.

        This method is a helper method to CreateNRFIPredictions() and used to gather the team offense statistics from
        the MLB API that is used in NRFI bet prediction creation. The YRFI percentage for the team is also
        calculated (see CalculateYRFIPercentage() in the Team class). The gathered data is returned as a dictionary.

        Args:
            a_teamID (int): The ID used by the MLB API of the team to get the stats for.
            a_season (int): The season to get the stats from.
            a_startDate (datetime): The date representing the start of the date range to consider.
            a_endDate (datetime): The date representing the end of the date range to consider.
            a_homeOrAway (string): A string indicating if the team passed to this method is the home or away team.

        Returns:
            A dictionary containing all the team offensive statistics that are necessary to make the NRFI betting
            predictions.
        """
        teamObj = Team(a_teamID)
        teamStats = teamObj.GetTeamOffensiveStatistics(a_season, a_startDate, a_endDate)
        
        if not teamStats:
            return {}
        
        #Extract the team statistics from the MLB API.
        '''
        The calculation portion of this method has been omitted for privacy reasons.
        If you wish to know more about how the NRFI/YRFI bet predictions are created, reach out to me.
        '''
        
        #Format the statistics into a neat dictionary.
        formattedDictionary = {} #Omitted.
        
        return formattedDictionary
    
    def CreateHittingPredictions(self, a_scheduleDataFrame, a_openingDayDate, a_currentDate, a_season):
        """Creates the hitting predictions and processes them into a pandas DataFrame.

        This method is used to create the hitting predictions and return them as a pandas DataFrame. A prediction is
        made for only qualified hitters that are playing on the day the predictions are being made for. For each
        qualified hitter (a hitter with at least 3.1 plate appearances per game played), the game(s) that hitter is
        playing in is extracted from the schedule DataFrame (see FindGamesOnSchedule()). From those games,
        a Hitter object is created for the hitter, and a Pitcher object is created for the pitcher that hitter is
        facing. Statistics for the starting pitcher the hitter will be facing, along with individual hitting
        statistics for the hitter is generated from the MLB API using methods from both the Hitter and Pitcher
        class. Finally, the hitting prediction is created (see CalculateAdjustedBA(), CalculateCareerStatsFactor(),
        CalculateCareerStatsFactor(), CalculateOverallHittingScore()), and added to the result DataFrame. Each row in
        the DataFrame also contains the statistics as well as other helpful information that were used in the bet
        prediction creation. If any important statistics are missing, or hitters/pitchers have not met minimum game
        requirements, the individual prediction is omitted from the final DataFrame.

        Args:
            a_scheduleDataFrame (pandas.DataFrame): A pandas DataFrame containing the schedule information.
            a_openingDayDate (datetime): The date of opening day of the season the schedule was generated for.
            a_currentDate (datetime): The date the predictions are being generated for.
            a_season (int): The season the schedule was generated for.

        Returns:
            A pandas DataFrame containing the hitting bet predictions. The DataFrame is sorted by the Overall Hitting
            Score column, with the best hitting predictions at the top. A higher Overall Hitting Score is better.

        Assistance Received:
            https://stackoverflow.com/questions/16476924/how-to-iterate-over-rows-in-a-pandas-dataframe
            https://stackoverflow.com/questions/71565413/adding-a-dictionary-to-a-row-in-a-pandas-dataframe-using-concat-in-pandas-1-4
        """
        #Create the base pandas DataFrame that will hold all the hitting prediction data.
        hittingDataFrame = pd.DataFrame(columns=self.HITTING_COLUMNS)

        #Get a list of all the hitters that will be in the DataFrame.
        allHitters = Hitter.GetAllHitters(a_season)
        
        #Loop through each of the qualified hitters.
        for hitter in allHitters:
            #Extract the basic information about the hitter.
            hitterName = hitter['playerName']
            hitterID = hitter['playerID']
            hitterTeamName = hitter['teamName']
            hitterTeamID = hitter['teamID']
            
            #Extract the hitter's season offensive statistics.
            '''
            The stat extraction portion of this method has been omitted for privacy reasons.
            If you wish to know more about how the hitting bet predictions are created, reach out to me.
            '''

            #Now that all the hitter's general data has been gathered, loop through each game they are playing on that day.
            #Note: There can be double headers, which means two different pitchers they are facing on the same day.
            gamesToCheck = self.FindGamesOnSchedule(a_scheduleDataFrame, hitterTeamName)
            for game in gamesToCheck:
                #Each "game" is returned as a tuple, with game[0] representing a row in the pandas DataFrame, and game[1] representing 
                #if the pitcher is on the home or away team.
                gameInformation = game[0]
                homeOrAway = game[1]
                gameDatetimeObj = datetime.strptime(gameInformation['Date'], '%m/%d/%Y')
                
                #Extract basic information about the pitcher the hitter will be facing.
                pitcherName = gameInformation[homeOrAway + ' Team Probable Pitcher Name']
                pitcherID = gameInformation[homeOrAway + ' Team Probable Pitcher ID']
                pitcherTeamName = gameInformation[homeOrAway + ' Team Name']
                pitcherTeamID = gameInformation[homeOrAway + ' Team ID']
                
                #Extract statistics based on the pitcher. Make sure the data can be extracted and the pitcher has enough games started.
                pitcherObj = Pitcher(pitcherID)
                pitcherStats = pitcherObj.GetPitchingStatistics(a_season, a_openingDayDate, gameDatetimeObj)
                if not pitcherStats or pitcherStats['gamesStarted'] < self.MINIMUM_GAMES_STARTED:
                    continue

                handInformation = pitcherObj.GetHandInformation()
                if not handInformation:
                    continue
                pitchHand = handInformation['pitchHand']

                '''
                The stat extraction portion of this method has been omitted for privacy reasons.
                If you wish to know more about how the hitting bet predictions are created, reach out to me.
                '''
                
                #Calculate all the offensive factors and scores for the individual hitter.
                '''
                The calculation portion of this method has been omitted for privacy reasons.
                If you wish to know more about how the hitting bet predictions are created, reach out to me.
                '''

                #Add a row into the hitter DataFrame.
                hitterRow = {} #Omitted.
               
                #Add the created game row into the DataFrame.
                hittingDataFrame = pd.concat([hittingDataFrame, pd.DataFrame([hitterRow])], ignore_index=True)
        
        #Sort by overall Hitting Score in descending order.
        sortedHittingDataFrame = hittingDataFrame.sort_values(by='Overall Hitting Score', ascending=False)
        return sortedHittingDataFrame
    
    def FindGamesOnSchedule(self, a_scheduleDataFrame, a_hitterTeamName):
        """Finds the game on a schedule DataFrame that the hitter is playing in.

        This method is a helper method for the CreateHittingPredictions() method and used to find all the games on
        the schedule DataFrame where the hitter is playing in. Every row on the DataFrame is looped through,
        and if the hitter's team matches one of the teams playing in that game, the row is added to the return list.
        Additionally, the team the hitter is facing (away or home) is also added to the return list to make prediction
        creation easier.

        Args:
            a_scheduleDataFrame (pandas.DataFrame): A pandas DataFrame containing the schedule information.
            a_hitterTeamName (string): The name of the team the hitter is currently on.

        Returns:
            A list of tuples, with the first element being a pandas Series object representing the row from the schedule
            DataFrame, and the second being the hitter's opponent's team name as a string.
        """
        #Loop through each game on the schedule, and search for the hitter's team.
        resultRows = []
        for _, row in a_scheduleDataFrame.iterrows():
            #Add on a key that will help determine if the pitcher the hitter is facing is on the home or away team (since there are two pitchers).
            if row['Home Team Name'] == a_hitterTeamName:
                resultRows.append((row, 'Away'))
            elif row['Away Team Name'] == a_hitterTeamName:
                resultRows.append((row, 'Home'))
                
        return resultRows
                
    #BET CALCULATION METHODS
    def CalculatePitchingScore(self, a_pitchingStats, a_homeOrAway):
        """Calculates a pitching score for an individual pitcher.

        This method calculates and returns a pitching score for a provided pitcher. Lower scores are considered better for NRFI, 
        while higher scores are considered better for YRFI.

        Args:
            a_pitchingStats (dict): A dictionary containing multiple pitching statistics for the pitcher.
            a_homeOrAway (string): A string indicating if the pitcher is on the home or away team of the game.

        Returns:
            A float, representing the pitching score calculated for the pitcher.
        """
        
        '''
        The calculation portion of this method has been omitted for privacy reasons.
        If you wish to know more about how the NRFI/YRFI bet predictions are created, reach out to me.
        '''
        
        return pitchingScore
        
    def CalculateTeamHittingScore(self, a_teamStats, a_homeOrAway):
        """Calculates a team hitting score for an individual team.

        This method calculates and returns a team hitting score for a provided team. Lower scores are considered better for NRFI, 
        while higher scores are considered better for YRFI.

        Args:
            a_teamStats (dict): A dictionary containing multiple team offensive statistics for the team.
            a_homeOrAway (string): A string indicating if the team is on the home or away team of the game.

        Returns:
            A float, representing the team hitting score calculated for the team.
        """
        
        '''
        The calculation portion of this method has been omitted for privacy reasons.
        If you wish to know more about how the NRFI/YRFI bet predictions are created, reach out to me.
        '''
        
        return teamHittingScore
    
    def CalculateOverallNRFIScore(self, a_homePitcherNRFIScore, a_awayPitcherNRFIScore, a_ballparkFactor, a_weatherFactor):
        """Calculates the overall NRFI score for a game.

        This method is used to calculate the overall NRFI score of an MLB game.

        Args:
            a_homePitcherNRFIScore (float): The NRFI score for the home team pitcher.
            a_awayPitcherNRFIScore (float): The NRFI score for the away team pitcher.
            a_ballparkFactor (int): The ballpark factor of the stadium where the game is being played.
            a_weatherFactor (float): The weather factor at the stadium where the game is being played.

        Returns:
            A float, representing the overall NRFI score for a game.
        """
        
        '''
        The calculation portion of this method has been omitted for privacy reasons.
        If you wish to know more about how the NRFI/YRFI bet predictions are created, reach out to me.
        '''

        return overallNRFIScore

    def CalculateAdjustedBA(self, a_vsLeftBA, a_vsRightBA, a_vsLeftBAA, a_vsRightBAA, a_batHand, a_pitchHand):
        """Calculates the adjusted batting average for a hitter.

        This method is used to calculate the adjusted batting average for a hitter.

        Args:
            a_vsLeftBA (float): The batting average of the hitter when facing lefty pitchers.
            a_vsRightBA (float): The batting average of the hitter when facing righty pitchers.
            a_vsLeftBAA (float): The batting average against of the pitcher when facing lefty hitters.
            a_vsRightBAA (float): The batting average against of the pitcher when facing righty hitters.
            a_batHand (string): The batting hand of the hitter (left, right, or switch).
            a_pitchHand (string): The throwing hand of the pitcher (left or right).

        Returns:
            A float, representing the adjusted batting average for a hitter.
        """
        
        '''
        The calculation portion of this method has been omitted for privacy reasons.
        If you wish to know more about how the hitting bet predictions are created, reach out to me.
        '''
        
        return adjustedBA
    
    def CalculateHotColdFactor(self, a_L10PlateAppearances, a_L10BA):
        """Calculates the hot/cold factor for a hitter.

        This method is used to calculate the hot/cold factor for a hitter.

        Args:
            a_L10PlateAppearances (int): The number of plate appearances the hitter has in their last 10 games.
            a_L10BA (float): The batting average of the hitter in their last 10 games.

        Returns:
            A tuple, containing the hot/cold factor description as a string and hot/cold factor value as a float.
        """
       
        '''
        The calculation portion of this method has been omitted for privacy reasons.
        If you wish to know more about how the hitting bet predictions are created, reach out to me.
        '''
        
        return description, factor
        
    def CalculateCareerStatsFactor(self, a_careerPlateAppearances, a_careerBA):
        """Calculates the career stats factor for a hitter off a pitcher.

        This method is used to calculate the career stats factor for a hitter.

        Args:
            a_careerPlateAppearances (int): The number of plate appearances the hitter has facing a certain pitcher.
            a_careerBA (float): The batting average of the hitter when facing a certain pitcher.

        Returns:
            A tuple, containing the career stats factor description as a string and career stats factor value as a
            float.
        """
        
        '''
        The calculation portion of this method has been omitted for privacy reasons.
        If you wish to know more about how the hitting bet predictions are created, reach out to me.
        '''
        
        return description, factor
    
    def CalculateOverallHittingScore(self, a_adjustedBA, a_hotColdFactor, a_careerStatsFactor, a_weatherFactor, a_ballparkFactor):
        """Calculates the overall hitting score for a hitter.

        This method is used to calculate the overall hitting score for a hitter.

        Args:
            a_adjustedBA (float): The adjusted batting average of the hitter.
            a_hotColdFactor (float):  The hot/cold factor of the hitter based on their last 10 games.
            a_careerStatsFactor (float): The career stats factor of the hitter based on their stats off a specific pitcher.
            a_weatherFactor (float): The weather factor at the stadium where the game is being played.
            a_ballparkFactor (int): The ballpark factor of the stadium where the game is being played.

        Returns:
            A float, representing the overall hitting score for that hitter.
        """
        
        '''
        The calculation portion of this method has been omitted for privacy reasons.
        If you wish to know more about how the hitting bet predictions are created, reach out to me.
        '''
        
        return overallHittingScore

    #ACCURACY TESTING METHODS
    def AccuracyTestNRFIYRFI(self, a_topX):
        """Tests the accuracy of NRFI and YRFI bets.

        This method is used to test the accuracy of NRFI and YRFI bets that have already been made. The NRFI and YRFI
        bets for previous days are located in the \\Testing Data\\NRFI directory, in the form of Excel
        spreadsheets. For each spreadsheet containing bet predictions, the spreadsheet is read in as a pandas
        DataFrame. Then, all the factors and scores used in the NRFI and YRFI bet predictions are re-calculated in
        case the weights of certain factors or statistics has been changed. The a_topX best NRFI and YRFI bets are
        then extracted from the re-calculated bet predictions, and a Game object is created for each so that it can
        be determined if a NRFI or YRFI occurred for that game. The success rates are tallied up, and once all games
        have been reviewed, the success rates are returned. Spreadsheets that do not have the minimum required bet
        predictions required are skipped and not included in the success rate calculation.

        Args:
            a_topX (int): The number of top bets for each day to consider for the accuracy testing.

        Returns:
            A dictionary, containing both the NRFI and YRFI success rates, as well as the total games analyzed and the
            total NRFI and YRFI successes.
        """
        #Directory of the NRFI test data.
        directory = os.getcwd() + '\\Testing Data\\NRFI'
        
        #Loop through each simulated day of bet predictions in the testing directory.
        allFiles = os.listdir(directory)
        
        #Counter variables to determine overall accuracy.
        totalGames = 0
        totalNRFI = 0
        totalYRFI = 0
        
        for file in allFiles:
            #Read in the contents of the file into a pandas DataFrame. Note: All testing data is in the format .xlsx (excel file).
            nrfiDataFrame = pd.read_excel(directory + '\\' + file)
            
            #Skip empty data frames.
            if int(len(nrfiDataFrame) == 0):
                continue
            
            #Loop through each row of the DataFrame.
            for index, game in nrfiDataFrame.iterrows():
                #Pull the statistics from the individual game row for each pitcher and team.
                homePitcherStats = self.PullPitcherStatsFromTable(game, 'Home')
                awayPitcherStats = self.PullPitcherStatsFromTable(game, 'Away')
                
                homeTeamStats = self.PullTeamStatsFromTable(game, 'Home')
                awayTeamStats = self.PullTeamStatsFromTable(game, 'Away')
                
                #Re-calculate the overall NRFI values. This is because the individual weights may have changed for each stat.
                '''
                The calculation portion of this method has been omitted for privacy reasons.
                If you wish to know more about how the NRFI/YRFI bet predictions are created, reach out to me.
                '''
                
                sortedNRFIDataFrame = nrfiDataFrame.sort_values(by='Overall NRFI Score')           
                
            #Extract the best 3 NRFI predictions and the worst 3 NRFI predictions (for YRFI). Make sure there is the minimum number of predictions.
            if int(len(sortedNRFIDataFrame) < (a_topX * 2)) or int(len(sortedNRFIDataFrame)) < self.MINIMUM_PREDICTIONS_FOR_NRFIYRFI:
                continue
            else:
                totalGames += a_topX
            
            topXNRFI = sortedNRFIDataFrame.head(a_topX)
            topXYRFI = sortedNRFIDataFrame.tail(a_topX)

            #Loop through each best NRFI prediction.         
            for index, game in topXNRFI.iterrows():
                #Extract the game ID from the game, and create a Game object based on the game ID.
                gameID = game['Game ID']
                gameObj = Game(gameID)
                
                if not gameObj.DidYRFIOccur():
                    totalNRFI += 1
                    
            #Loop through each best YRFI prediction.         
            for index, game in topXYRFI.iterrows():
                #Extract the game ID from the game, and create a Game object based on the game ID.
                gameID = game['Game ID']
                gameObj = Game(gameID)
                
                if gameObj.DidYRFIOccur():
                    totalYRFI += 1
        
        #Return the total percentage of success for NRFI predictions and YRFI predictions.
        if totalGames == 0:
            return 'No games found in test data!'

        nrfiSuccessRate = totalNRFI / totalGames
        yrfiSuccessRate = totalYRFI / totalGames
        
        return { 'NRFI Success Rate': nrfiSuccessRate, 
                 'YRFI Success Rate': yrfiSuccessRate, 
                 'Total Games': totalGames, 
                 'Total NRFI': totalNRFI, 
                 'Total YRFI': totalYRFI }
    
    def AccuracyTestHitting(self, a_topX):
        """Tests the accuracy of hitting bets.

        This method is used to test the accuracy of the hitting bets that have already been made. The hitting bets
        for previous days are located in the \\Testing Data\\Hitting directory, in the form of Excel spreadsheets.
        For each spreadsheet containing bet predictions, the spreadsheet is read in as a pandas DataFrame. Then,
        all the factors and scores used in the hitting bet predictions are re-calculated in case the weights of
        certain factors or statistics has been changed. The a_topX best hitting bet prediction scores are extracted
        from the re-calculated bet predictions, and a Hitter object is created for each of the hitters. Using that
        Hitter object, it is tested if the hitter has achieved certain bet thresholds on that day (over 0.5 hits,
        over 1.5 hits, over 1.5 hits + runs + RBIs, and over 2.5 hits + runs + RBIs). The success rates are tallied
        up, and once all games have been reviewed, the success rates are returned. Spreadsheets that do not have the
        minimum required bet predictions required are skipped and not included in the success rate calculation.

        Args:
            a_topX (int): The number of top bets for each day to consider for the accuracy testing.

        Returns:
            A dictionary, containing the accuracy of the hitting bets for multiple different types of hitting bets.
            This includes the success rates for over 0.5 hits, over 1.5 hits, over 1.5 hits + runs + RBIs, and over
            2.5 hits + runs + RBIs. The total hitters analyzed and totals for these bet types are included as well.
        """
        #Directory of the Hitting test data.
        directory = os.getcwd() + '\\Testing Data\\Hitting'
        
        #Loop through each simulated day of bet predictions in the testing directory.
        allFiles = os.listdir(directory)
        
        #Counter variables to determine overall accuracy. Note: HRR = Hits, Runs, and RBIs combined.
        totalHitters = 0
        totalAtLeast1Hit = 0
        totalAtLeast2Hits = 0
        totalAtLeast2HRR = 0            #Over 1.5 Hits + Runs + RBIs
        totalAtLeast3HRR = 0            #Over 2.5 Hits + Runs + RBIs
        
        for file in allFiles:
            #Read in the contents of the file into a pandas DataFrame. Note: All testing data is in the format .xlsx (excel file).
            hittingDataFrame = pd.read_excel(directory + '\\' + file)
            
            #Skip empty data frames.
            if int(len(hittingDataFrame) == 0):
                continue
            
            #Loop through each row of the DataFrame.
            for index, hitter in hittingDataFrame.iterrows():
                #Pull the statistics of interest involved in making the overall hitting prediction score.
                '''
                The calculation portion of this method has been omitted for privacy reasons.
                If you wish to know more about how the hitting bet predictions are created, reach out to me.
                '''

                sortedHittingDataFrame = hittingDataFrame.sort_values(by='Overall Hitting Score', ascending=False)   
            
            #Extract the top X hitters from the data frame. Make sure there is the minimum number of predictions.
            if int(len(sortedHittingDataFrame)) < self.MINIMUM_PREDICTIONS_FOR_HITTING:
                continue
        
            #Loop through each of the top X hitters.
            topXHitters = sortedHittingDataFrame.head(a_topX)
        
            for index, hitter in topXHitters.iterrows():
                hitterID = hitter['Hitter ID']
                gameDate = hitter['Date']
            
                #Create a Hitter object from that hitter's ID and extract their stats from that day.
                hitterObj = Hitter(hitterID)
                betStats = hitterObj.HittingBetReview(gameDate)
                
                #Make sure the hitter played that day, if they didn't, skip the hitter. Sometimes hitters have off-days.
                if not betStats:
                    continue
                else:
                    totalHitters += 1
                
                #Add up the total bet thresholds that the hitter reached during that day.
                if betStats['atLeast1Hit']: totalAtLeast1Hit += 1
                if betStats['atLeast2Hits']: totalAtLeast2Hits += 1
                if betStats['atLeast2HRR']: totalAtLeast2HRR += 1
                if betStats['atLeast3HRR']: totalAtLeast3HRR += 1

            #Find the total success rate for each of the bet types and return them.
            atLeast1HitSuccessRate = totalAtLeast1Hit / totalHitters
            atLeast2HitsSuccessRate = totalAtLeast2Hits / totalHitters
            atLeast2HRRSuccessRate = totalAtLeast2HRR / totalHitters
            atLeast3HRRSuccessRate = totalAtLeast3HRR / totalHitters
            
        return { 'Over 0.5 Hits Success Rate': atLeast1HitSuccessRate,
                 'Over 1.5 Hits Success Rate': atLeast2HitsSuccessRate,
                 'Over 1.5 HRR Success Rate': atLeast2HRRSuccessRate,
                 'Over 2.5 HRR Success Rate': atLeast3HRRSuccessRate,
                 'Total Hitters': totalHitters,
                 'Over 0.5 Hits Total': totalAtLeast1Hit,
                 'Over 1.5 Hits Total': totalAtLeast2Hits,
                 'Over 1.5 HRR Total': totalAtLeast2HRR,
                 'Over 2.5 HRR Total': totalAtLeast3HRR }
        
    def PullPitcherStatsFromTable(self, a_gameRow, a_homeOrAway):
        """Helper method for the AccuracyTestNRFIYRFI() method, to pull the pitcher stats from the bet prediction table.

        Args:
            a_gameRow (pandas.Series): A row from the NRFI/YRFI bet prediction DataFrame, representing an MLB game.
            a_homeOrAway (string): A string indicating to pull stats for the home or away pitcher.

        Returns:
            A dictionary, with the extracted pitcher statistics in the correct format.
        """
        formattedDictionary = {} #Omitted.
        
        return formattedDictionary
    
    def PullTeamStatsFromTable(self, a_gameRow, a_homeOrAway):
        """Helper method for the AccuracyTestNRFIYRFI() method, to pull the team stats from the bet prediction table.

        Args:
            a_gameRow (pandas.Series): A row from the NRFI/YRFI bet prediction DataFrame, representing an MLB game.
            a_homeOrAway (string): A string indicating to pull stats for the home or away team.

        Returns:
            A dictionary, with the extracted team statistics in the correct format.
        """
        formattedDictionary = {} #Omitted.
        
        return formattedDictionary
    
    #BAYESIAN OPTIMIZATION METHODS
    def NRFIBlackBoxFunction(self):
        """Calculates the NRFI bet prediction accuracy with provided weights for each statistic.

        This method acts as the black box method for the Bayesian Optimization algorithm. First, the passed weights
        are normalized so that the pitcher related weights as well as the team offensive related weights add up to 1. 
        Then, the actual weights are set to the updated weights and the bet predictions are re-calculated and new accuracy 
        determined (see AccuracyTestNRFIYRFI()). The accuracy value is returned and is used to help optimize the weights of 
        each statistic to produce the highest possible accuracy percentage.

        Returns:
            A float, representing the accuracy of the newly generated NRFI bet predictions with the provided weights for
            each statistic.
        """
        #Find the sums of all the weights for the pitcher statistics and all the weights for the team offensive statistics.
        
        '''
        The calculation portion of this method has been omitted for privacy reasons.
        If you wish to know more about how the NRFI/YRFI bet predictions are created, reach out to me.
        '''

        #Find the accuracy percentage for the best NRFI prediction and return that value. This is the value that is trying to be optimized.
        accuracy = self.AccuracyTestNRFIYRFI(1)
        return accuracy['NRFI Success Rate']

    def OptimizeNRFIWeights(self, a_lowerBounds, a_upperBounds, a_numInitPoints, a_numberOfIterations):
        """Optimizes the weights of statistics for NRFI/YRFI bet prediction creation.

        This method optimizes the weights used in the calculations for NRFI/YRFI bet prediction
        creation. To do this, this method utilizes an algorithm called Bayesian Optimization from the library
        bayes_opt. First, preliminary information is set to the algorithm such as the black box function 
        (NRFIBlackBoxFunction()), the lower and upper bounds of each weight, the number of initial points of random
        exploration, and the number of iterations to run the algorithm for. Once the algorithm completes all of its
        iterations, the weights are normalized to ensure that the pitching related weights add up to 1 and the team
        offense weights add up to 1. The optimized weights are then
        returned as a dictionary containing their values.

        Args:
            a_lowerBounds (float): The lower bound of what the weights can be (usually 0).
            a_upperBounds (float): The upper bound of what the weights can be (usually 1).
            a_numInitPoints (int): The total number of initial points of random exploration used in the optimization.
            a_numberOfIterations (int): The total number of iterations to run the algorithm for.

        Returns:
            A dictionary, containing all the optimized version of the weights used in NRFY/YRFI bet prediction
            creation. Each weight is between 0 and 1, and both the pitcher and team offense weights add up to 1
            separately.

        Assistance Received:
            https://github.com/bayesian-optimization/BayesianOptimization
            https://rmcantin.github.io/bayesopt/html/
        """
        #Set up the Bayesian Optimization object from the BayesianOptimization class.
        optimizer = BayesianOptimization(
            #Set the black box function for the algorithm. This is the function that returns a single number that is trying to be maximized.
            f=self.NRFIBlackBoxFunction,
            
            #Set the bounds for each weight.
            pbounds={
                #Omitted.
            },
            
            #Create a random seed.
            random_state=1,  
        )

        #Run the Bayesian Optimization algorithm and extract the results.
        optimizer.maximize(init_points=a_numInitPoints, n_iter=a_numberOfIterations)
        optimizedWeights = optimizer.max['params']
        
        #Re-normalize the pitcher and team weights to add back up to 1.
        '''
        The calculation portion of this method has been omitted for privacy reasons.
        If you wish to know more about how the NRFI/YRFI bet predictions are created, reach out to me.
        '''
            
        return optimizedWeights