#SERVER file. Handles everything related to the server and database access.

from re import A
from quart import Quart, jsonify
import asyncio
from sqlalchemy import create_engine, Column, Integer, String, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import pandas as pd
from BetPredictor import BetPredictor

#CONSTANTS
TABLE_NAMES = ['TodaySchedule', 'ArchiveSchedule', 'TodayNRFI', 'ArchiveNRFI', 'TodayHitting', 'ArchiveHitting']

OPENING_DAY_2023 = datetime.strptime('03/30/2023', '%m/%d/%Y')
CLOSING_DAY_2023 = datetime.strptime('10/01/2023', '%m/%d/%Y')

CURRENT_OPENING_DAY = OPENING_DAY_2023
CURRENT_CLOSING_DAY = CLOSING_DAY_2023
CURRENT_SEASON = 2023

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
async def viewTable(a_tableName):
    #First make sure that the table name is valid. If it isn't, return a 404 error.
    if a_tableName not in TABLE_NAMES:
        return jsonify({'error': 'Invalid Table Name'}), 404 

    #Create a session connection to the database.
    session = Session()
    
    #Get the table class definition based on the request.
    tableClassDefinition = GetTableClassDefinition(a_tableName)

    #Query the database for the data.
    data = session.query(tableClassDefinition).all()
    session.close()
    
    #Make sure there is data in the table.
    if not data:
        return jsonify({}), 200
    
    #Loop through each row of the table in the database.
    tableColumns = tableClassDefinition.__table__.columns
    tableInformation = []
    for row in data:
        data_row = {}
        
        #Loop through each column for each row.
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
            
        #Append the row to the overall table information.
        tableInformation.append(data_row)

    return jsonify(tableInformation), 200

#Helper function for the view route, used to get the class definition for a table.
def GetTableClassDefinition(a_tableName):
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
    #Convert spaces to underscores.
    modifiedColumnName = a_columnName.replace(' ', '_')
    
    #Remove special characters as necessary (/ and .)
    modifiedColumnName = modifiedColumnName.replace('.', '')
    modifiedColumnName = modifiedColumnName.replace('/', '')
    
    return modifiedColumnName

#Moves all of the data in one of the database tables, to another. Used from moving data from a "Today" table to an "Archive" table.
async def MoveDataToArchive(a_sourceTable, a_destinationTable):
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
            
        #Add the newly created desination row to the destination table.
        session.add(destinationRow)
        session.commit()
        
    session.close()
    
#Deletes the contents of a database table.
async def DeleteData(a_table):
    #Create a session connection to the database.
    session = Session()

    #Delete the contents of the provided table.
    session.query(a_table).delete()
    session.commit()        
    session.close()

#Make sure that the tables are created if they do not already exist.
Base.metadata.create_all(engine)

#Start the server.
app.run()
