# -*- coding: utf-8 -*-
"""
Created on Thu Dec  3 12:50:19 2020

@author: zefyr
"""

import unittest

import gamePlay
import comms
import main
import playerPC
import playerPi
import settings
import numpy as np

class TestPlaySpace(unittest.TestCase):
    ## initialize playSpace
    def setUp(self):
        self.numPlayers = 4
        self.numObstacles = 0
        self.numPowerups = 0
        self.edgeLength = 10
        self.ITSPEED = 2
        self.p = gamePlay.PlaySpace(self.numPlayers, self.edgeLength, self.numObstacles, self.numPowerups)
        
    
    ## check default variables assigned correctly
    def testInitEdgeLength(self):
        self.assertTrue(self.p.edgeLength == self.edgeLength)
        
    def testInitNumPlayers(self):
        self.assertTrue(self.p.numPlayers == self.numPlayers)
        
    ## check for landing players on same spot in error. Currently
    ## functionality to prevent that doesn't exist so this isn't always
    ## expected to pass
    def testInitPlacePlayers(self):
        mask = [1,1,0]
        for i in range(len(self.p.players)):
            for j in range(i+1, len(self.p.players)):
                ipos = np.multiply(self.p.players[i]['position'],mask)
                jpos = np.multiply(self.p.players[j]['position'],mask)
                self.assertFalse(np.array_equal(ipos,jpos),
                                msg = '{},{}'.format(self.p.players[i], self.p.players[j]))
    
    ## function not yet implemented, untestable
    def testPlaceObstacles(self):
        mask = [1,1,0]
        for i in range(len(self.p.obstacles)):
            print(self.p.obstacles[i])
            for j in range(i+1, len(self.p.obstacles)):
                ipos = np.multiply(self.p.obstacles[i]['position'],mask)
                jpos = np.multiply(self.p.obstacles[j]['position'],mask)
                self.assertFalse(np.array_equal(ipos,jpos),
                                msg = '{},{}'.format(self.p.obstacles[i], self.p.obstacles[j]))
    
    ## function not yet implemented, untestable
    def testPlacePowerups(self):
        mask = [1,1,0]
        for i in range(len(self.p.powerUps)):
            print(self.p.powerUps[i]['position'])
            for j in range(i+1, len(self.p.powerUps)):
                ipos = np.multiply(self.p.powerUps[i]['position'],mask)
                jpos = np.multiply(self.p.powerUps[j]['position'],mask)
                self.assertFalse(np.array_equal(ipos,jpos),
                                msg = '{},{}'.format(self.p.powerUps[i], self.p.powerUps[j]))
    
    ## function not yet implemented, untestable

# not it collision with edge
    def testCheckCollisionWithEdgeUpNotItTrue(self):
        self.verticalAxis = np.array([0,1,0])
        self.horizontalAxis = np.array([1,0,0])
        self.p.players[0]['position'] = np.array([5,10,5])
        self.p.players[1]['position'] = np.array([1,1,1])
        self.p.players[2]['position'] = np.array([1,1,1])
        self.p.players[3]['position'] = np.array([1,1,1])
        self.p.players[0]['it'] = False
        
        expectedReturn = (1,0,0,1)
        actualResult = self.p.checkCollision(1, '^')
        self.assertEqual(expectedReturn, actualResult,
                         msg = '{}'.format(actualResult))
    
    def testCheckCollisionWithEdgeUpNotItFalse(self):
        self.verticalAxis = np.array([0,1,0])
        self.horizontalAxis = np.array([1,0,0])
        self.p.players[0]['position'] = np.array([5,9,5])
        self.p.players[1]['position'] = np.array([1,1,1])
        self.p.players[2]['position'] = np.array([1,1,1])
        self.p.players[3]['position'] = np.array([1,1,1])
        self.p.players[0]['it'] = False
        
        expectedReturn = (0,0,0,-1)
        actualResult = self.p.checkCollision(1, '^')
        self.assertEqual(expectedReturn, actualResult,
                         msg = '{}'.format(actualResult))

    def testCheckCollisionWithEdgeRightNotItTrue(self):
        self.verticalAxis = np.array([0,1,0])
        self.horizontalAxis = np.array([1,0,0])
        self.p.players[0]['position'] = np.array([10,5,5])
        self.p.players[1]['position'] = np.array([1,1,1])
        self.p.players[2]['position'] = np.array([1,1,1])
        self.p.players[3]['position'] = np.array([1,1,1])
        self.p.players[0]['it'] = False
        
        expectedReturn = (1,0,0,1)
        actualResult = self.p.checkCollision(1, '<')
        self.assertEqual(expectedReturn, actualResult,
                         msg = '{}'.format(actualResult))
    
    def testCheckCollisionWithEdgeRightNotItFalse(self):
        self.verticalAxis = np.array([0,1,0])
        self.horizontalAxis = np.array([1,0,0])
        self.p.players[0]['position'] = np.array([9,5,5])
        self.p.players[1]['position'] = np.array([1,1,1])
        self.p.players[2]['position'] = np.array([1,1,1])
        self.p.players[3]['position'] = np.array([1,1,1])
        self.p.players[0]['it'] = False
        
        expectedReturn = (0,0,0,-1)
        actualResult = self.p.checkCollision(1, '<')
        self.assertEqual(expectedReturn, actualResult,
                         msg = '{}'.format(actualResult))
    
    def testCheckCollisionWithEdgeLeftNotItTrue(self):
        self.verticalAxis = np.array([0,1,0])
        self.horizontalAxis = np.array([1,0,0])
        self.p.players[0]['position'] = np.array([1,5,5])
        self.p.players[1]['position'] = np.array([1,1,1])
        self.p.players[2]['position'] = np.array([1,1,1])
        self.p.players[3]['position'] = np.array([1,1,1])
        self.p.players[0]['it'] = False
        
        expectedReturn = (1,0,0,1)
        actualResult = self.p.checkCollision(1, '>')
        self.assertEqual(expectedReturn, actualResult,
                         msg = '{}'.format(actualResult))
    
    def testCheckCollisionWithEdgeLeftNotItFalse(self):
        self.verticalAxis = np.array([0,1,0])
        self.horizontalAxis = np.array([1,0,0])
        self.p.players[0]['position'] = np.array([2,5,9])
        self.p.players[1]['position'] = np.array([1,1,1])
        self.p.players[2]['position'] = np.array([1,1,1])
        self.p.players[3]['position'] = np.array([1,1,1])
        self.p.players[0]['it'] = False
        
        expectedReturn = (0,0,0,-1)
        actualResult = self.p.checkCollision(1, '>')
        self.assertEqual(expectedReturn, actualResult,
                         msg = '{}'.format(actualResult))
    
    def testCheckCollisionWithEdgeDownNotItTrue(self):
        self.verticalAxis = np.array([0,1,0])
        self.horizontalAxis = np.array([1,0,0])
        self.p.players[0]['position'] = np.array([5,1,5])
        self.p.players[1]['position'] = np.array([1,1,1])
        self.p.players[2]['position'] = np.array([1,1,1])
        self.p.players[3]['position'] = np.array([1,1,1])
        self.p.players[0]['it'] = False
        
        expectedReturn = (1,0,0,1)
        actualResult = self.p.checkCollision(1, 'v')
        self.assertEqual(expectedReturn, actualResult,
                         msg = '{}'.format(actualResult))
    
    def testCheckCollisionWithEdgeDownNotItFalse(self):
        self.verticalAxis = np.array([0,1,0])
        self.horizontalAxis = np.array([1,0,0])
        self.p.players[0]['position'] = np.array([5,2,5])
        self.p.players[1]['position'] = np.array([1,1,1])
        self.p.players[2]['position'] = np.array([1,1,1])
        self.p.players[3]['position'] = np.array([1,1,1])
        self.p.players[0]['it'] = False
        
        expectedReturn = (0,0,0,-1)
        actualResult = self.p.checkCollision(1, 'v')
        self.assertEqual(expectedReturn, actualResult,
                         msg = '{}'.format(actualResult))

# #it collision with edge

    def testCheckCollisionWithEdgeUpItTrueOneSpace(self):
        self.verticalAxis = np.array([0,1,0])
        self.horizontalAxis = np.array([1,0,0])
        self.p.players[0]['position'] = np.array([5,10,5])
        self.p.players[1]['position'] = np.array([1,1,1])
        self.p.players[2]['position'] = np.array([1,1,1])
        self.p.players[3]['position'] = np.array([1,1,1])
        self.p.players[0]['it'] = True
        
        expectedReturn = (1,0,0,1)
        actualResult = self.p.checkCollision(1, '^')
        self.assertEqual(expectedReturn, actualResult,
                         msg = '{}'.format(actualResult))

    def testCheckCollisionWithEdgeUpItTrueSpeed(self):
        self.verticalAxis = np.array([0,1,0])
        self.horizontalAxis = np.array([1,0,0])
        self.p.players[0]['position'] = np.array([5,9,5])
        self.p.players[1]['position'] = np.array([1,1,1])
        self.p.players[2]['position'] = np.array([1,1,1])
        self.p.players[3]['position'] = np.array([1,1,1])
        self.p.players[0]['it'] = True
        
        expectedReturn = (1,0,0,2)
        actualResult = self.p.checkCollision(1, '^')
        self.assertEqual(expectedReturn, actualResult,
                         msg = '{}'.format(actualResult))
    
    def testCheckCollisionWithEdgeUpItFalse(self):
        self.verticalAxis = np.array([0,1,0])
        self.horizontalAxis = np.array([1,0,0])
        self.p.players[0]['position'] = np.array([5,8,5])
        self.p.players[1]['position'] = np.array([1,1,1])
        self.p.players[2]['position'] = np.array([1,1,1])
        self.p.players[3]['position'] = np.array([1,1,1])
        self.p.players[0]['it'] = True
        
        expectedReturn = (0,0,0,-1)
        actualResult = self.p.checkCollision(1, '^')
        self.assertEqual(expectedReturn, actualResult,
                         msg = '{}'.format(actualResult))

    def testCheckCollisionWithEdgeRightItTrueOneSpace(self):
        self.verticalAxis = np.array([0,1,0])
        self.horizontalAxis = np.array([1,0,0])
        self.p.players[0]['position'] = np.array([10,5,5])
        self.p.players[1]['position'] = np.array([1,1,1])
        self.p.players[2]['position'] = np.array([1,1,1])
        self.p.players[3]['position'] = np.array([1,1,1])
        self.p.players[0]['it'] = True
        
        expectedReturn = (1,0,0,1)
        actualResult = self.p.checkCollision(1, '<')
        self.assertEqual(expectedReturn, actualResult,
                         msg = '{}'.format(actualResult))

    def testCheckCollisionWithEdgeRightItTrueSpeed(self):
        self.verticalAxis = np.array([0,1,0])
        self.horizontalAxis = np.array([1,0,0])
        self.p.players[0]['position'] = np.array([9,5,5])
        self.p.players[1]['position'] = np.array([1,1,1])
        self.p.players[2]['position'] = np.array([1,1,1])
        self.p.players[3]['position'] = np.array([1,1,1])
        self.p.players[0]['it'] = True
        
        expectedReturn = (1,0,0,2)
        actualResult = self.p.checkCollision(1, '<')
        self.assertEqual(expectedReturn, actualResult,
                         msg = '{}'.format(actualResult))
    
    def testCheckCollisionWithEdgeRightItFalse(self):
        self.verticalAxis = np.array([0,1,0])
        self.horizontalAxis = np.array([1,0,0])
        self.p.players[0]['position'] = np.array([8,5,5])
        self.p.players[1]['position'] = np.array([1,1,1])
        self.p.players[2]['position'] = np.array([1,1,1])
        self.p.players[3]['position'] = np.array([1,1,1])
        self.p.players[0]['it'] = True
        
        expectedReturn = (0,0,0,-1)
        actualResult = self.p.checkCollision(1, '<')
        self.assertEqual(expectedReturn, actualResult,
                         msg = '{}'.format(actualResult))
        
    def testCheckCollisionWithEdgeLeftItTrueOneSpace(self):
        self.verticalAxis = np.array([0,1,0])
        self.horizontalAxis = np.array([1,0,0])
        self.p.players[0]['position'] = np.array([1,5,5])
        self.p.players[1]['position'] = np.array([1,1,1])
        self.p.players[2]['position'] = np.array([1,1,1])
        self.p.players[3]['position'] = np.array([1,1,1])
        self.p.players[0]['it'] = True
        
        expectedReturn = (1,0,0,1)
        actualResult = self.p.checkCollision(1, '>')
        self.assertEqual(expectedReturn, actualResult,
                         msg = '{}'.format(actualResult))

    def testCheckCollisionWithEdgeLeftItTrueSpeed(self):
        self.verticalAxis = np.array([0,1,0])
        self.horizontalAxis = np.array([1,0,0])
        self.p.players[0]['position'] = np.array([2,5,5])
        self.p.players[1]['position'] = np.array([1,1,1])
        self.p.players[2]['position'] = np.array([1,1,1])
        self.p.players[3]['position'] = np.array([1,1,1])
        self.p.players[0]['it'] = True
        
        expectedReturn = (1,0,0,2)
        actualResult = self.p.checkCollision(1, '>')
        self.assertEqual(expectedReturn, actualResult,
                         msg = '{}'.format(actualResult))
    
    def testCheckCollisionWithEdgeLeftItFalse(self):
        self.verticalAxis = np.array([0,1,0])
        self.horizontalAxis = np.array([1,0,0])
        self.p.players[0]['position'] = np.array([3,5,5])
        self.p.players[1]['position'] = np.array([1,1,1])
        self.p.players[2]['position'] = np.array([1,1,1])
        self.p.players[3]['position'] = np.array([1,1,1])
        self.p.players[0]['it'] = True
        
        expectedReturn = (0,0,0,-1)
        actualResult = self.p.checkCollision(1, '>')
        self.assertEqual(expectedReturn, actualResult,
                         msg = '{}'.format(actualResult))

    def testCheckCollisionWithEdgeDownItTrueOneSpace(self):
        self.verticalAxis = np.array([0,1,0])
        self.horizontalAxis = np.array([1,0,0])
        self.p.players[0]['position'] = np.array([5,1,5])
        self.p.players[1]['position'] = np.array([1,1,1])
        self.p.players[2]['position'] = np.array([1,1,1])
        self.p.players[3]['position'] = np.array([1,1,1])
        self.p.players[0]['it'] = True
        
        expectedReturn = (1,0,0,1)
        actualResult = self.p.checkCollision(1, 'v')
        self.assertEqual(expectedReturn, actualResult,
                         msg = '{}'.format(actualResult))

    def testCheckCollisionWithEdgeDownItTrueSpeed(self):
        self.verticalAxis = np.array([0,1,0])
        self.horizontalAxis = np.array([1,0,0])
        self.p.players[0]['position'] = np.array([5,2,5])
        self.p.players[1]['position'] = np.array([1,1,1])
        self.p.players[2]['position'] = np.array([1,1,1])
        self.p.players[3]['position'] = np.array([1,1,1])
        self.p.players[0]['it'] = True
        
        expectedReturn = (1,0,0,2)
        actualResult = self.p.checkCollision(1, 'v')
        self.assertEqual(expectedReturn, actualResult,
                         msg = '{}'.format(actualResult))
    
    def testCheckCollisionWithEdgeDownItFalse(self):
        self.verticalAxis = np.array([0,1,0])
        self.horizontalAxis = np.array([1,0,0])
        self.p.players[0]['position'] = np.array([5,3,5])
        self.p.players[1]['position'] = np.array([1,1,1])
        self.p.players[2]['position'] = np.array([1,1,1])
        self.p.players[3]['position'] = np.array([1,1,1])
        self.p.players[0]['it'] = True
        
        expectedReturn = (0,0,0,-1)
        actualResult = self.p.checkCollision(1, 'v')
        self.assertEqual(expectedReturn, actualResult,
                         msg = '{}'.format(actualResult))

# #check for collision among players (not it)

    def testCheckCollisionWithPlayerNotItUpTrue(self):
        self.verticalAxis = np.array([0,1,0])
        self.horizontalAxis = np.array([1,0,0])
        self.p.players[0]['position'] = np.array([5,2,5])
        self.p.players[1]['position'] = np.array([5,1,1])
        self.p.players[2]['position'] = np.array([1,1,1])
        self.p.players[3]['position'] = np.array([1,1,1])
        self.p.players[0]['it'] = False
        self.p.players[1]['it'] = False
        
        expectedReturn = (1,0,0,1)
        actualResult = self.p.checkCollision(2, '^')
        self.assertEqual(expectedReturn, actualResult,
                         msg = '{}'.format(actualResult))

    def testCheckCollisionWithPlayerNotItUpFalse(self):
        self.verticalAxis = np.array([0,1,0])
        self.horizontalAxis = np.array([1,0,0])
        self.p.players[0]['position'] = np.array([5,3,5])
        self.p.players[1]['position'] = np.array([5,1,1])
        self.p.players[2]['position'] = np.array([1,1,1])
        self.p.players[3]['position'] = np.array([1,1,1])
        self.p.players[0]['it'] = False
        self.p.players[1]['it'] = False
        
        expectedReturn = (0,0,0,-1)
        actualResult = self.p.checkCollision(2, '^')
        self.assertEqual(expectedReturn, actualResult,
                         msg = '{}'.format(actualResult))

    def testCheckCollisionWithPlayerNotItDownTrue(self):
        self.verticalAxis = np.array([0,1,0])
        self.horizontalAxis = np.array([1,0,0])
        self.p.players[0]['position'] = np.array([5,2,5])
        self.p.players[1]['position'] = np.array([5,1,1])
        self.p.players[2]['position'] = np.array([1,1,1])
        self.p.players[3]['position'] = np.array([1,1,1])
        self.p.players[0]['it'] = False
        self.p.players[1]['it'] = False
        
        expectedReturn = (1,0,0,1)
        actualResult = self.p.checkCollision(1, 'v')
        self.assertEqual(expectedReturn, actualResult,
                         msg = '{}'.format(actualResult))

    def testCheckCollisionWithPlayerNotItDownFalse(self):
        self.verticalAxis = np.array([0,1,0])
        self.horizontalAxis = np.array([1,0,0])
        self.p.players[0]['position'] = np.array([5,3,5])
        self.p.players[1]['position'] = np.array([5,1,1])
        self.p.players[2]['position'] = np.array([1,1,1])
        self.p.players[3]['position'] = np.array([1,1,1])
        self.p.players[0]['it'] = False
        self.p.players[1]['it'] = False
        
        expectedReturn = (0,0,0,-1)
        actualResult = self.p.checkCollision(1, 'v')
        self.assertEqual(expectedReturn, actualResult,
                         msg = '{}'.format(actualResult))
        
    def testCheckCollisionWithPlayerNotItLeftTrue(self):
        self.verticalAxis = np.array([0,1,0])
        self.horizontalAxis = np.array([1,0,0])
        self.p.players[0]['position'] = np.array([2,5,5])
        self.p.players[1]['position'] = np.array([1,5,1])
        self.p.players[2]['position'] = np.array([1,1,1])
        self.p.players[3]['position'] = np.array([1,1,1])
        self.p.players[0]['it'] = False
        self.p.players[1]['it'] = False
        
        expectedReturn = (1,0,0,1)
        actualResult = self.p.checkCollision(1, '>')
        self.assertEqual(expectedReturn, actualResult,
                         msg = '{}'.format(actualResult))

    def testCheckCollisionWithPlayerNotItLeftFalse(self):
        self.verticalAxis = np.array([0,1,0])
        self.horizontalAxis = np.array([1,0,0])
        self.p.players[0]['position'] = np.array([3,5,5])
        self.p.players[1]['position'] = np.array([1,5,1])
        self.p.players[2]['position'] = np.array([1,1,1])
        self.p.players[3]['position'] = np.array([1,1,1])
        self.p.players[0]['it'] = False
        self.p.players[1]['it'] = False
        
        expectedReturn = (0,0,0,-1)
        actualResult = self.p.checkCollision(1, '>')
        self.assertEqual(expectedReturn, actualResult,
                         msg = '{}'.format(actualResult))
        
    def testCheckCollisionWithPlayerNotItRightTrue(self):
        self.verticalAxis = np.array([0,1,0])
        self.horizontalAxis = np.array([1,0,0])
        self.p.players[0]['position'] = np.array([2,5,5])
        self.p.players[1]['position'] = np.array([1,5,1])
        self.p.players[2]['position'] = np.array([1,1,1])
        self.p.players[3]['position'] = np.array([1,1,1])
        self.p.players[0]['it'] = False
        self.p.players[1]['it'] = False
        
        expectedReturn = (1,0,0,1)
        actualResult = self.p.checkCollision(2, '<')
        self.assertEqual(expectedReturn, actualResult,
                         msg = '{}'.format(actualResult))

    def testCheckCollisionWithPlayerNotItRightFalse(self):
        self.verticalAxis = np.array([0,1,0])
        self.horizontalAxis = np.array([1,0,0])
        self.p.players[0]['position'] = np.array([3,5,5])
        self.p.players[1]['position'] = np.array([1,5,1])
        self.p.players[2]['position'] = np.array([1,1,1])
        self.p.players[3]['position'] = np.array([1,1,1])
        self.p.players[0]['it'] = False
        self.p.players[1]['it'] = False
        
        expectedReturn = (0,0,0,-1)
        actualResult = self.p.checkCollision(2, '<')
        self.assertEqual(expectedReturn, actualResult,
                         msg = '{}'.format(actualResult))

    def testCheckCollisionWithPlayerUpItTrueOneSpace(self):
        self.verticalAxis = np.array([0,1,0])
        self.horizontalAxis = np.array([1,0,0])
        self.p.players[0]['position'] = np.array([5,2,5])
        self.p.players[1]['position'] = np.array([5,1,1])
        self.p.players[2]['position'] = np.array([1,1,1])
        self.p.players[3]['position'] = np.array([1,1,1])
        self.p.players[0]['it'] = False
        self.p.players[1]['it'] = True
        
        expectedReturn = (1,1,0,1)
        actualResult = self.p.checkCollision(2, '^')
        self.assertEqual(expectedReturn, actualResult,
                         msg = '{}'.format(actualResult))

    def testCheckCollisionWithPlayerUpItTrueSpeed(self):
        self.verticalAxis = np.array([0,1,0])
        self.horizontalAxis = np.array([1,0,0])
        self.p.players[0]['position'] = np.array([5,3,5])
        self.p.players[1]['position'] = np.array([5,1,1])
        self.p.players[2]['position'] = np.array([1,1,1])
        self.p.players[3]['position'] = np.array([1,1,1])
        self.p.players[0]['it'] = False
        self.p.players[1]['it'] = True
        
        expectedReturn = (1,1,0,2)
        actualResult = self.p.checkCollision(2, '^')
        self.assertEqual(expectedReturn, actualResult,
                         msg = '{}'.format(actualResult))
        
    def testCheckCollisionWithPlayerDownItTrueOneSpace(self):
        self.verticalAxis = np.array([0,1,0])
        self.horizontalAxis = np.array([1,0,0])
        self.p.players[0]['position'] = np.array([5,1,5])
        self.p.players[1]['position'] = np.array([5,2,1])
        self.p.players[2]['position'] = np.array([1,1,1])
        self.p.players[3]['position'] = np.array([1,1,1])
        self.p.players[0]['it'] = False
        self.p.players[1]['it'] = True
        
        expectedReturn = (1,1,0,1)
        actualResult = self.p.checkCollision(2, 'v')
        self.assertEqual(expectedReturn, actualResult,
                         msg = '{}'.format(actualResult))

    def testCheckCollisionWithPlayerDownItTrueSpeed(self):
        self.verticalAxis = np.array([0,1,0])
        self.horizontalAxis = np.array([1,0,0])
        self.p.players[0]['position'] = np.array([5,1,5])
        self.p.players[1]['position'] = np.array([5,3,1])
        self.p.players[2]['position'] = np.array([1,1,1])
        self.p.players[3]['position'] = np.array([1,1,1])
        self.p.players[0]['it'] = False
        self.p.players[1]['it'] = True
        
        expectedReturn = (1,1,0,2)
        actualResult = self.p.checkCollision(2, 'v')
        self.assertEqual(expectedReturn, actualResult,
                         msg = '{}'.format(actualResult))

    def testCheckCollisionWithPlayerLeftItTrueOneSpace(self):
        self.verticalAxis = np.array([0,1,0])
        self.horizontalAxis = np.array([1,0,0])
        self.p.players[0]['position'] = np.array([1,5,5])
        self.p.players[1]['position'] = np.array([2,5,1])
        self.p.players[2]['position'] = np.array([1,1,1])
        self.p.players[3]['position'] = np.array([1,1,1])
        self.p.players[0]['it'] = False
        self.p.players[1]['it'] = True
        
        expectedReturn = (1,1,0,1)
        actualResult = self.p.checkCollision(2, '>')
        self.assertEqual(expectedReturn, actualResult,
                         msg = '{}'.format(actualResult))

    def testCheckCollisionWithPlayerLeftItTrueSpeed(self):
        self.verticalAxis = np.array([0,1,0])
        self.horizontalAxis = np.array([1,0,0])
        self.p.players[0]['position'] = np.array([1,5,5])
        self.p.players[1]['position'] = np.array([3,5,1])
        self.p.players[2]['position'] = np.array([1,1,1])
        self.p.players[3]['position'] = np.array([1,1,1])
        self.p.players[0]['it'] = False
        self.p.players[1]['it'] = True
        
        expectedReturn = (1,1,0,2)
        actualResult = self.p.checkCollision(2, '>')
        self.assertEqual(expectedReturn, actualResult,
                         msg = '{}'.format(actualResult))
        
    def testCheckCollisionWithPlayerRightItTrueOneSpace(self):
        self.verticalAxis = np.array([0,1,0])
        self.horizontalAxis = np.array([1,0,0])
        self.p.players[0]['position'] = np.array([2,5,5])
        self.p.players[1]['position'] = np.array([1,5,1])
        self.p.players[2]['position'] = np.array([1,1,1])
        self.p.players[3]['position'] = np.array([1,1,1])
        self.p.players[0]['it'] = False
        self.p.players[1]['it'] = True
        
        expectedReturn = (1,1,0,1)
        actualResult = self.p.checkCollision(2, '<')
        self.assertEqual(expectedReturn, actualResult,
                         msg = '{}'.format(actualResult))

    def testCheckCollisionWithPlayerRightItTrueSpeed(self):
        self.verticalAxis = np.array([0,1,0])
        self.horizontalAxis = np.array([1,0,0])
        self.p.players[0]['position'] = np.array([3,5,5])
        self.p.players[1]['position'] = np.array([1,5,1])
        self.p.players[2]['position'] = np.array([1,1,1])
        self.p.players[3]['position'] = np.array([1,1,1])
        self.p.players[0]['it'] = False
        self.p.players[1]['it'] = True
        
        expectedReturn = (1,1,0,2)
        actualResult = self.p.checkCollision(2, '<')
        self.assertEqual(expectedReturn, actualResult,
                         msg = '{}'.format(actualResult))

    ## movePlayer depends on checkCollision implementation. While that method
    ## is not yet implemented, only testMovePlayer is testable, and it will
    ## move players regardless of collisions
    
    def testMovePlayerMoveUpNotIt(self):
        self.verticalAxis = np.array([0,1,0])
        self.horizontalAxis = np.array([1,0,0])
        self.p.players[0]['position'] = np.array([5,5,5])
        self.p.players[1]['position'] = np.array([1,1,1])
        self.p.players[2]['position'] = np.array([1,1,1])
        self.p.players[3]['position'] = np.array([1,1,1])
        self.p.players[0]['it'] = False
        playerNum = 1
        
        self.p.movePlayer(playerNum, '^')
        expected = np.array([5,5+1,5])
        self.assertTrue(np.array_equal(expected, self.p.players[playerNum - 1]['position']),
                         msg = '{}'.format(self.p.players))
        
    def testMovePlayerMoveDownNotIt(self):
        self.verticalAxis = np.array([0,1,0])
        self.horizontalAxis = np.array([1,0,0])
        self.p.players[0]['position'] = np.array([5,5,5])
        self.p.players[1]['position'] = np.array([1,1,1])
        self.p.players[2]['position'] = np.array([1,1,1])
        self.p.players[3]['position'] = np.array([1,1,1])
        self.p.players[0]['it'] = False
        playerNum = 1
        
        self.p.movePlayer(playerNum, 'v')
        expected = np.array([5,5-1,5])
        self.assertTrue(np.array_equal(expected, self.p.players[playerNum - 1]['position']),
                          msg = '{}'.format(self.p.players))
    
    def testMovePlayerMoveLeftNotIt(self):
        self.verticalAxis = np.array([0,1,0])
        self.horizontalAxis = np.array([1,0,0])
        self.p.players[0]['position'] = np.array([5,5,5])
        self.p.players[1]['position'] = np.array([1,1,1])
        self.p.players[2]['position'] = np.array([1,1,1])
        self.p.players[3]['position'] = np.array([1,1,1])
        self.p.players[0]['it'] = False
        playerNum = 1
        
        self.p.movePlayer(playerNum, '>')
        expected = np.array([5-1,5,5])
        self.assertTrue(np.array_equal(expected, self.p.players[playerNum - 1]['position']),
                          msg = '{}'.format(self.p.players))
        
    def testMovePlayerMoveRightNotIt(self):
        self.verticalAxis = np.array([0,1,0])
        self.horizontalAxis = np.array([1,0,0])
        self.p.players[0]['position'] = np.array([5,5,5])
        self.p.players[1]['position'] = np.array([1,1,1])
        self.p.players[2]['position'] = np.array([1,1,1])
        self.p.players[3]['position'] = np.array([1,1,1])
        self.p.players[0]['it'] = False
        playerNum = 1
        
        self.p.movePlayer(playerNum, '<')
        expected = np.array([5+1,5,5])
        self.assertTrue(np.array_equal(expected, self.p.players[playerNum - 1]['position']),
                          msg = '{}'.format(self.p.players))
        
    def testMovePlayerMoveUpIt(self):
        self.verticalAxis = np.array([0,1,0])
        self.horizontalAxis = np.array([1,0,0])
        self.p.players[0]['position'] = np.array([5,5,5])
        self.p.players[1]['position'] = np.array([1,1,1])
        self.p.players[2]['position'] = np.array([1,1,1])
        self.p.players[3]['position'] = np.array([1,1,1])
        self.p.players[0]['it'] = True
        playerNum = 1
        
        self.p.movePlayer(playerNum, '^')
        expected = np.array([5,5+gamePlay.ITSPEED,5])
        self.assertTrue(np.array_equal(expected, self.p.players[playerNum - 1]['position']),
                          msg = '{}'.format(self.p.players))
        
    def testMovePlayerMoveDownIt(self):
        self.verticalAxis = np.array([0,1,0])
        self.horizontalAxis = np.array([1,0,0])
        self.p.players[0]['position'] = np.array([5,5,5])
        self.p.players[1]['position'] = np.array([1,1,1])
        self.p.players[2]['position'] = np.array([1,1,1])
        self.p.players[3]['position'] = np.array([1,1,1])
        self.p.players[0]['it'] = True
        playerNum = 1
        
        self.p.movePlayer(playerNum, 'v')
        expected = np.array([5,5-gamePlay.ITSPEED,5])
        self.assertTrue(np.array_equal(expected, self.p.players[playerNum - 1]['position']),
                          msg = '{}'.format(self.p.players))
    
    def testMovePlayerMoveLeftIt(self):
        self.verticalAxis = np.array([0,1,0])
        self.horizontalAxis = np.array([1,0,0])
        self.p.players[0]['position'] = np.array([5,5,5])
        self.p.players[1]['position'] = np.array([1,1,1])
        self.p.players[2]['position'] = np.array([1,1,1])
        self.p.players[3]['position'] = np.array([1,1,1])
        self.p.players[0]['it'] = True
        playerNum = 1
        
        self.p.movePlayer(playerNum, '>')
        expected = np.array([5-gamePlay.ITSPEED,5,5])
        self.assertTrue(np.array_equal(expected, self.p.players[playerNum - 1]['position']),
                          msg = '{}'.format(self.p.players))
        
    def testMovePlayerMoveRightIt(self):
        self.verticalAxis = np.array([0,1,0])
        self.horizontalAxis = np.array([1,0,0])
        self.p.players[0]['position'] = np.array([5,5,5])
        self.p.players[1]['position'] = np.array([1,1,1])
        self.p.players[2]['position'] = np.array([1,1,1])
        self.p.players[3]['position'] = np.array([1,1,1])
        self.p.players[0]['it'] = True
        playerNum = 1
        
        self.p.movePlayer(playerNum, '<')
        expected = np.array([5+gamePlay.ITSPEED,5,5])
        self.assertTrue(np.array_equal(expected, self.p.players[playerNum - 1]['position']),
                          msg = '{}'.format(self.p.players)) 

    ## just needs to be implemented
    def testMovePlayerTag(self):
        pass

    ## pending powerup implementation
    def testMovePlayerPowerup(self):
        pass
    
    ## check rotatePlaySpace funtion. Due to use of numpy arrays and cross 
    ## products, should not be necessary to unit test based on starting from
    ## other orientations, just test each of the four rotations
    def testRotatePlaySpaceUp(self):
        self.p.verticalAxis = np.array([0,1,0])
        self.p.horizontalAxis = np.array([1,0,0])
        expectedHorizontal = self.p.horizontalAxis
        expectedVertical = np.array([0, 0, -1])
        self.p.rotatePlaySpace('^')
        self.assertTrue(np.array_equal(expectedHorizontal, self.p.horizontalAxis),
                         msg = '{}'.format(self.p.horizontalAxis))
        self.assertTrue(np.array_equal(expectedVertical, self.p.verticalAxis),
                         msg = '{}'.format(self.p.verticalAxis))
        
    def testRotatePlaySpaceDown(self):
        self.p.verticalAxis = np.array([0,1,0])
        self.p.horizontalAxis = np.array([1,0,0])
        expectedHorizontal = self.p.horizontalAxis
        expectedVertical = np.array([0, 0, 1])
        self.p.rotatePlaySpace('v')
        self.assertTrue(np.array_equal(expectedHorizontal, self.p.horizontalAxis),
                         msg = '{}'.format(self.p.horizontalAxis))
        self.assertTrue(np.array_equal(expectedVertical, self.p.verticalAxis),
                         msg = '{}'.format(self.p.verticalAxis))

    def testRotatePlaySpaceLeft(self):
        self.p.verticalAxis = np.array([0,1,0])
        self.p.horizontalAxis = np.array([1,0,0])
        expectedHorizontal = np.array([0, 0, 1])
        expectedVertical = self.p.verticalAxis
        self.p.rotatePlaySpace('<')
        self.assertTrue(np.array_equal(expectedHorizontal, self.p.horizontalAxis),
                         msg = '{}'.format(self.p.horizontalAxis))
        self.assertTrue(np.array_equal(expectedVertical, self.p.verticalAxis),
                         msg = '{}'.format(self.p.verticalAxis))
        
    def testRotatePlaySpaceRight(self):
        self.p.verticalAxis = np.array([0,1,0])
        self.p.horizontalAxis = np.array([1,0,0])
        expectedHorizontal = np.array([0, 0, -1])
        expectedVertical = self.p.verticalAxis
        self.p.rotatePlaySpace('>')
        self.assertTrue(np.array_equal(expectedHorizontal, self.p.horizontalAxis),
                         msg = '{}'.format(self.p.horizontalAxis))
        self.assertTrue(np.array_equal(expectedVertical, self.p.verticalAxis),
                         msg = '{}'.format(self.p.verticalAxis))
    
    ## function not yet implemented, untestable
    def testSetRotationCoolDown(self):
        pass
    
    ## function not yet implemented, untestable
    def testRotationCoolDown(self):
        pass
    
class TestGamePlay(unittest.TestCase):
    ## initialize playSpace
    def setUp(self):
        self.numPlayers = 4
        self.g = gamePlay.GamePlay(self.numPlayers)
        
    ## check default variables assigned correctly
    def testInitGameOver(self):
        self.assertFalse(self.g.gameOver)
        
    ## check playspace created with desired number of players -- should be
    ## sufficient proof of success for playspace creation as playspace tests 
    ## already happened
    def testGamePlaySpace(self):
        self.assertEqual(self.numPlayers, len(self.g.playSpace.players))
        
if __name__ == '__main__':
    unittest.main()
    