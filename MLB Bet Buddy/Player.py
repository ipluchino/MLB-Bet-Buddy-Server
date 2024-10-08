#********************************************************************************************************************************
# Author: Ian Pluchino                                                                                                          *
# Class: Player class                                                                                                           *
# Description: A base class to represent an MLB player. Parent to the Pitcher and Hitter classes.                               *
# Date: 5/2/24                                                                                                                  *
#********************************************************************************************************************************

from Endpoints import Endpoints

class Player():
    #CONSTRUCTOR
    def __init__(self, a_playerID = 592450):
        """Constructor for the Player class.

        This constructor is used to create and initialize a Player object. The player ID provided to the constructor
        is set as a member variable. If a player ID is not provided, Aaron Judge's player ID is used by default.

        Args:
            a_playerID (int): The ID used by the MLB API to represent a player.

        Returns:
            Nothing.
        """
        #Endpoint object from the Endpoints class to handle MLB API access.
        self.m_endpointObj = Endpoints()
        
        #Passed player ID that represents a single MLB player.
        self.m_playerID = a_playerID
        
    #GETTERS
    def GetPlayerID(self):
        """Gets the player ID of the player this class is representing.
        Returns:
            An integer, representing the player's ID used by the MLB API.
        """
        return self.m_playerID

    #SETTERS
    def SetPlayer(self, a_playerID):
        """Sets the instance of the class to a new player.
        
        Args:
            a_playerID (int): The player ID used by the MLB API to represent the player.

        Returns:
            Nothing.
        """
        self.m_playerID = a_playerID

    #UTILITY METHODS
    def GetHandInformation(self):
        """Gets the hand information for a player.

        This method obtains the dominant hand that a player hits and pitches from. The bat hand, or the side the 
        player goes up to bat, can be right, left, or switch (the player hits from both sides depending on the 
        pitcher). The pitch hand can only be left or right.

        Returns:
            A dictionary containing the hand information for the player.
        """
        #Create the endpoint to get general player information and access the endpoint.
        generalInfoEndpoint = self.m_endpointObj.GetGeneralPlayerInfoEndpoint(self.m_playerID)
        generalInfoData = self.m_endpointObj.AccessEndpointData(generalInfoEndpoint)
        
        #Make sure the player ID provided is valid and could be found. 
        if 'people' not in generalInfoData:
            return {}
        
        #Extract the bat hand and pitching hand, and return the information as a dictionary.
        fullName = generalInfoData['people'][0]['fullName']
        batHand = generalInfoData['people'][0]['batSide']['description']
        pitchHand = generalInfoData['people'][0]['pitchHand']['description']

        return { 'fullName': fullName,
                 'batHand': batHand,
                 'pitchHand': pitchHand }
    
    @staticmethod
    def FindPlayerID(a_playerFullName):
        """Searches for a player ID based on a player's full name.

        This method is used to obtain a player's ID that's used for the MLB API, based on a full name. In the case
        where the full name is shared between two players, the most recent player with that name is returned.

        Args:
            a_playerFullName (string): An MLB player full name.

        Returns:
            An integer, representing the player's ID.
        """
        #Create a temporary endpoint object.
        tempEndpointObj = Endpoints()
        
        #Create the ID lookup endpoint.
        IDLookupEndpoint = tempEndpointObj.GetPlayerIDLookupEndpoint(a_playerFullName)
        
        #Access the created endpoint and store the data.
        IDLookupData = tempEndpointObj.AccessEndpointData(IDLookupEndpoint)
       
        peopleFound = IDLookupData['people']
                
        #Make sure that the player being searched for could be found before extracting the name. Return 0 if the 
        #player ID could not be successfully found.
        if not peopleFound:
            return 0
        
        #Always opt to return the first of the people found in case there are multiple people found (extremely rare).
        return peopleFound[0]['id']