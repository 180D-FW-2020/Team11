# -*- coding: utf-8 -*-
"""
Created on Mon Nov  9 12:54:08 2020

@author: zefyr
"""

import gamePlay as g
import playerPi
import playerPC
import player_sub as sub
import player_client as cli
from threading import Thread

# Should have better way to set these values than hard coding
isPi = False
isPrimary = False
playerId = 1
numPlayers = 4
            
def piProcess():
    '''
    Processes run on the pi. This detects a rotation on the pi, sends it,
    and then waits for permission to detect a new rotation.
    
    Currently requires changes:
        * add threading to support simulataneous listen for direction and rotation
        * add threading to support simultaneous listen for display update and
            player action
    '''
    subscriber = sub.Receiver("primaryNode")
    client = cli.Transmitter("player")
    
    pi = playerPi.PlayerPi(playerId)   
    canSend = True
    
    while True:
        if canSend:
            rotation = pi.getRotation()
            package = pi.pack(rotation)
            client.update(package)
            client.send()
            canSend = False
        else:
            message = subscriber.receive()
            canSend = pi.unpack(message)

def pcProcess():
    '''
    Processes run on the pc. This detects a direction with the camera, sends it,
    and then waits for permission to detect a new direction. It also runs a
    display update on a separate thread which can access the local pc class, so
    that the display just updates when display information is updated from a
    received message.
    
    Currently requires changes:
        * add threading to support simulataneous listen for direction and rotation
        * add threading to support simultaneous listen for display update and
            player action
    '''
    subscriber = sub.Receiver("primaryNode")
    client = cli.Transmitter("player")
    
    pc = playerPC.PlayerPC(playerId, numPlayers)
    canSend = True
    
    display = Thread(target=displayProcess, args=(pc))
    display.start()
    
    while True:
        if canSend:
            direction = pc.getDirection()
            package = pc.pack(direction)
            client.update(package)
            client.send()
            canSend = False
        else:
            message = subscriber.receive()
            canSend = pc.unpack(message)
            
def centralNodeProcess():
    '''
    Processes run on the central node only, which will run on a separate thread
    from that particular player's personal processes (pcProcess above). This
    waits for messages from player PCs and Pi's about direction and rotation.
    When a message is received, the PlaySpace and game state are updated, and
    a message is sent to player PCs and Pi's indicating the update.
    '''
    subscriber = sub.Receiver("player")
    client = cli.Transmitter("primaryNode")
    
    game = g.GamePlay(numPlayers, primaryNode = True)
    
    while True:
        message = subscriber.receive()
        playerId, direction, rotation = game.unpack(message)
        if (direction):
            game.playSpace.movePlayer(playerId, direction)
        elif (rotation):
            game.playSpace.rotatePlaySpace(rotation)
        else:
            # This shouldn't happen
            print("A message was received without direction or rotation")
            
        message = game.pack()
        client.update(message)

def displayProcess(pc):
    '''
    Updates the display as needed.
    '''
    
    while True:
        if pc.displayUpdate: pc.updateDisplay()

### Select processes to run for instance
if isPi:
    try:
        piProcess()
    except:
        print("An error occurred with pi processes")
elif isPrimary:
    try:
        central = Thread(target=centralNodeProcess)
        player = Thread(target=pcProcess)
        central.start()
        player.start()
    except:
        print("An error occurred with primary node processes")
else:
    # Only other case is this is the playerPC
    try:
        pcProcess()
    except:
        print("An error occurred with non primary node processes")