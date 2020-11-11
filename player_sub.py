import random
import re
from paho.mqtt import client as mqtt_client


broker = 'broker.emqx.io'
port = 1883
topic = "ece180d/playerComms"
# generate client ID with pub prefix randomly
client_id = f'python-mqtt-{random.randint(0, 100)}'

import time
import random
from paho.mqtt import client as mqtt_client
import json
broker = 'broker.emqx.io'
port = 1883
topic = "ece180d/team11"
client_id = f'python-mqtt-{random.randint(0, 1000)}'

class Reciever:

    def on_connect(self, client, userdata, flags, rc):
        if rc == 0:
            self.client.subscribe(self.topic)
            print("Connected to Player Communication Channel!")
        else:
            print("Failed to connect, return code %d\n", rc)

    def __on_message(self, client, userdata, msg):
        
        print(f"Received `{msg.payload.decode()}` from `{msg.topic}`")
        message = msg.payload.decode()
       # info = re.findall(r'\d+', message)
       # playerID = int(info[0])
       # Direction = int(info[1])
       # Rotation = int(info[2])
       # print("player ID : ", {playerID}, ", Direction: ",{Direction}, "Rotation :", {Rotation})
        self.received = True

    def __init__(self, topic):
        self.client = mqtt_client.Client(client_id)
        self.client.on_connect = self.on_connect
        self.client.on_message = self.__on_message
        self.client.connect(broker, port)
        self.topic = topic
        self.received = False

        self.client.connect_async('mqtt.eclipse.org')

    def recieve(self, duration):
            if duration == 0:
                self.client.loop_start()
                while True:
                    pass
                self.client.loop_stop()
            if duration == -1:
                self.client.loop_start()
                while self.received == False:
                    pass
                self.client.loop_stop()
            else:
                self.client.loop_start()
                time.sleep(duration)

            



if __name__ == '__main__':
    player1 = Reciever("ece180d/team11")
    player1.recieve(0)


