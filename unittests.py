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
        self.edgeLength = 10
        self.p = gamePlay.PlaySpace(self.numPlayers, self.edgeLength, 0, 0)
    
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
        pass
    
    ## function not yet implemented, untestable
    def testPlacePowerups(self):
        pass
    
    ## function not yet implemented, untestable
    def testCheckCollision(self):
        pass
    
    ## movePlayer depends on checkCollision implementation. While that method
    ## is not yet implemented, only testMovePlayer is testable, and it will
    ## move players regardless of collisions
    def testMovePlayerMoveUpNotIt(self):
        playerNum = 1
        self.p.players[playerNum - 1]['position'] = np.array([5,5,5])
        self.p.players[playerNum - 1]['it'] = False
        self.p.movePlayer(playerNum, '^')
        expected = np.array([5,5+1,5])
        self.assertTrue(np.array_equal(expected, self.p.players[playerNum - 1]['position']),
                         msg = '{}'.format(self.p.players))
        
    def testMovePlayerMoveDownNotIt(self):
        playerNum = 1
        self.p.players[playerNum - 1]['position'] = np.array([5,5,5])
        self.p.players[playerNum - 1]['it'] = False
        self.p.movePlayer(playerNum, 'v')
        expected = np.array([5,5-1,5])
        self.assertTrue(np.array_equal(expected, self.p.players[playerNum - 1]['position']),
                         msg = '{}'.format(self.p.players))
    
    def testMovePlayerMoveLeftNotIt(self):
        playerNum = 1
        self.p.players[playerNum - 1]['position'] = np.array([5,5,5])
        self.p.players[playerNum - 1]['it'] = False
        self.p.movePlayer(playerNum, '<')
        expected = np.array([5-1,5,5])
        self.assertTrue(np.array_equal(expected, self.p.players[playerNum - 1]['position']),
                         msg = '{}'.format(self.p.players))
        
    def testMovePlayerMoveRightNotIt(self):
        playerNum = 1
        self.p.players[playerNum - 1]['position'] = np.array([5,5,5])
        self.p.players[playerNum - 1]['it'] = False
        self.p.movePlayer(playerNum, '>')
        expected = np.array([5+1,5,5])
        self.assertTrue(np.array_equal(expected, self.p.players[playerNum - 1]['position']),
                         msg = '{}'.format(self.p.players))
        
    def testMovePlayerMoveUpIt(self):
        playerNum = 1
        self.p.players[playerNum - 1]['position'] = np.array([5,5,5])
        self.p.players[playerNum - 1]['it'] = True
        self.p.movePlayer(playerNum, '^')
        expected = np.array([5,5+gamePlay.ITSPEED,5])
        self.assertTrue(np.array_equal(expected, self.p.players[playerNum - 1]['position']),
                         msg = '{}'.format(self.p.players))
        
    def testMovePlayerMoveDownIt(self):
        playerNum = 1
        self.p.players[playerNum - 1]['position'] = np.array([5,5,5])
        self.p.players[playerNum - 1]['it'] = True
        self.p.movePlayer(playerNum, 'v')
        expected = np.array([5,5-gamePlay.ITSPEED,5])
        self.assertTrue(np.array_equal(expected, self.p.players[playerNum - 1]['position']),
                         msg = '{}'.format(self.p.players))
    
    def testMovePlayerMoveLeftIt(self):
        playerNum = 1
        self.p.players[playerNum - 1]['position'] = np.array([5,5,5])
        self.p.players[playerNum - 1]['it'] = True
        self.p.movePlayer(playerNum, '<')
        expected = np.array([5-gamePlay.ITSPEED,5,5])
        self.assertTrue(np.array_equal(expected, self.p.players[playerNum - 1]['position']),
                         msg = '{}'.format(self.p.players))
        
    def testMovePlayerMoveRightIt(self):
        playerNum = 1
        self.p.players[playerNum - 1]['position'] = np.array([5,5,5])
        self.p.players[playerNum - 1]['it'] = True
        self.p.movePlayer(playerNum, '>')
        expected = np.array([5+gamePlay.ITSPEED,5,5])
        self.assertTrue(np.array_equal(expected, self.p.players[playerNum - 1]['position']),
                         msg = '{}'.format(self.p.players))
    
    ## pending checkCollision implementation
    def testMovePlayerTag(self):
        pass
    
    ## pending checkCollision implementation
    def testMovePlayerPowerup(self):
        pass
    
    ## pending checkCollision implementation
    def testMovePlayerCollision(self):
        pass
    
    ## check rotatePlaySpace funtion. Due to use of numpy arrays and cross 
    ## products, should not be necessary to unit test based on starting from
    ## other orientations, just test each of the four rotations
    def testRotatePlaySpaceUp(self):
        self.verticalAxis = np.array([0,1,0])
        self.horizontalAxis = np.array([1,0,0])
        expectedHorizontal = self.p.horizontalAxis
        expectedVertical = np.array([0, 0, -1])
        self.p.rotatePlaySpace('^')
        self.assertTrue(np.array_equal(expectedHorizontal, self.p.horizontalAxis),
                         msg = '{}'.format(self.p.horizontalAxis))
        self.assertTrue(np.array_equal(expectedVertical, self.p.verticalAxis),
                         msg = '{}'.format(self.p.verticalAxis))
        
    def testRotatePlaySpaceDown(self):
        self.verticalAxis = np.array([0,1,0])
        self.horizontalAxis = np.array([1,0,0])
        expectedHorizontal = self.p.horizontalAxis
        expectedVertical = np.array([0, 0, 1])
        self.p.rotatePlaySpace('v')
        self.assertTrue(np.array_equal(expectedHorizontal, self.p.horizontalAxis),
                         msg = '{}'.format(self.p.horizontalAxis))
        self.assertTrue(np.array_equal(expectedVertical, self.p.verticalAxis),
                         msg = '{}'.format(self.p.verticalAxis))

    def testRotatePlaySpaceLeft(self):
        self.verticalAxis = np.array([0,1,0])
        self.horizontalAxis = np.array([1,0,0])
        expectedHorizontal = np.array([0, 0, 1])
        expectedVertical = self.verticalAxis
        self.p.rotatePlaySpace('<')
        self.assertTrue(np.array_equal(expectedHorizontal, self.p.horizontalAxis),
                         msg = '{}'.format(self.p.horizontalAxis))
        self.assertTrue(np.array_equal(expectedVertical, self.p.verticalAxis),
                         msg = '{}'.format(self.p.verticalAxis))
        
    def testRotatePlaySpaceRight(self):
        self.verticalAxis = np.array([0,1,0])
        self.horizontalAxis = np.array([1,0,0])
        expectedHorizontal = np.array([0, 0, -1])
        expectedVertical = self.verticalAxis
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
    