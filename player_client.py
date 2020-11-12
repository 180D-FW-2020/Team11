import time
import random
from paho.mqtt import client as mqtt_client
import json
broker = 'broker.emqx.io'
port = 1883
client_id = f'python-mqtt-{random.randint(0, 1000)}'

class Transmitter:

    def on_connect(self, client, userdata, flags, rc):
            if rc == 0:
                print("Connected to Player Communications!")
            else:
                print("Failed to connect, return code %d\n", rc)

  #  def __on_message(self, client, userdata, message):
        #filter data to get only json
        #parse message
   #     self.message.append(json.loads(str(message.payload)[2:-1]))

    def __init__(self, topic):
        self.client = mqtt_client.Client()
        self.topic = topic
        self.message = []

        self.client.on_connect = self.on_connect
        self.client.connect(broker, port)
    #    self.client.on_message = self.__on_message

        self.client.connect_async('mqtt.eclipse.org')


    def update(self, newinfo):
   #     msg = {
    #        "Player ID" : PlayerID,
    #        "Direction" : Direction,
    #        "Rotation" : Rotation, 
    #    }
        msg = newinfo
        self.message["messages"].append(msg)
     #   self.message.append(PlayerID)
      #  self.message.append(Direction)
      #  self.message.append(Rotation)
      
    def send(self):
        self.client.loop_start()
        self.client.publish(self.topic, json.dumps(self.message), qos=1)
        print(json.dumps(self.message))
        self.message = {"messages" :[]}
        self.client.loop_stop()
      #  self.client.disconnect()




if __name__ == '__main__':
    player1 = Transmitter("ece180d/team11")
   # player1.update(1, 1, 1)
  #  player1.send()
    player1.update("it's a good day")
    player1.send()
    player1.update(2)
    player1.send()
    #player1.update(4,0,2)
    #player1.send()
    #player1.update(7,3,2)
    #player1.send()