# -*- coding: utf-8 -*-
"""
Created on Fri Nov  6 22:58:30 2020

@author: zefyr
"""

import gamePlay as g

class PlayerPC:
    '''
    This class manages all tasks relevant to each player at the PC level. This
    includes interacting with the camera and microphone, packing and unpacking 
    messages to and from the central node, and displaying updates.    
    '''
    def __init__(self, playerId, numPlayers):
        try:
            # This is a dummy number, how do we set each player number distinctly
            # without hardcoding?
            self.playerId = playerId
            self.camera = Camera()
            self.microphone = Microphone()
            self.displayUpdate = False
            
            #light version of playSpace for display only
            self.playSpace = g.PlaySpace(numPlayers, 0, 0, 0)
            
        except:
            print("An error occurred initializing PlayerPC")
            
    def getDirection(self):
        '''
        Gets direction information from the camera.
        '''
        try:
            direction = self.camera.getDirection()
            return direction
        except:
            print("Error getting direction information from the camera")

    def getCommand(self):
        ''' 
        Gets command information from the microphone.
        '''
        try:
            command = self.microphone.getCommand()
            return command
        except:
            print("Error getting command information from microphone")
            
    def pack(self, direction):
        '''
        Packs a message for the central node containing player number, direction,
        and command.
        
        Returns the message for transmission.
        '''
        try:
            #0 is a dummy value, this should be updated with message packing code
            message = 0
            return message
        except:
            print("Error sending package to primary node")
    
    def unpack(self, package):
        '''
        Unpacks message from the central node to obtain updates for the display,
        permission to send more messages, or (usually) both. Saves to local
        instance of playSpace.
        
        Return true to give permission to PC to transmit messages again.
        '''
        try:
            # Unpack message data into self.playSpace. You can access players
            # with the self.playSpace.players list, in which self.playSpace.players[2]
            # is player 2.
            # canSend will usually be updated to true, but there may be cases
            # in which it should not be.
            # 1 is a dummy value
            canSend = 1
            # If any updates result in a display update, set displayUpdate to
            # true so it will update
            self.displayUpdate = True
            return canSend
        except:
            print("Error getting package from primary node")
        
    def updateDisplay(self):
        '''
        Prints current contents of local playSpace to player's screen.
        '''
        try:
            print("Update display")
            # Prints current state of playspace based on received package
        except:
            print("Error updating display")

class Camera:
    def __init__(self):
        try:
            pass
        except:
            print("Error initializing camera")
            
    def getDirection(self):
        '''
        Looks for a direction command, and when one is found, classifies and
        returns it.
        '''
        try:
            # All the getting direction stuff. 0 is a dummy number
            direction = 0
            return direction
        except:
            print("Error getting direction from camera")
            
class Microphone:
    def __init__(self):
        try:
            pass
        except:
            print("Error initializing microphone")
            
    def getCommand(self):
        '''
        Listens for a voice command, and when one is found, classifies and
        returns it.
        '''
        try:
            # All the getting command stuff. 0 is a dummy number
            command = 0
            return command
        except:
            print("Error getting command from microphone")