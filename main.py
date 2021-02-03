# -*- coding: utf-8 -*-
"""
Created on Mon Nov  9 12:54:08 2020

@author: zefyr

"""

# Should have better way to set these values than hard coding

import settings
import gamePlay as g
import playerPi
import playerPC
import comms
from threading import Thread
import cv2
import multiprocessing
import random
import time
import traceback
import datetime
import numpy as np
import platform
if 'arm' not in platform.machine().lower():
    import pygame

MOTION_DELAY = 1

testWithoutPi = False
            
def piProcess():
    '''
    Processes run on the pi. This detects a rotation on the pi, sends it,
    and then waits for permission to detect a new rotation.
    '''
    if settings.verbose: print("Starting pi process", flush=True)
    
    clientId = f'{datetime.datetime.now().strftime("%H%M%S")}{random.randint(0, 1000)}'
    pi = playerPi.PlayerPi(clientId)
    #displayReceived = False
    #stop = False
    
    receiver = comms.Receiver((comms.initial,
                               comms.assign,
                               comms.coolDown,
                               comms.axes,
                               comms.start,
                               comms.stop),
                              clientId)
    transmitter = comms.Transmitter()
    receiver.start()
    
    #First, get initial load with full playspace info
    while not pi.initialReceived:
        
        # Keep checking for an initial load
        if len(receiver.packages):
            # Sets initialReceived to true if initial load
            pi.unpack(receiver.packages.pop(0))
            
    # Send handshake to confirm receipt of first load
    package = pi.pack(pi.clientId)
    transmitter.transmit(comms.piConfirmation, package)
    
    # Receive playerId. May not correspond to playerId for the same player's PC
    # but that doesn't matter, this is only for ease of reading logs
    while not pi.playerId:
    
        # Keep checking for a message assigning the player number
        if len(receiver.packages):
            # Gets true if initial load received, false and deletes message
            # from queue otherwise
            pi.unpack(receiver.packages.pop(0))
            
    # Send handshake to confirm receipt of playerId
    package = pi.pack(pi.playerId)
    transmitter.transmit(comms.ready, package)
    
    stop = [0]
    # Send transmitter to separate thread to handle getting player input and
    # sending to central, while current process gets display updates
    transmit = Thread(target=piTransmit, args = (transmitter, pi, stop,))
    transmit.daemon = True
    transmit.start()
    
    # Gameplay receiver loop checks for new packages in the queue. Packages
    # set the rotation cooldown or end the game.
    #while not pi.gameOver:
    while not pi.gameOver:
        if len(receiver.packages):
            pi.unpack(receiver.packages.pop(0))
    print("pi game over", flush=True)

    stop[0] = True
    transmit.join()
    receiver.stop()

def piTransmit(transmitter, pi, stop):
    '''
    Separate thread for receiving player input on Pi and transmitting it to 
    central.
    '''
    while not pi.gameOver:
        rotation = pi.getRotation(stop)
        if rotation:
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
    if settings.verbose: print("Starting pc process", flush=True)
    breakEarly = False
    
    # Initialize the PyGame
    pygame.init()
    pygame.mixer.init()

    # Start settings soundtrack
    pygame.mixer.music.load('SoundEffects/ready_two_run.wav')
    pygame.mixer.music.set_volume(0.3)
    pygame.mixer.music.play(-1)
    
    clientId = f'{datetime.datetime.now().strftime("%H%M%S")}{random.randint(0, 1000)}'
    pc = playerPC.PlayerPC(clientId)
    #displayReceived = False
    stop = [0]
    
    receiver = comms.Receiver((comms.initial,
                               comms.assign,
                               comms.move,
                               comms.tag,
                               comms.start,
                               comms.stop,
                               comms.axes,
                               comms.coolDown,
                               comms.pickup,
                               comms.activePower),
                              clientId)
    transmitter = comms.Transmitter()
    receiver.start()
    
    # Send receiver to separate thread
    packageReceipt = Thread(target=pcPackageReceipt, args = (receiver, pc, stop,))
    packageReceipt.daemon = True
    packageReceipt.start()
    
    # Get settings. If not isPrimary, other returned variables are all 0. If
    # primary, spawn primary player stuff
    isPrimary, playMode, numPlayers, edgeLength, numObstacles, numPowerups = pc.settings()
    if isPrimary:
        stopCentral = multiprocessing.Value('i', False)
        central = multiprocessing.Process(target=centralNodeProcess, args = (stopCentral, playMode, numPlayers, edgeLength, numObstacles, numPowerups, ))
        central.daemon = True
        central.start()
    
    pc.loading("Waiting for initial game state...")

    #First, get initial load with full playspace info
    while not pc.initialReceived and not breakEarly:
        if cv2.waitKey(1) & 0xFF == ord('q'):
            breakEarly = True
            break
        # # Keep checking for an initial load
        # if len(receiver.packages):
            
        #     # Get initial load and set the base display background
        #     pc.unpack(receiver.packages.pop(0))
        #     pc.updateDisplay()
    
    if not breakEarly:
        pc.loading("Initial game state received. Waiting for player ID assignment...")
        # Send handshake to confirm receipt of first load
        package = pc.pack(pc.clientId)
        transmitter.transmit(comms.pcConfirmation, package)
    
    # Check for assignment of a player ID
    while not pc.playerId and not breakEarly:
        if cv2.waitKey(1) & 0xFF == ord('q'):
            breakEarly = True
            break
        # # Keep checking for assignment
        # if len(receiver.packages):
        #     pc.unpack(receiver.packages.pop(0))
        
    # # Get confirmation from player that they are ready, and send that to central
    # # to complete handshake process
    # while not pc.ready:
    #     command = pc.getCommand(stop)
    #     if command == comms.ready:
    #         pc.ready = True
    #         package = pc.pack(pc.ready)
    #         transmitter.transmit(comms.ready, package)
    
    if not breakEarly:
        pc.loading(f"You are player {pc.playerId}. Say ""ready"" when you're ready to join...")
        # Send command receipt to separate loop
        command = Thread(target=pcCommand, args = (transmitter, pc, stop,))
        command.daemon = True
        command.start()
    else:
        command = 0

    # Gameplay receiver loop checks for new packages in the queue. Packages
    # update the display and may end the game also.
    # while not pc.gameOver:
    #     if len(receiver.packages):
    #         pc.unpack(receiver.packages.pop(0))
    #     #if pc.displayUpdate:
    #         pc.updateDisplay()
    #     if cv2.waitKey(1) & 0xFF == ord('q'):
    #         break
    # cv2.destroyAllWindows()
    
    if not breakEarly:
        frameCapture = cv2.VideoCapture(settings.camera)
        frameCapture.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        frameCapture.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
    else:
        frameCapture = 0
    
    readySent = False
    while not pc.start and not breakEarly:
        if not readySent and pc.ready:
            pc.loading(f"You are ready! Waiting for other players to be ready...")
            readySent = True
        if cv2.waitKey(1) & 0xFF == ord('q'):
            breakEarly = True
            break
            
    pygame.mixer.music.stop()
    cv2.destroyAllWindows()
    cv2.waitKey(1)
    
    # Start game soundtrack
    pygame.mixer.music.load('SoundEffects/Run.wav')
    pygame.mixer.music.set_volume(0.1)
    pygame.mixer.music.play(-1)
    
    delay = datetime.datetime.now()
    #cv2.startWindowThread()
    if breakEarly: stop[0] = True
        
    while not pc.gameOver and not stop[0] and not breakEarly:
        direction, pc.cameraImage = pc.getDirection(frameCapture)
        #cv2.imshow('frame',pc.cameraImage)
        pc.updateDisplay(event = False)

        if direction and datetime.datetime.now()>delay:
            package = pc.pack(direction)
            transmitter.transmit(comms.direction, package)
            delay = datetime.datetime.now() + datetime.timedelta(seconds = MOTION_DELAY)
            

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
        
    if frameCapture:
        frameCapture.release()
    cv2.destroyAllWindows()
    
    stop[0] = True
    packageReceipt.join()
    if command:
        command.join()
    if isPrimary:
        stopCentral.value = True
        central.join()
    receiver.stop()

def pcPackageReceipt(receiver, pc, stop):
    '''
    Gets packages from central and updates the display information with the new
    event. Does not update the display on screen, which must be handled in the 
    main thread for Mac compatibility.
    '''
    while not pc.gameOver and not stop[0]:
        if len(receiver.packages):
            pc.unpack(receiver.packages.pop(0))
            #pc.updateDisplay()
        # if cv2.waitKey(1) & 0xFF == ord('q'):
        #     break
    #cv2.destroyAllWindows()
        
def pcCommand(transmitter, pc, stop):
    '''
    Separate thread for receiving player input on PC and transmitting it to 
    central.
    '''
    while not pc.gameOver and not stop[0]:
        # Returned command is a topic. Package is sent to provide player ID.
        command = pc.getCommand(stop)
        if command:
            package = pc.pack(command)
            transmitter.transmit(command, package)
    
def centralNodeProcess(stop, playMode, numPlayers, edgeLength, numObstacles, numPowerups):
    '''
    Processes run on the central node only, which will run on a separate thread
    from that particular player's personal processes (pcProcess above). This
    waits for messages from player PCs and Pi's about direction and rotation.
    When a message is received, the PlaySpace and game state are updated, and
    a message is sent to player PCs and Pi's indicating the update.
    '''
    if settings.verbose: print("Starting central process", flush=True)
    
    clientId = f'{datetime.datetime.now().strftime("%H%M%S")}{random.randint(0, 1000)}'
    receiver = comms.Receiver((comms.piConfirmation,
                               comms.pcConfirmation,
                               comms.direction,
                               comms.command,
                               comms.ready,
                               comms.powerUp,
                               comms.rotation,
                               comms.pickup),
                              clientId)
    transmitter = comms.Transmitter()
    receiver.start()
    
    game = g.GamePlay(playMode, numPlayers, edgeLength, numObstacles, numPowerups)

    initialPackage = game.pack()
    
    # Send initial message until all devices confirm receipt
    devicesPending = True
    pcs = [i for i in range(1, game.numPlayers+1)]
    readiesPC = [i for i in range(1, game.numPlayers+1)]
    pcsReceived = []

    if testWithoutPi:
        pis = []
        readiesPi = []
    else:
        pis = [i for i in range(game.numPlayers+1, 2*game.numPlayers+1)]
        readiesPi = [i for i in range(game.numPlayers+1, 2*game.numPlayers+1)]
    pisReceived = []
    
    readies = [i for i in range(1, game.numPlayers+1)]
    
    while devicesPending:
        
        # Transmit the initial playspace info
        transmitter.transmit(comms.initial, initialPackage)
        
        # Check if any packages in the queue
        if len(receiver.packages):
            if settings.verbose: print("Central first loop found", receiver.packages, flush=True)
            # If yes, unpack the first one and use to identify which device is
            # now connected. Confirmation topics are for the first step in the 
            # handshake, providing central with a client ID for the PC or Pi.
            # Central then associates a player ID with that device and sends it
            # out. When the device has received its number successfully, it
            # sends a Ready, completing device registration.
            client, player, pi, pc, ready = game.unpack(receiver.packages.pop(0))
            
            if pi and client not in pisReceived:
                pisReceived.append(client)
                package = game.pack(clientId = client, playerId = pis.pop(0))
                transmitter.transmit(comms.assign, package)
            elif pc and client not in pcsReceived:
                pcsReceived.append(client)
                package = game.pack(clientId = client, playerId = pcs.pop(0))
                transmitter.transmit(comms.assign, package)
            elif ready:
                if player in readiesPC:
                    readiesPC.remove(player)
                elif player in readiesPi:
                    readiesPi.remove(player)
        # Repeat until no devices left to join
        devicesPending = len(pcs)+len(pis)+len(readiesPC)+len(readiesPi)
        if settings.verbose:
            print("Pending pis:", pis, flush=True)
            print("Pending pcs:", pcs, flush=True)
            print("Pending ready pis:", readiesPi, flush=True)
            print("Pending ready pcs:", readiesPC, flush=True)
        time.sleep(1)
    
    game.start = True
    if settings.verbose: print("All player devices connected", flush=True)
    package = game.pack(game.start)
    transmitter.transmit(comms.start, package)
    
    # Then start the game
    while not game.isGameOver() and not stop.value:
        
        # Poll for messages in queue
        if len(receiver.packages):
            
            # On receipt, get the first message and do stuff relevant to the
            # message topic
            print("Central attempting unpack:", receiver.packages, flush=True)
            package = receiver.packages.pop(0)
            topic, message = game.unpack(package)
            #topic, message = game.unpack(receiver.packages.pop(0))
                        
            # Generally this should result in some outbound message
            if message:
                transmitter.transmit(topic, message)
            else:
                if settings.verbose:
                    print("No outbound message to send", flush=True)
        
        # Check if a rotation cooldown is in place
        if game.playSpace.rotationCoolDownTime:
            
            # If yes, check if it's now ended, in which case a message should
            # be sent.
            cooldown, topic, message = game.playSpace.rotationCoolDownRemaining()
            
            if not cooldown and message:
                
                # If it's now ended, send a message to announce it
                transmitter.transmit(topic, message)
    
    message = game.pack(stop.value)
    transmitter.transmit(comms.stop, message)
    receiver.stop()

### Select processes to run for instance
if __name__ == '__main__':
    if 'arm' in platform.machine().lower():
        #piProcess()
        try:
            if settings.verbose: print("will run pi stuff", flush=True)
            piProcess()
        except:
            print("An error occurred with pi processes", flush=True)
            traceback.print_exc() 
    # elif settings.isPrimary:
    #     try:
    #         if settings.verbose: print("will run central stuff", flush=True)
    #         # central = Thread(target=centralNodeProcess)
    #         # player = Thread(target=pcProcess)
            
            
    #         stop = multiprocessing.Value('i', False)
            
    #         # player multiprocess must created first for Mac compatibility with
    #         # OpenCV when displaying stuff later
    #         player = multiprocessing.Process(target=pcProcess, args = (stop, ))
    #         player.daemon = True
    #         central = multiprocessing.Process(target=centralNodeProcess, args = (stop, ))
    #         central.daemon = True
            
    #         player.start()
    #         central.start()
            
    #         player.join()
    #         central.join()
    #     except:
    #         print("An error occurred with primary node processes", flush=True)
    #         traceback.print_exc() 
    else:
        # Only other case is this is the playerPC
        try:
            if settings.verbose: print("will run pc stuff", flush=True)
            pcProcess()
        except:
            print("An error occurred with non primary node processes", flush=True)
            traceback.print_exc() 

