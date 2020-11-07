# -*- coding: utf-8 -*-
"""
Created on Fri Nov  6 20:46:40 2020

@author: zefyr
"""
import random as r

ROTATION_COOLDOWN = 20

class GamePlay:
    def __init__(self, primaryNode = True):
        try:
            if primaryNode:
                args = self.settings()
            else: args = (0, 0, 0, 0)
            self.startPlaySpace(args)
        except:
            print("An error occurred initializing GamePlay")
    
    def settings(self):
        try:
            print("This will prompt a player for the game settings")
            # use mic to get edgeLength, numObstacles, numPowerups, this is dummy
            numPlayers, edgeLength, numObstacles, numPowerups = (0, 0, 0, 0)
            return numPlayers, edgeLength, numObstacles, numPowerups
        except:
            print("An error occurred getting settings")
    
    def startPlaySpace(self, args):
        try:
            self.playSpace = PlaySpace(args)
        except:
            print("An error occurred generating the playspace")
            
    def getPlayerInput(self):
        try:
            print("This will get package date from players and", 
                  "return a player number with a rotation",
                  "or direction")
            #return rotation, direction
        except:
            print("An error occurred getting player input")
    
    def updateAllNodes(self):
        try:
            print("This sends a message to all nodes with the current playspace",
                  "and player data, and clears nodes to send new messages")
        except:
            print("An error occurred updating nodes")
            
class PlaySpace:
    def __init__(self, numPlayers, edgeLength, numObstacles, numPowerups):
        try:
            self.edgeLength = edgeLength
            if numObstacles: self.placeObstacles(numObstacles)
            if numPowerups: self.placePowerUps(numPowerups)
            
            self.verticalAxis = 1
            self.horizontalAxis = 2
            self.rotationCoolDownRemaining = 0
            
            if numPlayers:
                self.numPlayers = numPlayers
                self.playersNotIt = self.placePlayers(numPlayers)

        except:
            print("An error occurred initializing PlaySpace")
            
    def placePlayers(self, numPlayers):
        try:
            it = r.randrange(0, numPlayers, 1)
            players = []
            for i in range (numPlayers):
                # Get a random position a reasonable distance from other players
                # with respect to edge length. Don't use origin, this is dummy code
                x, y, z = (0, 0, 0)                
                if(i == it): it = True
                else: it = False
                players.append(Player(i, x, y, z, it))
        except:
            print("An error occurred placing players")
            
    def placeObstacles(self, numObstacles):
        try:
            print("This will place up to number of obstacles in appropriately",
                    "randomized positions, with respect to edge length")
        except:
            print("An error occurred placing obstacles")
    
    def placePowerUps(self, numPowerUps):
        try:
            print("This will place up to number of powerups in appropriately",
                    "randomized positions, with respect to edge length")
        except:
            print("An error occurred placing powerups")
            
    def movePlayer(self, player, direction):
        try:
            # First check for collision
            collision, tag, powerup = self.checkCollision(player, direction)
            # If collision is a tag, do the tagging stuff
            # If collision is obstacle/wall/non tag player bump, do nothing
            # Otherwise move. If there's a powerup there, pick it up
            if(tag):
                tag.setIt()
                player.setNotIt()
                if player in self.playersNotIt:
                    self.playersNotIt.remove(player)
                
        except:
            print("An error occurred moving player", player, ":", direction)

    def rotatePlaySpace(self, player, rotation):
        try:
            print("This will attempt to rotate the playspace")
        except:
            print("An error occurred rotating", rotation, "from player", player)
    
    def checkCollision(self, player, direction):
        try:
            print("This will check if an obstacle exists where the player wants",
                  "to move")
            # Return tuple (collision, tag, powerup):
            #  - collision: bool indicating a collision with obstacle, edge, or
            #       another player where the moving player is not it
            #  - tag: if the moving player is it and the obstacle is another
            #       player, this is the other player, else 0
            #  - powerup: if the obstacle is a powerup, this is the index for it
            collision, tag, powerup = (0,0,0)
            return collision, tag, powerup
        except:
            print("An error occurred checking collision")
    
    def setRotationCoolDown(self):
        try:
            self.rotationCoolDownRemaining = ROTATION_COOLDOWN
        except:
            print("An error occurred setting the rotation cooldown")
    
    def rotationCoolDown(self):
        try:
            if(self.rotationCoolDownRemaining>0): self.rotationCoolDownRemaining -= 1
        except:
            print("An error occurred decrementing the rotation cooldown")
            
class Player:
    def __init__(self, playerNum, x, y, z, it):
        try:
            self.playerNum = playerNum;
            self.x = x
            self.y = y
            self.z = z
            self.it = it
        except:
            print("An error occurred initializing Player")
    
    def setPosition(self, x, y, z):
        try:
            self.x = x
            self.y = y
            self.z = z
        except:
            print("An error occurred updating player position")

    def setIt(self):
        try:
            if(not self.it): self.it = True
            else: print("Tagged person was already it, something went wrong")
        except:
            print("An error occurred updating who is it")

    def setNotIt(self):
        try:
            if(self.it): self.it = False
            else: print("Tagged person was already not it, something went wrong")
        except:
            print("An error occurred updating who is it")            