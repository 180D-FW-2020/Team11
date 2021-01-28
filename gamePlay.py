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
            edgeLength, numObstacles, numPowerups = (10, 0, 4)
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
            print("Central unpacking message:", message, topic)
            
            if self.start:
                if topic == comms.direction:
                    return self.playSpace.movePlayer(message['playerId'],
                                                        message['val'])
                elif topic == comms.rotation:
                    return self.playSpace.rotatePlaySpace(message['val'])
                else:
                    print("Message received after game start without direction or rotation")
            else:
                if topic == comms.piConfirmation:
                    return message['playerId'], True, False, False
                elif topic == comms.pcConfirmation:
                    return message['playerId'], False, True, False
                elif topic == comms.ready:
                    return message['playerId'], False, False, True
                # Unplanned case
                else:
                    print("Message received before game start without pi or pc confirmation")
                    return False, False, False, False
            
        except:
            print("An error occurred getting player input")
            traceback.print_exc() 
    
    def pack(self, message = None):
        '''
        Packs initial load of playspace for players.
        
        Returns message for transmission.
        '''
        try:
            if not message:
                message = copy.deepcopy(self.playSpace.__dict__)
                for p in message['players']:
                    p['position'] = p['position'].tolist()
                for o in message['obstacles']:
                    o['position'] = o['position'].tolist()
                for u in message['powerUps']:
                    u['position'] = u['position'].tolist()
                message['verticalAxis'] = message['verticalAxis'].tolist()
                message['horizontalAxis'] = message['horizontalAxis'].tolist()
                return message
            else:
                return {'val': message}
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
            
            
            self.verticalAxis = np.array([0,1,0])
            self.horizontalAxis = np.array([1,0,0])
                        
            self.rotationCoolDownTime = 0
            
            if numPlayers:
                self.numPlayers = numPlayers
                self.players, self.playersNotIt = self.placePlayers(numPlayers)
            
            if numObstacles: 
                self.obstacles = self.placeObstacles(numObstacles)
            if numPowerups: 
                self.powerUps = self.placePowerUps(numPowerups)

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
         #           if len(self.players) != 0:
          #              if (self.players[i-1]['position'][0] == postion[0]) and (self.players[i-1]['position'][1] == postion[1]):
           #                 if position[0] != 1:
            #                    position[0] -= 1
             #               else:
              #                  position[0] += 1
                else: position = np.array([0, 0, 0])
                
                if(i == playerIt): 
                    it = True
                    self.it = i
                else:
                    it = False
                    playersNotIt.append(i)
                players.append({'playerId': i,
                                'position': position,
                                'it': it,
                                'powerUpHeld': 0,
                                'powerUpActive': 0,
                                'powerUpTimer': 0})
            
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
            obstacles = []
            for i in range (numObstacles):
                # Get a random position a reasonable distance from other players
                # with respect to edge length. Don't use origin, this is dummy code
                
                if self.edgeLength:
                    position = np.array([r.randrange(1, self.edgeLength + 1, 1),
                                r.randrange(1, self.edgeLength + 1, 1),
                                r.randrange(1, self.edgeLength + 1, 1)])
                    for j in range(len(self.players)):
                        if (self.players[j]['position'][0] == position[0]) and (self.players[j]['position'][1] == position[1]):
                            if position[0] != 1:
                                position[0] -= 1
                            else:
                                position[0] += 1
                else: position = np.array([0, 0, 0])
                
                
                obstacles.append({'position': position})
            
            return obstacles
        except:
            print("An error occurred placing obstacles")
            traceback.print_exc() 
    
    def placePowerUps(self, numPowerUps):
        '''
        Randomly places powerups in the playspace with respect to the edgelength
        and any other powerups.
        '''
        try:
            powerups = []
            for i in range (numPowerUps):
                # Get a random position a reasonable distance from other players
                # with respect to edge length. Don't use origin, this is dummy code
                
                if self.edgeLength:
                    position = np.array([r.randrange(1, self.edgeLength + 1, 1),
                                r.randrange(1, self.edgeLength + 1, 1),
                                r.randrange(1, self.edgeLength + 1, 1)])
                    powerupID = r.randrange(1,3)
                    for j in range(len(self.players)):
                        if (self.players[j]['position'][0] == position[0]) and (self.players[j]['position'][1] == position[1]):
                            if position[0] != 1:
                                position[0] -= 1
                            else:
                                position[0] += 1
                    for j in range(len(self.obstacles)):
                        if (self.obstacles[j]['position'][0] == position[0]) and (self.obstacles[j]['position'][1] == position[1]):
                            if position[0] != 1:
                                position[0] -= 1
                            else:
                                position[0] += 1
                else: position = np.array([0, 0, 0])
                
                
                powerups.append({'powerUp': powerupID,
                                'position': position})
            
            return powerups
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
            collision, tag, powerUp, overlap = self.checkCollision(playerId, direction)
            if settings.verbose: print("collision info: ", collision, tag, powerUp, overlap)
            # If collision is a tag, do the tagging stuff but don't move player
            if tag:
                self.players[tag - 1]['it'] = True
                self.players[self.it - 1]['it'] = False
                if tag in self.playersNotIt:
                    self.playersNotIt.remove(tag)
                self.it = tag
                topic = comms.tag
                displayUpdates = {'tagged': tag,
                                  'untagged': playerId}
            # If collision is obstacle/wall/non tag player bump, do nothing
            elif collision and (overlap == 1):
                topic = 0
                displayUpdates = 0
            # Otherwise move. If there's a powerup there, pick it up
            
            else:
                if self.players[playerId - 1]['it']: speed = ITSPEED
                else: speed = 1
                
                if (powerUp != 0):
                    self.players[playerId-1]['powerUpHeld'] = powerUp

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

                if powerUp != 0:
                    self.players[playerId - 1]['powerUpHeld'] = powerUp
                    
                topic = comms.move
                displayUpdates = {'playerId': playerId,
                                'position': self.players[playerId - 1]['position'].tolist()}
            if settings.verbose: print("end of move: ", self.players[playerId-1])
            return topic, displayUpdates
        
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

            #check that no collisions occur on rotation
            for i in range(len(self.verticalAxis)):
                if abs(self.verticalAxis[i]) == 1:
                    verticalindex = i
            for i in range(len(self.horizontalAxis)):
                if abs(self.horizontalAxis[i]) == 1:
                    horizontalindex = i
            
            for i in range(len(self.players)):
                for j in range(len(self.players)):
                    if j > i:
                        if (self.players[i]['position'][verticalindex] == self.players[j]['position'][verticalindex]) and (self.players[i]['position'][horizontalindex] == self.players[j]['position'][horizontalindex]):
                            if self.players[i]['position'][horizontalindex] != 1:
                                self.players[i]['position'][horizontalindex] -= 1
                            else:
                                self.players[i]['position'][horizontalindex] += 1

            return comms.axes, displayUpdates  
        except:
            print("An error occurred rotating", rotation)
            traceback.print_exc() 
    
    def replacePowerUp(self, index):
        mypower = self.powerUps
        mypower.pop(index)
        # update display to remove powerup
        position = np.array([r.randrange(1, self.edgeLength + 1, 1),
                    r.randrange(1, self.edgeLength + 1, 1),
                    r.randrange(1, self.edgeLength + 1, 1)])
        powerupID = r.randrange(1,3)
        for j in range(len(self.players)):
            if (self.players[j]['position'][0] == position[0]) and (self.players[j]['position'][1] == position[1]):
                if position[0] != 1:
                    position[0] -= 1
                else:
                   position[0] += 1
        for j in range(len(self.obstacles)):
            if (self.obstacles[j]['position'][0] == position[0]) and (self.obstacles[j]['position'][1] == position[1]):
                if position[0] != 1:
                    position[0] -= 1
                else:
                    position[0] += 1          
                
        self.powerUps.append({'powerUp': powerupID,
                                'position': position})
        # update display to indicate new powerup
        self.powerUps = mypower
        return self.powerUps

    def checkCollision(self, playerId, direction):
        '''
        Takes a player and direction, figures out if they are going to run into 
        stuff.
        
        Return tuple (collision, tag, powerup, overlap):
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
            posVertical = np.abs(self.verticalAxis)
            posHorizontal = np.abs(self.horizontalAxis)
            playArea = np.add(posVertical, posHorizontal)
            initloc = self.players[playerId-1]['position']*playArea

            #set future location                
            if direction == '^':
                axis = posVertical
                inverse = posHorizontal
                location = self.players[playerId - 1]['position']*axis + speed*self.verticalAxis

            elif direction == 'v':
                axis = posVertical
                inverse = posHorizontal
                location = self.players[playerId - 1]['position']*axis - speed*self.verticalAxis

            # right indicates screen left
            elif direction == '>':
                axis = posHorizontal
                inverse = posVertical
                location = self.players[playerId - 1]['position']*axis - speed*self.horizontalAxis
            
            # left indicates screen right
            elif direction == '<':
                axis = posHorizontal
                inverse = posVertical
                location = self.players[playerId - 1]['position']*axis + speed*self.horizontalAxis
            
            #get the position index that is changing
            for i in range(len(axis)):
                if abs(axis[i]) == 1:
                    index = i

            # check if collision with edges of playspace
            if (abs(location[index]) > (self.edgeLength)):
                collision = True
                overlap = int(abs(np.linalg.norm(initloc*axis) - (self.edgeLength+1)))
            elif (location[index] == 0):
                collision = True
                if (self.players[playerId - 1]['it']):
                    overlap = int(2)
                else:
                    overlap = 1
            elif (self.players[playerId - 1]['it']) and (abs(self.players[playerId - 1]['position'][index]) == 1) and (abs(location[index]) == 1):
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

            #check to see collision with obstacle
                for i in range(len(self.obstacles)):
                    
                    myloc = (location + inverse*self.players[playerId - 1]['position'])
                    yourloc = (self.obstacles[i]['position']*playArea)
                    distance = myloc - yourloc
                    difference = initloc - yourloc
                    movement = np.subtract(difference, distance)
                    if (np.linalg.norm(distance) < 1):
                        collision = True
                        overlap = int(np.linalg.norm(difference))
                    elif (np.linalg.norm(difference) == 1) and (np.linalg.norm(distance) == 1) and ((initloc == myloc).all() == False):
                        collision = True
                        overlap = int(np.linalg.norm(difference))

            #check to see collision with powerup
                for i in range(len(self.powerUps)):
                    
                    myloc = (location + inverse*self.players[playerId - 1]['position'])
                    yourloc = (self.powerUps[i]['position']*playArea)
                    distance = myloc - yourloc
                    difference = initloc - yourloc
                    movement = np.subtract(difference, distance)
                    if (np.linalg.norm(distance) < 1):
                        if self.players[playerId - 1]['powerUpHeld'] == 0:
                            powerup = self.powerUps[i]['powerUp']
                            self.replacePowerUp(i)
                        else:
                            collision = True
                            overlap = int(np.linalg.norm(difference))
                    elif (np.linalg.norm(difference) == 1) and (np.linalg.norm(distance) == 1) and ((initloc == myloc).all() == False):
                        if self.players[playerId - 1]['powerUpHeld'] == 0:
                            powerup = self.powerUps[i]['powerUp']
                            self.replacePowerUp(i)
                        else:
                            collision = True
                            overlap = int(np.linalg.norm(difference))

            #check to see if not it players collide with each other or if collide with it resulting in tag

            if (self.players[playerId - 1]['it'] == False):
                for i in range(len(self.players)):
                    if (i != (playerId - 1)):
                        myloc = (location + inverse*self.players[playerId - 1]['position'])
                        yourloc = (self.players[i]['position']*playArea)
                        distance = myloc - yourloc
                        if (yourloc == myloc).all():
                            collision = True
                            overlap = 1

            #check to see collision with obstacle
                for j in range(len(self.obstacles)):
                    
                    myloc = (location + inverse*self.players[playerId - 1]['position'])
                    yourloc = (self.obstacles[j]['position']*playArea)
                    distance = myloc - yourloc
                    if (yourloc == myloc).all():
                        collision = True
                        overlap = 1

            #check to see collision with powerup
                for j in range(len(self.powerUps)):
                    
                    myloc = (location + inverse*self.players[playerId - 1]['position'])
                    yourloc = (self.powerUps[j]['position']*playArea)
                    distance = myloc - yourloc
                    if (yourloc == myloc).all():
                        if self.players[playerId - 1]['powerUpHeld'] == 0:
                            powerup = self.powerUps[j]['powerUp']
                            self.replacePowerUp(i)
                        else:
                            collision = True
                            overlap = 1

                    #    elif ((self.players[i]['it'] == True) and (np.linalg.norm(distance) < 1)):
                            # tag = playerId
                     #       collision = True
                      #      overlap = 1
            
            return collision, tag, powerup, overlap
        except:
            print("An error occurred checking collision")
            traceback.print_exc() 
    
    def activatePowerUp(self, playerId):
        try:
            if self.players[playerId-1]['powerUpHeld'] == 0:
                #indicate on display no powerups held
                pass
            elif self.players[playerId-1]['powerUpHeld'] == 1:
                #speed powerup
                self.players[playerId-1]['powerUpHeld'] == 0
                self.players[playerId-1]['powerUpActive'] == 1
                self.setPowerUpTimer(playerId)
                pass
            elif self.players[playerId-1]['powerUpHeld'] == 2:
                #freeze powerup
                self.players[playerId-1]['powerUpHeld'] == 0
                self.players[playerId-1]['powerUpActive'] == 2
                self.setPowerUpTimer(playerId)
                pass
            elif self.players[playerId-1]['powerUpHeld'] == 3:
                pass
        except:
            print("An error occurred activating powerup")
            traceback.print_exc() 

    def setPowerUpTimer(self, playerId):
        '''
        Sets the rotation cooldown to end a designated time after now
        '''
        try:
            self.players[playerId-1]['powerUpTimer'] = datetime.datetime.now() + datetime.timedelta(seconds = settings.ROTATION_COOLDOWN)
        except:
            print("An error occurred setting the rotation cooldown")
            traceback.print_exc() 
    
    def powerUpTimerRemaining(self, playerID):
        '''
        Checks if the cooldown is active. Return true if yes, false if no
        '''
        try:
            # Check if a timer is even in place. If not, abort. This should
            # be an edge case: the method should only be called when a timer
            # is known to be active
            if not self.players[playerId-1]['powerUpTimer']:
                if settings.verbose:
                    print("powerUpTimerRemaining called without checking",
                          "if timer in place.")
                return False
            
            # If timer is in place, check to see if it ended before now. If
            # yes, the timer is over, so zero out the timer and return false
            elif self.players[playerId-1]['powerUpTimer'] < datetime.datetime.now():
                self.players[playerId-1]['powerUpTimer'] = 0
                return False
            
            # Otherwise the timer is still active, so return true and keep things going
            else:
                return True
        except:
            print("An error occurred decrementing the rotation cooldown")
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

if __name__ == "__main__":
    myp = PlaySpace(1,10,0,1)
    myp.players[0]['position'] = np.array([5,9,5])
    myp.powerUps[0]['position'] = np.array([5,10,5])
    myp.movePlayer(1, '^')
    print(myp.powerUps)
    print(myp.players)
