#SERVER file. Handles everything related to the server and database access.

from quart import Quart, jsonify
import asyncio
from quart.app import P
from sqlalchemy import create_engine, Column, Integer, String, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime, timedelta
from BetPredictor import BetPredictor
from Game import Game
from Hitter import Hitter
import pandas as pd

#CONSTANTS
#Names of the valid tables in the database.
TABLE_NAMES = ['TodaySchedule', 'ArchiveSchedule', 'TodayNRFI', 'ArchiveNRFI', 'TodayHitting', 'ArchiveHitting']

#Important dates and season information.
OPENING_DAY_2023 = datetime.strptime('03/30/2023', '%m/%d/%Y')
OPENING_DAY_2024 = datetime.strptime('03/20/2024', '%m/%d/%Y')

CLOSING_DAY_2023 = datetime.strptime('10/01/2023', '%m/%d/%Y')
CLOSING_DAY_2024 = datetime.strptime('09/29/2024', '%m/%d/%Y')

CURRENT_OPENING_DAY = OPENING_DAY_2024
CURRENT_CLOSING_DAY = CLOSING_DAY_2024
CURRENT_SEASON = 2024

#QUART AND SQLALCHEMY SETUP.
app = Quart(__name__)                                           #Quart server object.
Base = declarative_base()                                       #Base model database class from SQLAlchemy.
engine = create_engine('sqlite:///database.db', echo=True)      #Database engine location.
Session = sessionmaker(bind=engine)                             #Session to create a connection with the database.

#DATABASE TABLE MODELS. Note: There will be two tables for each kind of table, an active "today" table and an archive table. Both tables of each type will use the same column structure.
#Base table model for a schedule of MLB games.
class ScheduleBaseModel():
    id = Column('id', Integer, primary_key=True)
    Game_ID = Column('Game ID', Integer)
    Date = Column('Date', String)
    DateTime_String = Column('DateTime String', String)
    Time = Column('Time', String)	
    Home_Team_Name = Column('Home Team Name', String)	
    Home_Team_ID = Column('Home Team ID', Integer)	
    Home_Team_Record = Column('Home Team Record', String)	
    Home_Team_Probable_Pitcher_Name = Column('Home Team Probable Pitcher Name', String)	
    Home_Team_Probable_Pitcher_ID = Column('Home Team Probable Pitcher ID', Integer)	
    Away_Team_Name = Column('Away Team Name', String)	
    Away_Team_ID = Column('Away Team ID', Integer)	
    Away_Team_Record = Column('Away Team Record', String)	
    Away_Team_Probable_Pitcher_Name = Column('Away Team Probable Pitcher Name', String)	
    Away_Team_Probable_Pitcher_ID = Column('Away Team Probable Pitcher ID', Integer)	
    Stadium = Column('Stadium', String)
    Ballpark_Factor = Column('Ballpark Factor', Integer)	
    Weather_Description = Column('Weather Description', String)	
    Weather_Code = Column('Weather Code', Integer)	
    Temperature = Column('Temperature', String)	
    Wind_Speed = Column('Wind Speed', String)

#Today schedule table.
class TodayScheduleTable(ScheduleBaseModel, Base):
    __tablename__ = 'TodaySchedule'

#Archive schedule table.
class ArchiveScheduleTable(ScheduleBaseModel, Base):
    __tablename__ = 'ArchiveSchedule'

#Base table model for the NRFI/YRFI bet predictions. Only need a single table for both types of bets.
class NRFIBaseModel():
    id = Column('id', Integer, primary_key=True)
    Game_ID = Column('Game ID', Integer)	
    Date = Column('Date', String)
    DateTime_String = Column('DateTime String', String)
    Home_Pitcher_Name = Column('Home Pitcher Name', String)
    Home_Pitcher_ID = Column('Home Pitcher ID', Integer)
    Home_Pitcher_Games_Started = Column('Home Pitcher Games Started', Integer)
    Home_Pitcher_Record = Column('Home Pitcher Record', String)	
    Home_Pitcher_ERA = Column('Home Pitcher ERA', Float)	
    Home_Pitcher_WHIP = Column('Home Pitcher WHIP', Float)
    Home_Pitcher_Strikeouts_Per_9 = Column('Home Pitcher Strikeouts Per 9', Float)
    Home_Pitcher_Homeruns_Per_9 = Column('Home Pitcher Homeruns Per 9', Float)	
    Home_Pitcher_YRFI_Percentage = Column('Home Pitcher YRFI Percentage', Float)	
    Away_Pitcher_Name = Column('Away Pitcher Name', String)	
    Away_Pitcher_ID = Column('Away Pitcher ID', Integer)
    Away_Pitcher_Games_Started = Column('Away Pitcher Games Started', Integer)
    Away_Pitcher_Record = Column('Away Pitcher Record', String)
    Away_Pitcher_ERA = Column('Away Pitcher ERA', Float)
    Away_Pitcher_WHIP = Column('Away Pitcher WHIP', Float)
    Away_Pitcher_Strikeouts_Per_9 = Column('Away Pitcher Strikeouts Per 9', Float)
    Away_Pitcher_Homeruns_Per_9 = Column('Away Pitcher Homeruns Per 9', Float)
    Away_Pitcher_YRFI_Percentage = Column('Away Pitcher YRFI Percentage', Float)
    Home_Team_Name = Column('Home Team Name', String)	
    Home_Team_ID = Column('Home Team ID', Integer)
    Home_Team_BA = Column('Home Team BA', Float)
    Home_Team_Strikeout_Rate = Column('Home Team Strikeout Rate', Float)
    Home_Team_Homerun_Rate = Column('Home Team Homerun Rate', Float)
    Home_Team_YRFI_Percentage = Column('Home Team YRFI Percentage', Float)
    Away_Team_Name = Column('Away Team Name', String)
    Away_Team_ID = Column('Away Team ID', Integer)
    Away_Team_BA = Column('Away Team BA', Float)
    Away_Team_Strikeout_Rate = Column('Away Team Strikeout Rate', Float)
    Away_Team_Homerun_Rate = Column('Away Team Homerun Rate', Float)
    Away_Team_YRFI_Percentage = Column('Away Team YRFI Percentage', Float)
    Home_Pitcher_Pitching_Score = Column('Home Pitcher Pitching Score', Float)
    Away_Pitcher_Pitching_Score = Column('Away Pitcher Pitching Score', Float)	
    Home_Team_Hitting_Score = Column('Home Team Hitting Score', Float)	
    Away_Team_Hitting_Score = Column('Away Team Hitting Score', Float)	
    Home_Pitcher_NRFI_Score = Column('Home Pitcher NRFI Score', Float)	
    Away_Pitcher_NRFI_Score = Column('Away Pitcher NRFI Score', Float)	
    Stadium = Column('Stadium', String)	
    Ballpark_Factor = Column('Ballpark Factor', Integer)	
    Weather_Description = Column('Weather Description', String)	
    Weather_Code = Column('Weather Code', Integer)	
    Temperature = Column('Temperature', String)	
    Wind_Speed = Column('Wind Speed', String)
    Weather_Factor = Column('Weather Factor', Float)
    Overall_NRFI_Score = Column('Overall NRFI Score', Float)
    
#Today NRFI/YRFI table.
class TodayNRFITable(NRFIBaseModel, Base):
    __tablename__ = 'TodayNRFI'

#Archive NRFI/YRFI table.
class ArchiveNRFITable(NRFIBaseModel, Base):
    __tablename__ = 'ArchiveNRFI'

#Base table model for the hitting bet predictions.    
class HittingBaseModel():
    id = Column('id', Integer, primary_key=True)
    Game_ID = Column('Game ID', Integer)	
    Date = Column('Date', String)
    DateTime_String = Column('DateTime String', String)
    Hitter_Name = Column('Hitter Name', String)	
    Hitter_ID = Column('Hitter ID', Integer)	
    Hitter_Team_Name = Column('Hitter Team Name', String)	
    Hitter_Team_ID = Column('Hitter Team ID', Integer)	
    Bat_Hand = Column('Bat Hand', String)	
    BA = Column('BA', Float)	
    OBP = Column('OBP', Float)	
    OPS = Column('OPS', Float)	
    Homers = Column('Homers', Integer)	
    Vs_Left_BA = Column('Vs. Left BA', Float)	
    Vs_Right_BA = Column('Vs. Right BA', Float)	
    Pitcher_Name = Column('Pitcher Name', String)	
    Pitcher_ID = Column('Pitcher ID', Integer)	
    Pitcher_Team_Name = Column('Pitcher Team Name', String)	
    Pitcher_Team_ID = Column('Pitcher Team ID', Integer)	
    Pitching_Hand = Column('Pitching Hand', String)	
    Vs_Left_BAA = Column('Vs. Left BAA', Float)	
    Vs_Right_BAA = Column('Vs. Right BAA', Float)	
    Career_Plate_Appearances_Vs_Pitcher = Column('Career Plate Appearances Vs. Pitcher', Integer)	
    Career_BA_Vs_Pitcher = Column('Career BA Vs. Pitcher', Float)	
    Career_OPS_Vs_Pitcher = Column('Career OPS Vs. Pitcher', Float)	
    Last_10_Games_Plate_Appearances = Column('Last 10 Games Plate Appearances', Integer)	
    Last_10_Games_BA = Column('Last 10 Games BA', Float)	
    Last_10_Games_OPS = Column('Last 10 Games OPS', Float)	
    Adjusted_BA = Column('Adjusted BA', Float)
    HotCold_Description = Column('Hot/Cold Description', String)	
    HotCold_Factor = Column('Hot/Cold Factor', Float)	
    Career_Stats_Description = Column('Career Stats Description', String)	
    Career_Stats_Factor = Column('Career Stats Factor', Float)	
    Stadium = Column('Stadium', String)	
    Ballpark_Factor = Column('Ballpark Factor', Integer)	
    Weather_Description = Column('Weather Description', String)	
    Weather_Code = Column('Weather Code', Integer)	
    Temperature = Column('Temperature', String)	
    Wind_Speed = Column('Wind Speed', String)	
    Weather_Factor = Column('Weather Factor', Float)
    Overall_Hitting_Score = Column('Overall Hitting Score', Float)
    
#Today hitting table.
class TodayHittingTable(HittingBaseModel, Base):
    __tablename__ = 'TodayHitting'
    
#Archive hitting table.
class ArchiveHittingTable(HittingBaseModel, Base):
    __tablename__ = 'ArchiveHitting'
    
#SERVER ROUTES
#Route to view data from any of the tables. Data is returned in a JSON format.
@app.route('/view/<a_tableName>', methods=['GET'])
async def ViewTable(a_tableName):
    """Route used to view data from any of the tables in the database.

    This route is used to view the information from any of the tables that are stored in the database. The desired
    table is specified in the request. If the table name being requested is not valid, a 404 error is returned and an
    error message is added into the response JSON. If the table name is valid, a connection is made with the
    database, and the data from the database is acquired. The data returned from the database is looped through in
    order to build a list of dictionaries (each dictionary represents a row of the table) so that it can be returned
    in a JSON format once all rows have been processed.

    Args:
        a_tableName (string): The name of the table in the database to return the information from.

    Returns:
        A response containing JSON data representing the information that's stored in the database for the requested
        table. The JSON contains an error message if an invalid table name is provided.

    Assistance Received:
        https://stackoverflow.com/questions/37369686/how-can-i-use-a-string-to-to-represent-an-sqlalchemy-object-attribute
    """
    #First make sure that the table name is valid. If it isn't, return a 404 error.
    if a_tableName not in TABLE_NAMES:
        return jsonify({'error': 'Invalid table name.'}), 404 

    #Create a session connection to the database.
    session = Session()
    
    #Get the table class definition based on the request.
    tableClassDefinition = GetTableClassDefinition(a_tableName)

    #Query the database for the data.
    data = session.query(tableClassDefinition).all()
    session.close()
    
    #Make sure there is data in the table.
    if not data:
        return jsonify([]), 200
    
    #Loop through each row of the returned data from the database.
    tableColumns = tableClassDefinition.__table__.columns
    result = []
    for row in data:
        data_row = {}
        
        #Loop through each column of each row.
        #Assistance: https://stackoverflow.com/questions/37369686/how-can-i-use-a-string-to-to-represent-an-sqlalchemy-object-attribute
        for column in tableColumns:
            #Extract information about the individual column, and append it to the row's data. 
            columnName = column.name
            
            #Skip the id column.
            if columnName == 'id':
                continue
            
            #Note: The column name is fixed from spaces to underscores, since the variables in the database model class has underscores, not spaces.
            columnValue = getattr(row, ConvertColumnName(columnName))
            
            data_row[columnName] = columnValue        
            
        #Append the row to the overall result.
        result.append(data_row)

    return jsonify(result), 200

#Route to view information in the database on a specific date --> Mostly used with the archive tables to view specific past bet predictions.
@app.route('/view/<a_tableName>/<a_dateStr>', methods=['GET'])
async def ViewTableSpecificDate(a_tableName, a_dateStr):
    """Route used to view data from a specific date from any of the tables in the database.

    This route is used to view specific information from a certain date from any of the tables that are stored in the
    database. The desired table and date of the information returned is specified in the request. If the table name
    being requested is not valid or the date provided does not follow the required format, a 404/400 error is
    returned and an error message is added into the response JSON. If the table name is valid, a connection is made
    with the database, and the data from the database where the dates match is acquired. The data returned from the
    database is looped through in order to build a list of dictionaries (each dictionary represents a row of the
    table) so that it can be returned in a JSON format once all rows have been processed.

    Args:
        a_tableName (string): The name of the table in the database to return the information from.
        a_dateStr (string): The date to get the schedule or bet predictions from  in the format MM-DD-YYYY.

    Returns:
        A response containing JSON data representing the information that's stored in the database for the requested
        table and date. The JSON contains an error message if an invalid table name is provided.

    Assistance Received:
        https://stackoverflow.com/questions/37369686/how-can-i-use-a-string-to-to-represent-an-sqlalchemy-object-attribute
    """
    #First make sure that the table name is valid. If it isn't, return a 404 error.
    if a_tableName not in TABLE_NAMES:
        return jsonify({'error': 'Invalid table name.'}), 404 
    
    #Next, make sure the request has the date in a valid format. The format expected is: MM-DD-YYYY. Example: 05/15/2023
    try:
        #If it is valid, make sure to convert it into the correct format. Dates are stored in the database in the format MM/DD/YYYY
        dateTimeObj = datetime.strptime(a_dateStr, '%m-%d-%Y')
        formattedDateString = datetime.strftime(dateTimeObj, '%m/%d/%Y')
    except:
        return jsonify({'error': 'Invalid Date Format. Please use the format MM-DD-YYYY. Example: 05/15/2023'}), 400
    
    #If the date is in the correct format, query the database for records with that date.
    tableClassDefinition = GetTableClassDefinition(a_tableName)
    session = Session()
    data =  session.query(tableClassDefinition).filter(tableClassDefinition.Date == formattedDateString).all()
    session.close()
    
    #Make sure there is data in the returned database query.
    if not data:
        return jsonify([]), 200

    #Loop through each row of the returned data from the database.
    tableColumns = tableClassDefinition.__table__.columns
    result = []
    for row in data:
        data_row = {}
        
        #Loop through each column of each row. 
        for column in tableColumns:
            #Extract information about the individual column, and append it to the row's data. 
            columnName = column.name
            
            #Skip the id column.
            if columnName == 'id':
                continue
            
            #Note: The column name is fixed from spaces to underscores, since the variables in the database model class has underscores, not spaces.
            columnValue = getattr(row, ConvertColumnName(columnName))
            
            data_row[columnName] = columnValue        
            
        #Append the row to the overall result.
        result.append(data_row)

    return jsonify(result), 200
    
#Route to trigger an update for bet predictions for a new day.
@app.route('/update', methods=['GET'])
async def TriggerUpdate():
    """Route to trigger an update for the schedule and bet predictions.

    This route is used to trigger an update of the schedule and bet predictions for a new day. The current date that
    this route is called is generated, and the schedule along with the bet predictions are generated asynchronously
    so that the server is still responsive while a bet update is ongoing (see UpdateBetPredictions()). Once the
    schedule and bet predictions are generated they are inserted into their correct tables in the database.

    Returns:
        A response containing simple json data letting the user know that a bet prediction update was successful.

    Assistance Received:
        https://superfastpython.com/asyncio-to_thread/
    """
    date = datetime.now()

    #Asynchronously create and update the bet predictions for a new day.
    #It is done asynchronously in the background so that the server does not freeze up while the bet predictions are being created.
    await asyncio.to_thread(UpdateBetPredictions, CURRENT_OPENING_DAY, date, CURRENT_SEASON)

    return jsonify({'result': 'Bet update successfully completed.'}), 200 

#Helper function for the update route. Creates all of the bet prediction dataframes and then stores them in the database.
def UpdateBetPredictions(a_openingDayDate, a_date, a_season):
    """Creates the schedule table and bet predictions, and stores them in the database.

    This function is called asynchronously, and utilizes the BetPredictor class to create the schedule, NRFI/YRFI bet
    predictions, and the hitting bet predictions. Once the schedule and bet predictions are created,
    they are inserted into the database for storage (see UpdateTableInDatabase()).

    Args:
        a_openingDayDate (datetime): The date of opening day of the season.
        a_date (datetime): The date the schedule and bet predictions will be generated for.
        a_season (int): The season the schedule and bet predictions will be generated for.

    Returns:
        Nothing.
    """
    bp = BetPredictor()
    
    #Create all three bet prediction tables.
    print('Creating Schedule table.')
    scheduleDataFrame = bp.CreateSchedule(a_date, a_season)
    print('Creating NRFI table.')
    NRFIDataFrame = bp.CreateNRFIPredictions(scheduleDataFrame, a_openingDayDate, a_season)
    print('Creating Hitting table.')
    hittingDataFrame = bp.CreateHittingPredictions(scheduleDataFrame, a_openingDayDate, a_date, a_season)
    print('All done creating tables, updating them into the database.')
         
    #Update the database with the newly created bet predictions.
    UpdateTableInDatabase(scheduleDataFrame, TodayScheduleTable, ArchiveScheduleTable)   
    UpdateTableInDatabase(NRFIDataFrame, TodayNRFITable, ArchiveNRFITable)    
    UpdateTableInDatabase(hittingDataFrame, TodayHittingTable, ArchiveHittingTable)    

def UpdateTableInDatabase(a_dataFrame, a_todayTable, a_archiveTable):
    """Triggers a database update for a table.

    This function is used to update one of the three main "Today" tables, based on information from a provided
    DataFrame. First, all the data inside the "Today" table is copied over into its respective archive table (see
    MoveDataToArchive()). Then, the "Today" table is completely cleared (see DeleteData()). Every row of the provided
    DataFrame is then looped through and inserted into the database inside the "a_todayTable" table.

    Args:
        a_dataFrame (pandas.DataFrame): A pandas DataFrame containing information to insert into a database table.
        a_todayTable (string): The name of the table to insert the DataFrame's data into.
        a_archiveTable (string): The name of the archive table to copy the existing today table data into.

    Returns:
        Nothing.
    """
    #First, move the data from the today table to its archive table.
    MoveDataToArchive(a_todayTable, a_archiveTable)
    
    #Next, clear the data in the today table.
    DeleteData(a_todayTable)
    
    #Then, insert the newly created data into the today table.
    session = Session()
    
    #Loop through each row of the provided dataframe.
    for index, row in a_dataFrame.iterrows():
        data_dict = {}
        #Loop through each column of each row, and create a dictionary representing its data.
        for column in a_todayTable.__table__.columns:
            columnName = column.name

            #Skip the id column, since it is automatically handled by SQLAlchemy.
            if columnName == 'id':
                continue

            data_dict[ConvertColumnName(column.name)] = row[column.name]
    
        #Unpack the dictionary because it sends each key/value pair as an argument to the constructor.
        data = a_todayTable(**data_dict)
        session.add(data)
    
    session.commit()
    session.close()

#Helper function for the view route, used to get the class definition for a table.
def GetTableClassDefinition(a_tableName):
    """Helper function for the view routes of the server, used to get the class definition for a table.

    Args:
        a_tableName (string): The name of the table to get the class definition for.

    Returns:
        A "type", representing the class definition for a table used in the database.
    """
    if a_tableName == 'TodaySchedule':
        return TodayScheduleTable
    elif a_tableName == 'ArchiveSchedule':
        return ArchiveScheduleTable
    elif a_tableName == 'TodayNRFI':
        return TodayNRFITable
    elif a_tableName == 'ArchiveNRFI':
        return ArchiveNRFITable
    elif a_tableName == 'TodayHitting':
        return TodayHittingTable
    elif a_tableName == 'ArchiveHitting':
        return ArchiveHittingTable
    #An invalid table name is provided to this function.
    else:
        return None    

#Helper function for the view route, used to convert column names into their variable names in the model classes (since class variables cannot contain spaces and other special characters).
def ConvertColumnName(a_columnName):
    """Helper function used to convert column names when going from database column names to table class names.

    This helper function is used to convert a column name that's used in the actual database, to the corresponding
    column name used in the table subclasses (TodaySchedule, ArchiveSchedule, etc.). Spaces are replaced by
    underscores, and any periods or slashes are removed since these characters cannot be in variable names. An
    example is conversion of "Game ID" to "Game_ID". This function is used when dealing with column names
    programmatically.

    Args:
        a_columnName (string): The name of the column used in the actual database to be converted.

    Returns:
        A string, representing the converted column name.
    """
    #Convert spaces to underscores.
    modifiedColumnName = a_columnName.replace(' ', '_')
    
    #Remove special characters as necessary (/ and .)
    modifiedColumnName = modifiedColumnName.replace('.', '')
    modifiedColumnName = modifiedColumnName.replace('/', '')
    
    return modifiedColumnName

#Moves all of the data in one of the database tables, to another. Used from moving data from a "Today" table to an "Archive" table.
def MoveDataToArchive(a_sourceTable, a_destinationTable):
    """Moves data from a source table to a destination table.

    This function is used to copy all the data from a source table into a destination table. A connection is made with
    the database, and the data from the source table is extracted. Then, each row of the source table is looped
    through, and each column in each of those rows (besides the id column) is copied into a new row that will be
    inserted into the destination table. If the column types mismatch between the two tables, an error is displayed
    and no data is copied over to the destination table. This process continues until all the rows from the source
    table are successfully copied over to the destination table.

    Args:
        a_sourceTable (string): The name of the source table.
        a_destinationTable: The name of the destination table to receive the copied data.

    Returns:
        Nothing.
    """
    #Create a session connection to the database.
    session = Session()
    
    #Query the database for the source data.
    data = session.query(a_sourceTable).all()
    
    #Make sure data was returned before trying to move anything.
    if not data:
        return
    
    #Loop through each row of the source table.
    tableColumns = a_sourceTable.__table__.columns
    for sourceRow in data:
        destinationRow = a_destinationTable()
        
        #Loop through each column of each row.
        for sourceColumn in tableColumns:
            sourceColumnName = sourceColumn.name
            
            #Allow SQLAlchemy to automatically handle the id column.
            if sourceColumnName == 'id':
                continue
            
            #Attempt to copy the data from the source table row to the destination table row. 
            try:
                columnValue = getattr(sourceRow, ConvertColumnName(sourceColumnName))
                setattr(destinationRow, ConvertColumnName(sourceColumnName), columnValue)
            except Exception as error:
                print(error)
                print('Error moving data - column mismatch! Could not move the data from the source table to the destination table.')
                return
            
        #Add the newly created destination row to the destination table.
        session.add(destinationRow)
        session.commit()
        
    session.close()
    
#Deletes the contents of a database table.
def DeleteData(a_table):
    """Deletes the contents of a database table.

    This function is used to delete the contents of a databased, based on the provided name of the table to be deleted.
    A connection is created with the database, and a query to clear the table is sent.

    Args:
        a_table (string): The name of the table to be deleted.

    Returns:
        Nothing.
    """
    #Create a session connection to the database.
    session = Session()

    #Delete the contents of the provided table.
    session.query(a_table).delete()
    session.commit()        
    session.close()
    
'''
#https://stackoverflow.com/questions/17717877/convert-sqlalchemy-query-result-to-a-list-of-dicts
@app.route('/accuracy', methods=['GET'])
async def Accuracy():
    session = Session()
    
    date = CURRENT_OPENING_DAY
    
    #Initialize the totals for the accuracy check.
    totalGames = 0
    totalNRFIWin = 0
    totalYRFIWin = 0
    totalHitters = 0
    totalAtLeast1HitWin = 0
    totalAtLeast2HitsWin = 0
    totalAtLeast2HRRWin = 0           
    totalAtLeast3HRRWin = 0           

    while date < datetime.today():
        formattedDateString = datetime.strftime(date, '%m/%d/%Y')
       
        NRFIYRFIdata = session.query(ArchiveNRFITable).filter(ArchiveNRFITable.Date == formattedDateString).all()
        Hittingdata = session.query(ArchiveHittingTable).filter(ArchiveHittingTable.Date == formattedDateString).all()     
        
        NRFIYRFIDataFrame = pd.DataFrame([row.__dict__ for row in NRFIYRFIdata])
        hittingDataFrame = pd.DataFrame([row.__dict__ for row in Hittingdata])
        
        #Test the accuracy of the top NRFI and YRFI bets.
        if not NRFIYRFIDataFrame.empty:
            topNRFIBet = NRFIYRFIDataFrame.head(1)
            topYRFIBet = NRFIYRFIDataFrame.tail(1)
        
            topNRFIGame = Game(int(topNRFIBet['Game_ID']))
            topYRFIGame = Game(int(topYRFIBet['Game_ID']))
        
            if not topNRFIGame.DidYRFIOccur(): totalNRFIWin += 1
            if topYRFIGame.DidYRFIOccur(): totalYRFIWin += 1

        date += timedelta(days=1)
        
    session.close()
    
    print(totalNRFIWin)
    print(totalYRFIWin)
    
    return jsonify({'done': 'done'}), 200 
    

#Make sure that the tables are created if they do not already exist.
Base.metadata.create_all(engine)

#Start the server.
app.run(host='Omitted', port='Omitted')
'''