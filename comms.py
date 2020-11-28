# -*- coding: utf-8 -*-
"""
Created on Mon Nov 23 15:55:26 2020

@author: zefyr
"""

from paho.mqtt import client as mqtt_client
import json

broker = 'broker.emqx.io'
port = 1883
verbose = True

class Transmitter:
    '''
    Used for transmitting data. To use:
        
    1. Create a transmitter using a topic following MQTT standards, ie:
        
        transmitter = Transmitter("someTopic")
        
    2. Send a single message which can be converted to JSON:
        
        transmitter.transmit(someMessage)
    '''
    def __init__(self, topic):
        self.topic = topic
        self.connected = False
        
        self.client = mqtt_client.Client()
        self.client.on_connect = self.on_connect
        self.client.connect(broker, port)

    def on_connect(self, client, userdata, flags, rc):
        if rc == 0:
            self.connected = True
            if verbose:
                print("Transmitter connected: ", self.topic)
        else:
            print("Failed to connect, return code %d\n", rc)
            
    def transmit(self, package):
        if verbose:
            print("Sending", package, "from", self.topic)
        self.client.publish(self.topic, json.dumps(package), qos=0)
        
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
        self.topic = topic
        self.connected = False
        self.clientId = clientId

        self.client = mqtt_client.Client(client_id = clientId)
        self.client.on_connect = self.on_connect        
        self.client.on_message = self.on_message
        self.client.connect(broker, port)
        
        self.packages = []

    def on_connect(self, client, userdata, flags, rc):
        if rc == 0:
            self.client.subscribe(self.topic, qos = 0)
            if verbose:
                print("Receiver connected: ", self.topic, self.clientId)
        else:
            if verbose:
                print("Failed to connect, return code %d\n", rc)

    def on_message(self, client, userdata, msg):
        if verbose:
            print(f"Received `{msg.payload.decode()}` from `{msg.topic}`")
        self.packages.append(json.loads(msg.payload.decode()))

    def start(self):
        self.client.loop_start()
        
    def stop(self):
        self.client.loop_stop()