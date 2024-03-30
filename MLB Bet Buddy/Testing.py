#Test file - to test all of the features and individual components of the bet predictor.

from Endpoints import Endpoints
from datetime import datetime
from Team import Team
from Game import Game
from Player import Player
from Hitter import Hitter
from Pitcher import Pitcher
from LocalFactors import LocalFactors
from BetPredictor import BetPredictor

#Constants - will use 2023 for testing purposes.
OPENING_DAY = datetime.strptime('03/30/2023', '%m/%d/%Y')
CLOSING_DAY = datetime.strptime('10/01/2023', '%m/%d/%Y')
SEASON = 2023
DATE = datetime.strptime('06/15/2023', '%m/%d/%Y')
DATE_STRING = DATE.strftime('%m/%d/%Y')

#Testing the Team class.
print('TESTING THE TEAM CLASS')
team = Team.CreateFromName('New York Yankees')
print('The name of the team is:', team.GetTeamName(), '\n')
print('The team ID is:', team.GetTeamID(), '\n')
print('Their record on', DATE_STRING, 'is:', team.GetRecord(DATE, SEASON), '\n')
print('Their offensive statistics through', DATE_STRING, 'are:', team.GetTeamOffensiveStatistics(SEASON, OPENING_DAY, DATE), '\n')
#print('Their YRFI percentage through', DATE_STRING, 'is', team.CalculateYRFIPercentage(SEASON, OPENING_DAY, DATE), '\n')

#Testing the Game class.
print('TESTING THE GAME CLASS')
game = Game(718781)
print('Information about the Yankees opening day game:')
game.PrintGameInfo()

#Testing the Player class.
print('TESTING THE PLAYER CLASS')
playerID = Player.FindPlayerID('Anthony Volpe')
print('The player ID for Anthony Volpe is:', playerID, '\n')
player = Player(playerID)
print('The hand information for Anthony Volpe is:', player.GetHandInformation(), '\n')

#Testing the Pitcher class.
print('TESTING THE PITCHER CLASS')
pitcher = Pitcher(Player.FindPlayerID('Gerrit Cole'))
print('Gerrit Cole\'s pitching statistics through', DATE_STRING, 'are:', pitcher.GetPitchingStatistics(SEASON, OPENING_DAY, DATE), '\n')
print('Gerrit Cole\'s lefty/righty splits for the', SEASON, 'season are:', pitcher.GetLRPitchingSplits(SEASON), '\n')
#print('Gerrit Cole\'s YRFI percentage through', DATE_STRING, 'is', pitcher.CalculateYRFIPercentage(SEASON, OPENING_DAY, DATE), '\n')

#Testing the Hitter class.
print('TESTING THE HITTER CLASS')
hitter = Hitter(Player.FindPlayerID('Austin Hays'))
print('Austin Hays\' offensive statistics through', DATE_STRING, 'are:', hitter.GetOffensiveStatistics(SEASON, OPENING_DAY, DATE), '\n')

careerStats = hitter.GetCareerStatsOffPitcher(pitcher.GetPlayerID())
print('Austin Hays\' career stats against Gerrit Cole are:', careerStats, '\n')
print('Austin Hays is \"', hitter.ClassifyHitting(careerStats['battingAverage'])[0], '\" based on his career stats against Gerrit Cole.', '\n')

L10Stats = hitter.Last10Stats(SEASON, DATE)
print('Austin Hays\' last 10 games stats starting from', DATE_STRING, 'are:', L10Stats, '\n')
print('Austin Hays is \"', hitter.ClassifyHitting(L10Stats['battingAverage'])[0], '\" based on his last 10 games stats starting from', DATE_STRING + '.', '\n')
print('Austin Hays\' lefty/righty splits for the', SEASON, 'season are:', hitter.GetLRHittingSplits(SEASON), '\n')

qualifiedHitters = Hitter.GetAllHitters(SEASON)
print('In total, there were', len(qualifiedHitters), 'qualified hitters in the', SEASON, 'season.', '\n')

#Testing the LocalFactors class.
print('TESTING THE LOCALFACTORS CLASS')
localFactors = LocalFactors()
stadium = 'Coors Field'

print('The ballpark factor at', stadium, 'is:', localFactors.GetBallparkFactor(stadium), '\n')
print('The home team that plays at', stadium, 'is:', localFactors.GetHomeTeamForStadium(stadium), '\n')
print('The city that', stadium, 'is in is:', localFactors.GetCityForStadium(stadium), '\n')
print('Does', stadium, 'have a roof?', localFactors.HasRoof(stadium), '\n')

localTime = '1:00 PM'
#print('The weather information at', localTime, 'at', stadium, 'is:', localFactors.GetWeather(stadium, localTime), '\n')

#Testing the BetPredictor class.
'''
date = datetime.strptime('03/29/2024', '%m/%d/%Y')
OPENING_DAY = datetime.strptime('03/20/2024', '%m/%d/%Y')

bp = BetPredictor()

schedule = bp.CreateSchedule(date, 2024)
schedule.to_excel('schedule_' + date.strftime('%m-%d-%Y') +'.xlsx')

NRFI = bp.CreateNRFIPredictions(schedule, OPENING_DAY, 2024)
NRFI.to_excel('NRFI_' + date.strftime('%m-%d-%Y') +'.xlsx')
    
hitting = bp.CreateHittingPredictions(schedule, OPENING_DAY, date, 2024)
hitting.to_excel('hitting_' + date.strftime('%m-%d-%Y') +'.xlsx')
'''
