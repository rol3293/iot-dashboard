from paho.mqtt import client as mqtt_client
from helper import setLED
import random

light_sensivity = 1000
broker = '127.0.0.1'
port = 1883
topic = "light"
# generate client ID with pub prefix randomly
client_id = f'light-{random.randint(0, 100)}'

setLED(False)


def connect_mqtt() -> mqtt_client:
    def on_connect(client, userdata, flags, rc):
        if rc == 0:
            print("Connected to MQTT Broker!")
        else:
            print("Failed to connect, return code %d\n", rc)

    client = mqtt_client.Client(client_id)
    client.on_connect = on_connect
    client.connect(broker, port)
    return client


def subscribe(client: mqtt_client):
    def on_message(client, userdata, msg):
        global light_sensivity
        light_sensivity = float(msg.payload.decode())
    client.subscribe(topic)
    client.on_message = on_message

def run():
    client = connect_mqtt()
    subscribe(client)
    client.loop_start()