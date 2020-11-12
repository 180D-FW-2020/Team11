import time
import random
import re
import json
from paho.mqtt import client as mqtt_client

broker = 'broker.emqx.io'
port = 1883
topic = "ece180d/playerComms"
# generate client ID with pub prefix randomly
client_id = f'python-mqtt-{random.randint(0, 1000)}'
verbose = False

class Receiver:

    def on_connect(self, client, userdata, flags, rc):
        if rc == 0:
            self.client.subscribe(self.topic)
            if verbose:
                print("Connected to Player Communication Channel!")
        else:
            if verbose:
                print("Failed to connect, return code %d\n", rc)

    def __on_message(self, client, userdata, msg):
        if verbose:
            print(f"Received `{msg.payload.decode()}` from `{msg.topic}`")
        self.message = json.loads(msg.payload.decode())
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
        self.message = ''

    def receive(self, duration):
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
                return self.message
            else:
                self.client.loop_start()
                time.sleep(duration)

            



if __name__ == '__main__':
    player1 = Receiver("ece180d/team11/nodeToPrimary")
    #player1.recieve(-1)


