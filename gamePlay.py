# -*- coding: utf-8 -*-
"""
Created on Fri Nov  6 20:46:40 2020

@author: zefyr
"""

import logging
import random as r
import numpy as np
import traceback
import comms
import datetime
import settings
import copy

ITSPEED = 2 #spaces
ROTATION_COOLDOWN = 10 #seconds
POWERUP_TIMER = 5 # seconds

class GamePlay:
    def __init__(self, playMode, numPlayers, edgeLength, numObstacles, numPowerups):
        try:
            self.gameOver = False
            self.start = False
            self.numPlayers = numPlayers
            self.playMode = playMode
            
            self.playSpace = PlaySpace(self.numPlayers, edgeLength, numObstacles, numPowerups)
            
        except:
            print("An error occurred initializing GamePlay", flush=True)
            traceback.print_exc() 
    
    # def settings(self):
    #     '''
    #     This prompts the central node player for game settings: edgelength,
    #     number of obstacles, and number of powerups. Number of players too
    #     would be ideal.
        
    #     Returns those settings.
    #     '''
    #     try:
    #         # These are dummy values

    #         self.playMode, self.numPlayers, edgeLength, numObstacles, numPowerups = (settings.playMode, settings.numPlayers, 10, 4, 4)
    #         return self.numPlayers, edgeLength, numObstacles, numPowerups 

    #     except:
    #         print("An error occurred getting settings", flush=True)
    #         traceback.print_exc() 
    
    def unpack(self, package):
        '''
        Unpacks message from a pc or pi containing a player number with a
        rotation or direction.
            
        Returns playerId, rotation, and direction.
        '''
        try:
            topic, message = package
            print("Central unpacking message:", message, topic, flush=True)
            
            if self.start:
                if topic == comms.direction:
                    return self.playSpace.movePlayer(message['playerId'],
                                                        message['val'])
                elif topic == comms.rotation:
                    return self.playSpace.rotatePlaySpace(message['val'])
                elif topic == comms.powerUp:
                    return self.playSpace.activatePowerUp(message['playerId'])
                elif topic == comms.drop:
                    return self.playSpace.dropPowerUp(message['playerId'])
                else:
                    print("Message received after game start without direction or rotation", flush=True)
                    return False, False
            else:
                # Before game start, messages are returned with values
                # clientId (str), playerId (int), pi (bool), pc (bool), ready
                # (bool). 
                if topic == comms.piConfirmation:
                    return message['val'], 0, True, False, False
                elif topic == comms.pcConfirmation:
                    return message['val'], 0, False, True, False
                elif topic == comms.ready:
                    return 0, message['playerId'], False, False, True
                # Unplanned case
                else:
                    print("Message received before game start without pi or pc confirmation", flush=True)
                    return False, False, False, False, False
            
        except:
            print("An error occurred getting player input", flush=True)
            traceback.print_exc() 
    
    def pack(self, message = None, clientId = None, playerId = None):
        '''
        Packs initial load of playspace for players.
        
        Returns message for transmission.
        '''
        try:
            if clientId:
                return {'clientId': clientId,
                    'playerId': playerId}
            elif not message:
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
            print("An error occurred packing the playspace", flush=True)
            traceback.print_exc() 

    def isGameOver(self):
        try:
            # Standard play mode: play until everyone has been tagged at least once
            if self.playMode == "standard" and len(self.playSpace.playersNotIt) == 0:
                return True
            # Infinite play mode: play forever
            elif self.playMode == "infinite":
                return False
            # Any other play mode is not handled: play like infinite
            else:
                return False
        except:
            print("An error occurred determining if the game is over")
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
            self.freezeTimer = 0
            self.rotationCoolDownSeconds = 0
            
            if numPlayers:
                self.numPlayers = numPlayers
                self.players, self.playersNotIt = self.placePlayers(numPlayers)
                
                # Counts the number of times each player has been tagged
                self.tagCount = [0 for i in range(self.numPlayers)]
            
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
            mask = np.array([1, 1, 0])
            for i in range (1, numPlayers+1):
                
                if self.edgeLength:
                    unique = False
                    while not unique:
                        position = np.array([r.randrange(1, self.edgeLength + 1, 1),
                                    r.randrange(1, self.edgeLength + 1, 1),
                                    r.randrange(1, self.edgeLength + 1, 1)])
                        unique = True
                        for p in players:
                            if unique and np.array_equal(position * mask, p['position'] * mask):
                                unique = False
                                
                else: position = np.array([0, 0, 0])
                
                if(i == playerIt): 
                    it = True
                    self.it = i
                else:
                    it = False
                    playersNotIt.append(i)
                
                unique = False
                while not unique:
                    brightEnough = False
                    while not brightEnough:
                        bp = r.randrange(0, 256)
                        gp = r.randrange(0, 256)
                        rp = r.randrange(0, 256)
                        if bp+gp+rp>200: brightEnough = True
                    unique = True
                    for p in players:
                        if unique and (abs(bp - p['color'][0]) + abs(gp - p['color'][1]) + abs(rp - p['color'][2])) < 200:
                            unique = False
                
                bi = min(bp + 70, 255)
                gi = min(gp + 70, 255)
                ri = min(rp + 70, 255)
                
                color = (bp, gp, rp)
                itColor = (bi, gi, ri)
                players.append({'playerId': i,
                                'position': position,
                                'it': it,
                                'powerUpHeld': 0,
                                'powerUpActive': 0,
                                'powerUpTimer': 0,
                                'color': color,
                                'itColor': itColor})
            
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
                    powerupID = r.randrange(1,3) #reminder
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
                        if (self.obstacles[j]['position'][0] == position[0]) and (self.obstacles[j]['position'][2] == position[2]):
                            if position[0] != 1:
                                position[0] -= 1
                            else:
                                position[0] += 1         
                        if (self.obstacles[j]['position'][1] == position[1]) and (self.obstacles[j]['position'][2] == position[2]):
                            if position[2] != 1:
                                position[2] -= 1
                            else:
                                position[2] += 1     
                else: position = np.array([0, 0, 0])
                
                
                powerups.append({'powerUp': powerupID,
                                'position': position})
            
            return powerups
        except:
            print("An error occurred placing powerups")
            traceback.print_exc() 
    
    def dropPowerUp(self, playerId):
        self.players[playerId-1]['powerUpHeld'] = 0
        message = {'playerId': playerId}
        return comms.dropped, message

    def movePlayer(self, playerId, direction, spacesOverride = 0, pickUpPowerups = True):
        '''
        Takes a player ID and direction and checks if a move is possible. If yes,
        makes the move and returns info about the move.
        '''
        try:
            #first check if play is frozen
            if self.freezeTimer:
                if self.players[playerId-1]['powerUpActive'] != 2:
                    topic = 0
                    displayUpdates = 0
                    return topic, displayUpdates
            if settings.verbose: print("start of move: ", self.players[playerId-1])
            
            sOverride = spacesOverride
            pUpPowerups = pickUpPowerups
            # First check for collision
            collision, tag, powerUp, overlap, powerupIndex = self.checkCollision(playerId, direction, spacesOverride = sOverride, pickUpPowerups = pUpPowerups)
            if settings.verbose: print("collision info: ", collision, tag, powerUp, overlap)
            # If collision is a tag, do the tagging stuff but don't move player
            if tag:
                self.players[tag - 1]['it'] = True
                self.players[self.it - 1]['it'] = False
                if tag in self.playersNotIt:
                    self.playersNotIt.remove(tag)
                self.it = tag
                self.tagCount[tag-1] += 1
                topic = comms.tag
                displayUpdates = {'tagged': tag,
                                  'untagged': playerId,
                                  'count': self.tagCount}
            # If collision is obstacle/wall/non tag player bump, do nothing
            elif collision and (overlap == 1):
                topic = 0
                displayUpdates = 0
            # Otherwise move. If there's a powerup there, pick it up
            
            else:
                if spacesOverride:
                    speed = spacesOverride
                else:
                    if self.players[playerId - 1]['it']: speed = ITSPEED
                    else: speed = 1
        
                    if self.powerUpTimerRemaining(playerId) and (self.players[playerId - 1]['powerUpActive'] == 1):
                        speed *= 2                

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
                
                if (powerUp != 0):
                    self.players[playerId-1]['powerUpHeld'] = powerUp
                    replacement = self.replacePowerUp(powerupIndex)
                    displayUpdates.update(replacement)
                    topic = comms.pickup
            
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
            if not self.rotationCoolDownSeconds:
                newAxis = np.cross(self.horizontalAxis, self.verticalAxis)
                if rotation == '^':
                    self.verticalAxis = -1 * newAxis
                elif rotation == 'v':
                    self.verticalAxis = newAxis
                elif rotation == '<':
                    self.horizontalAxis = newAxis
                elif rotation == '>':
                    self.horizontalAxis = -1 * newAxis
                # displayUpdates = {'horizontalAxis': self.horizontalAxis.tolist(),
                #                       'verticalAxis': self.verticalAxis.tolist(),
                #                       'coolDown': ROTATION_COOLDOWN}
                # self.setRotationCoolDown()

                #check that no collisions occur on rotation
                for i in range(len(self.verticalAxis)):
                    if abs(self.verticalAxis[i]) == 1:
                        verticalindex = i
                for i in range(len(self.horizontalAxis)):
                    if abs(self.horizontalAxis[i]) == 1:
                        horizontalindex = i
                
                movePlayer = False
                for i in range(len(self.players)):
                    for j in range(len(self.players)):
                        if j > i:
                            if (self.players[i]['position'][verticalindex] == self.players[j]['position'][verticalindex]) and (self.players[i]['position'][horizontalindex] == self.players[j]['position'][horizontalindex]):
                                movePlayer = True
                                # collision, tag, powerUp, overlap, replacement = self.checkCollision(j+1, '<')
                                # if overlap > 1:
                                #     self.movePlayer(j+1, '<')
                                # else:
                                #     collision, tag, powerUp, overlap, replacement = self.checkCollision(j+1, '^')
                                #     if overlap > 1:
                                #         self.movePlayer(j+1, '^')
                                #     else:
                                #         collision, tag, powerUp, overlap, replacement = self.checkCollision(j+1, '>')
                                #         if overlap > 1:
                                #             self.movePlayer(j+1, '>')
                                #         else:
                                #             collision, tag, powerUp, overlap, replacement = self.checkCollision(j+1, 'v')
                                #             if overlap > 1:
                                #                 self.movePlayer(j+1, 'v')
                    if not movePlayer:
                        for p in range(len(self.powerUps)):
                            if (self.players[i]['position'][verticalindex] == self.powerUps[p]['position'][verticalindex]) and (self.players[i]['position'][horizontalindex] == self.powerUps[p]['position'][horizontalindex]):
                                movePlayer = True
                            # collision, tag, powerUp, overlap, replacement = self.checkCollision(i+1, '<')
                            # if overlap > 1:
                            #     self.movePlayer(i+1, '<')
                            # else:
                            #     collision, tag, powerUp, overlap, replacement = self.checkCollision(i+1, '^')
                            #     if overlap > 1:
                            #         self.movePlayer(i+1, '^')
                            #     else:
                            #         collision, tag, powerUp, overlap, replacement = self.checkCollision(i+1, '>')
                            #         if overlap > 1:
                            #             self.movePlayer(i+1, '>')
                            #         else:
                            #             collision, tag, powerUp, overlap, replacement = self.checkCollision(i+1, 'v')
                            #             if overlap > 1:
                            #                 self.movePlayer(i+1, 'v')
                    if not movePlayer:
                        for o in range(len(self.obstacles)):
                            if (self.players[i]['position'][verticalindex] == self.obstacles[o]['position'][verticalindex]) and (self.players[i]['position'][horizontalindex] == self.obstacles[o]['position'][horizontalindex]):
                                movePlayer = True
                            # collision, tag, powerUp, overlap, replacement = self.checkCollision(i+1, '<')
                            # if overlap > 1:
                            #     self.movePlayer(i+1, '<')
                            # else:
                            #     collision, tag, powerUp, overlap, replacement = self.checkCollision(i+1, '^')
                            #     if overlap > 1:
                            #         self.movePlayer(i+1, '^')
                            #     else:
                            #         collision, tag, powerUp, overlap, replacement = self.checkCollision(i+1, '>')
                            #         if overlap > 1:
                            #             self.movePlayer(i+1, '>')
                            #         else:
                            #             collision, tag, powerUp, overlap, replacement = self.checkCollision(i+1, 'v')
                            #             if overlap > 1:
                            #                 self.movePlayer(i+1, 'v')
                            
                    if movePlayer:
                        _, moveUpdates = self.movePlayer(i+1, '<')
                        if not moveUpdates: _, moveUpdates = self.movePlayer(i+1, '^')
                        if not moveUpdates: _, moveUpdates = self.movePlayer(i+1, '>')
                        if not moveUpdates: _, moveUpdates = self.movePlayer(i+1, 'v')
                        # for j in range(3):
                        #     _, moveUpdates = self.movePlayer(i+1, '<', spacesOverride = j)
                        #     if not moveUpdates: _, moveUpdates = self.movePlayer(i+1, '^', spacesOverride = j)
                        #     if not moveUpdates: _, moveUpdates = self.movePlayer(i+1, '>', spacesOverride = j)
                        #     if not moveUpdates: _, moveUpdates = self.movePlayer(i+1, 'v', spacesOverride = j)

                    
                    displayUpdates = {'horizontalAxis': self.horizontalAxis.tolist(),
                                      'verticalAxis': self.verticalAxis.tolist(),
                                      'coolDown': ROTATION_COOLDOWN,
                                      'players': self.players}
                    for p in displayUpdates['players']:
                        # Somewhere position is getting stored as list instead of numpy array, should find and fix
                        if type(p['position']) is not list:
                            p['position'] = p['position'].tolist()
                        p['powerUpTimer'] = 0
                    
                    self.setRotationCoolDown()
                return comms.axes, displayUpdates
            else:
                return 0, 0
        except:
            print("An error occurred rotating", rotation)
            traceback.print_exc() 
    
    def replacePowerUp(self, index):
        # update display to remove powerup
        position = np.array([r.randrange(1, self.edgeLength + 1, 1),
                    r.randrange(1, self.edgeLength + 1, 1),
                    r.randrange(1, self.edgeLength + 1, 1)])
        powerupID = r.randrange(1,3) #reminder
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
            if (self.obstacles[j]['position'][0] == position[0]) and (self.obstacles[j]['position'][2] == position[2]):
                if position[0] != 1:
                    position[0] -= 1
                else:
                    position[0] += 1         
            if (self.obstacles[j]['position'][1] == position[1]) and (self.obstacles[j]['position'][2] == position[2]):
                if position[2] != 1:
                    position[2] -= 1
                else:
                    position[2] += 1       
        
        self.powerUps.pop(index)
        newPower = {'powerUp' : powerupID,
                    'position' : position}
        self.powerUps.append(newPower)
        # update display to indicate new powerup
        displayUpdates = {'index': index,
                                  'powerUp': powerupID,
                                  'positionpower': position.tolist()}
        return displayUpdates

    def checkCollision(self, playerId, direction, spacesOverride = 0, pickUpPowerups = True):
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
            if spacesOverride:
                speed = spacesOverride
            else:
                if self.players[playerId - 1]['it']: speed = ITSPEED
                else: speed = 1
                if self.powerUpTimerRemaining(playerId) and (self.players[playerId - 1]['powerUpActive'] == 1):
                        speed *= 2
            collision = 0
            tag = 0
            powerup = 0
            overlap = int(-1)
            powerupIndex = 0
            replacement = {}
            posVertical = np.abs(self.verticalAxis)
            posHorizontal = np.abs(self.horizontalAxis)
            playArea = np.add(posVertical, posHorizontal)
            initloc = self.players[playerId-1]['position']*playArea
            overlapChanges = 0

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

            for i in range(len(inverse)):
                if abs(inverse[i]) == 1:
                    inverseindex = i

            # check if collision with edges of playspace
            if (abs(location[index]) > (self.edgeLength)):
                collision = True
                myoverlap = int(abs(np.linalg.norm(initloc*axis) - (self.edgeLength+1)))
                if myoverlap <= abs(overlap) or overlapChanges == 0:
                    overlapChanges += 1
                    overlap = myoverlap
            elif (location[index] == 0):
                collision = True
                if (self.players[playerId - 1]['it']):
                    myoverlap = int(2)
                    if myoverlap <= abs(overlap) or overlapChanges == 0:
                        overlapChanges += 1
                        overlap = myoverlap
                else:
                    myoverlap = 1
                    if myoverlap <= abs(overlap) or overlapChanges == 0:
                        overlapChanges += 1
                        overlap = myoverlap
            elif (self.players[playerId - 1]['it']) and (abs(self.players[playerId - 1]['position'][index]) == 1) and (abs(location[index]) == 1):
                collision = True
                myoverlap = int(1)
                if myoverlap <= abs(overlap) or overlapChanges == 0:
                    overlapChanges += 1
                    overlap = myoverlap
            elif np.linalg.norm((np.linalg.norm(location[index]))-(np.linalg.norm(initloc[index]))) < speed:
                collision = True
                myoverlap = int(np.linalg.norm(initloc[index]))
                if myoverlap <= abs(overlap) or overlapChanges == 0:
                    overlapChanges += 1
                    overlap = myoverlap


            #check to see if tag by it
            if (self.players[playerId - 1]['it']) or (speed > 1):
                for i in range(len(self.players)):
                    if (i != (playerId - 1)):
                        myloc = (location + inverse*self.players[playerId - 1]['position'])
                        yourloc = (self.players[i]['position']*playArea)
                        distance = myloc - yourloc
                        difference = initloc - yourloc
                        movement = np.subtract(difference, distance)
                        if (np.linalg.norm(distance) < 1):
                            if (self.players[playerId - 1]['it']): tag = i+1
                            collision = True
                            overlap = int(np.linalg.norm(difference))
                        elif (np.linalg.norm(difference) == 1) and (np.linalg.norm(distance) == 1) and ((initloc == myloc).all() == False):
                            if (self.players[playerId - 1]['it']): tag = i+1
                            collision = True
                            overlap = int(np.linalg.norm(difference))
                        elif (initloc[inverseindex] == yourloc[inverseindex]):
                            if ((np.linalg.norm(location[index]) <  np.linalg.norm(self.players[i]['position'][index])) and (np.linalg.norm(initloc[index]) >  np.linalg.norm(self.players[i]['position'][index]))) or ((np.linalg.norm(location[index]) >  np.linalg.norm(self.players[i]['position'][index])) and (np.linalg.norm(initloc[index]) <  np.linalg.norm(self.players[i]['position'][index]))):
                                if (self.players[playerId - 1]['it']): tag = i+1
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
                        myoverlap = int(np.linalg.norm(difference))
                        if myoverlap <= abs(overlap) or overlapChanges == 0:
                            overlapChanges += 1
                            overlap = myoverlap
                    elif (np.linalg.norm(difference) == 1) and (np.linalg.norm(distance) == 1) and ((initloc == myloc).all() == False):
                        collision = True
                        myoverlap = int(np.linalg.norm(difference))
                        if myoverlap <= abs(overlap) or overlapChanges == 0:
                            overlapChanges += 1
                            overlap = myoverlap
                    elif (initloc[inverseindex] == yourloc[inverseindex]):
                        if ((np.linalg.norm(location[index]) <  np.linalg.norm(self.obstacles[i]['position'][index])) and (np.linalg.norm(initloc[index]) >  np.linalg.norm(self.obstacles[i]['position'][index]))) or ((np.linalg.norm(location[index]) >  np.linalg.norm(self.obstacles[i]['position'][index])) and (np.linalg.norm(initloc[index]) <  np.linalg.norm(self.obstacles[i]['position'][index]))):
                                collision = True
                                myoverlap = int(np.linalg.norm(difference))
                                if myoverlap <= abs(overlap) or overlapChanges == 0:
                                    overlapChanges += 1
                                    overlap = myoverlap

            #check to see collision with powerup
                for i in range(len(self.powerUps)):
                    
                    myloc = (location + inverse*self.players[playerId - 1]['position'])
                    yourloc = (self.powerUps[i]['position']*playArea)
                    distance = myloc - yourloc
                    difference = initloc - yourloc
                    movement = np.subtract(difference, distance)
                    if (np.linalg.norm(distance) < 1):
                        if self.players[playerId - 1]['powerUpHeld'] == 0 and pickUpPowerups:
                            powerup = self.powerUps[i]['powerUp']
                            #replacement = self.replacePowerUp(i)
                            powerupIndex = i
                
                        else:
                            collision = True
                            myoverlap = int(np.linalg.norm(difference))
                            if myoverlap <= abs(overlap) or overlapChanges == 0:
                                overlapChanges += 1
                                overlap = myoverlap
                    elif (np.linalg.norm(difference) == 1) and (np.linalg.norm(distance) == 1) and ((initloc == myloc).all() == False):
                        if self.players[playerId - 1]['powerUpHeld'] == 0 and pickUpPowerups:
                            powerup = self.powerUps[i]['powerUp']
                            #replacement = self.replacePowerUp(i)
                            powerupIndex = i
           
                        else:
                            collision = True
                            myoverlap = int(np.linalg.norm(difference))
                            if myoverlap <= abs(overlap) or overlapChanges == 0:
                                overlapChanges += 1
                                overlap = myoverlap
                    elif (initloc[inverseindex] == yourloc[inverseindex]):
                        if ((np.linalg.norm(location[index]) <  np.linalg.norm(self.powerUps[i]['position'][index])) and (np.linalg.norm(initloc[index]) >  np.linalg.norm(self.powerUps[i]['position'][index]))) or ((np.linalg.norm(location[index]) >  np.linalg.norm(self.powerUps[i]['position'][index])) and (np.linalg.norm(initloc[index]) <  np.linalg.norm(self.powerUps[i]['position'][index]))):
                            if self.players[playerId - 1]['powerUpHeld'] == 0 and pickUpPowerups:
                                powerup = self.powerUps[i]['powerUp']
                                #replacement = self.replacePowerUp(i)
                                powerupIndex = i
            
                            else:
                                collision = True
                                myoverlap = int(np.linalg.norm(difference))
                                if myoverlap <= abs(overlap) or overlapChanges == 0:
                                    overlapChanges += 1
                                    overlap = myoverlap

            #check to see if not it players collide with each other or if collide with it resulting in tag

            if (self.players[playerId - 1]['it'] == False):
                for i in range(len(self.players)):
                    if (i != (playerId - 1)):
                        myloc = (location + inverse*self.players[playerId - 1]['position'])
                        yourloc = (self.players[i]['position']*playArea)
                        distance = myloc - yourloc
                        if (yourloc == myloc).all():
                            collision = True
                            overlap = int(1)

            #check to see collision with obstacle
                for j in range(len(self.obstacles)):
                    
                    myloc = (location + inverse*self.players[playerId - 1]['position'])
                    yourloc = (self.obstacles[j]['position']*playArea)
                    distance = myloc - yourloc
                    if (yourloc == myloc).all():
                        collision = True
                        overlap = int(1)

            #check to see collision with powerup
                for j in range(len(self.powerUps)):
                    
                    myloc = (location + inverse*self.players[playerId - 1]['position'])
                    yourloc = (self.powerUps[j]['position']*playArea)
                    distance = myloc - yourloc
                    if (yourloc == myloc).all():
                        if self.players[playerId - 1]['powerUpHeld'] == 0 and pickUpPowerups:
                            powerup = self.powerUps[j]['powerUp']
                            #replacement = self.replacePowerUp(j)
                            powerupIndex = j
          
                        else:
                            collision = True
                            overlap = int(1)

                    #    elif ((self.players[i]['it'] == True) and (np.linalg.norm(distance) < 1)):
                            # tag = playerId
                     #       collision = True
                      #      overlap = 1
            
            return collision, tag, powerup, overlap, powerupIndex
        except:
            print("An error occurred checking collision")
            traceback.print_exc() 

    def activatePowerUp(self, playerId):
        try:
            message = {'powerUp': 0}
            if self.players[playerId-1]['powerUpHeld'] == 0:
                #indicate on display no powerups held
                pass
            elif self.players[playerId-1]['powerUpHeld'] == 1:
                #speed powerup
                self.players[playerId-1]['powerUpHeld'] = 0
                self.players[playerId-1]['powerUpActive'] = 1
                time = self.setPowerUpTimer(playerId)
                message['powerUp'] = 1
                message['speedTimer'] = True
                
            elif self.players[playerId-1]['powerUpHeld'] == 2:
                #freeze powerup
                self.players[playerId-1]['powerUpHeld'] = 0
                self.players[playerId-1]['powerUpActive'] = 2
                self.setPowerUpTimer(0)
                message['powerUp'] = 2
                message['freezeTimer'] = True
                
            elif self.players[playerId-1]['powerUpHeld'] == 3:
                #swap places with an existing player
                #recquires comms and display updates
                if self.numPlayers == 1:
                    self.players[playerId-1]['powerUpHeld'] == 0
                    message['playerId'] = playerId
                    return comms.activePower, message
                playerSwap = r.randrange(1, self.numPlayers+1, 1)
                if playerSwap == playerId and playerId != 1:
                    playerSwap -= 1
                elif playerSwap == playerId and playerId == 1:
                    playerSwap += 1
                self.players[playerId-1]['powerUpHeld'] = 0
                xValue = self.players[playerId-1]['position'][0]
                yValue = self.players[playerId-1]['position'][1]
                zValue = self.players[playerId-1]['position'][2]
                self.players[playerId-1]['position'][0] = self.players[playerSwap-1]['position'][0]
                self.players[playerId-1]['position'][1] = self.players[playerSwap-1]['position'][1]
                self.players[playerId-1]['position'][2] = self.players[playerSwap-1]['position'][2]
                self.players[playerSwap-1]['position'][0] = xValue
                self.players[playerSwap-1]['position'][1] = yValue
                self.players[playerSwap-1]['position'][2] = zValue
                message['powerUp'] = 3
                message['swap'] = playerSwap
                message['position'] = self.players[playerId-1]['position'].tolist()
                
            else:
                print("Invalid power up")

            message['playerId'] = playerId
            return comms.activePower , message
        except:
            print("An error occurred activating powerup")
            traceback.print_exc() 

    def setPowerUpTimer(self, playerId):
        '''
        Sets the timer cooldown to end a designated time after now
        '''
        try:
            if playerId != 0:
                if settings.verbose: print(type(playerId))
                time = datetime.datetime.now() + datetime.timedelta(seconds = POWERUP_TIMER)
                self.players[playerId-1]['powerUpTimer'] = time
                return time
            else:
                self.freezeTimer = datetime.datetime.now() + datetime.timedelta(seconds = POWERUP_TIMER)
                return 
        except:
            print("An error occurred setting the timer ")
            traceback.print_exc() 
    
    def powerUpTimerRemaining(self, playerId):
        '''
        Checks if the timer is active. Return true if yes, false if no
        '''
        try:
            # Check if a timer is even in place. If not, abort. This should
            # be an edge case: the method should only be called when a timer
            # is known to be active
            if playerId != 0:
                if not self.players[playerId-1]['powerUpTimer']:
                    if settings.verbose:
                        print("player currently has no active power up")
                    return False, 0, 0
                
                # If timer is in place, check to see if it ended before now. If
                # yes, the timer is over, so zero out the timer and return false
                elif self.players[playerId-1]['powerUpTimer'] < datetime.datetime.now():
                    self.players[playerId-1]['powerUpTimer'] = 0
                    self.players[playerId-1]['powerUpActive'] = 0
                    if settings.verbose:
                        print(self.players[playerId-1])
                    message = {'power': "speed", 'speedTimer': False, 'playerId': playerId}
                    return False, comms.timerOver, message
                
                # Otherwise the timer is still active, so return true and keep things going
                else:
                    return True, 0, 0
            else:
                if not self.freezeTimer:
                    if settings.verbose:
                        print("player currently has no active power up")
                    return False, 0, 0
                
                # If timer is in place, check to see if it ended before now. If
                # yes, the timer is over, so zero out the timer and return false
                elif self.freezeTimer < datetime.datetime.now():
                    self.freezeTimer = 0
                    for i, player in enumerate(self.players):
                        if player['powerUpActive'] == 2:
                            player['powerUpActive'] = 0
                            message = {'power': "freeze", 'freezeTimer': False, 'playerId': player['playerId']}
                            return False, comms.timerOver, message
                
                # Otherwise the timer is still active, so return true and keep things going
                else:
                    return True, 0, 0
        except:
            print("An error occurred decrementing the rotation cooldown")
            traceback.print_exc()

    def setRotationCoolDown(self):
        '''
        Sets the rotation cooldown to end a designated time after now
        '''
        try:
            self.rotationCoolDownTime = datetime.datetime.now() + datetime.timedelta(seconds = ROTATION_COOLDOWN)
            self.rotationCoolDownSeconds = ROTATION_COOLDOWN
        except:
            print("An error occurred setting the rotation cooldown")
            traceback.print_exc() 
    
    def rotationCoolDownRemaining(self):
        '''
        Checks if the cooldown is active. Return true if yes, false if no
        '''
        
        # Check if a cooldown is even in place. If not, abort. This should
        # be an edge case: the method should only be called when a cooldown
        # is known to be active
        if not self.rotationCoolDownTime:
            if settings.verbose:
                print("rotationCoolDownRemaining called without checking",
                      "if cooldown in place.")
            return False, 0, 0
        
        else:
            timeRemaining = self.rotationCoolDownTime - datetime.datetime.now()

            # If current time is before rotation cooldown end time, timedelta
            # object will have days = 0. 
            if not timeRemaining.days:

                # Only send up to one update per second
                if not self.rotationCoolDownSeconds == timeRemaining.seconds:
                    self.rotationCoolDownSeconds = timeRemaining.seconds
                    message = {'coolDown': timeRemaining.seconds}
                    return False, comms.coolDown, message
                # Timer still going but no update to send
                else: return False, 0, 0
            
            # If current time is after cooldown end time, then days = -1 and
            # timer is over
            else:
                self.rotationCoolDownTime = 0
                message = {'coolDown': 0}
                return False, comms.coolDown, message
        # # If cooldown is in place, check to see if it ended before now. If
        # # yes, the cooldown is over, so zero out the cooldown and return false
        # elif self.rotationCoolDownTime < datetime.datetime.now():
        #     self.rotationCoolDownTime = 0
        #     message = {'coolDown': False}
        #     return False, comms.coolDown, message
        
        # # Otherwise the cooldown is still active, so return true and keep things going
        # else:
        #     return True, 0, 0
