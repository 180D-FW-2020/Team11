# -*- coding: utf-8 -*-
"""
Created on Mon Nov  9 12:54:08 2020

@author: zefyr

"""

# Should have better way to set these values than hard coding

import logging
import datetime
import os
from pathlib import Path

if not os.path.exists("logs"): os.makedirs("logs")
p = Path("logs")
file = datetime.datetime.now().strftime("%H%M%S.txt")
logFormat = "%(asctime)s::%(levelname)s::%(name)s::"\
             "%(filename)s::%(lineno)d::%(message)s"
logging.basicConfig(level='DEBUG', filename=p/file, format=logFormat)

import settings
import gamePlay as g
import playerPi
import playerPC
import comms
from threading import Thread
import multiprocessing
import random
import time
import traceback
import numpy as np
import platform
if 'arm' not in platform.machine().lower():
    import pygame
    import cv2

MOTION_DELAY = 500

testWithoutPi = False
            
def piProcess():
    '''
    Processes run on the pi. This detects a rotation on the pi, sends it,
    and then waits for permission to detect a new rotation.
    '''
    log = ("Starting pi processes")
    logging.info(log)
    if settings.verbose: print(log, flush=True)
    
    clientId = f'{datetime.datetime.now().strftime("%H%M%S")}{random.randint(0, 1000)}'
    abort = False
    
    try:
        pi = playerPi.PlayerPi(clientId)
    except:
        log = "An error occurred initializing PlayerPi"
        logging.error(log)
        if settings.verbose: print(log, flush=True)
        traceback.print_exc()
        abort = True    
    
    if not abort:
        try:
            receiver = comms.Receiver((comms.initial,
                                       comms.assign,
                                       comms.coolDown,
                                       comms.axes,
                                       comms.start,
                                       comms.stop),
                                      clientId)
        except:
            log = "An error occurred initializing pi process receiver"
            logging.error(log)
            if settings.verbose: print(log, flush=True)
            traceback.print_exc()
            abort = True
            receiver = 0
    
    if not abort:
        try:
            transmitter = comms.Transmitter()
        except:
            log = "An error occurred initializing pi process transmitter"
            logging.error(log)
            if settings.verbose: print(log, flush=True)
            traceback.print_exc()
            abort = True
    
    if not abort:
        try:
            receiver.start()
        except:
            log = "An error occurred starting pi process receiver"
            logging.error(log)
            if settings.verbose: print(log, flush=True)
            traceback.print_exc()
            abort = True
    
    if not abort:
        #First, get initial load with full playspace info
        while not pi.initialReceived:
            
            # Keep checking for an initial load
            if len(receiver.packages):
                try:
                    # Sets initialReceived to true if initial load
                    pi.unpack(receiver.packages.pop(0))
                except:
                    log = f"An error occurred unpacking a message on the pi queue. Current queue: {receiver.packages}"
                    logging.error(log)
                    if settings.verbose: print(log, flush=True)
                    traceback.print_exc()
    
        # Send handshake to confirm receipt of first load
        try:
            package = pi.pack(pi.clientId)
        except:
            log = "An error occurred packing the clientId"
            logging.error(log)
            if settings.verbose: print(log, flush=True)
            traceback.print_exc()
            abort = True
    
    if not abort:
        try:
            transmitter.transmit(comms.piConfirmation, package)
        except:
            log = "An error occurred transmitting the clientId"
            logging.error(log)
            if settings.verbose: print(log, flush=True)
            traceback.print_exc()
            abort = True
    
    if not abort:
        # Receive playerId. May not correspond to playerId for the same player's PC
        # but that doesn't matter, this is only for ease of reading logs
        while not pi.playerId:
        
            # Keep checking for a message assigning the player number
            if len(receiver.packages):
                try:
                    # Gets true if initial load received, false and deletes message
                    # from queue otherwise
                    pi.unpack(receiver.packages.pop(0))
                except:
                    log = f"An error occurred unpacking a message on the pi queue. Current queue: `{receiver.packages}`"
                    logging.error(log)
                    if settings.verbose: print(log, flush=True)
                    traceback.print_exc()                
            
        try:
            # Send handshake to confirm receipt of playerId
            package = pi.pack(pi.playerId)
        except:
            log = "An error occurred packing the playerId"
            logging.error(log)
            if settings.verbose: print(log, flush=True)
            traceback.print_exc()
            abort = True
        
    if not abort:
        try:
            transmitter.transmit(comms.ready, package)
        except:
            log = "An error occurred transmitting the playerId"
            logging.error(log)
            if settings.verbose: print(log, flush=True)
            traceback.print_exc()
            abort = True
    
    stop = [abort]
    # Send transmitter to separate thread to handle getting player input and
    # sending to central, while current process gets display updates
    if not abort:
        transmit = Thread(target=piTransmit, args = (transmitter, pi, stop,))
        transmit.daemon = True
        try:
            transmit.start()
        except:
            log = "An error occurred starting the piTransmit thread"
            logging.error(log)
            if settings.verbose: print(log, flush=True)
            traceback.print_exc()
            abort = True
    
    # Gameplay receiver loop checks for new packages in the queue. Packages
    # set the rotation cooldown or end the game.
    #while not pi.gameOver:
    if not abort:
        while not pi.gameOver:
            if len(receiver.packages):
                try:
                    pi.unpack(receiver.packages.pop(0))
                except:
                        log = f"An error occurred unpacking a message on the pi queue. Current queue: `{receiver.packages}`"
                        logging.error(log)
                        if settings.verbose: print(log, flush=True)
                        traceback.print_exc()
    if abort:
        log = "pi processes aborted due to unresolvable errors"
    else:
        log = "pi game over"
    logging.info(log)
    if settings.verbose: print(log, flush=True)

    stop[0] = True
    
    try:
        transmit.join()
    except:
        log = "Unable to join transmit thread. Possible it was not instantiated, if game aborted early."
        logging.error(log)
        if settings.verbose: print(log, flush=True)
        traceback.print_exc()
    
    if receiver:
        receiver.stop()

def piTransmit(transmitter, pi, stop):
    '''
    Separate thread for receiving player input on Pi and transmitting it to 
    central.
    '''
    # Hold until receive start message
    while not pi.start and not pi.gameOver:
        pass
    
    delay = datetime.datetime.now()
    # Get rotation information and transmit it
    while not pi.gameOver:
        
        if datetime.datetime.now()>delay:
            try:
                rotation = pi.getRotation(stop)
            except:
                log = "An error occurred getting a rotation"
                logging.error(log)
                if settings.verbose: print(log, flush=True)
                traceback.print_exc()
                rotation = 0
                
            if rotation:
                try:
                    package = pi.pack(rotation)
                except:
                    log = "An error occurred packing a rotation"
                    logging.error(log)
                    if settings.verbose: print(log, flush=True)
                    traceback.print_exc()
                    package = 0
                
                if package:
                    try:
                        transmitter.transmit(comms.rotation, package)
                        delay = datetime.datetime.now() + datetime.timedelta(milliseconds = MOTION_DELAY)
                    except:
                        log = "An error occurred transmitting a rotation"
                        logging.error(log)
                        if settings.verbose: print(log, flush=True)
                        traceback.print_exc()

def pcProcess():
    '''
    Processes run on the pc. This detects a direction with the camera, sends it,
    and then waits for permission to detect a new direction. It also runs a
    display update on a separate thread which can access the local pc class, so
    that the display just updates when display information is updated from a
    received message.
    '''   
    log = ("Starting PC processes")
    logging.info(log)
    if settings.verbose: print(log, flush=True)
    
    breakEarly = False
    abort = False
    abortPygame = False
    
    try:
        # Initialize the PyGame
        pygame.init()
    except:
        log = "An error occurred initializing Pygame"
        logging.error(log, exc_info = True)
        if settings.verbose:
            print(log, flush=True)
            traceback.print_exc()
        abortPygame = True
    
    if not abortPygame:
        try:
            pygame.mixer.init()
        except:
            log = "An error occurred initializing Pygame mixer"
            logging.error(log, exc_info = True)
            if settings.verbose:
                print(log, flush=True)
                traceback.print_exc()
            abortPygame = True

    if not abortPygame:
        try:
            # Start settings soundtrack
            pygame.mixer.music.load('SoundEffects/ready_two_run.wav')
            pygame.mixer.music.set_volume(0.1)
        except:
            log = "An error occurred loading settings music"
            logging.error(log, exc_info = True)
            if settings.verbose:
                print(log, flush=True)
                traceback.print_exc()
            abortPygame = True
    
    if not abortPygame:
        try:
            pygame.mixer.music.play(-1)
        except:
            log = "An error occurred starting settings music"
            logging.error(log, exc_info = True)
            if settings.verbose:
                print(log, flush=True)
                traceback.print_exc()
            abortPygame = True
    
    clientId = f'{datetime.datetime.now().strftime("%H%M%S")}{random.randint(0, 1000)}'
    
    try:
        pc = playerPC.PlayerPC(clientId)
    except:
        log = "An error has occurred initializing PlayerPC"
        logging.error(log, exc_info = True)
        if settings.verbose:
            print(log, flush=True)
            traceback.print_exc()
        abort = True
    
    stop = [0]
    

    if not abort:
        try:
            receiver = comms.Receiver((comms.initial,
                                       comms.assign,
                                       comms.move,
                                       comms.tag,
                                       comms.launch,
                                       comms.start,
                                       comms.stop,
                                       comms.axes,
                                       comms.coolDown,
                                       comms.pickup,
                                       comms.activePower,
                                       comms.timerOver,
                                       comms.dropped),
                                      clientId)
        except:
            log = "An error occurred initializing PC process reciever"
            logging.error(log, exc_info = True)
            if settings.verbose:
                print(log, flush=True)
                traceback.print_exc()
            abort = True
            receiver = 0

    
    if not abort:
        try:
            transmitter = comms.Transmitter()
        except:
            log = "An error occurred initializing PC process transmitter"
            logging.error(log, exc_info = True)
            if settings.verbose:
                print(log, flush=True)
                traceback.print_exc()
            abort = True
    
    if not abort:
        try:
            receiver.start()
        except:
            log = "An error occurred starting the PC process receiver"
            logging.error(log, exc_info = True)
            if settings.verbose:
                print(log, flush=True)
                traceback.print_exc()
            abort = True
    
    if not abort and not pc.gameOver:
        try:
            # Send receiver to separate thread
            packageReceipt = Thread(target=pcPackageReceipt, args = (receiver, pc, stop,))
            packageReceipt.daemon = True
        except:
            log = "An error occurred sending receiver to separate thread"
            logging.error(log, exc_info = True)
            if settings.verbose:
                print(log, flush=True)
                traceback.print_exc()
            abort = True
        
    if not abort and not pc.gameOver:
        try:
            packageReceipt.start()
        except:
            log = "An error occurred starting the package receipt"
            logging.error(log, exc_info = True)
            if settings.verbose:
                print(log, flush=True)
                traceback.print_exc()
            abort = True
    
    if not abort and not pc.gameOver:
        try:
            # Get settings. If not isPrimary, other returned variables are all 0. If
            # primary, spawn primary player stuff
            isPrimary, playMode, numPlayers, edgeLength, numObstacles, numPowerups = pc.settings()
        except:
            log = "An error occurred getting settings"
            logging.error(log, exc_info = True)
            if settings.verbose:
                print(log, flush=True)
                traceback.print_exc()
            abort = True
    
    if not abort and isPrimary and not pc.gameOver:
        try:
            stopCentral = multiprocessing.Value('i', False)
        except:
            log = "An error occurred creating stop central flag"
            logging.error(log, exc_info = True)
            if settings.verbose:
                print(log, flush=True)
                traceback.print_exc()
            abort = True
            
        if not abort and not pc.gameOver:
            try:
                central = multiprocessing.Process(target=centralNodeProcess, args = (stopCentral, playMode, numPlayers, edgeLength, numObstacles, numPowerups, ))
                central.daemon = True
            except:
                log = "An error occurred creating central multiprocess"
                logging.error(log, exc_info = True)
                if settings.verbose:
                    print(log, flush=True)
                    traceback.print_exc()
                abort = True
                
        if not abort and not pc.gameOver:
            try:
                central.start()
            except:
                log = "An error occurred starting central multiprocess"
                logging.error(log, exc_info = True)
                if settings.verbose:
                    print(log, flush=True)
                    traceback.print_exc()
                abort = True
    
    if not abort and not pc.gameOver:
        try:
            pc.loading("Waiting for initial game state...")
        except:
            log = "An error occurred generating loading screen"
            logging.error(log, exc_info = True)
            if settings.verbose:
                print(log, flush=True)
                traceback.print_exc()
            abort = True
    
    if not abort and not pc.gameOver:
        #First, get initial load with full playspace info
        while not pc.initialReceived and not pc.gameOver:
            try:
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    abort = True
                    break
            except:
                log = "An error occurred evaluating display close out"
                logging.error(log, exc_info = True)
                if settings.verbose:
                    print(log, flush=True)
                    traceback.print_exc()
    
    if not abort and not pc.gameOver:
        try:
            pc.loading("Initial game state received. Waiting for player ID assignment...")
        except:
            log = "An error occurred updating loading screen"
            logging.error(log, exc_info = True)
            if settings.verbose:
                print(log, flush=True)
                traceback.print_exc()
        
        try:
            # Send handshake to confirm receipt of first load
            package = pc.pack(pc.clientId)
        except:
            log = "An error occurred packaging clientID"
            logging.error(log, exc_info = True)
            if settings.verbose:
                print(log, flush=True)
                traceback.print_exc()
            abort = True
    
    if not abort and not pc.gameOver:
        try:
            transmitter.transmit(comms.pcConfirmation, package)
        except:
            log = "An error occurred transmitting clientID"
            logging.error(log, exc_info = True)
            if settings.verbose:
                print(log, flush=True)
                traceback.print_exc()
            abort = True
            
    if not abort and not pc.gameOver:
        # Check for assignment of a player ID
        while not pc.playerId and not pc.gameOver:
            try:
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    abort = True
                    break
            except:
                log = "An error occurred evaluating display close out"
                logging.error(log, exc_info = True)
                if settings.verbose:
                    print(log, flush=True)
                    traceback.print_exc()
    
    if not abort and not pc.gameOver:
        try:
            pc.loading(f"You are player {pc.playerId}. Say ""ready"" when you're ready to join...")
        except:
            log = "An error occurred displaying ready instructions"
            logging.error(log, exc_info = True)
            if settings.verbose:
                print(log, flush=True)
                traceback.print_exc()
            abort = True
        
    if not abort and not pc.gameOver:
        try:
            # Send command thread to separate loop
            command = Thread(target=pcCommand, args = (transmitter, pc, stop,))
            command.daemon = True
        except:
            log = "An error occurred creating command thread"
            logging.error(log, exc_info = True)
            if settings.verbose:
                print(log, flush=True)
                traceback.print_exc()
            abort = True
    
    if not abort and not pc.gameOver:
        try:
            command.start()
        except:
            log = "An error occurred "
            logging.error(log, exc_info = True)
            if settings.verbose:
                print(log, flush=True)
                traceback.print_exc()
            abort = True
    
    readySent = False
    while not abort and not pc.launch and not pc.gameOver:
        if not readySent and pc.ready:
            try:
                pc.loading("You are ready! Waiting for other players to be ready...")
                readySent = True
            except:
                log = "An error occurred displaying ready instructions"
                logging.error(log, exc_info = True)
                if settings.verbose:
                    print(log, flush=True)
                    traceback.print_exc()
                abort = True
        
        if not abort:
            try:
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    abort = True
                    break
            except:
                log = "An error occurred evaluating display close out"
                logging.error(log, exc_info = True)
                if settings.verbose:
                    print(log, flush=True)
                    traceback.print_exc()

    try:
        pygame.mixer.music.stop()
    except:
        log = "An error occurred stopping settings music"
        logging.error(log, exc_info = True)
        if settings.verbose:
            print(log, flush=True)
            traceback.print_exc()
        abortPygame = True
    
    try:
        cv2.destroyAllWindows()
        cv2.waitKey(1)
    except:
        log = "An error occurred closing settings display"
        logging.error(log, exc_info = True)
        if settings.verbose:
            print(log, flush=True)
            traceback.print_exc()
        abort = True
    
    if not abort and not pc.gameOver:
        try:
            frameCapture = cv2.VideoCapture(settings.camera)
            frameCapture.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
            frameCapture.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        except:
            log = "An error occurred creating video capture window"
            logging.error(log, exc_info = True)
            if settings.verbose:
                print(log, flush=True)
                traceback.print_exc()
            abort = True
            
    # Start game soundtrack
    if not abortPygame and not abort and not pc.gameOver:
        try:
            pygame.mixer.music.load('SoundEffects/Run.wav')
            pygame.mixer.music.set_volume(0.1)
        except:
            log = "An error occurred loading gameplay music"
            logging.error(log, exc_info = True)
            if settings.verbose:
                print(log, flush=True)
                traceback.print_exc()
            abortPygame = True
        
    if not abortPygame and not abort and not pc.gameOver:
        try:
            pygame.mixer.music.play(-1)
        except:
            log = "An error occurred starting gameplay music"
            logging.error(log, exc_info = True)
            if settings.verbose:
                print(log, flush=True)
                traceback.print_exc()
            abortPygame = True
    
    if not abort and not pc.gameOver:
        try:
            blink = Thread(target=pcBlink, args = (pc, stop,))
            blink.daemon = True
        except:
            log = "An error occurred creating blink thread"
            logging.error(log, exc_info = True)
            if settings.verbose:
                print(log, flush=True)
                traceback.print_exc()
            # If blink thread doesn't work for some reason but display stuff
            # has worked so far, no need to abort -- this should just mean the
            # player won't blink at start of game
    
    if not abort and not pc.gameOver:
        try:
            blink.start()
        except:
            log = "An error occurred starting blink thread"
            logging.error(log, exc_info = True)
            if settings.verbose:
                print(log, flush=True)
                traceback.print_exc()
    
    # launch display and show feed while blink thread blinks players before
    # letting people start
    while not pc.start and not abort and not pc.gameOver:
        try:
            direction = pc.getDirection(frameCapture)
        except:
            log = "An error occurred getting camera feed"
            logging.error(log, exc_info = True)
            if settings.verbose:
                print(log, flush=True)
                traceback.print_exc()
        
        try:
            pc.updateDisplay()
        except:
            log = "An error occurred updating display"
            logging.error(log, exc_info = True)
            if settings.verbose:
                print(log, flush=True)
                traceback.print_exc()
        
        try:
            if cv2.waitKey(1) & 0xFF == ord('q'):
                abort = True
                break
        except:
            log = "An error occurred evaluating display close out"
            logging.error(log, exc_info = True)
            if settings.verbose:
                print(log, flush=True)
                traceback.print_exc()
    
    try:
        blink.join()
    except:
        log = "An error occurred joining blink thread"
        logging.error(log, exc_info = True)
        if settings.verbose:
            print(log, flush=True)
            traceback.print_exc()
    
    delay = datetime.datetime.now()
    #cv2.startWindowThread()
    if abort: stop[0] = True
    
    while not pc.gameOver and not stop[0]:
        try:
            direction = pc.getDirection(frameCapture)
        except:
            log = "An error occurred getting camera feed"
            logging.error(log, exc_info = True)
            if settings.verbose:
                print(log, flush=True)
                traceback.print_exc()
        
        try:
            pc.updateDisplay()
        except:
            log = "An error occurred updating display"
            logging.error(log, exc_info = True)
            if settings.verbose:
                print(log, flush=True)
                traceback.print_exc()

        if direction and datetime.datetime.now()>delay:
            try:
                package = pc.pack(direction)
            except:
                log = "An error occurred packaging the direction"
                logging.error(log, exc_info = True)
                if settings.verbose:
                    print(log, flush=True)
                    traceback.print_exc()
                    package = 0
            
            if package:
                try:
                    transmitter.transmit(comms.direction, package)
                    delay = datetime.datetime.now() + datetime.timedelta(milliseconds = MOTION_DELAY)
                except:
                    log = "An error occurred transmitting the direction"
                    logging.error(log, exc_info = True)
                    if settings.verbose:
                        print(log, flush=True)
                        traceback.print_exc()
        try:
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
        except:
            log = "An error occurred evaluating display close out"
            logging.error(log, exc_info = True)
            if settings.verbose:
                print(log, flush=True)
                traceback.print_exc()
        
    try:
        pygame.mixer.music.stop()
    except:
        log = "An error occurred ending gameplay music"
        logging.error(log, exc_info = True)
        if settings.verbose:
            print(log, flush=True)
            traceback.print_exc()
        abortPygame = True
        
    try:
        frameCapture.release()
    except:
        log = "An error occurred releasing the camera feed"
        logging.error(log, exc_info = True)
        if settings.verbose:
            print(log, flush=True)
            traceback.print_exc()
    
    try:
        cv2.destroyAllWindows()
    except:
        log = "An error occurred closing the display"
        logging.error(log, exc_info = True)
        if settings.verbose:
            print(log, flush=True)
            traceback.print_exc()
    
    stop[0] = True
    
    try:
        command.join()
    except:
        log = "An error occurred joining the command thread"
        logging.error(log, exc_info = True)
        if settings.verbose:
            print(log, flush=True)
            traceback.print_exc()
    
    if isPrimary:
        stopCentral.value = True
        try:
            central.join()
        except:
            log = "An error occurred joining the central multiprocess"
            logging.error(log, exc_info = True)
            if settings.verbose:
                print(log, flush=True)
                traceback.print_exc()
    
    try:
        packageReceipt.join()
    except:
        log = "An error occurred joining the package receipt thread"
        logging.error(log, exc_info = True)
        if settings.verbose:
            print(log, flush=True)
            traceback.print_exc()
    
    try:
        receiver.stop()
    except:
        log = "An error occurred stopping the receiver"
        logging.error(log, exc_info = True)
        if settings.verbose:
            print(log, flush=True)
            traceback.print_exc()

def pcBlink(pc, stop):
    '''
    Blinks player on game startup
    '''
    on = True
    while not pc.start and not stop[0]:
        pc.blinkPlayer(on)
        on = not on
        time.sleep(0.3)
        
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
                               comms.drop,
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
    
    while devicesPending and not stop.value:
        
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
    
    if not stop.value:
        game.start = True
        if settings.verbose: print("All player devices connected", flush=True)
        package = game.pack(game.start)
        transmitter.transmit(comms.launch, package)
        
        # Let players blink on screen a moment before playing
        time.sleep(5)
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

        #check if there is a freeze timer in place
        if game.playSpace.freezeTimer:
            
            # If yes, check if it's now ended, in which case a message should
            # be sent.
            freeze, topic, message = game.playSpace.powerUpTimerRemaining(0)
            
            if not freeze and message:
                
                # If it's now ended, send a message to announce it
        #        self.game.playSpace.players[message['playerId']-1]['activePowerUp'] = 0
                transmitter.transmit(topic, message)
        
        for i, player in enumerate(game.playSpace.players):
            if player['powerUpTimer']:
                speed, topic, message = game.playSpace.powerUpTimerRemaining(player['playerId'])
            
                if not speed and message:
                    
                    # If it's now ended, send a message to announce it
              #      self.game.playSpace.players[message['playerId']-1]['activePowerUp'] = 0
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

