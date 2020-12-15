# -*- coding: utf-8 -*-
"""
Created on Fri Nov  6 20:46:40 2020

@author: zefyr
"""
import random as r
import numpy as np
import traceback
import comms
import datetime
import settings
import copy

ITSPEED = 2 #spaces

class GamePlay:
    def __init__(self, numPlayers):
        try:
            self.gameOver = False
            self.start = False
            
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
            
            if self.start:
                if topic == comms.direction:
                    return self.playSpace.movePlayer(message['playerId'],
                                                        message['val'])
                elif topic == comms.rotation:
                    return self.playSpace.rotatePlaySpace(message['val'])
                else: print("Message received after game start without direction or rotation")
            else:
                if topic == comms.piConfirmation:
                    return message['playerId'], True, False
                elif topic == comms.pcConfirmation:
                    return message['playerId'], False, True
                # Unplanned case
                else: print("Message received before game start without pi or pc confirmation")
            
        except:
            print("An error occurred getting player input")
            traceback.print_exc() 
    
    def pack(self):
        '''
        Packs initial load of playspace for players.
        
        Returns message for transmission.
        '''
        try:
            message = copy.deepcopy(self.playSpace.__dict__)
            for p in message['players']:
                p['position'] = p['position'].tolist()
            message['verticalAxis'] = message['verticalAxis'].tolist()
            message['horizontalAxis'] = message['horizontalAxis'].tolist()
            return message
        except:
            print("An error occurred packing the playspace")
            traceback.print_exc() 
            
class PlaySpace:
    def __init__(self, numPlayers, edgeLength, numObstacles, numPowerups):
        try:
            self.edgeLength = edgeLength
            self.obstacles = []
            self.powerUps = []
            self.it = 0
            
            if numObstacles: self.placeObstacles(numObstacles)
            if numPowerups: self.placePowerUps(numPowerups)
            
            self.verticalAxis = np.array([0,1,0])
            self.horizontalAxis = np.array([1,0,0])
                        
            self.rotationCoolDownTime = 0
            
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
                
                if(i == playerIt): 
                    it = True
                    self.it = i
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
            if settings.verbose: print("start of move: ", self.players[playerId-1])
            # First check for collision
            collision, tag, powerup, overlap = self.checkCollision(playerId, direction)
            if settings.verbose: print("collision info: ", collision, tag, powerup, overlap)
            # If collision is a tag, do the tagging stuff but don't move player
            if tag:
                self.players[tag - 1]['it'] = True
                self.players[self.it - 1]['it'] = False
                if tag in self.playersNotIt:
                    self.playersNotIt.remove(tag)
                self.it = tag
                displayUpdates = {'tagged': tag,
                                  'untagged': playerId}
            # If collision is obstacle/wall/non tag player bump, do nothing
            elif collision and (overlap == 1):
                displayUpdates = 0
            # Otherwise move. If there's a powerup there, pick it up
            
            else:
                if self.players[playerId - 1]['it']: speed = ITSPEED
                else: speed = 1
                
                if direction == '^':
                    if collision and (overlap > 1):
                        self.players[playerId - 1]['position'] += (overlap-1)*self.verticalAxis
                    else:
                        self.players[playerId - 1]['position'] += speed*self.verticalAxis
                elif direction == 'v':
                    if collision and (overlap > 1):
                        self.players[playerId - 1]['position'] -= (overlap-1)*self.verticalAxis
                    else:
                        self.players[playerId - 1]['position'] -= speed*self.verticalAxis
                        
                # right indicates screen left
                elif direction == '>':
                    if collision and (overlap > 1):
                        self.players[playerId - 1]['position'] -= (overlap-1)*self.horizontalAxis
                    else:
                        self.players[playerId - 1]['position'] -= speed*self.horizontalAxis
                        
                # left indicates screen right
                elif direction == '<':
                    if collision and (overlap > 1):
                        self.players[playerId - 1]['position'] += (overlap-1)*self.horizontalAxis
                    else:
                        self.players[playerId - 1]['position'] += speed*self.horizontalAxis
                displayUpdates = {'playerId': playerId,
                                'position': self.players[playerId - 1]['position'].tolist()}
            if settings.verbose: print("start of move: ", self.players[playerId-1])
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
            displayUpdates = {'horizontalAxis': self.horizontalAxis.tolist(),
                                  'verticalAxis': self.verticalAxis.tolist(),
                                  'coolDown': True}
            self.setRotationCoolDown()
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
         - overlap: the number of spaces that can be moved until player overlaps with object colliding into
        '''
        try:
            if self.players[playerId - 1]['it']: speed = ITSPEED
            else: speed = 1
            collision = 0
            tag = 0
            powerup = 0
            overlap = int(-1)
            playArea = self.horizontalAxis + self.verticalAxis
            initloc = self.players[playerId-1]['position']*playArea

            #set future location                
            if direction == '^':
                axis = self.verticalAxis
                inverse = self.horizontalAxis
                location = self.players[playerId - 1]['position']*self.verticalAxis + speed*self.verticalAxis

            elif direction == 'v':
                axis = self.verticalAxis
                inverse = self.horizontalAxis
                location = self.players[playerId - 1]['position']*self.verticalAxis - speed*self.verticalAxis

            # right indicates screen left
            elif direction == '>':
                axis = self.horizontalAxis
                inverse = self.verticalAxis
                location = self.players[playerId - 1]['position']*self.horizontalAxis - speed*self.horizontalAxis
            
            # left indicates screen right
            elif direction == '<':
                axis = self.horizontalAxis
                inverse = self.verticalAxis
                location = self.players[playerId - 1]['position']*self.horizontalAxis + speed*self.horizontalAxis
            
            #get the position index that is changing
            for i in range(len(axis)):
                if abs(axis[i]) == 1:
                    index = i

            # check if collision with edges of playspace
            if (abs(location[index]) > (self.edgeLength)):
                collision = True
                overlap = int(abs(np.linalg.norm(initloc*axis) - (self.edgeLength+1)))
                return collision, tag, powerup, overlap
            elif (location[index] == 0):
                collision = True
                if (self.players[playerId - 1]['it']):
                    overlap = int(2)
                else:
                    overlap = 1
            elif (self.players[playerId - 1]['it']) and (self.players[playerId - 1]['position'][index] > 0) and (location[index] < 0):
                collision = True
                overlap = int(1)


            #check to see if tag by it
            if (self.players[playerId - 1]['it']):
                for i in range(len(self.players)):
                    if (i != (playerId - 1)):
                        myloc = (location + inverse*self.players[playerId - 1]['position'])
                        yourloc = (self.players[i]['position']*playArea)
                        distance = myloc - yourloc
                        difference = initloc - yourloc
                        movement = np.subtract(difference, distance)
                        if (np.linalg.norm(distance) < 1):
                            tag = i+1
                            collision = True
                            overlap = int(np.linalg.norm(difference))
                        elif (np.linalg.norm(difference) == 1) and (np.linalg.norm(distance) == 1) and ((initloc == myloc).all() == False):
                            tag = i+1
                            collision = True
                            overlap = int(np.linalg.norm(difference))


            

            #check to see if not it players collide with each other or if collide with it resulting in tag

            if (self.players[playerId - 1]['it'] == False):
                for i in range(len(self.players)):
                    if (i != (playerId - 1)):
                        myloc = (location + inverse*self.players[playerId - 1]['position'])
                        yourloc = (self.players[i]['position']*playArea)
                        distance = myloc - yourloc
                        if (yourloc == myloc).all() and (self.players[i]['it'] == False):
                            collision = True
                            overlap = 1
                        elif ((self.players[i]['it'] == True) and (np.linalg.norm(distance) < 1)):
                            tag = playerId
                            collision = True
                            overlap = 1
            
            return collision, tag, powerup, overlap
        except:
            print("An error occurred checking collision")
            traceback.print_exc() 
    
    def setRotationCoolDown(self):
        '''
        Sets the rotation cooldown to end a designated time after now
        '''
        try:
            self.rotationCoolDownTime = datetime.datetime.now() + datetime.timedelta(seconds = settings.ROTATION_COOLDOWN)
        except:
            print("An error occurred setting the rotation cooldown")
            traceback.print_exc() 
    
    def rotationCoolDownRemaining(self):
        '''
        Checks if the cooldown is active. Return true if yes, false if no
        '''
        try:
            # Check if a cooldown is even in place. If not, abort. This should
            # be an edge case: the method should only be called when a cooldown
            # is known to be active
            if not self.rotationCoolDownTime:
                if settings.verbose:
                    print("rotationCoolDownRemaining called without checking",
                          "if cooldown in place.")
                return False, 0, 0
            
            # If cooldown is in place, check to see if it ended before now. If
            # yes, the cooldown is over, so zero out the cooldown and return false
            elif self.rotationCoolDownTime < datetime.datetime.now():
                self.rotationCoolDownTime = 0
                message = {'coolDown': False}
                return False, comms.coolDown, message
            
            # Otherwise the cooldown is still active, so return true and keep things going
            else:
                return True, 0, 0
        except:
            print("An error occurred decrementing the rotation cooldown")
            traceback.print_exc()
