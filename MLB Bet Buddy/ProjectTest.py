#********************************************************************************************************************************
# Author: Ian Pluchino                                                                                                          *
# File: ProjectTest file                                                                                                        *
# Description: Tests all the components of the project.                                                                         *
# Date: 5/2/24                                                                                                                  *
#********************************************************************************************************************************

from datetime import datetime
from Team import Team
from Game import Game
from Player import Player
from Hitter import Hitter
from Pitcher import Pitcher
from LocalFactors import LocalFactors
from BetPredictor import BetPredictor

#CONSTANTS
OPENING_DAY = datetime.strptime('03/20/2024', '%m/%d/%Y')
CLOSING_DAY = datetime.strptime('09/29/2024', '%m/%d/%Y')
SEASON = 2024
DATE = datetime.today()
DATE_STRING = DATE.strftime('%m/%d/%Y')

#Testing the Team class.
print('TESTING THE TEAM CLASS')
team = Team.CreateFromName('New York Yankees')
print('The name of the team is:', team.GetTeamName(), '\n')
print('The team ID is:', team.GetTeamID(), '\n')
print('Their record on', DATE_STRING, 'is:', team.GetRecord(DATE, SEASON), '\n')
print('Their offensive statistics through', DATE_STRING, 'are:', team.GetTeamOffensiveStatistics(SEASON, OPENING_DAY, DATE), '\n')
print('Their YRFI percentage through', DATE_STRING, 'is', team.CalculateYRFIPercentage(SEASON, OPENING_DAY, DATE), '\n')

#Testing the Game class.
print('TESTING THE GAME CLASS')
game = Game(746418)
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
pitcher = Pitcher(Player.FindPlayerID('Marcus Stroman'))
print('Marcus Stroman\'s pitching statistics through', DATE_STRING, 'are:', pitcher.GetPitchingStatistics(SEASON, OPENING_DAY, DATE), '\n')
print('Marcus Stroman\'s lefty/righty splits for the', SEASON, 'season are:', pitcher.GetLRPitchingSplits(SEASON), '\n')
print('Marcus Stroman\'s YRFI percentage through', DATE_STRING, 'is', pitcher.CalculateYRFIPercentage(SEASON, OPENING_DAY, DATE), '\n')

#Testing the Hitter class.
print('TESTING THE HITTER CLASS')
hitter = Hitter(Player.FindPlayerID('Andrew McCutchen'))
print('Andrew McCutchen\'s offensive statistics through', DATE_STRING, 'are:', hitter.GetOffensiveStatistics(SEASON, OPENING_DAY, DATE), '\n')

careerStats = hitter.GetCareerStatsOffPitcher(pitcher.GetPlayerID())
print('Andrew McCutchen\'s career stats against Marcus Stroman are:', careerStats, '\n')
if not careerStats:
    print('Andrew McCutchen does not have career statistics against Marcus Stroman.', '\n')
else:
    print('Andrew McCutchen is \"', hitter.ClassifyHitting(careerStats['battingAverage'])[0], '\" based on his career stats against Marcus Stroman.', '\n')

last10Stats = hitter.Last10Stats(SEASON, DATE)
print('Andrew McCutchen\'s last 10 games stats starting from', DATE_STRING, 'are:', last10Stats, '\n')
if not last10Stats:
    print('Andrew McCutchen does not have recent last 10 games stats starting from', DATE_STRING + '.', '\n')
else:
    print('Andrew McCutchen is \"', hitter.ClassifyHitting(last10Stats['battingAverage'])[0], '\" based on his last 10 games stats starting from', DATE_STRING + '.', '\n')
print('Andrew McCutchen\'s lefty/righty splits for the', SEASON, 'season are:', hitter.GetLRHittingSplits(SEASON), '\n')

qualifiedHitters = Hitter.GetAllHitters(SEASON)
print('In total, there are', len(qualifiedHitters), 'qualified hitters in the', SEASON, 'season.', '\n')

#Testing the LocalFactors class.
print('TESTING THE LOCALFACTORS CLASS')
localFactors = LocalFactors()
stadium = 'Coors Field'

print('The ballpark factor at', stadium, 'is:', localFactors.GetBallparkFactor(stadium), '\n')
print('The home team that plays at', stadium, 'is:', localFactors.GetHomeTeamForStadium(stadium), '\n')
print('The city that', stadium, 'is in is:', localFactors.GetCityForStadium(stadium), '\n')
print('Does', stadium, 'have a roof?', localFactors.HasRoof(stadium), '\n')

localTime = '1:00 PM'
print('The weather information at', localTime, 'at', stadium, 'is:', localFactors.GetWeather(stadium, localTime), '\n')

#Testing the BetPredictor class.
print('TESTING THE BETPREDICTOR CLASS', '\n')
bp = BetPredictor()

schedule = bp.CreateSchedule(DATE, 2024)
print('SCHEDULE FOR', DATE_STRING + ':')
print(schedule)

NRFIYRFI = bp.CreateNRFIPredictions(schedule, OPENING_DAY, 2024)
print('NRFI/YRFI BET PREDICTIONS FOR', DATE_STRING + ':')
print(NRFIYRFI)

hitting = bp.CreateHittingPredictions(schedule, OPENING_DAY, DATE, 2024)
print('HITTING BET PREDICTIONS FOR', DATE_STRING + ':')
print(hitting)

print('TESTING THE ACCURACY OF BET PREDICTIONS FOR GAME DATA FROM 2022-2023')
NRFIYRFIAccuracy = bp.AccuracyTestNRFIYRFI(1)
print('NRFI/YRFI ACCURACY:', NRFIYRFIAccuracy, '\n')

hittingAccuracy = bp.AccuracyTestHitting(3)
print('HITTING ACCURACY:', hittingAccuracy, '\n')