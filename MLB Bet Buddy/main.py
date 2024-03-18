from Endpoints import Endpoints
from datetime import datetime, timedelta
from Team import Team
from Game import Game
from Player import Player
from Hitter import Hitter
from Pitcher import Pitcher
from LocalFactors import LocalFactors
from BetPredictor import BetPredictor

#Temporarily opening day for 2023.
OPENING_DAY = datetime.strptime('03/30/2023', '%m/%d/%Y')
CLOSING_DAY = datetime.strptime('10/01/2023', '%m/%d/%Y')
SEASON = 2023

'''
e = Endpoints()

#TESTING ALL ENDPOINTS
print(e.GetGameEndpoint(765727) + '\n')                                                                                 #Analyzing an individual game.
print(e.GetTeamOffensiveEndpoint(111, 2023, OPENING_DAY, datetime.strptime('05/15/2023', '%m/%d/%Y')) + '\n')           #Yankees offensive statistics in a date range.
print(e.GetIndividualHittingEndpoint(592450, 2023, OPENING_DAY, datetime.strptime('08/11/2023', '%m/%d/%Y')) + '\n')    #Aaron Judge stats in a date range.
print(e.GetIndividualPitchingEndpoint(543037, 2023, OPENING_DAY, datetime.strptime('08/11/2023', '%m/%d/%Y')) + '\n')   #Gerrit Cole stats in a date range.s
print(e.GetTodayScheduleEndpoint(OPENING_DAY, OPENING_DAY) + '\n')                                                           #Schedule on opening day.
print(e.GetStandingsEndpoint(datetime.strptime('06/30/2023', '%m/%d/%Y'), 2023) + '\n')                                 #Standings on 6/30/2023.
print(e.GetHittingGameLogEndpoint(592450, 2023, OPENING_DAY, datetime.strptime('04/30/2023', '%m/%d/%Y')) + '\n')       #1 month game log of Aaron Judge.
print(e.GetPitchingGameLogEndpoint(543037, 2023, OPENING_DAY, datetime.strptime('04/30/2023', '%m/%d/%Y')) + '\n')      #1 month game log of Gerrit Cole.
print(e.GetCareerHittingNumbersEndpoint(592450, 601713) + '\n')                                                         #Aaron Judge career numbers vs Pivetta.
print(e.GetTeamGameLogEndpoint(147, 2023, OPENING_DAY, datetime.strptime('04/30/2023', '%m/%d/%Y')) + '\n')             #Yankees game log from opening day until 04/30/2023.

test_endpoint = e.GetCareerHittingNumbersEndpoint(592450, 601713)
print(e.AccessEndpointData(test_endpoint))
'''

'''
#TESTING THE TEAM CLASS.
testDate = datetime.strptime('05/11/2023', '%m/%d/%Y')

#Testing with Cardinals.
test = Team(138)
print('Team ID:', test.GetTeamID())
print('Team Name:', test.GetTeamName())
print('Team Record on', str(testDate) + ':', test.GetRecord(testDate, SEASON), '\n')

#Switching and testing with yankees.
testDate = datetime.strptime('07/27/2023', '%m/%d/%Y')
test.SetTeam(114)
print('Team ID:', test.GetTeamID())
print('Team Name:', test.GetTeamName())
print('Team Record on', str(testDate) + ':', test.GetRecord(testDate, SEASON), '\n')

print('Team offensive statistics for the Yankees for the entire 2023 season: \n')
print(test.GetTeamOffensiveStatistics(2023, OPENING_DAY, CLOSING_DAY))
'''

'''
#TESTING THE GAME, TEAM, AND LOCALFACTORS CLASSES TOGETHER.f
g = Game(718253)

print('Game ID:', g.GetGameID())
print('Date:', g.GetGameDate())
print('Game Time:', g.GetGameTime(), '\n')

print('Home Team:', g.GetHomeTeamName())
print('Home Starting Pitcher:', g.GetHomeStartingPitcherName())
homeTeam = Team(g.GetHomeTeamID())
print('Home Team Record:', homeTeam.GetRecord(g.GetGameDate(), 2023), '\n')

print('Away Team:', g.GetAwayTeamName())
print('Away Starting Pitcher:', g.GetAwayStartingPitcherName())
awayTeam = Team(g.GetAwayTeamID())
print('Away Team Record:', awayTeam.GetRecord(g.GetGameDate(), 2023), '\n')

print('Stadium:', g.GetStadium())
ballparkFactors = LocalFactors()
print('Ballpark Factor:', ballparkFactors.GetBallparkFactor(g.GetStadium()))
print('Ballpark City:', ballparkFactors.GetCityForStadium(g.GetStadium()))
print('Ballpark Weather:', ballparkFactors.GetWeather(g.GetStadium(), g.GetGameTime()))
print('Game final?', g.IsGameFinal(), '\n')

print('Was a run scored in the first inning?', g.DidYRFIOccur())
print('Did the home team score in the first inning?', g.DidTeamScoreFirstInning(g.GetHomeTeamID()))
print('Did the away team score in the first inning?', g.DidTeamScoreFirstInning(g.GetAwayTeamID()))
print('Did the home pitcher,', g.GetHomeStartingPitcherName(), ', let up a run in the first inning?', g.DidPitcherLetUpRunFirstInning(g.GetHomeStartingPitcherID()))
print('Did the away pitcher,', g.GetAwayStartingPitcherName(), ', let up a run in the first inning?', g.DidPitcherLetUpRunFirstInning(g.GetAwayStartingPitcherID()))
print()
'''

'''
print('\n')
print('PLAYER ID LOOKUP TESTING:')
print('Aaron Judge ID:', Player.FindPlayerID('Aaron Judge'))
print('Anthony Volpe ID:', Player.FindPlayerID('Anthony Volpe'))
print('Gerrit Cole ID:', Player.FindPlayerID('Gerrit Cole'))
print('Bo Bichette ID:', Player.FindPlayerID('Bo Bichette'))
print('Fake Player ID:', Player.FindPlayerID('Totally Fake Player'))
'''

'''
#Note: Test player with only 2 at bats in 2023 is Alejo Lopez.

h = Hitter(Player.FindPlayerID('Aaron Judge'))
p = Pitcher(Player.FindPlayerID('Tyler Wells'))

d1 = datetime.strptime('05/10/2023', '%m/%d/%Y')
d2 = datetime.strptime('06/10/2023', '%m/%d/%Y')
print('Aaron Judge\'s stats from', d1, 'TO', d2, ':')
print(h.GetOffensiveStatistics(2023, d1, d2))

print('\n')
print('Aaron Judge\'s vsLeft and vsRight splits:')
print(h.GetLRHittingSplits(2023))

print('\n')
print('Aaron Judge\'s stats hitting against Tyler Wells')
print(h.GetCareerStatsOffPitcher(p.GetPlayerID()))
print('\n')
'''

'''
#TESTING PITCHER STATISTICS.
print('Gerrit Cole\'s statistics from opening day to closing day:')
p2 = Pitcher(Player.FindPlayerID('Gerrit Cole'))
print(p2.GetPitchingStatistics(2023, OPENING_DAY, CLOSING_DAY))
print('\n')

print('Gerrit Cole hand information:')
print(p2.GetHandInformation())
print('\n')

print('Gerrit Cole LR Splits:')
print(p2.GetLRPitchingSplits(2023))

#print(p2.CalculateYRFIPercentage(2023, OPENING_DAY, CLOSING_DAY))
'''

'''
allHitters = Hitter.GetAllHitters(2023)
print('All hitters that need to be checked in the 2023 season. In total there are', len(allHitters), 'hitters that need to be checked.')
for h in allHitters:
    print(h)9
    #currentHitter = Hitter(h['playerID'])
    #print(currentHitter.GetOffensiveStatistics(2023, d1, d2))
'''
    
'''
#TESTING WEATHER GATHERING FOR ALL STADIUMS.
localFactors = LocalFactors()

for stadium in localFactors.BALLPARK_INFORMATION:
    print(localFactors.GetWeather(stadium, '7:41 PM'))  
'''

'''
#LAST 10 GAMES TESTING.
date = datetime.strptime('06/10/2023', '%m/%d/%Y')

allHitters = Hitter.GetAllHitters(2023)
print(len(allHitters))

for hitter in allHitters:
    currentHitter = Hitter(hitter['playerID'])
    print(currentHitter.Last10Stats(2023, date))
'''

'''
#TESTING TEAM YRFI PERCENTAGE
date = datetime.strptime('06/10/2023', '%m/%d/%Y')
#for team in Team.MLB_TEAM_IDS:
#    teamObj = Team(team['id'])
#    YRFIRate = teamObj.CalculateYRFIPercentage(2023, OPENING_DAY, date)
#    print(teamObj.GetTeamName(), YRFIRate)

team = Team.CreateFromName('Toronto Blue Jays')
print(team.GetTeamName(), team.GetTeamID())
print(team.CalculateYRFIPercentage(2023, OPENING_DAY, CLOSING_DAY))
'''

'''
date = datetime.strptime('07/02/2023', '%m/%d/%Y')
while True:
    bp = BetPredictor()

    schedule = bp.CreateSchedule(date, 2023)
    #schedule.to_excel('schedule.xlsx')
    schedule.to_excel('schedule_' + date.strftime('%m-%d-%Y') +'.xlsx')

    #NRFI = bp.CreateNRFIPredictions(schedule, OPENING_DAY, 2023)
    #NRFI.to_excel('NRFI.xlsx')
    #NRFI.to_excel('NRFI_' + date.strftime('%m-%d-%Y') +'.xlsx')
    
    hitting = bp.CreateHittingPredictions(schedule, OPENING_DAY, date, 2023)
    hitting.to_excel('hitting_' + date.strftime('%m-%d-%Y') +'.xlsx')
    
    date += timedelta(days=1)
'''

'''
t = Team(147)
print(t.GetTeamName())
print(t.CalculateYRFIPercentage(2024, datetime.strptime('03/28/2024', '%m/%d/%Y'), datetime.strptime('03/28/2024', '%m/%d/%Y')))
'''


#bp = BetPredictor()
#date = datetime.strptime('07/08/2023', '%m/%d/%Y')
#schedule = bp.CreateSchedule(date, 2023)
#schedule.to_excel('schedule_' + date.strftime('%m-%d-%Y') +'.xlsx')

#NRFI = bp.CreateNRFIPredictions(schedule, OPENING_DAY, 2023)
#NRFI.to_excel('NRFI_' + date.strftime('%m-%d-%Y') +'.xlsx')

#hitting = bp.CreateHittingPredictions(schedule, OPENING_DAY, date, 2023)
#hitting.to_excel('hitting_' + date.strftime('%m-%d-%Y') +'.xlsx')

#p = Pitcher(641656)
#print(p.GetPitchingStatistics(2023, OPENING_DAY, datetime.strptime('07/01/2023', '%m/%d/%Y')))

'''
#Testing factor calculations
h = Hitter(Player.FindPlayerID('Luis Arraez'))
x = h.Last10Stats(2023, date)
y = h.GetCareerStatsOffPitcher(Player.FindPlayerID('Tyler Wells'))
print(x)
print(y)

description, factor = bp.CalculateHotColdFactor(x)
print(description, factor)

description, factor = bp.CalculateCareerStatsFactor(y)
print(description, factor)
'''

#Testing accuracy checker.
#bp = BetPredictor()
#print(bp.AccuracyTestNRFI(1))
#print(bp.OptimizeNRFIWeights(0.2, 1, 5, 40))

bp = BetPredictor()
print(bp.AccuracyTestHitting(10))

#x = Hitter(Player.FindPlayerID('Anthony Volpe'))
#print(x.HittingBetReview('08/11/2023'))