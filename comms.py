# -*- coding: utf-8 -*-
"""
Created on Mon Nov 23 15:55:26 2020

@author: zefyr
"""

import logging
from paho.mqtt import client as mqtt_client
import json
import settings
import datetime
import traceback

broker = 'broker.emqx.io'
port = 1883
qos_ = 0

### Topics ###
initial = settings.uniqueComms + "ece180d/team11/init"
assign = settings.uniqueComms + "ece180d/team11/assign"
move = settings.uniqueComms + "ece180d/team11/move"
tag = settings.uniqueComms + "ece180d/team11/tag"
axes = settings.uniqueComms + "ece180d/team11/axes"
direction = settings.uniqueComms + "ece180d/team11/direc"
ready = settings.uniqueComms + "ece180d/team11/ready"
command = settings.uniqueComms + "ece180d/team11/command"
powerUp = settings.uniqueComms + "ece180d/team11/powerUp"
power = settings.uniqueComms + "ece180d/team11/power"
launch = settings.uniqueComms + "ece180d/team11/launch"
start = settings.uniqueComms + "ece180d/team11/start"
stop = settings.uniqueComms + "ece180d/team11/stop"
rotation = settings.uniqueComms + "ece180d/team11/rot"
coolDown = settings.uniqueComms + "ece180d/team11/cool"
piConfirmation = settings.uniqueComms + "ece180d/team11/piconf"
pcConfirmation = settings.uniqueComms + "ece180d/team11/pcconf"
pickup = settings.uniqueComms + "ece180d/team11/pickup"
activePower = settings.uniqueComms + "ece180d/team11/activePower"
timerOver = settings.uniqueComms + "ece180d/team11/timer"
drop = settings.uniqueComms + "ece180d/team11/drop"
dropped = settings.uniqueComms + "ece180d/team11/dropped"


class Transmitter:
    '''
    Used for transmitting data. To use:
        
    1. Create a transmitter using a topic following MQTT standards, ie:
        
        transmitter = Transmitter("someTopic")
        
    2. Send a single message which can be converted to JSON:
        
        transmitter.transmit(someMessage)
    '''
    def __init__(self):
        #self.topic = topic
        self.connected = False
        
        self.client = mqtt_client.Client()
        self.client.on_connect = self.on_connect
        self.client.connect(broker, port, keepalive=1800)

    def on_connect(self, client, userdata, flags, rc):
        if rc == 0:
            self.connected = True
            
            log = "Transmitter connected"
            logging.info(log)
            if settings.verbose: print(log, flush=True)
        else:
            print("Failed to connect, return code %d\n", rc, flush=True)
            
    def transmit(self, topic, package):
        # Add message ID for troubleshooting
        package['MessageId'] = datetime.datetime.now().strftime("%M%S%f")
        
        # Retry up to 5 times
        unsent = 1
        count = 5
        while unsent and count:
            unsent, _ = self.client.publish(topic, json.dumps(package), qos=qos_)
            count = count - 1
        
        if unsent:
            log = f"Failed to published `{package}` from `{topic}`"
            logging.info(log)
            if settings.verbose: print(log, flush=True)
        else:
            log = f"Published `{package}` from `{topic}`"
            logging.info(log)
            if settings.verbose: print(log, flush=True)
        
class Receiver:
    '''
    Used for receiving data. To use:
    1. Create a receiver using a topic following MQTT standards, ie:
        
        receiver = Receiver("someTopic")
        
    2. Start the receiver. This runs a thread in the background.
    
        receiver.start()
        
    3. Check for receipt and obtain incoming messages converted from JSON from
        the queue, ie:
            
        while True:
            if len(receiver.packages):
                newMessage = receiver.packages.pop(0)
    
    4. When done receiving stuff, end the background thread:
        
        receiver.stop()
    '''
    def __init__(self, topic, clientId):        
        # Allow for multiple topic subscriptions
        if type(topic) == tuple:
            topics = []
            for t in topic:
                topics.append((t, qos_))
            self.topic = topics
        else:
            self.topic = (topic, qos_)
        
        self.connected = False
        self.clientId = clientId

        self.client = mqtt_client.Client(client_id = clientId)
        self.client.on_connect = self.on_connect        
        self.client.on_message = self.on_message
        self.client.on_subscribe = self.on_subscribe
        self.client.connect(broker, port)
        
        # Queue for package handling. Received packages are added to queue by
        # MQTT loop activities and then removed by game loop
        self.packages = []

    def on_connect(self, client, userdata, flags, rc):
        if rc == 0:
            self.client.subscribe(self.topic)
            log = f"Receiver connected: `{self.topic}`"
            logging.info(log)
            if settings.verbose: print(log, flush=True)
        else:
            log = f"Failed to connect, return code `{rc}`"
            logging.info(log)
            if settings.verbose: print(log, flush=True)
                
    def on_subscribe(self, client, userdata, mid, granted_qos):
        log = "Subscribed"
        logging.info(log)
        if settings.verbose: print(log, flush=True)

    def on_message(self, client, userdata, msg):
        log = f"Received `{msg.payload.decode()}` from `{msg.topic}`"
        logging.info(log)
        if settings.verbose: print(log, flush=True)
        
        # Store topic and decoded dictionary payload
        try:
            self.packages.append((msg.topic, json.loads(msg.payload.decode())))
        except:
            log = f"Failed to add message to queue: `{msg.payload.decode()}` from `{msg.topic}`"
            logging.info(log)
            if settings.verbose: print(log, flush=True)
            traceback.print_exc()

    def start(self):
        self.client.loop_start()
        
    def stop(self):
        self.client.loop_stop()