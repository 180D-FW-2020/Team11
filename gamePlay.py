# -*- coding: utf-8 -*-
"""
Created on Fri Nov  6 20:46:40 2020

@author: zefyr
"""
import random as r
import numpy as np
import traceback
import comms

ROTATION_COOLDOWN = 20
ITSPEED = 2

class GamePlay:
    def __init__(self, numPlayers):
        try:
            self.gameOver = False
            
            args = self.settings()
            self.playSpace = PlaySpace(numPlayers, *args)
        except:
            print("An error occurred initializing GamePlay")
            traceback.print_exc() 
    
    def settings(self):
        '''
        This prompts the central node player for game settings: edgelength,
        number of obstacles, and number of powerups. Number of players too
        would be ideal.
        
        Returns those settings.
        '''
        try:
            # These are dummy values
            edgeLength, numObstacles, numPowerups = (10, 0, 0)
            return edgeLength, numObstacles, numPowerups
        except:
            print("An error occurred getting settings")
            traceback.print_exc() 
    
    def unpack(self, package):
        '''
        Unpacks message from a pc or pi containing a player number with a
        rotation or direction.
            
        Returns playerId, rotation, and direction.
        '''
        try:
            topic, message = package
            
            if topic == comms.piConfirmation:
                return message['playerId'], True, False
            elif topic == comms.pcConfirmation:
                return message['playerId'], False, True
            elif topic == comms.direction:
                return self.playSpace.movePlayer(message['playerId'],
                                                    message['val'])
            elif topic == comms.rotation:
                return self.playSpace.rotatePlaySpace(message['val'])
            
            else:
                # Unplanned case
                print("A message was received without direction or rotation")
            
        except:
            print("An error occurred getting player input")
            traceback.print_exc() 
    
    def pack(self):
        '''
        Packs initial load of playspace for players.
        
        Returns message for transmission.
        '''
        try:
            return self.playSpace.__dict__
        except:
            print("An error occurred packing the playspace")
            traceback.print_exc() 
            
class PlaySpace:
    def __init__(self, numPlayers, edgeLength, numObstacles, numPowerups):
        try:
            self.edgeLength = edgeLength
            self.obstacles = []
            self.powerUps = []
            
            if numObstacles: self.placeObstacles(numObstacles)
            if numPowerups: self.placePowerUps(numPowerups)
            
            self.verticalAxis = np.array([0,1,0])
            self.horizontalAxis = np.array([1,0,0])
                        
            self.rotationCoolDownRemaining = 0
            
            if numPlayers:
                self.numPlayers = numPlayers
                self.players, self.playersNotIt = self.placePlayers(numPlayers)

        except:
            print("An error occurred initializing PlaySpace")
            traceback.print_exc() 
            
    def placePlayers(self, numPlayers):
        '''
        Randomly places players in the playspace with respect to the edgelength
        and any placed obstacles, and randomly assigns who is It. Returns a list
        of players, and a list of just the players who are not It.
        '''
        try:
            playerIt = r.randrange(1, numPlayers+1, 1)
            players = []
            playersNotIt = []
            for i in range (1, numPlayers+1):
                # Get a random position a reasonable distance from other players
                # with respect to edge length. Don't use origin, this is dummy code
                
                if self.edgeLength:
                    position = np.array([r.randrange(1, self.edgeLength + 1, 1),
                                r.randrange(1, self.edgeLength + 1, 1),
                                r.randrange(1, self.edgeLength + 1, 1)])
                else: position = np.array([0, 0, 0])
                
                if(i == playerIt): it = True
                else:
                    it = False
                    playersNotIt.append(i)
                players.append({'playerId': i,
                                'position': position,
                                'it': it})
            
            return players, playersNotIt
        except:
            print("An error occurred placing players")
            traceback.print_exc() 
            
    def placeObstacles(self, numObstacles):
        '''
        Randomly places obstacles in the playspace with respect to the edgelength
        and any other obstacles.
        '''
        try:
            # Add obstacle code here
            pass
        except:
            print("An error occurred placing obstacles")
            traceback.print_exc() 
    
    def placePowerUps(self, numPowerUps):
        '''
        Randomly places powerups in the playspace with respect to the edgelength
        and any other powerups.
        '''
        try:
            # Add powerUp code here
            pass
        except:
            print("An error occurred placing powerups")
            traceback.print_exc() 
            
    def movePlayer(self, playerId, direction):
        '''
        Takes a player ID and direction and checks if a move is possible. If yes,
        makes the move and returns info about the move.
        '''
        try:
            # First check for collision
            collision, tag, powerup = self.checkCollision(playerId, direction)
            # If collision is a tag, do the tagging stuff but don't move player
            if tag:
                self.players[tag - 1]['it'] = True
                self.players[playerId - 1]['it'] = False
                if tag.PlayerId in self.playersNotIt:
                    self.playersNotIt.remove(tag)
                displayUpdates = {'tagged': tag,
                                  'untagged': playerId}
            # If collision is obstacle/wall/non tag player bump, do nothing
            elif collision:
                displayUpdates = 0
            # Otherwise move. If there's a powerup there, pick it up
            else:
                if self.players[playerId - 1]['it']: speed = ITSPEED
                else: speed = 1
                
                if direction == '^':
                    self.players[playerId - 1]['position'] += speed*self.verticalAxis
                elif direction == 'v':
                    self.players[playerId - 1]['position'] -= speed*self.verticalAxis
                elif direction == '<':
                    self.players[playerId - 1]['position'] -= speed*self.horizontalAxis
                elif direction == '>':
                    self.players[playerId - 1]['position'] += speed*self.horizontalAxis
                displayUpdates = {'playerId': playerId,
                                  'position': self.players[playerId - 1]['position']}
                
            return comms.move, displayUpdates                
        
        except:
            print("An error occurred moving player", playerId, ":", direction)
            traceback.print_exc() 

    def rotatePlaySpace(self, rotation):
        '''
        Takes a rotation, rotates the playspace, returns movement information.
        '''
        try:
            newAxis = np.cross(self.horizontalAxis, self.verticalAxis)
            if rotation == '^':
                self.verticalAxis = -1 * newAxis
            elif rotation == 'v':
                self.verticalAxis = newAxis
            elif rotation == '<':
                self.horizontalAxis = newAxis
            elif rotation == '>':
                self.horizontalAxis = -1 * newAxis
            displayUpdates = {'horizontalAxis': self.horizontalAxis,
                                  'verticalAxis': self.verticalAxis}
                
            return comms.axes, displayUpdates  
        except:
            print("An error occurred rotating", rotation)
            traceback.print_exc() 
    
    def checkCollision(self, playerId, direction):
        '''
        Takes a player and direction, figures out if they are going to run into 
        stuff.
        
        Return tuple (collision, tag, powerup):
         - collision: bool indicating a collision with obstacle, edge, or
             another player where the moving player is not it
         - tag: if the moving player is it and the obstacle is another
             player, this is the other playerId, else 0
         - powerup: if the obstacle is a powerup, this is the index for it

        '''
        try:
            if self.players[playerId - 1].it: speed = ITSPEED
            else: speed = 1
            collision = False
            tag = False
            powerup = False

            #check to see if collision with edge                
            if direction == '^':
                location = self.players[playerId - 1]['position'] + speed*self.verticalAxis
                if (location >= (self.edgeLength + 1)):
                    collision = True
            elif direction == 'v':
                location = self.players[playerId - 1]['position'] - speed*self.verticalAxis
                if (location <= 0):
                    collision = True
            elif direction == '<':
                location = self.players[playerId - 1]['position'] - speed*self.horizontalAxis
                if (location <= 0):
                    collision = True
            elif direction == '>':
                location = self.players[playerId - 1]['position'] + speed*self.horizontalAxis
                if (location >= (self.edgeLength + 1)):
                    collision = True
            
            #check to see if tag by it
            if (self.players[playerId - 1]['it']):
                for i in self.playersNotIt:
                    if ((self.players[i-1]['position'] > self.players[playerId - 1]['position']) and (self.players[i-1]['position'] <= location)):
                        tag = True
                    elif ((self.players[i-1]['position'] < self.players[playerId - 1]['position']) and (self.players[i-1]['position'] >= location)):
                        tag = True
            
            #check to see if not it players collide with each other or if collide with it resulting in tag
            elif (self.players[playerId - 1]['it'] == False):
                for i in range(len(self.players)):
                    if ((self.players[i]['position'] == location) and (self.players[i]['it'] == False)):
                        collision = True
                    elif ((self.players[i]['it'] == True) and (abs(location - self.players[i]['position']) < 1)):
                        tag = True
            
            return collision, tag, powerup
        except:
            print("An error occurred checking collision")
            traceback.print_exc() 
    
    def setRotationCoolDown(self):
        '''
        Starts the rotation cooldown
        '''
        try:
            self.rotationCoolDownRemaining = ROTATION_COOLDOWN
        except:
            print("An error occurred setting the rotation cooldown")
            traceback.print_exc() 
    
    def rotationCoolDown(self):
        '''
        Counts down the rotation cooldown.
        '''
        try:
            if(self.rotationCoolDownRemaining>0): self.rotationCoolDownRemaining -= 1
        except:
            print("An error occurred decrementing the rotation cooldown")
            traceback.print_exc() 
            
# class Player:
#     def __init__(self, playerId, x, y, z, it):
#         try:
#             self.playerId = playerId;
#             self.position = [x, y, z]
#             self.it = it
#         except:
#             print("An error occurred initializing Player")

#     def setIt(self):
#         '''
#         Sets the player as It
#         '''
#         try:
#             if(not self.it):
#                 self.it = True
#             else: print("Tagged person was already it, something went wrong")
#         except:
#             print("An error occurred updating who is it")

#     def setNotIt(self):
#         '''
#         Sets the player as Not It
#         '''
#         try:
#             if(self.it): self.it = False
#             else: print("Tagged person was already not it, something went wrong")
#         except:
#             print("An error occurred updating who is it")