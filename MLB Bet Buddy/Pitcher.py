#Pitcher class. Child to Player class to handle everything regarding a pitcher.

from Endpoints import Endpoints
from Player import Player

class Pitcher(Player):
    #CONSTRUCTOR - default pitcher ID is Gerrit Cole from the NYY.
    #Assistance: https://www.geeksforgeeks.org/calling-a-super-class-constructor-in-python/
    def __init__(self, a_pitcherID = 543037):
        super().__init__(a_pitcherID) 





