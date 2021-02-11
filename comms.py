# -*- coding: utf-8 -*-
"""
Created on Mon Nov 23 15:55:26 2020

@author: zefyr
"""

from paho.mqtt import client as mqtt_client
import json
import settings
import datetime

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
start = settings.uniqueComms + "ece180d/team11/start"
stop = settings.uniqueComms + "ece180d/team11/stop"
rotation = settings.uniqueComms + "ece180d/team11/rot"
coolDown = settings.uniqueComms + "ece180d/team11/cool"
piConfirmation = settings.uniqueComms + "ece180d/team11/piconf"
pcConfirmation = settings.uniqueComms + "ece180d/team11/pcconf"
pickup = settings.uniqueComms + "ece180d/team11/pickup"
activePower = settings.uniqueComms + "ece180d/team11/activePower"
timerOver = settings.uniqueComms + "ece180d/team11/timer"


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
        self.client.connect(broker, port)

    def on_connect(self, client, userdata, flags, rc):
        if rc == 0:
            self.connected = True
            if settings.verbose:
                print("Transmitter connected", flush=True)
        else:
            print("Failed to connect, return code %d\n", rc, flush=True)
            
    def transmit(self, topic, package):
        unsent = 1
        count = 5
        package['MessageId'] = datetime.datetime.now().strftime("%M%S%f")
        while unsent and count:
            unsent, _ = self.client.publish(topic, json.dumps(package), qos=qos_)
            count = count - 1
        
        if unsent:
            log = f"Failed to published `{package}` from `{topic}`"
            #self.logger.info(log)
            if settings.verbose: print(log)
        else:
            log = f"Published `{package}` from `{topic}`"
            #self.logger.info(log)
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
        
        self.packages = []

    def on_connect(self, client, userdata, flags, rc):
        if rc == 0:
            self.client.subscribe(self.topic)
            if settings.verbose:
                print("Receiver connected: ", self.topic, self.clientId, flush=True)
        else:
            if settings.verbose:
                print("Failed to connect, return code %d\n", rc, flush=True)
                
    def on_subscribe(self, client, userdata, mid, granted_qos):
        if settings.verbose:
            print("Subscribed, mid = ", mid, flush=True)

    def on_message(self, client, userdata, msg):
        if settings.verbose:
            print(f"Received `{msg.payload.decode()}` from `{msg.topic}`", flush=True)
        
        # Store topic and decoded dictionary payload
        self.packages.append((msg.topic, json.loads(msg.payload.decode())))

    def start(self):
        self.client.loop_start()
        
    def stop(self):
        self.client.loop_stop()