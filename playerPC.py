# -*- coding: utf-8 -*-
"""
Created on Fri Nov  6 22:58:30 2020

@author: zefyr
"""

import gamePlay as g
import numpy as np
import cv2
import traceback
import comms
import speech_recognition as sr

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
            traceback.print_exc() 
            
    def getDirection(self):
        '''
        Gets direction information from the camera.
        '''
        try:
            direction = self.camera.getDirection()
            return direction
        except:
            print("Error getting direction information from the camera")
            traceback.print_exc() 

    def getCommand(self):
        ''' 
        Gets command information from the microphone.
        '''
        try:
            command = self.microphone.getCommand()
            return command
        except:
            print("Error getting command information from microphone")
            traceback.print_exc() 
            
    def pack(self, val):
        '''
        Packs a message for the central node containing player number and a
        value, which may be a confirmation of initial message receipt, a 
        direction, or a command.
        
        Returns the message for transmission.
        '''
        try:
            message = {'playerId': self.playerId,
                       'val': val}
            return message
        except:
            print("Error sending package to primary node")
            traceback.print_exc() 
    
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
            topic, message = package
            if topic == comms.move:
                self.playSpace.players[message['playerId'] - 1].position = message['position']
            elif topic == comms.axes:
                self.playSpace.verticalAxis = message['verticalAxis']
                self.playSpace.horizontalAxis = message['horizontalAxis']
            elif topic == comms.tag:
                self.playSpace.players[message['tagged'] - 1].it = True
                self.playSpace.players[message['playerId'] - 1].it = False
            elif topic == comms.initial:
                self.playSpace.__dict__= message
                # Return True for initial message
                return True
            return False
        except:
            print("Error getting package from primary node")
            traceback.print_exc() 
        
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
                hpos = np.dot(self.playSpace.horizontalAxis, player['position'])
                if hpos<0:
                    hpos = self.playSpace.edgeLength + hpos + 1
                    print(hpos)
                vpos = -1*np.dot(self.playSpace.verticalAxis, player['position'])
                if vpos<0:
                    vpos = self.playSpace.edgeLength + vpos + 1
                display = cv2.circle(display,(dist*hpos + int(dist/2), dist*vpos + int(dist/2)),
                                      int(dist/3), playerColors[i], -1)
                if player['it']:
                    display = cv2.circle(display,(dist*hpos + int(dist/2), dist*vpos + int(dist/2)),
                                      int(dist/3), itColor, int(dist/10))
            cv2.imshow('display',display)
            self.displayUpdate = False
        except:
            print("Error updating display")
            traceback.print_exc() 

class Camera:
    def __init__(self):
        try:
            pass
        except:
            print("Error initializing camera")
            traceback.print_exc() 
            
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
            traceback.print_exc() 
            
class Microphone:
    def __init__(self, phrases):
		self.phrases = phrases
		self.active = False

	def listen(self):
		self.active = True

	def stop(self):
		self.active = False
            
    def getCommand(self):
        '''
        Listens for a voice command, and when one is found, classifies and
        returns it.
        '''
        if self.active:
			r = sr.Recognizer()

			with sr.Microphone() as source:
				r.adjust_for_ambient_noise(source)

				
				print("Please say something...")

				audio = r.listen(source)

				command = ""

        		try:
            		# All the getting command stuff. 0 is a dummy number
            		command = r.recognize_google(audio)


					print("You said : \n " + command)


					#Check for conditionals
					for key in self.phrases:
						if(key.lower() in command.lower()):
							self.phrases[key]()

            		return command

        		except:
            		print("Error getting command from microphone")
            		traceback.print_exc() 


