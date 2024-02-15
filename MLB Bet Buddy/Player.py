#PLAYER CLASS. A general parent class to represent an MLB player.

from Endpoints import Endpoints

class Player():
    #CONSTRUCTOR - default player ID is Aaron Judge from the NYY.
    def __init__(self, a_playerID = 592450):
        #Endpoint object from the Endpoints class to handle MLB API access.
        self.m_endpointObj = Endpoints()
        
        #Passed plyaer ID that represents a single MLB player.
        self.m_playerID = a_playerID
        
    #Getters
    #Gets the player ID of the player this class is representing.
    def GetPlayerID(self):
        return self.m_playerID
    
    #Static function to get the ID of a player from their name alone.
    #Assistance Received: https://www.digitalocean.com/community/tutorials/python-static-method#using-staticmethod
    @staticmethod
    def FindPlayerID(a_playerFullName):
        #Create a temporary endpoint object.
        tempEndpointObj = Endpoints()
        
        #Create the ID lookup endpoint.
        IDLookupEndpoint = tempEndpointObj.GetPlayerIDLookupEndpoint(a_playerFullName)
        
        #Access the created endpoint and store the data.
        IDLookupData = tempEndpointObj.AccessEndpointData(IDLookupEndpoint)
       
        peopleFound = IDLookupData['people']
                
        #Make sure that the player being searched for could be found before extracting the name. Return 0 if the player ID could not be successfully found.
        if not peopleFound:
            return 0
        
        #Always opt to return the first of the people found in case there are multiple people found (extremely rare).
        return peopleFound[0]['id']

        

       
        
        
    




