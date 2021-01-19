# -*- coding: utf-8 -*-
"""
Created on Mon Nov 23 15:55:26 2020

@author: zefyr
"""

from paho.mqtt import client as mqtt_client
import json
import settings
import logging
import logHandling
import datetime

broker = 'broker.emqx.io'
port = 1883
qos_ = 1

### Topics ###
initial = "ece180d/team11/init"
move = "ece180d/team11/move"
tag = "ece180d/team11/tag"
axes = "ece180d/team11/axes"
direction = "ece180d/team11/direc"
ready = "ece180d/team11/ready"
command = "ece180d/team11/command"
start = "ece180d/team11/start"
stop = "ece180d/team11/stop"
rotation = "ece180d/team11/rot"
coolDown = "ece180d/team11/cool"
piConfirmation = "ece180d/team11/piconf"
pcConfirmation = "ece180d/team11/pcconf"


class Transmitter:
    '''
    Used for transmitting data. To use:
        
    1. Create a transmitter using a topic following MQTT standards, ie:
        
        transmitter = Transmitter("someTopic")
        
    2. Send a single message which can be converted to JSON:
        
        transmitter.transmit(someMessage)
    '''
    def __init__(self, logger):        
        self.connected = False
        self.logger = logger
        print("Logger has type:", type(self.logger))
        
        self.client = mqtt_client.Client()
        self.client.enable_logger(logger=None)
        self.client.on_connect = self.on_connect
        self.client.on_publish = self.on_publish
        self.client.connect(broker, port)

    def on_connect(self, client, userdata, flags, rc):
        if rc == 0:
            self.connected = True
            
            log = "Transmitter connected"
            self.logger.info(log)
            if settings.verbose: print(log)
        else:
            log = f"Transmitter failed to connect, return code `{rc}`"
            self.logger.info(log)
            if settings.verbose: print(log)
            
    def on_publish(self, client, userdata, mid):
        pass
            
    def transmit(self, topic, package):
        unsent = 1
        count = 10
        package['ID'] = datetime.datetime.now().strftime("%M%S%f")
        while unsent and count:
            unsent, _ = self.client.publish(topic, json.dumps(package), qos=qos_)
            count = count - 1        
        
        if unsent:
            log = f"Failed to published `{package}` from `{topic}`"
            self.logger.info(log)
            if settings.verbose: print(log)
        else:
            log = f"Published `{package}` from `{topic}`"
            self.logger.info(log)
            if settings.verbose: print(log)
        
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
    def __init__(self, topic, clientId, logger):
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
        self.logger = logger

        self.client = mqtt_client.Client(client_id = clientId, clean_session=True)
        self.client.enable_logger(logger=None)
        self.client.on_connect = self.on_connect        
        self.client.on_message = self.on_message
        self.client.on_subscribe = self.on_subscribe
        self.client.connect(broker, port)
        
        self.packages = []

    def on_connect(self, client, userdata, flags, rc):
        if rc == 0:
            ret = self.client.subscribe(self.topic)
            
            log = f"Receiver connected: `{self.topic}`, client id = `{self.clientId}`, ret = `{ret}`"
            self.logger.info(log)
            if settings.verbose: print(log)
        else:
            log = f"Receiver failed to connect, return code `{rc}`"
            self.logger.info(log)
            if settings.verbose: print(log)
                
    def on_subscribe(self, client, userdata, mid, granted_qos):
        log = f"Subscribed, qos `{granted_qos}`"
        self.logger.info(log)
        if settings.verbose: print(log)

    def on_message(self, client, userdata, msg):
        log = f"Received `{msg.payload.decode()}` from `{msg.topic}`"
        self.logger.info(log)
        if settings.verbose: print(log)
        
        # Store topic and decoded dictionary payload
        self.packages.append((msg.topic, json.loads(msg.payload.decode())))

    def start(self):
        self.client.loop_start()
        
    def stop(self):
        self.client.loop_stop()