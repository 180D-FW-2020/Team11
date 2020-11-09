# -*- coding: utf-8 -*-
"""
Created on Fri Nov  6 22:58:30 2020

@author: zefyr
"""
import gamePlay

class PlayerPC:
    def __init__(self, isPrimaryNode):
        try:
            # This is a dummy number, how do we set each player number distinctly
            # without hardcoding?
            self.playerNum = 1
            self.camera = Camera();
            self.microphone = Microphone();
        except:
            print("An error occurred initializing PlayerPC")
            
    def getDirection(self):
        try:
            direction = self.camera.getDirection()
            return direction
        except:
            print("Error getting direction information from the camera")

    def getCommand(self):
        try:
            command = self.microphone.getCommand()
            return command
        except:
            print("Error getting command information from microphone")
            
    def sendPackage(self, direction):
        try:
            print("Send package with player number, direction, and dummy rotation",
                  "to primary node")
        except:
            print("Error sending package to primary node")
    
    def unpack(self, package):
        try:
            # Unpack package via comms class stuff to get updates for display
            display = 0
            return display
        except:
            print("Error getting package from primary node")
        
    def updateDisplay(self):
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
        try:
            # All the getting command stuff. 0 is a dummy number
            command = 0
            return command
        except:
            print("Error getting command from microphone")