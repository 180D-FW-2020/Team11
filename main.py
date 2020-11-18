# -*- coding: utf-8 -*-
"""
Created on Mon Nov  9 12:54:08 2020

@author: zefyr
"""

# Should have better way to set these values than hard coding
isPi = False
isPrimary = True
playerId = 1
numPlayers = 4

import gamePlay as g
if isPi: import playerPi
else: import playerPC
import player_sub as sub
import player_client as cli
from threading import Thread
import cv2

nodeToPrimary = "ece180d/team11/nodeToPrimary"
primaryToNode = "ece180d/team11/primaryToNode"
            
def piProcess():
    '''
    Processes run on the pi. This detects a rotation on the pi, sends it,
    and then waits for permission to detect a new rotation.
    
    Currently requires changes:
        * add threading to support simulataneous listen for direction and rotation
        * add threading to support simultaneous listen for display update and
            player action
    '''
    subscriber = sub.Receiver(primaryToNode)
    client = cli.Transmitter(nodeToPrimary)
    
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
            message = subscriber.receive(-1)
            canSend = pi.unpack(message)

def pcProcess():
    '''
    Processes run on the pc. This detects a direction with the camera, sends it,
    and then waits for permission to detect a new direction. It also runs a
    display update on a separate thread which can access the local pc class, so
    that the display just updates when display information is updated from a
    received message.
    
    Currently requires changes:
        * add threading to support simultaneous listen for direction and rotation
        * add threading to support simultaneous listen for display update and
            player action
    '''
    print("PC connecting")
    subscriber = sub.Receiver(primaryToNode)
    client = cli.Transmitter(nodeToPrimary)
    
    pc = playerPC.PlayerPC(playerId, numPlayers)
    canSend = True
    
    display = Thread(target=displayProcess, args=(pc, ))
    display.start()
    
    while True:
        if canSend:
            print("pc checking for direction")
            direction = pc.getDirection()
            package = pc.pack(direction)
            client.update(package)
            client.send()
            canSend = False
        else:
            message = subscriber.receive(-1)
            canSend = pc.unpack(message)
            
def centralNodeProcess():
    '''
    Processes run on the central node only, which will run on a separate thread
    from that particular player's personal processes (pcProcess above). This
    waits for messages from player PCs and Pi's about direction and rotation.
    When a message is received, the PlaySpace and game state are updated, and
    a message is sent to player PCs and Pi's indicating the update.
    '''
    print("central connecting")
    subscriber = sub.Receiver(nodeToPrimary)
    client = cli.Transmitter(primaryToNode)
    
    game = g.GamePlay(numPlayers, primaryNode = True)
    # This is for the initial playspace transmission. Update with threading to
    # transmit continuously while receiving messages from players until all
    # players confirm receipt.
    message = game.pack()
    client.update(message)
    client.send()
    
    while True:
        print("central looking for message")
        message = subscriber.receive(-1)
        playerId, direction, rotation = game.unpack(message)
        if (direction):
            message = game.playSpace.movePlayer(playerId, direction)
        elif (rotation):
            message = game.playSpace.rotatePlaySpace(rotation)
        else:
            # This shouldn't happen
            print("A message was received without direction or rotation")
        
        if message:
            client.update(message)
            client.send()

def displayProcess(pc):
    '''
    Updates the display as needed.
    '''
    while True:
        if pc.displayUpdate:
            pc.updateDisplay()
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    cv2.destroyAllWindows()

### Select processes to run for instance
if __name__ == '__main__':
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