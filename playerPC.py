# -*- coding: utf-8 -*-
"""
Created on Fri Nov  6 22:58:30 2020

@author: zefyr
"""

import gamePlay as g
import numpy as np
import cv2

cameraWorking = False

player1c = (255, 99, 174)
player2c = (0, 127, 255)
player3c = (255, 0, 255)
player4c = (255, 255, 0)
playerColors = [player1c, player2c, player3c, player4c]
itColor = (255, 198, 220)

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
            
            self.gameOver = False
            
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
            package = {'playerId': self.playerId,
                       'direction': direction,
                       'rotation': 0}
            return package
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
            # if package['messageType'] == 'move':
            #     self.playSpace.players[package['playerId'] - 1].position = package['position']
            # elif package['messageType'] == 'tag':
            #     self.playSpace.players[package['tagged'] - 1].it = True
            #     self.playSpace.players[package['playerId'] - 1].it = False
            # elif package['messageType'] == 'init':
            #     self.playSpace.__dict__= package
            #     for player in self.playSpace.players:
            #         for j in self.playSpace.players[player].__dict__:
            #             j = package['players'][player][j]
            canSend = True
            # If any updates result in a display update, set displayUpdate to
            # true so it will update     
            
            return canSend
        except:
            print("Error getting package from primary node")
        
    def updateDisplay(self):
        '''
        Prints current contents of local playSpace to player's screen.
        '''
        try:
            display = np.zeros((1000,1000,3), np.uint8)
            dist = int(1000/(self.playSpace.edgeLength + 2))
            
            for i in range(self.playSpace.edgeLength + 1):
                display = cv2.line(display, ((i+1)*dist,dist), ((i+1)*dist,1000-dist),(0,255,0),10)
            for i in range(self.playSpace.edgeLength + 1):
                display = cv2.line(display, (dist,(i+1)*dist), (1000-dist,(i+1)*dist),(0,255,0),10)
            # Prints current state of playspace based on received package
            for i, player in enumerate(self.playSpace.players):
                hpos = np.dot(self.playSpace.horizontalAxis, player.position)
                if hpos<0:
                    hpos = self.playSpace.edgeLength + hpos + 1
                    print(hpos)
                vpos = -1*np.dot(self.playSpace.verticalAxis, player.position)
                if vpos<0:
                    vpos = self.playSpace.edgeLength + vpos + 1
                display = cv2.circle(display,(dist*hpos + int(dist/2), dist*vpos + int(dist/2)),
                                      int(dist/3), playerColors[i], -1)
                if player.it:
                    display = cv2.circle(display,(dist*hpos + int(dist/2), dist*vpos + int(dist/2)),
                                      int(dist/3), itColor, int(dist/10))
            cv2.imshow('display',display)
            self.displayUpdate = False
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
            # Update this to incorporate camera code, this will do for now though
            while cameraWorking:
                #classify stuff, replace dummy code
                direction = 0
                if direction:
                    return direction
            while not cameraWorking:
                pass
                # val = int(input())
                # if val == 8: direction = '^'
                # elif val == 2: direction = 'v'
                # elif val == 4: direction = '<'
                # elif val == 6: direction = '>'
                # else: direction = 0
                # if direction:
                #     return direction
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