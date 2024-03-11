#LOCALFACTORS CLASS. Handles everything regarding local factors of the bet predictions - including ballpark factors and weather.

from Endpoints import Endpoints
from datetime import datetime, timedelta

class LocalFactors():
    #CONSTANTS
    #API key for the Weather API
    WEATHER_API_KEY = 'Example Weather API Key'
    
    #All MLB stadiums and their corresponding information about them.
    #NOTE: Ballpark factors based on data from 2021-2023.
    BALLPARK_INFORMATION = {
        'Coors Field': { 'homeTeam': 'Colorado Rockies', 'ballparkFactor': 112, 'city': 'Denver', 'hasRoof': False },
        'Fenway Park': { 'homeTeam': 'Boston Red Sox', 'ballparkFactor': 108, 'city': 'Boston', 'hasRoof': False },
        'Great American Ball Park': { 'homeTeam': 'Cincinnati Reds', 'ballparkFactor': 107, 'city': 'Cincinnati', 'hasRoof': False },
        'Kauffman Stadium': { 'homeTeam': 'Kansas City Royals', 'ballparkFactor': 104, 'city': 'Kansas City', 'hasRoof': False },
        'Nationals Park': { 'homeTeam': 'Washington Nationals', 'ballparkFactor': 103, 'city': 'Washington', 'hasRoof': False },
        'Globe Life Field': { 'homeTeam': 'Texas Rangers', 'ballparkFactor': 102, 'city': 'Arlington', 'hasRoof': True },
        'PNC Park': { 'homeTeam': 'Pittsburgh Pirates', 'ballparkFactor': 101, 'city': 'Pittsburgh', 'hasRoof': False },
        'Truist Park': { 'homeTeam': 'Atlanta Braves', 'ballparkFactor': 101, 'city': 'Atlanta', 'hasRoof': False },
        'Wrigley Field': { 'homeTeam': 'Chicago Cubs', 'ballparkFactor': 101, 'city': 'Chicago', 'hasRoof': False },
        'Citizens Bank Park': { 'homeTeam': 'Philadelphia Phillies', 'ballparkFactor': 101, 'city': 'Philadelphia', 'hasRoof': False },
        'Oriole Park at Camden Yards': { 'homeTeam': 'Baltimore Orioles', 'ballparkFactor': 101, 'city': 'Baltimore', 'hasRoof': False },
        'Chase Field': { 'homeTeam': 'Arizona Diamondbacks', 'ballparkFactor': 100, 'city': 'Phoenix', 'hasRoof': True },
        'Target Field': { 'homeTeam': 'Minnesota Twins', 'ballparkFactor': 100, 'city': 'Minneapolis', 'hasRoof': False },
        'Angel Stadium': { 'homeTeam': 'Los Angeles Angels', 'ballparkFactor': 100, 'city': 'Anaheim', 'hasRoof': False },
        'Rogers Centre': { 'homeTeam': 'Toronto Blue Jays', 'ballparkFactor': 100, 'city': 'Toronto', 'hasRoof': True },
        'Minute Maid Park': { 'homeTeam': 'Houston Astros', 'ballparkFactor': 100, 'city': 'Houston', 'hasRoof': True },
        'Guaranteed Rate Field': { 'homeTeam': 'Chicago White Sox', 'ballparkFactor': 100, 'city': 'Chicago', 'hasRoof': False },
        'Busch Stadium': { 'homeTeam': 'St. Louis Cardinals', 'ballparkFactor': 99, 'city': 'Saint Louis', 'hasRoof': False },
        'Dodger Stadium': { 'homeTeam': 'Los Angeles Dodgers', 'ballparkFactor': 99, 'city': 'Los Angeles', 'hasRoof': False },
        'Yankee Stadium': { 'homeTeam': 'New York Yankees', 'ballparkFactor': 98, 'city': 'New York', 'hasRoof': False },
        'loanDepot park': { 'homeTeam': 'Miami Marlins', 'ballparkFactor': 98, 'city': 'Miami', 'hasRoof': True },
        'Oracle Park': { 'homeTeam': 'San Francisco Giants', 'ballparkFactor': 97, 'city': 'San Francisco', 'hasRoof': False },
        'Comerica Park': { 'homeTeam': 'Detroit Tigers', 'ballparkFactor': 97, 'city': 'Detroit', 'hasRoof': False },
        'Progressive Field': { 'homeTeam': 'Cleveland Guardians', 'ballparkFactor': 97, 'city': 'Cleveland', 'hasRoof': False },
        'American Family Field': { 'homeTeam': 'Milwaukee Brewers', 'ballparkFactor': 97, 'city': 'Milwaukee', 'hasRoof': True },
        'Citi Field': { 'homeTeam': 'New York Mets', 'ballparkFactor': 96, 'city': 'New York', 'hasRoof': False },
        'Tropicana Field': { 'homeTeam': 'Tampa Bay Rays', 'ballparkFactor': 96, 'city': 'Saint Petersburg Florida', 'hasRoof': False },
        'Oakland Coliseum': {'homeTeam': 'Oakland Athletics', 'ballparkFactor': 96, 'city': 'Oakland', 'hasRoof': False },
        'Petco Park': { 'homeTeam': 'San Diego Padres', 'ballparkFactor': 95, 'city': 'San Diego', 'hasRoof': False },
        'T-Mobile Park': { 'homeTeam': 'Seattle Mariners', 'ballparkFactor': 92, 'city': 'Seattle', 'hasRoof': True }
    }
    
    #Represents the weather description codes and their associated impacts.
    LOW_WEATHER_IMPACT_CODES = []
    
    MODERATE_WEATHER_IMPACT_CODES = []
    
    HIGH_WEATHER_IMPACT_CODES = []
    
    #Weights of each weather impact classification.
    NO_WEATHER_IMPACT_WEIGHT = 'Omitted'
    
    LOW_WEATHER_IMPACT_WEIGHT = 'Omitted'
    
    MODERATE_WEATHER_IMPACT_WEIGHT = 'Omitted'
    
    HIGH_WEATHER_IMPACT_WEIGHT = 'Omitted'
    
    #CONSTRUCTOR
    def __init__(self):
        #Endpoint object from the Endpoints class to handle MLB API access.
        self.m_endpointObj = Endpoints()

    #Gets the ballpark factor for a stadium, if it exists.
    def GetBallparkFactor(self, a_stadiumName):
        if a_stadiumName in self.BALLPARK_INFORMATION:
            return self.BALLPARK_INFORMATION[a_stadiumName]['ballparkFactor']
        else:
            return 'Unknown'
        
    #Gets the home team for a stadium, if it exists.
    def GetHomeTeamForStadium(self, a_stadiumName):
        if a_stadiumName in self.BALLPARK_INFORMATION:
            return self.BALLPARK_INFORMATION[a_stadiumName]['homeTeam']
        else:
            return 'Unknown'
        
    #Gets the city that a stadium resides in, if it exists.
    def GetCityForStadium(self, a_stadiumName):
        if a_stadiumName in self.BALLPARK_INFORMATION:
            return self.BALLPARK_INFORMATION[a_stadiumName]['city']
        else:
            return 'Unknown'
        
    #Determines whether or not a stadium has a roof or not - useful since weather does not impact stadiums that have roofs.
    def HasRoof(self, a_stadiumName):
        if a_stadiumName in self.BALLPARK_INFORMATION:
            return self.BALLPARK_INFORMATION[a_stadiumName]['hasRoof']
        else:
            return 'Unknown'

    #Gets the weather at a stadium given a stadium name and a time.
    def GetWeather(self, a_stadiumName, a_timeOfGame):
        #Make sure the stadium exists.
        if a_stadiumName not in self.BALLPARK_INFORMATION:
            return 'Unknown'
        
        stadiumCity = self.GetCityForStadium(a_stadiumName)
        
        #Create the endpoint for the Weather API and access it's data.
        weatherEndpoint = self.m_endpointObj.GetWeatherEndpoint(self.WEATHER_API_KEY, stadiumCity)
        weatherData = self.m_endpointObj.AccessEndpointData(weatherEndpoint)
        
        #Extract the hourly forecast data from the data returned from the Weather API. Note: The hourly forecast is split into 24 individual hours based on a 24-hour clock.
        forecast = weatherData['forecast']['forecastday'][0]['hour']
        
        #Obtain the weather data for the hour closest to the start of the game. 
        index = self.ConvertTime(a_timeOfGame)
        hourlyForecast = forecast[index]
        
        cityName = weatherData['location']['name']
        region = weatherData['location']['region']
        temperatureF = hourlyForecast['temp_f']
        weatherCondition = hourlyForecast['condition']['text'].strip()
        weatherCode = int(hourlyForecast['condition']['code'])
        windSpeed = hourlyForecast['wind_mph']
        
        return { 'cityName': cityName,
                 'region': region,
                 'temperatureF': temperatureF,
                 'weatherCondition': weatherCondition,
                 'weatherCode': weatherCode,
                 'windSpeed': windSpeed }
        
    #Helper function to convert a time to its closest 24 hour time hour. Example: 7:07 PM --> 15.
    #Assistance: https://stackoverflow.com/questions/67686033/adding-hours-and-days-to-the-python-datetime
    def ConvertTime(self, a_timeToConvert):
        #Convert the string time to a datetime object.
        timeObj = datetime.strptime(a_timeToConvert, '%I:%M %p')
        
        #Round the time to the nearest hour by increasing the hour if necessary.
        if timeObj.minute >= 30:
            timeObj += timedelta(hours=1)

        return timeObj.hour
    
    #Determines the weather impact factor based on the weather classification code.
    def CalculateWeatherFactor(self, a_weatherCode, a_stadium):
        #Games that are played at stadiums with a roof are not impacted by the outside weather.
        if self.HasRoof(a_stadium) == True or self.HasRoof(a_stadium) == 'Unknown':
            return self.NO_WEATHER_IMPACT_WEIGHT
        
        if a_weatherCode in self.LOW_WEATHER_IMPACT_CODES:
            return self.LOW_WEATHER_IMPACT_WEIGHT
        elif a_weatherCode in self.MODERATE_WEATHER_IMPACT_CODES:
            return self.MODERATE_WEATHER_IMPACT_WEIGHT
        elif a_weatherCode in self.HIGH_WEATHER_IMPACT_CODES:
            return self.HIGH_WEATHER_IMPACT_WEIGHT
        else:
            #If the code was not in any of the above lists of codes, the weather does not have any impact on the bet predictions.
            return self.NO_WEATHER_IMPACT_WEIGHT