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

cameraWorking = True

## Display dummy values
player1c = (255, 99, 174)
player2c = (0, 127, 255)
player3c = (255, 0, 255)
player4c = (255, 255, 0)
playerColors = [player1c, player2c, player3c, player4c]
itColor = (255, 198, 220)

## Commands


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
            self.microphone = Microphone(None)
            self.displayUpdate = False
            
            #light version of playSpace for display only
            self.playSpace = g.PlaySpace(numPlayers, 0, 0, 0)
            
            self.gameOver = False
            
        except:
            print("An error occurred initializing PlayerPC")
            traceback.print_exc() 
            
    def getDirection(self, frameCapture):
        '''
        Gets direction information from the camera.
        '''
        try:
            direction = self.camera.getDirection(frameCapture)
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
            if topic == comms.move:
                self.playSpace.players[message['playerId'] - 1]['position'] = message['position']
            elif topic == comms.axes:
                self.playSpace.verticalAxis = message['verticalAxis']
                self.playSpace.horizontalAxis = message['horizontalAxis']
                self.playSpace.rotationCoolDownTime = message['coolDown']
            elif topic == comms.coolDown:
                self.playSpace.rotationCoolDownTime = message['coolDown']
            elif topic == comms.tag:
                self.playSpace.players[message['tagged'] - 1]['it'] = True
                self.playSpace.players[message['playerId'] - 1]['it'] = False
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
            if self.playSpace.rotationCoolDownTime:
                display = cv2.putText(display, "Cooldown!", (10,30), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2, cv2.LINE_AA)
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
            
    def getDirection(self, frameCapture):
        '''
        Looks for a direction command, and when one is found, classifies and
        returns it.
        '''
        try:
            # Update this to incorporate camera code, this will do for now though
            while cameraWorking:
                # Capture frame-by-frame
                _, frame = frameCapture.read()
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                
                direction = 0
                img = frame[120:360, 200:440]
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
                        if (area/(img.size) > 0.01) and (area/(img.size) < 0.1):
                    
                            leftmost = cnt[cnt[:,:,0].argmin()][0]
                            rightmost = cnt[cnt[:,:,0].argmax()][0]
                            topmost = cnt[cnt[:,:,1].argmin()][0]
                            bottommost = cnt[cnt[:,:,1].argmax()][0]
                            
                            leftright_x = abs((rightmost - leftmost)[0])
                            topbottom_y = abs((bottommost - topmost)[1])
                            
                            ratio = leftright_x/topbottom_y
                            
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
                            
    #                        if direction:
    #                            frame = cv2.putText(frame, direction, (10,frame.shape[0]-10), cv2.FONT_HERSHEY_SIMPLEX,
    #                                                2, (255, 255, 255), 2)
    #                            img = cv2.circle(img,tuple(leftmost), 10, (0,0,255), -1)
    #                            img = cv2.circle(img,tuple(rightmost), 10, (0,0,255), -1)
    #                            img = cv2.circle(img,tuple(topmost), 10, (0,0,255), -1)
    #                            img = cv2.circle(img,tuple(bottommost), 10, (0,0,255), -1)
    #                        break
    #
    #                cv2.imshow('frame', cv2.rectangle(frame,(200, 120), (440,360), (0,255,0),2))
    #                frame = cv2.flip(frame,1)
    #                # Display the resulting frame
    #                cv2.imshow('frame', frame)
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


