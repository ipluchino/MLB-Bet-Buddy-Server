#LOCALFACTORS CLASS. Handles everything regarding local factors of the bet predictions - including ballpark factors and weather.

class LocalFactors():
    #All MLB stadiums are their corresponding ballpark factors as well as their associated home teams.
    #NOTE: Based on data from 2021-2023.
    BALLPARK_FACTORS = {
        'Coors Field': { 'homeTeam': 'Colorado Rockies', 'ballparkFactor': 112 },
        'Fenway Park': { 'homeTeam': 'Boston Red Sox', 'ballparkFactor': 108 },
        'Great American Ball Park': { 'homeTeam': 'Cincinnati Reds', 'ballparkFactor': 107 },
        'Kauffman Stadium': { 'homeTeam': 'Kansas City Royals', 'ballparkFactor': 104 },
        'Nationals Park': { 'homeTeam': 'Washington Nationals', 'ballparkFactor': 103 },
        'Globe Life Field': { 'homeTeam': 'Texas Rangers', 'ballparkFactor': 102 },
        'PNC Park': { 'homeTeam': 'Pittsburgh Pirates', 'ballparkFactor': 101 },
        'Truist Park': { 'homeTeam': 'Atlanta Braves', 'ballparkFactor': 101 },
        'Wrigley Field': { 'homeTeam': 'Chicago Cubs', 'ballparkFactor': 101 },
        'Citizens Bank Park': { 'homeTeam': 'Philadelphia Phillies', 'ballparkFactor': 101 },
        'Oriole Park at Camden Yards': { 'homeTeam': 'Baltimore Orioles', 'ballparkFactor': 101 },
        'Chase Field': { 'homeTeam': 'Arizona Diamondbacks', 'ballparkFactor': 100 },
        'Target Field': { 'homeTeam': 'Minnesota Twins', 'ballparkFactor': 100 },
        'Angel Stadium': { 'homeTeam': 'Los Angeles Angels', 'ballparkFactor': 100 },
        'Rogers Centre': { 'homeTeam': 'Toronto Blue Jays', 'ballparkFactor': 100 },
        'Minute Maid Park': { 'homeTeam': 'Houston Astros', 'ballparkFactor': 100 },
        'Guaranteed Rate Field': { 'homeTeam': 'Chicago White Sox', 'ballparkFactor': 100 },
        'Busch Stadium': { 'homeTeam': 'St. Louis Cardinals', 'ballparkFactor': 99 },
        'Dodger Stadium': { 'homeTeam': 'Los Angeles Dodgers', 'ballparkFactor': 99 },
        'Yankee Stadium': { 'homeTeam': 'New York Yankees', 'ballparkFactor': 98 },
        'loanDepot park': { 'homeTeam': 'Miami Marlins', 'ballparkFactor': 98 },
        'Oracle Park': { 'homeTeam': 'San Francisco Giants', 'ballparkFactor': 97 },
        'Comerica Park': { 'homeTeam': 'Detroit Tigers', 'ballparkFactor': 97 },
        'Progressive Field': { 'homeTeam': 'Cleveland Guardians', 'ballparkFactor': 97 },
        'American Family Field': { 'homeTeam': 'Milwaukee Brewers', 'ballparkFactor': 97 },
        'Citi Field': { 'homeTeam': 'New York Mets', 'ballparkFactor': 96 },
        'Tropicana Field': { 'homeTeam': 'Tampa Bay Rays', 'ballparkFactor': 96 },
        'Oakland Coliseum': {'homeTeam': 'Oakland Athletics', 'ballparkFactor': 96 },
        'Petco Park': { 'homeTeam': 'San Diego Padres', 'ballparkFactor': 95 },
        'T-Mobile Park': { 'homeTeam': 'Seattle Mariners', 'ballparkFactor': 92 }
    }
    
    #CONSTRUCTOR
    def __init__(self):
        #Nothing to do here for now.
        pass

    #Gets the ballpark factor for a stadium, if it exists.
    def GetBallparkFactor(self, a_stadiumName):
        if a_stadiumName in self.BALLPARK_FACTORS:
            return self.BALLPARK_FACTORS[a_stadiumName]['ballparkFactor']
        else:
            return 'Unknown'
        
    #Gets the home team for a stadium, if it exists.
    def GetHomeTeamForStadium(self, a_stadiumName):
        if a_stadiumName in self.BALLPARK_FACTORS:
            return self.BALLPARK_FACTORS[a_stadiumName]['homeTeam']
        else:
            return 'Unknown'



