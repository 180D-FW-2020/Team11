# -*- coding: utf-8 -*-
"""
Created on Fri Nov  6 22:58:30 2020

@author: zefyr
"""

import logging
import gamePlay as g
import numpy as np
import cv2
import traceback
import copy
import comms
import settings
import json
import time
import datetime
import platform
if 'arm' not in platform.machine().lower():
    import speech_recognition as sr
    import pygame

cameraWorking = True

## Display values
OBSTACLE_COLOR = (255, 0, 255)
POWERUP_COLOR = (255, 255, 0)

COOLDOWN_POSITION = (60,30)
COOLDOWN_CLEAR_UPPERLEFT = (50,0)
COOLDOWN_CLEAR_LOWERRIGHT = (500,34)
COOLDOWN_TIMER_UPPERLEFT = (410,10)
COOLDOWN_TIMER_LOWERRIGHT = (410,34)
COOLDOWN_DISTANCE = 500 - 410

CAMERA_IMAGE_TOP = 110
CAMERA_IMAGE_BOTTOM = 590
CAMERA_IMAGE_LEFT = 980
CAMERA_IMAGE_RIGHT = 1620
FRAME_CLEAR_UPPERLEFT = (950, 80)
FRAME_CLEAR_LOWERRIGHT = (1650, 620)
FRAME_UPPERLEFT = (960, 90)
FRAME_LOWERRIGHT = (1640, 610)

IT_TEXT_POSITION = (990, 650)
IT_TEXT_CLEAR_UPPERLEFT = (960, 620)
IT_TEXT_CLEAR_LOWERRIGHT = (1650, 654)
IT_STATS_PRINT_HORIZONTAL = 990
IT_STATS_PRINT_VERTICAL = 686
IT_STATS_CLEAR_LEFT = 960
IT_STATS_CLEAR_RIGHT = 1650
IT_STATS_CLEAR_TOP = 660
IT_STATS_CLEAR_BOTTOM = 695
IT_STATS_NEWLINE = 35
IT_STATS_CIRCLE_OFFSET = 10

IT_STATS_MAXCIRCLE = int(35/3)
IT_STATS_MAXBORDER = int(35/10)

## Commands
phrases = {
    "ready" : comms.ready,
    "start" : comms.start,
    "stop" : comms.stop,
    "powerup" : comms.powerUp,
    "power up" : comms.powerUp,
    "drop" : comms.drop
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
            self.launch = False
            self.start = False
            self.powerUp = 0
            self.rotationTimeTotal = 0
            
            # Initialize the PyGame
            pygame.init()
            pygame.mixer.init()
            
            # Set up local sound effects
            self.boostSound = pygame.mixer.Sound('SoundEffects/Boost.wav')
            self.freezeSound = pygame.mixer.Sound('SoundEffects/Freeze.wav')
            self.pickupSound = pygame.mixer.Sound('SoundEffects/PickUp.wav')
            self.rotationSound = pygame.mixer.Sound('SoundEffects/Rotation2.wav')
            self.tagSound = pygame.mixer.Sound('SoundEffects/tag2.wav')
            self.teleportSound = pygame.mixer.Sound('SoundEffects/Teleport.wav')
            
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
    
                cv2.createTrackbar('Play Mode', 'menu2', 1, 1, self.nothing)
                cv2.createTrackbar('Players', 'menu2', 1, 9, self.nothing)
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
                        playMode = 'standard'
                    else:
                        cv2.putText(menu,
                                    "Play Mode: Infinite!",
                                    (50,50), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2, cv2.LINE_AA)
                        playMode = 'infinite'
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
                                (50,500), cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 255, 0), 2, cv2.LINE_AA)
                    
                    if numPlayers == 1 and playMode == 'standard':
                        cv2.putText(menu,
                                    "Standard play mode is not allowed for single player",
                                    (50,300), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2, cv2.LINE_AA)
                    
                    cv2.imshow('menu2',menu)
                    k = cv2.waitKey(1) & 0xFF
                    if k == 32 and numPlayers != 0 and edgeLength >= 5 and not (numPlayers == 1 and playMode == 'standard'):
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
            direction, self.cameraImage = self.camera.getDirection(frameCapture)
            self.display[CAMERA_IMAGE_TOP:CAMERA_IMAGE_BOTTOM, CAMERA_IMAGE_LEFT:CAMERA_IMAGE_RIGHT] = self.cameraImage
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
                    self.setPowerUp(message)
                elif topic == comms.timerOver:
                    self.setTimer(message)
                elif topic == comms.dropped:
                    self.dropPower(message)
            else:
                if topic == comms.initial and not self.initialReceived:
                    self.setPlayspace(message)
                elif topic == comms.assign and not self.playerId:
                    self.setAssign(message)
                elif topic == comms.launch:
                    self.launch = True
                elif topic == comms.start:
                    on = False
                    self.blinkPlayer(on)
                    self.start = True                    
            return False
        except:
            print("Error getting package from primary node", flush=True)
            traceback.print_exc()
            
    def setPlayspace(self, message = None):
        '''
        Loads the playspace. If input message, it's the initial playspace.
        Otherwise just reload based on new axes. This can also
        be called as the final step of another display update, in which case
        passDisplay should be updated with the new move instead of the current
        display.
        '''
        if message:
            self.playSpace.__dict__= message
            self.dist = int(1000/(self.playSpace.edgeLength + 2))
            self.initialReceived = True
            self.displayBase = np.zeros((1000,1700,3), np.uint8)
            # set columns
            for i in range(self.playSpace.edgeLength + 1):
                cv2.line(self.displayBase, ((i+1)*self.dist,self.dist), ((i+1)*self.dist,1000-self.dist - 9),(0,255,0),int(self.dist/10))
            # set rows
            for i in range(self.playSpace.edgeLength + 1):
                cv2.line(self.displayBase, (self.dist,(i+1)*self.dist), (1000-self.dist - 9,(i+1)*self.dist),(0,255,0),int(self.dist/10))
            
        display = copy.deepcopy(self.displayBase)
        
        # if playerId already assigned, set player frame and it indicator text
        if self.playerId:
            cv2.rectangle(display, FRAME_UPPERLEFT, FRAME_LOWERRIGHT, self.playSpace.players[self.playerId - 1]['color'], -1)
            if self.playSpace.players[self.playerId - 1]['it']:
                cv2.rectangle(display, FRAME_UPPERLEFT, FRAME_LOWERRIGHT, self.playSpace.players[self.playerId - 1]['itColor'], int(self.dist/10))
                cv2.putText(display, "You are it!", IT_TEXT_POSITION, cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2, cv2.LINE_AA)
            else:
                cv2.putText(display, "You are not it. Run!", IT_TEXT_POSITION, cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2, cv2.LINE_AA)
            if type(self.cameraImage) != int:
                display[CAMERA_IMAGE_TOP:CAMERA_IMAGE_BOTTOM, CAMERA_IMAGE_LEFT:CAMERA_IMAGE_RIGHT] = self.cameraImage
        
        for i, player in enumerate(self.playSpace.players):
            hpos = np.dot(self.playSpace.horizontalAxis, player['position'])
            if hpos<0:
                hpos = self.playSpace.edgeLength + hpos + 1
            vpos = -1*np.dot(self.playSpace.verticalAxis, player['position'])
            if vpos<0:
                vpos = self.playSpace.edgeLength + vpos + 1
            cv2.circle(display,(self.dist*hpos + int(self.dist/2), self.dist*vpos + int(self.dist/2)), 
                       int(self.dist/3), player['color'], -1)
            
            cv2.circle(display,(IT_STATS_PRINT_HORIZONTAL, IT_STATS_PRINT_VERTICAL + IT_STATS_NEWLINE*i - IT_STATS_CIRCLE_OFFSET),
                        min(int(self.dist/3), IT_STATS_MAXCIRCLE), player['color'], -1)
            if self.playerId and self.playerId - 1 == i:
                cv2.putText(display, f"has been tagged {self.playSpace.tagCount[i]} times (you)",
                            (IT_STATS_PRINT_HORIZONTAL + 50, IT_STATS_PRINT_VERTICAL + IT_STATS_NEWLINE*i),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 1, cv2.LINE_AA)
            else:
                cv2.putText(display, f"has been tagged {self.playSpace.tagCount[i]} times",
                            (IT_STATS_PRINT_HORIZONTAL + 50, IT_STATS_PRINT_VERTICAL + IT_STATS_NEWLINE*i),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 1, cv2.LINE_AA)
            
            if player['it']:
                cv2.circle(display,(self.dist*hpos + int(self.dist/2), self.dist*vpos + int(self.dist/2)),
                           int(self.dist/3), player['itColor'], int(self.dist/10))
                cv2.circle(display,(IT_STATS_PRINT_HORIZONTAL, IT_STATS_PRINT_VERTICAL + IT_STATS_NEWLINE*i - IT_STATS_CIRCLE_OFFSET),
                        min(int(self.dist/3), IT_STATS_MAXCIRCLE), player['itColor'], min(int(self.dist/10), IT_STATS_MAXBORDER))

        for i, obstacles in enumerate(self.playSpace.obstacles):
            hpos = np.dot(self.playSpace.horizontalAxis, obstacles['position'])
            if hpos<0:
                hpos = self.playSpace.edgeLength + hpos + 1
            vpos = -1*np.dot(self.playSpace.verticalAxis, obstacles['position'])
            if vpos<0:
                vpos = self.playSpace.edgeLength + vpos + 1
            cv2.rectangle(display, (self.dist*hpos + int(self.dist/4), self.dist*vpos + int(self.dist/4)),
                          (self.dist*hpos + int(self.dist*3/4), self.dist*vpos + int(self.dist*3/4)), OBSTACLE_COLOR, -1)
        
        for i, powerups in enumerate(self.playSpace.powerUps):
            hpos = np.dot(self.playSpace.horizontalAxis, powerups['position'])
            if hpos<0:
                hpos = self.playSpace.edgeLength + hpos + 1
            vpos = -1*np.dot(self.playSpace.verticalAxis, powerups['position'])
            if vpos<0:
                vpos = self.playSpace.edgeLength + vpos + 1
            cv2.line(display, (self.dist*hpos + int(self.dist/4), self.dist*vpos + int(self.dist/4)),
                     (self.dist*hpos + int(self.dist*3/4), self.dist*vpos + int(self.dist*3/4)), POWERUP_COLOR, int(self.dist/6))
            cv2.line(display, (self.dist*hpos + int(self.dist/4), self.dist*vpos + int(self.dist*3/4)),
                     (self.dist*hpos + int(self.dist*3/4), self.dist*vpos + int(self.dist/4)), POWERUP_COLOR, int(self.dist/6))
        
        if self.playSpace.players[self.playerId-1]['powerUpHeld'] == 0:
            cv2.rectangle(display, (540,920), (1500, 1000), (0,0,0), -1)
            cv2.putText(display, "No powerups held!", (550,960), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2, cv2.LINE_AA)

        self.display = display
        
    def blinkPlayer(self, on):
        '''
        Blinks the player icon on screen at start of game so player can find it
        '''
        display = copy.deepcopy(self.display)
        
        if on:
            # OpenCV doesn't like numpy data types for displaying color so have
            # to use getattr to convert back
            #color = np.array([255, 255, 255]) - np.array(self.playSpace.players[self.playerId - 1]['color'])
            #color = list(getattr(color, "tolist", lambda: color)())
            #itColor = np.array([255, 255, 255]) - np.array(self.playSpace.players[self.playerId - 1]['itColor'])
            #itColor = list(getattr(itColor, "tolist", lambda: itColor)())
            color = (0, 0, 0)
            itColor = (0, 0, 0)
        else:
            color = self.playSpace.players[self.playerId - 1]['color']
            itColor = self.playSpace.players[self.playerId - 1]['itColor']
        
        hpos = np.dot(self.playSpace.horizontalAxis, self.playSpace.players[self.playerId - 1]['position'])
        if hpos<0:
            hpos = self.playSpace.edgeLength + hpos + 1
        vpos = -1*np.dot(self.playSpace.verticalAxis, self.playSpace.players[self.playerId - 1]['position'])
        if vpos<0:
            vpos = self.playSpace.edgeLength + vpos + 1
        
        # invert
        cv2.circle(display,(self.dist*hpos + int(self.dist/2), self.dist*vpos + int(self.dist/2)),
                    int(self.dist/3), (0,0,0), -1)
        cv2.circle(display,(self.dist*hpos + int(self.dist/2), self.dist*vpos + int(self.dist/2)),
                    int(self.dist/3), (0,0,0), int(self.dist/10))
        cv2.circle(display,(self.dist*hpos + int(self.dist/2), self.dist*vpos + int(self.dist/2)),
                    int(self.dist/3), color, -1)
        if self.playSpace.players[self.playerId - 1]['it']:
            cv2.circle(display,(self.dist*hpos + int(self.dist/2), self.dist*vpos + int(self.dist/2)),
                        int(self.dist/3), itColor, int(self.dist/10))
            
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
        cv2.circle(display,(self.dist*hpos + int(self.dist/2), self.dist*vpos + int(self.dist/2)),
                              int(self.dist/3), (0,0,0), -1)
        cv2.circle(display,(self.dist*hpos + int(self.dist/2), self.dist*vpos + int(self.dist/2)),
                              int(self.dist/3), (0,0,0), int(self.dist/10))
        
        # Place in new position
        hpos = np.dot(self.playSpace.horizontalAxis, self.playSpace.players[message['playerId'] - 1]['position'])
        if hpos<0:
            hpos = self.playSpace.edgeLength + hpos + 1
        vpos = -1*np.dot(self.playSpace.verticalAxis, self.playSpace.players[message['playerId'] - 1]['position'])
        if vpos<0:
            vpos = self.playSpace.edgeLength + vpos + 1
        cv2.circle(display,(self.dist*hpos + int(self.dist/2), self.dist*vpos + int(self.dist/2)),
                              int(self.dist/3), self.playSpace.players[message['playerId'] - 1]['color'], -1)
        if self.playSpace.players[message['playerId'] - 1]['it']:
            cv2.circle(display,(self.dist*hpos + int(self.dist/2), self.dist*vpos + int(self.dist/2)),
                              int(self.dist/3), self.playSpace.players[message['playerId'] - 1]['itColor'], int(self.dist/10))
        
        self.display = display

    def dropPower(self, message):
        display = copy.deepcopy(self.display)
        self.playSpace.players[message['playerId']-1]['powerUpHeld'] = 0
        if self.playerId == message['playerId']:
                cv2.rectangle(display, (540,920), (1500, 1000), (0,0,0), -1)
                cv2.putText(display, "No powerups held!", (550,960), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2, cv2.LINE_AA)
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
        self.setPlayspace()
        self.rotationTimeTotal = message['coolDown']

        # Play rotation SFX
        self.rotationSound.play()
        
        # Set the cooldown message
        display = copy.deepcopy(self.display)
        cv2.putText(display, "Rotation cooldown!", COOLDOWN_POSITION, cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2, cv2.LINE_AA)

        self.display = display

    def setCooldown(self, message):
        '''
        Updates/clears the cooldown message.
        '''
        display = copy.deepcopy(self.display)
        cv2.rectangle(display, COOLDOWN_CLEAR_UPPERLEFT, COOLDOWN_CLEAR_LOWERRIGHT, (0,0,0), -1)
        if message['coolDown']:
            endpos = np.array(COOLDOWN_TIMER_LOWERRIGHT)
            endpos[0] += int(COOLDOWN_DISTANCE*message['coolDown']/self.rotationTimeTotal)
            cv2.putText(display, "Rotation cooldown! " + str(message['coolDown']), COOLDOWN_POSITION, cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2, cv2.LINE_AA)
            cv2.rectangle(display, COOLDOWN_TIMER_UPPERLEFT, tuple(endpos), (255, 255, 255), -1)
        else:
            self.playSpace.rotationCoolDownTime = message['coolDown']

        self.display = display

    def setPowerUp(self, message):
        display = copy.deepcopy(self.display)
        if settings.verbose:
            print("powerup held was", self.playSpace.players[message['playerId']-1]['powerUpHeld'])
        if message['powerUp'] == 0:
            self.playSpace.players[message['playerId']-1]['powerUpHeld'] = 0
            if self.playerId == message['playerId']:
                cv2.rectangle(display, (540,920), (1500, 1000), (0,0,0), -1)
                cv2.putText(display, "No powerups held!", (550,960), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2, cv2.LINE_AA)
            if settings.verbose:
                print("powerup held is", self.playSpace.players[message['playerId']-1]['powerUpHeld'])
                
        elif message['powerUp'] == 1:
            # Plays speed boost sound
            self.boostSound.play()
            
            #adjusts variables to indicate player now has powerup
            self.playSpace.players[message['playerId'] - 1]['powerUpTimer'] = message['speedTimer']
            self.playSpace.players[message['playerId'] - 1]['powerUpHeld'] = 0
            self.playSpace.players[message['playerId'] - 1]['powerUpActive'] = 1
            if settings.verbose:
                print("player", message['playerId'], "registered as", self.playerId, "has activated speed")
            if self.playerId == message['playerId']:
                cv2.rectangle(display, (540,920), (1500, 1000), (0,0,0), -1)
                cv2.putText(display, "RUN! - Speed powerup is active", (550,30), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2, cv2.LINE_AA)
            if settings.verbose:
                print("powerup held is", self.playSpace.players[message['playerId']-1]['powerUpHeld'])
                
        elif message['powerUp'] == 2:
            # Plays freeze sound
            self.freezeSound.play()
            
            #adjusts variables to indicate player now has powerup
            self.playSpace.freezeTimer = message['freezeTimer']
            self.playSpace.players[message['playerId'] - 1]['powerUpActive'] = 2
            self.playSpace.players[message['playerId'] - 1]['powerUpHeld'] = 0
            if settings.verbose:
                print("player", message['playerId'], "registered as", self.playerId, "has activated freeze")
            if self.playerId == message['playerId']:
                cv2.rectangle(display, (540,920), (1500, 1000), (0,0,0), -1)
                cv2.putText(display, "RUN! - Everyone else is frozen", (550,30), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2, cv2.LINE_AA)
            else:
                cv2.rectangle(display, (540,0), (1500, 40), (0,0,0), -1)
                cv2.putText(display, "FREEZE! - Someone activated freeze powerup", (550,30), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2, cv2.LINE_AA)
            if settings.verbose:
                print("powerup held is", self.playSpace.players[message['playerId']-1]['powerUpHeld'])
                
        elif message['powerUp'] == 3:
            # Plays swap sound
            self.teleportSound.play()
            
            self.playSpace.players[message['playerId']-1]['powerUpHeld'] = 0
            oldpos1 = self.playSpace.players[message['playerId'] - 1]['position']
            oldpos2 = message['position']
            self.playSpace.players[message['playerId'] - 1]['position'] = message['position']
            if settings.verbose:
                print("powerup held is", self.playSpace.players[message['playerId']-1]['powerUpHeld'])
            
            # Clear existing player 1
            hpos = np.dot(self.playSpace.horizontalAxis, oldpos1)
            if hpos<0:
                hpos = self.playSpace.edgeLength + hpos + 1
            vpos = -1*np.dot(self.playSpace.verticalAxis, oldpos1)
            if vpos<0:
                vpos = self.playSpace.edgeLength + vpos + 1
            display = cv2.circle(display,(self.dist*hpos + int(self.dist/2), self.dist*vpos + int(self.dist/2)),
                                int(self.dist/3)+10, (0,0,0), -1)

            # Clear existing player 2
            hpos = np.dot(self.playSpace.horizontalAxis, oldpos2)
            if hpos<0:
                hpos = self.playSpace.edgeLength + hpos + 1
            vpos = -1*np.dot(self.playSpace.verticalAxis, oldpos2)
            if vpos<0:
                vpos = self.playSpace.edgeLength + vpos + 1
            display = cv2.circle(display,(self.dist*hpos + int(self.dist/2), self.dist*vpos + int(self.dist/2)),
                                int(self.dist/3)+10, (0,0,0), -1)

            
            self.playSpace.players[message['swap'] - 1]['position'] = self.playSpace.players[message['playerId'] - 1]['position']
            self.playSpace.players[message['playerId'] - 1]['position'] = message['position']
            
            # Place in new position player 1
            hpos = np.dot(self.playSpace.horizontalAxis, self.playSpace.players[message['playerId'] - 1]['position'])
            if hpos<0:
                hpos = self.playSpace.edgeLength + hpos + 1
            vpos = -1*np.dot(self.playSpace.verticalAxis, self.playSpace.players[message['playerId'] - 1]['position'])
            if vpos<0:
                vpos = self.playSpace.edgeLength + vpos + 1
            display = cv2.circle(display,(self.dist*hpos + int(self.dist/2), self.dist*vpos + int(self.dist/2)),
                                int(self.dist/3), self.playSpace.players[message['playerId'] - 1]['color'], -1)
            if self.playSpace.players[message['playerId'] - 1]['it']:
                display = cv2.circle(display,(self.dist*hpos + int(self.dist/2), self.dist*vpos + int(self.dist/2)),
                                int(self.dist/3), self.playSpace.players[message['playerId'] - 1]['itColor'], 10)

            # Place in new position player 2
            hpos = np.dot(self.playSpace.horizontalAxis, self.playSpace.players[message['swap'] - 1]['position'])
            if hpos<0:
                hpos = self.playSpace.edgeLength + hpos + 1
            vpos = -1*np.dot(self.playSpace.verticalAxis, self.playSpace.players[message['swap'] - 1]['position'])
            if vpos<0:
                vpos = self.playSpace.edgeLength + vpos + 1
            display = cv2.circle(display,(self.dist*hpos + int(self.dist/2), self.dist*vpos + int(self.dist/2)),
                                int(self.dist/3), self.playSpace.players[message['swap'] - 1]['color'], -1)
            if self.playSpace.players[message['swap'] - 1]['it']:
                display = cv2.circle(display,(self.dist*hpos + int(self.dist/2), self.dist*vpos + int(self.dist/2)),
                                int(self.dist/3), self.playSpace.players[message['swap'] - 1]['itColor'], 10)
            
        self.display = display


    def setTimer(self,message):
        if message['power'] == "freeze":
            self.playSpace.freezeTimer = message['freezeTimer']
            self.playSpace.players[message['playerId']-1]['powerUpActive'] = 0
            cv2.rectangle(self.display, (540,0), (1500, 40), (0,0,0), -1)
        elif message['power'] == "speed":
            self.playSpace.players[message['playerId']-1]['powerUpTimer'] = 0
            self.playSpace.players[message['playerId']-1]['powerUpActive'] = 0
            if self.playerId == message['playerId']:
                cv2.rectangle(self.display, (540,0), (1500, 40), (0,0,0), -1)
            if settings.verbose:
                print("power up timer set to 0 ", self.playSpace.players[message['playerId']-1])
    
    def setPickup(self, message):
        '''
        Removes the powerup that was picked up, places a new one, and moves the
        player.
        '''
        display = copy.deepcopy(self.display)
        # Update powerups list
        oldPowerUp = self.playSpace.powerUps.pop(message['index'])
        self.powerUp = oldPowerUp['powerUp']
        oldpos = oldPowerUp['position']
        newPower = {'powerUp': message['powerUp'],
                    'position': message['positionpower']}
        self.playSpace.powerUps.append(newPower)
        self.playSpace.players[message['playerId']-1]['powerUpHeld'] = self.powerUp
        
        # Clear existing powerup
        hpos = np.dot(self.playSpace.horizontalAxis, oldpos)
        if hpos<0:
            hpos = self.playSpace.edgeLength + hpos + 1
        vpos = -1*np.dot(self.playSpace.verticalAxis, oldpos)
        if vpos<0:
            vpos = self.playSpace.edgeLength + vpos + 1
        cv2.rectangle(display, (self.dist*hpos + int(self.dist/8), self.dist*vpos + int(self.dist/8)),
                          (self.dist*hpos + int(self.dist*7/8), self.dist*vpos + int(self.dist*7/8)), (0,0,0), -1)
        
        # Play's pick up sound
        self.pickupSound.play()
        
        # Place in new position
        hpos = np.dot(self.playSpace.horizontalAxis, self.playSpace.powerUps[-1]['position'])
        if hpos<0:
            hpos = self.playSpace.edgeLength + hpos + 1
        vpos = -1*np.dot(self.playSpace.verticalAxis, self.playSpace.powerUps[-1]['position'])
        if vpos<0:
            vpos = self.playSpace.edgeLength + vpos + 1
        # display = cv2.circle(display,(self.dist*hpos + int(self.dist/2), self.dist*vpos + int(self.dist/2)),
        #                       int(self.dist/3), POWERUP_COLOR, -1)
        cv2.line(display, (self.dist*hpos + int(self.dist/4), self.dist*vpos + int(self.dist/4)),
                 (self.dist*hpos + int(self.dist*3/4), self.dist*vpos + int(self.dist*3/4)), POWERUP_COLOR, int(self.dist/6))
        cv2.line(display, (self.dist*hpos + int(self.dist/4), self.dist*vpos + int(self.dist*3/4)),
                 (self.dist*hpos + int(self.dist*3/4), self.dist*vpos + int(self.dist/4)), POWERUP_COLOR, int(self.dist/6))
        
        # Set display message
        
        if self.powerUp == 1 and self.playerId == message['playerId']:
            cv2.rectangle(display, (540,920), (1500, 1000), (0,0,0), -1)
            cv2.putText(display, "Speed powerup ready", (550,960), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2, cv2.LINE_AA)
        elif self.powerUp == 2 and self.playerId == message['playerId']:
            cv2.rectangle(display, (540,920), (1500, 1000), (0,0,0), -1)
            cv2.putText(display, "Freeze powerup ready", (550,960), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2, cv2.LINE_AA)
        elif self.powerUp == 3 and self.playerId == message['playerId']:
            cv2.rectangle(display, (540,920), (1500, 1000), (0,0,0), -1)
            cv2.putText(display, "Swap powerup ready", (550,960), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2, cv2.LINE_AA)

        # Move player, which also sets the display
        self.setMove(message, passDisplay = display)
    
    def setAssign(self, message):
        '''
        Sets player ID. Pending: announce loaded players to loading screen
        '''
        if message['clientId'] == self.clientId:
            self.playerId = message['playerId']
            # set player frame
            self.setPlayspace()
            # display = copy.deepcopy(self.display)
            # cv2.rectangle(display, FRAME_UPPERLEFT, FRAME_LOWERRIGHT, self.playSpace.players[self.playerId - 1]['color'], -1)
            
            # if self.playSpace.players[self.playerId - 1]['it']:
            #     cv2.rectangle(display, FRAME_UPPERLEFT, FRAME_LOWERRIGHT, self.playSpace.players[self.playerId - 1]['itColor'], int(self.dist/10))
            #     cv2.putText(display, "You are it!", IT_TEXT_POSITION, cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2, cv2.LINE_AA)
            # else:
            #     cv2.putText(display, "You are not it. Run!", IT_TEXT_POSITION, cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2, cv2.LINE_AA)
            # if type(self.cameraImage) != int:
            #     display[CAMERA_IMAGE_TOP:CAMERA_IMAGE_BOTTOM, CAMERA_IMAGE_LEFT:CAMERA_IMAGE_RIGHT] = self.cameraImage
            
            # # set player in the stats
            # cv2.rectangle(display, (IT_STATS_CLEAR_LEFT, IT_STATS_CLEAR_TOP + IT_STATS_NEWLINE*(self.playerId - 1)),
            #           (IT_STATS_CLEAR_RIGHT,IT_STATS_CLEAR_BOTTOM + IT_STATS_NEWLINE*(message['tagged'] - 1)), (0,0,0), -1)
            # cv2.putText(display, f"has been tagged {self.playSpace.tagCount[(message['tagged'] - 1)]} times (you)",
            #             (IT_STATS_PRINT_HORIZONTAL + 70, IT_STATS_PRINT_VERTICAL + IT_STATS_NEWLINE*(message['tagged'] - 1)),
            #             cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 1, cv2.LINE_AA)
            
            # self.display = display
            if settings.verbose: print(f'########## playerId set to `{self.playerId}` ############')
    
    def setTag(self, message):
        '''
        Updates tagged player to have a tag indicator, and untagged player to
        not.
        '''
        self.playSpace.players[message['tagged'] - 1]['it'] = True
        self.playSpace.players[message['untagged'] - 1]['it'] = False
        self.playSpace.it = self.playSpace.players[message['tagged'] - 1]
        self.playSpace.tagCount = message['count']
        
        # Play sound to indicate tag
        self.tagSound.play()
        
        display = copy.deepcopy(self.display)
        
        # Clear previous marks for players and replace with new ones
        hpos = np.dot(self.playSpace.horizontalAxis, self.playSpace.players[message['untagged'] - 1]['position'])
        if hpos<0:
            hpos = self.playSpace.edgeLength + hpos + 1
        vpos = -1*np.dot(self.playSpace.verticalAxis, self.playSpace.players[message['untagged'] - 1]['position'])
        if vpos<0:
            vpos = self.playSpace.edgeLength + vpos + 1
        cv2.circle(display,(self.dist*hpos + int(self.dist/2), self.dist*vpos + int(self.dist/2)),
                   int(self.dist/3), (0,0,0), -1)
        cv2.circle(display,(self.dist*hpos + int(self.dist/2), self.dist*vpos + int(self.dist/2)),
                   int(self.dist/3), (0,0,0), int(self.dist/10))
        cv2.circle(display,(self.dist*hpos + int(self.dist/2), self.dist*vpos + int(self.dist/2)),
                   int(self.dist/3), self.playSpace.players[message['untagged'] - 1]['color'], -1)
        
        hpos = np.dot(self.playSpace.horizontalAxis, self.playSpace.players[message['tagged'] - 1]['position'])
        if hpos<0:
            hpos = self.playSpace.edgeLength + hpos + 1
        vpos = -1*np.dot(self.playSpace.verticalAxis, self.playSpace.players[message['tagged'] - 1]['position'])
        if vpos<0:
            vpos = self.playSpace.edgeLength + vpos + 1
        cv2.circle(display,(self.dist*hpos + int(self.dist/2), self.dist*vpos + int(self.dist/2)),
                   int(self.dist/3), (0,0,0), -1)
        cv2.circle(display,(self.dist*hpos + int(self.dist/2), self.dist*vpos + int(self.dist/2)),
                   int(self.dist/3), self.playSpace.players[message['tagged'] - 1]['color'], -1)
        cv2.circle(display,(self.dist*hpos + int(self.dist/2), self.dist*vpos + int(self.dist/2)),
                   int(self.dist/3), self.playSpace.players[message['tagged'] - 1]['itColor'], int(self.dist/10))
        
        # reset player frame
        cv2.rectangle(display, FRAME_CLEAR_UPPERLEFT, FRAME_CLEAR_LOWERRIGHT, (0,0,0), -1)
        cv2.rectangle(display, FRAME_UPPERLEFT, FRAME_LOWERRIGHT, self.playSpace.players[self.playerId - 1]['color'], -1)
        if self.playSpace.players[self.playerId - 1]['it']:
            cv2.rectangle(display, FRAME_UPPERLEFT, FRAME_LOWERRIGHT, self.playSpace.players[self.playerId - 1]['itColor'], int(self.dist/10))
        
        # if this player was tagged/untagged
        if self.playerId == message['tagged']:
            cv2.rectangle(display, FRAME_UPPERLEFT, FRAME_LOWERRIGHT, self.playSpace.players[self.playerId - 1]['itColor'], int(self.dist/10))
            cv2.rectangle(display, IT_TEXT_CLEAR_UPPERLEFT, IT_TEXT_CLEAR_LOWERRIGHT, (0,0,0), -1)
            cv2.putText(display, "You are it!", IT_TEXT_POSITION, cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2, cv2.LINE_AA)
        elif self.playerId == message['untagged']:
            cv2.rectangle(display, IT_TEXT_CLEAR_UPPERLEFT, IT_TEXT_CLEAR_LOWERRIGHT, (0,0,0), -1)
            cv2.putText(display, "You are not it. Run!", IT_TEXT_POSITION, cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2, cv2.LINE_AA)
        
        # update tagged player stats
        cv2.rectangle(display, (IT_STATS_CLEAR_LEFT, IT_STATS_CLEAR_TOP + IT_STATS_NEWLINE*(message['tagged'] - 1)),
                      (IT_STATS_CLEAR_RIGHT,IT_STATS_CLEAR_BOTTOM + IT_STATS_NEWLINE*(message['tagged'] - 1)), (0,0,0), -1)
        cv2.circle(display,(IT_STATS_PRINT_HORIZONTAL, IT_STATS_PRINT_VERTICAL + IT_STATS_NEWLINE*(message['tagged'] - 1) - IT_STATS_CIRCLE_OFFSET),
                    min(int(self.dist/3), IT_STATS_MAXCIRCLE), self.playSpace.players[message['tagged'] - 1]['color'], -1)
        cv2.circle(display,(IT_STATS_PRINT_HORIZONTAL, IT_STATS_PRINT_VERTICAL + IT_STATS_NEWLINE*(message['tagged'] - 1) - IT_STATS_CIRCLE_OFFSET),
                        min(int(self.dist/3), IT_STATS_MAXCIRCLE), self.playSpace.players[message['tagged'] - 1]['itColor'], min(int(self.dist/10), IT_STATS_MAXBORDER))
        if self.playerId == message['tagged']:
            cv2.putText(display, f"has been tagged {self.playSpace.tagCount[(message['tagged'] - 1)]} times (you)",
                        (IT_STATS_PRINT_HORIZONTAL + 50, IT_STATS_PRINT_VERTICAL + IT_STATS_NEWLINE*(message['tagged'] - 1)),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 1, cv2.LINE_AA)
        else:
            cv2.putText(display, f"has been tagged {self.playSpace.tagCount[(message['tagged'] - 1)]} times",
                        (IT_STATS_PRINT_HORIZONTAL + 50, IT_STATS_PRINT_VERTICAL + IT_STATS_NEWLINE*(message['tagged'] - 1)),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 1, cv2.LINE_AA)
        
        # update untagged player stats
        cv2.rectangle(display, (IT_STATS_CLEAR_LEFT, IT_STATS_CLEAR_TOP + IT_STATS_NEWLINE*(message['untagged'] - 1)),
                      (IT_STATS_CLEAR_RIGHT,IT_STATS_CLEAR_BOTTOM + IT_STATS_NEWLINE*(message['untagged'] - 1)), (0,0,0), -1)
        cv2.circle(display,(IT_STATS_PRINT_HORIZONTAL, IT_STATS_PRINT_VERTICAL + IT_STATS_NEWLINE*(message['untagged'] - 1) - IT_STATS_CIRCLE_OFFSET),
                    min(int(self.dist/3), IT_STATS_MAXCIRCLE), self.playSpace.players[message['untagged'] - 1]['color'], -1)
        if self.playerId == message['untagged']:
            cv2.putText(display, f"has been tagged {self.playSpace.tagCount[(message['untagged'] - 1)]} times (you)",
                        (IT_STATS_PRINT_HORIZONTAL + 50, IT_STATS_PRINT_VERTICAL + IT_STATS_NEWLINE*(message['untagged'] - 1)),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 1, cv2.LINE_AA)
        else:
            cv2.putText(display, f"has been tagged {self.playSpace.tagCount[(message['untagged'] - 1)]} times",
                        (IT_STATS_PRINT_HORIZONTAL + 50, IT_STATS_PRINT_VERTICAL + IT_STATS_NEWLINE*(message['untagged'] - 1)),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 1, cv2.LINE_AA)
        
        self.display = display
    
    def updateDisplay(self):
        '''
        Prints current contents of local playSpace to player's screen.
        UPDATE: Currently, only called for the case where event = False.
        '''
        try:
            #self.display[CAMERA_IMAGE_TOP:CAMERA_IMAGE_BOTTOM, CAMERA_IMAGE_LEFT:CAMERA_IMAGE_RIGHT] = self.cameraImage
            cv2.imshow('display', self.display)
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
                            
                            if abs(bottommost[1] - leftmost[1]) > 20 and abs(bottommost[1] - rightmost[1]) > 20 \
                                and abs(topmost[1] - leftmost[1]) > 20 and abs(topmost[1] - rightmost[1]) > 20:
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


