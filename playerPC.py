# -*- coding: utf-8 -*-
"""
Created on Fri Nov  6 22:58:30 2020

@author: zefyr
"""

import gamePlay as g
import numpy as np
import cv2
import traceback
import copy
import comms
import settings
import json
import platform
if 'arm' not in platform.machine().lower():
    import speech_recognition as sr
    import pygame

cameraWorking = True

## Display dummy values
player1c = (255, 99, 174)
player2c = (0, 127, 255)
player3c = (255, 0, 255)
player4c = (255, 255, 0)
playerColors = [player1c, player2c, player3c, player4c]
itColor = (255, 198, 220)

## Commands
phrases = {
    "ready" : comms.ready,
    "start" : comms.start,
    "stop" : comms.stop,
    "powerup" : comms.powerUp,
    "power up" : comms.powerUp
}

class PlayerPC:
    '''
    This class manages all tasks relevant to each player at the PC level. This
    includes interacting with the camera and microphone, packing and unpacking 
    messages to and from the central node, and displaying updates.    
    '''
    def __init__(self, clientId):
        try:
            self.playerId = 0
            self.clientId = clientId
            self.camera = Camera()
            self.microphone = Microphone()
            self.displayUpdate = False
            
            #light version of playSpace for display only
            self.playSpace = g.PlaySpace(0, 0, 0, 0)
            self.displayBase = 0
            self.display = 0
            self.dist = 0
            
            self.cameraImage = 0
            
            self.initialReceived = False
            self.gameOver = False
            self.ready = False
            self.start = False
            self.swap = False
            
            # Initialize the PyGame
            pygame.init()
            pygame.mixer.init()
            
            # Set up local sound effects
            self.rotationSound = pygame.mixer.Sound('SoundEffects/Rotation2.mp3')
            
        except:
            print("An error occurred initializing PlayerPC", flush=True)
            traceback.print_exc()
            
    def settings(self):
        try:
            menu = np.zeros((1000,1700,3), np.uint8)
            cv2.namedWindow('menu1')
            cv2.createTrackbar('Primary?', 'menu1', 0, 1, self.nothing)
            while(True):
                menu = np.zeros((1000,1700,3), np.uint8)
                
                isPrimary = cv2.getTrackbarPos('Primary?','menu1')
                
                cv2.putText(menu,
                            "Set to 1 if you're the primary player. Only one person can be primary!",
                            (50,50), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2, cv2.LINE_AA)
                cv2.putText(menu,
                            "Move the trackbar slider right to be primary, otherwise leave it on the left.",
                            (50,100), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2, cv2.LINE_AA)
                if isPrimary == 0:
                    cv2.putText(menu,
                            "You chose: not primary",
                            (50,150), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 255), 2, cv2.LINE_AA)
                else:
                    cv2.putText(menu,
                            "You chose: primary",
                            (50,150), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 0), 2, cv2.LINE_AA)
                cv2.putText(menu,
                            "Press space to continue...",
                            (50,250), cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 255, 0), 2, cv2.LINE_AA)
                cv2.imshow('menu1',menu)
                
                k = cv2.waitKey(1) & 0xFF
                if k == 32:
                    break
            
            cv2.destroyWindow('menu1')
            cv2.waitKey(1)
            #cv2.destroyAllWindows()
            
            if isPrimary:
                cv2.namedWindow('menu2')
                
                menu = np.zeros((1000,1700,3), np.uint8)
    
                cv2.createTrackbar('Play Mode', 'menu2', 0, 1, self.nothing)
                cv2.createTrackbar('Players', 'menu2', 1, 10, self.nothing)
                cv2.createTrackbar('Play Size', 'menu2', 10, 20, self.nothing)
                cv2.createTrackbar('Obstacles', 'menu2', 10, 20, self.nothing)
                cv2.createTrackbar('Powerups', 'menu2', 3, 10, self.nothing)
                
                while(True):
                    menu = np.zeros((1000,1700,3), np.uint8)
                    
                    playMode = cv2.getTrackbarPos('Play Mode','menu2')
                    numPlayers = cv2.getTrackbarPos('Players','menu2')
                    edgeLength = cv2.getTrackbarPos('Play Size','menu2')
                    numObstacles = cv2.getTrackbarPos('Obstacles','menu2')
                    numPowerups = cv2.getTrackbarPos('Powerups','menu2')
                
                    if playMode == 0:
                        cv2.putText(menu,
                                    "Play Mode: Standard - last person tagged wins",
                                    (50,50), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2, cv2.LINE_AA)
                    else:
                        cv2.putText(menu,
                                    "Play Mode: Infinite!",
                                    (50,50), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2, cv2.LINE_AA)
                    if numPlayers == 0:
                        cv2.putText(menu,
                                    "Number of Players: 0. At least one player required.",
                                    (50,100), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2, cv2.LINE_AA)
                    else:
                        cv2.putText(menu,
                                    f"Number of Players: {numPlayers}",
                                    (50,100), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2, cv2.LINE_AA)
                    
                    if edgeLength < 6:
                        cv2.putText(menu,
                                    f"Play area size: {edgeLength}x{edgeLength}. At least 6x6 is required.",
                                    (50,150), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2, cv2.LINE_AA)
                    else:
                        cv2.putText(menu,
                                    f"Play area size: {edgeLength}x{edgeLength}. At least 6x6 is required.",
                                    (50,150), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2, cv2.LINE_AA)
                    
                    cv2.putText(menu,
                                f"Number of obstacles: {numObstacles}",
                                (50,200), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2, cv2.LINE_AA)
                    cv2.putText(menu,
                                f"Number of powerups: {numPowerups}",
                                (50,250), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2, cv2.LINE_AA)
                    cv2.putText(menu,
                                "Press space to continue...",
                                (50,350), cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 255, 0), 2, cv2.LINE_AA)
                    
                    cv2.imshow('menu2',menu)
                    k = cv2.waitKey(1) & 0xFF
                    if k == 32 and numPlayers != 0 and edgeLength >= 5:
                        break
                cv2.destroyWindow('menu2')
                cv2.waitKey(1)
                #cv2.destroyAllWindows()
            else:
                playMode, numPlayers, edgeLength, numObstacles, numPowerups = (0, 0, 0, 0, 0)
            #isPrimary, playMode, numPlayers, edgeLength, numObstacles, numPowerups = (settings.isPrimary, settings.playMode, settings.numPlayers, 10, 0, 4)
            return isPrimary, playMode, numPlayers, edgeLength, numObstacles, numPowerups 
        except:
            print("An error occurred getting settings", flush=True)
            traceback.print_exc()

    def nothing(self, x):
        pass

    def loading(self, message):
        try:
            loading = np.zeros((1000,1700,3), np.uint8)
            cv2.putText(loading, message,
                        (50,50), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2, cv2.LINE_AA)
            cv2.imshow('loading', loading)
        except:
            print("An error occurred in the loading process", flush=True)
            traceback.print_exc()
    
    def getDirection(self, frameCapture):
        '''
        Gets direction information from the camera.
        '''
        try:
            direction = self.camera.getDirection(frameCapture)
            return direction
        except:
            print("Error getting direction information from the camera", flush=True)
            traceback.print_exc() 

    def getCommand(self, stop):
        ''' 
        Gets command information from the microphone.
        '''
        try:
            command = self.microphone.getCommand(stop)
            return command
        except:
            print("Error getting command information from microphone", flush=True)
            traceback.print_exc() 
            
    def pack(self, val):
        '''
        Packs a message for the central node containing player number and a
        value, which may be a confirmation of initial message receipt, a 
        direction, or a command.
        
        Returns the message for transmission.
        '''
        try:
            if val:
                message = {'playerId': self.playerId,
                        'val': val}
            else:
                message = {'playerId': self.playerId}
            
            if val == comms.ready:
                self.ready = True
            return message
        except:
            print("Error sending package to primary node", flush=True)
            traceback.print_exc() 
    
    def unpack(self, package):
        '''
        Unpacks message from the central node to obtain updates for the display,
        permission to send more messages, or (usually) both. Saves to local
        instance of playSpace.
        
        Return true if it's the initial package, for handshake.
        '''
        try:
            # Unpack message data into self.playSpace. You can access players
            # with the self.playSpace.players list, in which self.playSpace.players[2]
            # is player 2.
            # canSend will usually be updated to true, but there may be cases
            # in which it should not be.
            # 1 is a dummy value
            topic, message = package
            if topic == comms.stop:
                self.gameOver = True
            elif self.start:
                if topic == comms.move:
                    self.setMove(message)
                elif topic == comms.axes:
                    self.setRotation(message)
                elif topic == comms.coolDown:
                    self.setCooldown(message)
                elif topic == comms.pickup:
                    self.setPickup(message)
                elif topic == comms.tag:
                    self.setTag(message)
                elif topic == comms.activePower:
                    if message['powerUp'] == 0:
                        self.display = cv2.putText(self.display, "No powerups held!", (10,30), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2, cv2.LINE_AA)
                    elif message['powerUp'] == 1:
                        self.playSpace.setPowerUpTimer([message['playerId']])
                        self.playSpace.players[message['playerId'] - 1]['powerUpHeld'] = 0
                        self.playSpace.players[message['playerId'] - 1]['powerUpActive'] = 1
                    elif message['powerUp'] == 2:
                        self.playSpace.setPowerUpTimer(0)
                        self.playSpace.players[message['playerId'] - 1]['powerUpActive'] = 2
                        self.playSpace.players[message['playerId'] - 1]['powerUpHeld'] = 0
                    elif message['powerUp'] == 3:
                        self.swap = True
                        self.playSpace.players[message['swap'] - 1]['position'] = self.playSpace.players[message['playerId'] - 1]['position']
                        self.playSpace.players[message['playerId'] - 1]['position'] = message['position']
            else:
                if topic == comms.initial and not self.initialReceived:
                    self.setPlayspace(message)
                elif topic == comms.assign:
                    self.setAssign(message)
                elif topic == comms.start:
                    self.start = True
            return False
        except:
            print("Error getting package from primary node", flush=True)
            traceback.print_exc()
            
    def setPlayspace(self, message):
        '''
        Loads the playspace. If input message is not None, it's the initial playspace.
        Otherwise just reload based on new axes. This can also
        be called as the final step of another display update, in which case
        passDisplay should be updated with the new move instead of the current
        display.
        '''
        if message:
            self.playSpace.__dict__= message
            self.dist = int(1000/(self.playSpace.edgeLength + 2))
            self.initialReceived = True
            
        display = np.zeros((1000,1700,3), np.uint8)
            
        for i in range(self.playSpace.edgeLength + 1):
            display = cv2.line(display, ((i+1)*self.dist,self.dist), ((i+1)*self.dist,1000-self.dist),(0,255,0),10)
        for i in range(self.playSpace.edgeLength + 1):
            display = cv2.line(display, (self.dist,(i+1)*self.dist), (1000-self.dist,(i+1)*self.dist),(0,255,0),10)
        
        for i, player in enumerate(self.playSpace.players):
            hpos = np.dot(self.playSpace.horizontalAxis, player['position'])
            if hpos<0:
                hpos = self.playSpace.edgeLength + hpos + 1
            vpos = -1*np.dot(self.playSpace.verticalAxis, player['position'])
            if vpos<0:
                vpos = self.playSpace.edgeLength + vpos + 1
            display = cv2.circle(display,(self.dist*hpos + int(self.dist/2), self.dist*vpos + int(self.dist/2)),
                                  int(self.dist/3), playerColors[i], -1)
            if player['it']:
                display = cv2.circle(display,(self.dist*hpos + int(self.dist/2), self.dist*vpos + int(self.dist/2)),
                                  int(self.dist/3), itColor, int(self.dist/10))

        for i, obstacles in enumerate(self.playSpace.obstacles):
            hpos = np.dot(self.playSpace.horizontalAxis, obstacles['position'])
            if hpos<0:
                hpos = self.playSpace.edgeLength + hpos + 1
            vpos = -1*np.dot(self.playSpace.verticalAxis, obstacles['position'])
            if vpos<0:
                vpos = self.playSpace.edgeLength + vpos + 1
            display = cv2.circle(display,(self.dist*hpos + int(self.dist/2), self.dist*vpos + int(self.dist/2)),
                                  int(self.dist/3), playerColors[2], -1)
        
        for i, powerups in enumerate(self.playSpace.powerUps):
            hpos = np.dot(self.playSpace.horizontalAxis, powerups['position'])
            if hpos<0:
                hpos = self.playSpace.edgeLength + hpos + 1
            vpos = -1*np.dot(self.playSpace.verticalAxis, powerups['position'])
            if vpos<0:
                vpos = self.playSpace.edgeLength + vpos + 1
            display = cv2.circle(display,(self.dist*hpos + int(self.dist/2), self.dist*vpos + int(self.dist/2)),
                                  int(self.dist/3), playerColors[3], -1)
        
        self.display = display
        
    def setMove(self, message, passDisplay = None):
        '''
        Moves a player on the display, based on the input message. This can also
        be called as the final step of another display update, in which case
        passDisplay should be updated with the new move instead of the current
        display.
        '''
        
        if passDisplay is None:
            display = copy.deepcopy(self.display)
        else:
            display = passDisplay
        oldpos = self.playSpace.players[message['playerId'] - 1]['position']
        self.playSpace.players[message['playerId'] - 1]['position'] = message['position']
        
        # Clear existing player
        hpos = np.dot(self.playSpace.horizontalAxis, oldpos)
        if hpos<0:
            hpos = self.playSpace.edgeLength + hpos + 1
        vpos = -1*np.dot(self.playSpace.verticalAxis, oldpos)
        if vpos<0:
            vpos = self.playSpace.edgeLength + vpos + 1
        display = cv2.circle(display,(self.dist*hpos + int(self.dist/2), self.dist*vpos + int(self.dist/2)),
                              int(self.dist/3)+int(self.dist/15), (0,0,0), -1)
        
        # Place in new position
        hpos = np.dot(self.playSpace.horizontalAxis, self.playSpace.players[message['playerId'] - 1]['position'])
        if hpos<0:
            hpos = self.playSpace.edgeLength + hpos + 1
        vpos = -1*np.dot(self.playSpace.verticalAxis, self.playSpace.players[message['playerId'] - 1]['position'])
        if vpos<0:
            vpos = self.playSpace.edgeLength + vpos + 1
        display = cv2.circle(display,(self.dist*hpos + int(self.dist/2), self.dist*vpos + int(self.dist/2)),
                              int(self.dist/3), playerColors[message['playerId'] - 1], -1)
        if self.playSpace.players[message['playerId'] - 1]['it']:
            display = cv2.circle(display,(self.dist*hpos + int(self.dist/2), self.dist*vpos + int(self.dist/2)),
                              int(self.dist/3), itColor, int(self.dist/10))
        
        self.display = display

    def setRotation(self, message):
        '''
        Updates the axes, updates the display accordingly, writes the cooldown
        message. The cooldown message is actually set to the display separately
        from other updates, but it's not frequent enough to add a high lag and
        the fractional delay in the display won't produce confusion.       
        '''
        # Set new axes
        self.playSpace.verticalAxis = message['verticalAxis']
        self.playSpace.horizontalAxis = message['horizontalAxis']
        self.playSpace.rotationCoolDownTime = message['coolDown']
        
        # Reload the playspace according to new axes
        self.setPlayspace(None)

        # Play rotation SFX
        self.rotationSound.play()
        
        # Set the cooldown message
        cv2.putText(self.display, "Cooldown!", (10,30), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2, cv2.LINE_AA)
        
    def setCooldown(self, message):
        '''
        Turns off the cooldown message.
        '''
        self.playSpace.rotationCoolDownTime = message['coolDown']
        cv2.rectangle(self.display, (10,0), (1000, 32), (0,0,0), -1)
    
    def setPickup(self, message):
        '''
        Removes the powerup that was picked up, places a new one, and moves the
        player.
        '''
        display = copy.deepcopy(self.display)
        # Update powerups list
        oldPowerUp = self.playSpace.powerUps.pop(message['index'])
        oldpos = oldPowerUp['position']
        newPower = {'powerUp': message['powerUp'],
                    'position': message['positionpower']}
        self.playSpace.powerUps.append(newPower)
        
        # Clear existing powerup
        hpos = np.dot(self.playSpace.horizontalAxis, oldpos)
        if hpos<0:
            hpos = self.playSpace.edgeLength + hpos + 1
        vpos = -1*np.dot(self.playSpace.verticalAxis, oldpos)
        if vpos<0:
            vpos = self.playSpace.edgeLength + vpos + 1
        display = cv2.circle(display,(self.dist*hpos + int(self.dist/2), self.dist*vpos + int(self.dist/2)),
                              int(self.dist/3)+int(self.dist/15), (0,0,0), -1)
        
        # Play's pick up sound
        #self.pickUpSound.play()
        
        # Place in new position
        hpos = np.dot(self.playSpace.horizontalAxis, self.playSpace.powerUps[-1]['position'])
        if hpos<0:
            hpos = self.playSpace.edgeLength + hpos + 1
        vpos = -1*np.dot(self.playSpace.verticalAxis, self.playSpace.powerUps[-1]['position'])
        if vpos<0:
            vpos = self.playSpace.edgeLength + vpos + 1
        display = cv2.circle(display,(self.dist*hpos + int(self.dist/2), self.dist*vpos + int(self.dist/2)),
                              int(self.dist/3), playerColors[3], -1)
        
        # Move player, which also sets the display
        self.setMove(message, passDisplay = display)
    
    def setAssign(self, message):
        '''
        Sets player ID. Pending: announce loaded players to loading screen
        '''
        if not self.playerId and message['clientId'] == self.clientId:
            self.playerId = message['playerId']
        if settings.verbose: print('########## playerId set to ############', self.playerId)
    
    def setTag(self, message):
        '''
        Updates tagged player to have a tag indicator, and untagged player to
        not.
        '''
        self.playSpace.players[message['tagged'] - 1]['it'] = True
        self.playSpace.players[message['untagged'] - 1]['it'] = False
        self.playSpace.it = self.playSpace.players[message['tagged'] - 1]
        
        # Play sound to indicate tag
        #self.tagSound.play()
        
        display = copy.deepcopy(self.display)
        
        # Clear previous marks for players and replace with new ones
        hpos = np.dot(self.playSpace.horizontalAxis, self.playSpace.players[message['untagged'] - 1]['position'])
        if hpos<0:
            hpos = self.playSpace.edgeLength + hpos + 1
        vpos = -1*np.dot(self.playSpace.verticalAxis, self.playSpace.players[message['untagged'] - 1]['position'])
        if vpos<0:
            vpos = self.playSpace.edgeLength + vpos + 1
        display = cv2.circle(display,(self.dist*hpos + int(self.dist/2), self.dist*vpos + int(self.dist/2)),
                              int(self.dist/3)+int(self.dist/15), (0,0,0), -1)
        display = cv2.circle(display,(self.dist*hpos + int(self.dist/2), self.dist*vpos + int(self.dist/2)),
                              int(self.dist/3), playerColors[message['untagged'] - 1], -1)
        
        hpos = np.dot(self.playSpace.horizontalAxis, self.playSpace.players[message['tagged'] - 1]['position'])
        if hpos<0:
            hpos = self.playSpace.edgeLength + hpos + 1
        vpos = -1*np.dot(self.playSpace.verticalAxis, self.playSpace.players[message['tagged'] - 1]['position'])
        if vpos<0:
            vpos = self.playSpace.edgeLength + vpos + 1
        display = cv2.circle(display,(self.dist*hpos + int(self.dist/2), self.dist*vpos + int(self.dist/2)),
                              int(self.dist/3)+int(self.dist/15), (0,0,0), -1)
        display = cv2.circle(display,(self.dist*hpos + int(self.dist/2), self.dist*vpos + int(self.dist/2)),
                              int(self.dist/3), playerColors[message['tagged'] - 1], -1)
        display = cv2.circle(display,(self.dist*hpos + int(self.dist/2), self.dist*vpos + int(self.dist/2)),
                              int(self.dist/3), itColor, int(self.dist/10))
        
        self.display = display
    
    def updateDisplay(self, event = True):
        '''
        Prints current contents of local playSpace to player's screen.
        UPDATE: Currently, only called for the case where event = False.
        '''
        try:
            if event:
                pass
                # self.display = copy.deepcopy(self.displayBase)
                # # Prints current state of playspace based on received package
                # for i, player in enumerate(self.playSpace.players):
                #     hpos = np.dot(self.playSpace.horizontalAxis, player['position'])
                #     if hpos<0:
                #         hpos = self.playSpace.edgeLength + hpos + 1
                #     vpos = -1*np.dot(self.playSpace.verticalAxis, player['position'])
                #     if vpos<0:
                #         vpos = self.playSpace.edgeLength + vpos + 1
                #     self.display = cv2.circle(self.display,(self.dist*hpos + int(self.dist/2), self.dist*vpos + int(self.dist/2)),
                #                           int(self.dist/3), playerColors[i], -1)
                #     if player['it']:
                #         self.display = cv2.circle(self.display,(self.dist*hpos + int(self.dist/2), self.dist*vpos + int(self.dist/2)),
                #                           int(self.dist/3), itColor, int(self.dist/10))

                # for i, obstacles in enumerate(self.playSpace.obstacles):
                #     hpos = np.dot(self.playSpace.horizontalAxis, obstacles['position'])
                #     if hpos<0:
                #         hpos = self.playSpace.edgeLength + hpos + 1
                #     vpos = -1*np.dot(self.playSpace.verticalAxis, obstacles['position'])
                #     if vpos<0:
                #         vpos = self.playSpace.edgeLength + vpos + 1
                #     self.display = cv2.circle(self.display,(self.dist*hpos + int(self.dist/2), self.dist*vpos + int(self.dist/2)),
                #                           int(self.dist/3), playerColors[2], -1)
                
                # for i, powerups in enumerate(self.playSpace.powerUps):
                #     hpos = np.dot(self.playSpace.horizontalAxis, powerups['position'])
                #     if hpos<0:
                #         hpos = self.playSpace.edgeLength + hpos + 1
                #     vpos = -1*np.dot(self.playSpace.verticalAxis, powerups['position'])
                #     if vpos<0:
                #         vpos = self.playSpace.edgeLength + vpos + 1
                #     self.display = cv2.circle(self.display,(self.dist*hpos + int(self.dist/2), self.dist*vpos + int(self.dist/2)),
                #                           int(self.dist/3), playerColors[3], -1)


                # if self.playSpace.rotationCoolDownTime:
                #     self.display = cv2.putText(self.display, "Cooldown!", (10,30), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2, cv2.LINE_AA)

                # if self.playSpace.powerUpTimerRemaining(0):
                #     self.display = cv2.putText(self.display, "Freeze!", (10,30), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2, cv2.LINE_AA)
                
                # if self.playSpace.players[self.playerId-1]['powerUpActive'] == 1:
                #     self.display = cv2.putText(self.display, "Freeze!", (10,30), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2, cv2.LINE_AA)

                # if self.swap == True:
                #     self.swap = False
                #     self.display = cv2.putText(self.display, "Swap!", (10,30), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2, cv2.LINE_AA)
            
            elif type(self.cameraImage) != int:
                self.display[260:740, 980:1620] = self.cameraImage
                cv2.imshow('display',self.display)
            #self.displayUpdate = False
        except:
            print("Error updating display", flush=True)
            traceback.print_exc() 

class Camera:
    def __init__(self):
        try:
            pass
        except:
            print("Error initializing camera", flush=True)
            traceback.print_exc() 
            
    def getDirection(self, frameCapture):
        '''
        Looks for a direction command, and when one is found, classifies and
        returns it.
        '''
        try:
            # Update this to incorporate camera code, this will do for now though
            if cameraWorking:
                # Capture frame-by-frame
                _, frame = frameCapture.read()
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                width = frame.shape[1]
                length = frame.shape[0]

                direction = 0
                img = frame[120:360, 80:320]
                ret,thresh = cv2.threshold(img,127,255,0)
                contours, hierarchy = cv2.findContours(thresh, 3, 2)
                
                if type(hierarchy) == np.ndarray:
                    ChildContour = hierarchy[0, :,2]
                    WithoutChildContour = (ChildContour==-1).nonzero()[0]
                    # get contours from indices
                    cntsA=[contours[i] for i in WithoutChildContour]
                    
                    for cnt in cntsA:
                        
                        area = cv2.contourArea(cnt)
                        
                        # Find first contour of reasonable proportion to overall size of sub image
                        if (area/(img.size) > 0.03) and (area/(img.size) < 0.1):
                    
                            leftmost = cnt[cnt[:,:,0].argmin()][0]
                            rightmost = cnt[cnt[:,:,0].argmax()][0]
                            topmost = cnt[cnt[:,:,1].argmin()][0]
                            bottommost = cnt[cnt[:,:,1].argmax()][0]
                            
                            # Values for horizontal to vertical ratio
                            leftright_x = abs((rightmost - leftmost)[0])
                            topbottom_y = abs((bottommost - topmost)[1])
                            
                            # Values for tilt ratio
                            leftright_y = abs((rightmost - leftmost)[1])
                            topbottom_x = abs((bottommost - topmost)[0])
                            
                            ratio = leftright_x/topbottom_y
                            tiltratio = max(leftright_y,topbottom_x)/area
                            
                            if tiltratio < 0.01:
                                # A horizontal to vertical ratio of about 0.48 corresponds with
                                # a vertical arrow
                                if ratio - 0.48 < 0.05:
                                    # if span from bottom to arrow wings is longer than from arrow wings to
                                    # top, it's an up arrow
                                    if abs(bottommost[1] - leftmost[1]) > abs(leftmost[1] - topmost[1]):
                                        direction = '^'
                                    else: direction = 'v'
                                    
                                # A horizontal to vertical ratio of about 2.10 corresponds with
                                # a horizontal arrow
                                elif 1/ratio - 2.10 < 0.05:
                                    # if span from right to arrow wings is longer than from arrow wings to
                                    # left, it's a left arrow
                                    if abs(rightmost[0] - topmost[0]) > abs(topmost[0] - leftmost[0]):
                                        direction = '<'
                                    else: direction = '>'
                                    
                                # Any other ratio is unlikely to be a reasonable orientation of our arrow
                                else:
                                    pass
                            
                            # if direction found, print stuff to screen
                            
                                if direction:
                                    img = cv2.circle(img,tuple(leftmost), 10, (0,0,255), -1)
                                    img = cv2.circle(img,tuple(rightmost), 10, (0,0,255), -1)
                                    img = cv2.circle(img,tuple(topmost), 10, (0,0,255), -1)
                                    img = cv2.circle(img,tuple(bottommost), 10, (0,0,255), -1)
                                    frame = cv2.putText(frame, direction, (int(frame.shape[1]/2),frame.shape[0]-10), cv2.FONT_HERSHEY_SIMPLEX,
                                                        4, (255, 255, 255), 10)
                                break
                
                frame = cv2.flip(cv2.rectangle(frame,(80, 120), (320,360), (0,255,0),2),1)
                
                #bound = int((frame.shape[1] - frame.shape[0])/2)
                #frame = frame[:, bound:frame.shape[1] - bound]
                dim = (640, 480)
            
                # Store the resulting frame
                frame = cv2.resize(frame, dim, interpolation = cv2.INTER_AREA)
                frame = np.expand_dims(frame, axis=2)
                return direction, frame
            
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
            print("Error getting direction from camera", flush=True)
            traceback.print_exc() 
            
class Microphone:
    def __init__(self):
        #self.active = False
        self.recognizer = sr.Recognizer()
        self.microphone = sr.Microphone()
        # for i, mic in enumerate(self.microphone.list_microphone_names()):
        #     print(i,mic)
        # print("Device", self.microphone.device_index)
            # if "sound mapper" not in mic.lower():
            #     self.microphone.device_index = i
            #     break

    # def listen(self):
    #     self.active = True

    # def stop(self):
    #     self.active = False
            
    def getCommand(self, stop):
        '''
        Listens for a voice command, and when one is found, classifies and
        returns it.
        '''
        try:
            with self.microphone as source:
                while not stop[0]:
                    
                    # UnknownValueError occurs when speech recognition can't
                    # interpret detected input
                    #with suppress(sr.UnknownValueError):
                    self.recognizer.adjust_for_ambient_noise(source)
                    
                    print("######## Please say something... #########", flush=True)
                    
                    audio = self.recognizer.listen(source, phrase_time_limit=2)
                    
                    try:
                        #command = self.recognizer.recognize_google_cloud(audio, credentials_json=json.dumps(googlecloud_json))
                        command = self.recognizer.recognize_google(audio)
                        #command = self.recognizer.recognize_ibm(audio, username=IBM_USERNAME, password=IBM_PASSWORD)
                        print("######## You said : " + command + "##########", flush=True)

                        # Check for valid input
                        for key in phrases:
                            if(key.lower() in command.lower()):
                                return phrases[key]
                    except sr.UnknownValueError:
                        print("Speech to Text could not understand audio")
                return False
        # except Exception as ex:
        #     template = "An exception of type {0} occurred. Arguments:\n{1!r}"
        #     message = template.format(type(ex).__name__, ex.args)
        #     print (message)
        except:
            print("Error getting command from microphone", flush=True)
            traceback.print_exc() 


