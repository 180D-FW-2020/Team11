# -*- coding: utf-8 -*-
"""
Created on Mon Nov  9 12:54:08 2020

@author: zefyr

"""

# Should have better way to set these values than hard coding

import settings
import gamePlay as g
if settings.isPi: import playerPi
else: import playerPC
import comms
from threading import Thread
import cv2
import multiprocessing
import random
import time
import traceback
import datetime
            
def piProcess():
    '''
    Processes run on the pi. This detects a rotation on the pi, sends it,
    and then waits for permission to detect a new rotation.
    '''
    if settings.verbose: print("Starting pi process")
    
    pi = playerPi.PlayerPi(settings.playerId)
    displayReceived = False
    stop = False
    
    clientId = f'python-mqtt-{random.randint(0, 1000)}'
    receiver = comms.Receiver((comms.initial,
                               comms.coolDown,
                               comms.axes),
                              clientId)
    transmitter = comms.Transmitter()
    receiver.start()
    
    #First, get initial load with full playspace info
    while not displayReceived:
        
        # Keep checking for an initial load
        if len(receiver.packages):
            # Gets true if initial load received, false and deletes message
            # from queue otherwise
            displayReceived = pi.unpack(receiver.packages.pop(0))
            
    # Send handshake to confirm receipt of first load
    package = pi.pack(displayReceived)
    transmitter.transmit(comms.piConfirmation, package)
    
    # Send transmitter to separate thread to handle getting player input and
    # sending to central, while current process gets display updates
    transmit = Thread(target=piTransmit, args = (transmitter, pi, lambda:stop,))
    transmit.start()
    
    # Gameplay receiver loop checks for new packages in the queue. Packages
    # set the rotation cooldown or end the game.
    while not pi.gameOver:
        if len(receiver.packages):
            pi.unpack(receiver.packages.pop(0))

    stop = True
    transmit.join()
    receiver.stop()

def piTransmit(transmitter, pi, stop):
    '''
    Separate thread for receiving player input on Pi and transmitting it to 
    central.
    '''
    while not pi.gameOver and not stop():
        if not pi.coolDown:
            rotation = pi.getRotation()
            package = pi.pack(rotation)
            transmitter.transmit(comms.rotation, package)
            
            # The cooldown will also be set by a message returned from central,
            # but this is here to ensure the pi doesn't send new rotation info
            # before that return message is received
            pi.coolDown = True

def pcProcess():
    '''
    Processes run on the pc. This detects a direction with the camera, sends it,
    and then waits for permission to detect a new direction. It also runs a
    display update on a separate thread which can access the local pc class, so
    that the display just updates when display information is updated from a
    received message.
    '''   
    if settings.verbose: print("Starting pc process")
    
    pc = playerPC.PlayerPC(settings.playerId, settings.numPlayers)
    displayReceived = False
    stop = False
    
    clientId = f'python-mqtt-{random.randint(0, 1000)}'
    receiver = comms.Receiver((comms.initial,
                               comms.move,
                               comms.tag,
                               comms.axes,
                               comms.coolDown),
                              clientId)
    transmitter = comms.Transmitter()
    receiver.start()
    
    #First, get initial load with full playspace info
    while not displayReceived:
        
        # Keep checking for an initial load
        if len(receiver.packages):
            
            # If message is initial load, displayReceived will be True
            displayReceived = pc.unpack(receiver.packages.pop(0))
            pc.updateDisplay()
            
    # Send handshake to confirm receipt of first load
    package = pc.pack(displayReceived)
    transmitter.transmit(comms.pcConfirmation, package)
    
    # Send transmitter to separate thread to handle getting player input and
    # sending to central, while current process gets display updates
    transmitDirection = Thread(target=pcTransmitDirection, args = (transmitter, pc, lambda:stop,))
    transmitDirection.start()
    
    ## transmitCommand methods not yet fully implemented
    #transmitCommand = Thread(target=pcTransmitCommand, args = (transmitter, pc, lambda:stop,))
    #transmitCommand.start()
    
    # Gameplay receiver loop checks for new packages in the queue. Packages
    # update the display and may end the game also.
    while not pc.gameOver:
        if len(receiver.packages):
            pc.unpack(receiver.packages.pop(0))
        #if pc.displayUpdate:
            pc.updateDisplay()
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    cv2.destroyAllWindows()
    
    stop = True
    transmitDirection.join()
    #transmitCommand.join()
    receiver.stop()

def pcTransmitDirection(transmitter, pc, stop):
    '''
    Separate thread for receiving player input on PC and transmitting it to 
    central.
    '''
    frameCapture = cv2.VideoCapture(settings.camera)
    frameCapture.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    frameCapture.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
    
    delay = datetime.datetime.now()
    
    while not pc.gameOver and not stop():
        direction, pc.cameraImage = pc.getDirection(frameCapture)
        #cv2.imshow('frame',pc.cameraImage)
        pc.updateDisplay(event = False)
        
        if direction and datetime.datetime.now()<delay:
            package = pc.pack(direction)
            transmitter.transmit(comms.direction, package)
            delay = datetime.datetime.now() + datetime.timedelta(seconds = settings.motionDelay)
            
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
        #time.sleep(settings.motionDelay)
    frameCapture.release()
    cv2.destroyAllWindows()
        
def pcTransmitCommand(transmitter, pc, stop):
    '''
    Separate thread for receiving player input on PC and transmitting it to 
    central.
    '''
    while not pc.gameOver and not stop():
        command = pc.getCommand()
        package = pc.pack(command)
        transmitter.transmit(comms.command, package)
    
def centralNodeProcess():
    '''
    Processes run on the central node only, which will run on a separate thread
    from that particular player's personal processes (pcProcess above). This
    waits for messages from player PCs and Pi's about direction and rotation.
    When a message is received, the PlaySpace and game state are updated, and
    a message is sent to player PCs and Pi's indicating the update.
    '''
    if settings.verbose: print("Starting central process")
    
    clientId = f'python-mqtt-{random.randint(0, 1000)}'
    receiver = comms.Receiver((comms.piConfirmation,
                               comms.pcConfirmation,
                               comms.direction,
                               comms.command,
                               comms.rotation),
                              clientId)
    transmitter = comms.Transmitter()
    receiver.start()
    
    game = g.GamePlay(settings.numPlayers)

    initialPackage = game.pack()
    
    # Send initial message until all devices confirm receipt
    devicesPending = True
    pcs = [i for i in range(1, settings.numPlayers+1)]
    pis = [i for i in range(1, settings.numPlayers+1)]
    
    while devicesPending:
        
        # Transmit the initial playspace info
        transmitter.transmit(comms.initial, initialPackage)
        
        # Check if any packages in the queue
        if len(receiver.packages):
            
            # If yes, unpack the first one and use to identify which device is
            # now connected
            playerId, pi, pc = game.unpack(receiver.packages.pop(0))
            
            if pi:
                pis.remove(playerId)
                if settings.verbose:
                    print("Player {}'s pi has arrived.".format(playerId))
            elif pc:
                pcs.remove(playerId)
                if settings.verbose:
                    print("Player {}'s pc has arrived.".format(playerId))
        
        # Repeat until no devices left to join
        devicesPending = len(pcs)+len(pis)
        time.sleep(1)
    
    if settings.verbose: print("All player devices connected")
    
    # Then start the game
    while not game.gameOver:
        
        # Poll for messages in queue
        if len(receiver.packages):
            
            # On receipt, get the first message and do stuff relevant to the
            # message topic
            topic, message = game.unpack(receiver.packages.pop(0))
                        
            # Generally this should result in some outbound message
            if message:
                transmitter.transmit(topic, message)
            else:
                if settings.verbose:
                    print("No outbound message to send")
        
        # Check if a rotation cooldown is in place
        if game.playSpace.rotationCoolDownTime:
            
            # If yes, check if it's now ended, in which case a message should
            # be sent.
            cooldown, topic, message = game.playSpace.rotationCoolDownRemaining()
            
            if not cooldown and message:
                
                # If it's now ended, send a message to announce it
                transmitter.transmit(topic, message)
    
    receiver.stop()

### Select processes to run for instance
if __name__ == '__main__':
    if settings.isPi:
        #piProcess()
        try:
            if settings.verbose: print("will run pi stuff")
            piProcess()
        except:
            print("An error occurred with pi processes")
            traceback.print_exc() 
    elif settings.isPrimary:
        try:
            if settings.verbose: print("will run central stuff")
            # central = Thread(target=centralNodeProcess)
            # player = Thread(target=pcProcess)
            central = multiprocessing.Process(target=centralNodeProcess)
            player = multiprocessing.Process(target=pcProcess)
            central.start()
            player.start()
        except:
            print("An error occurred with primary node processes")
            traceback.print_exc() 
    else:
        # Only other case is this is the playerPC
        try:
            if settings.verbose: print("will run pc stuff")
            pcProcess()
        except:
            print("An error occurred with non primary node processes")
            traceback.print_exc() 
