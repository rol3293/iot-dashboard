import random
from paho.mqtt import client as mqtt_client

selectedUser = (0, 'Default', 27.0, 65.0, 460)
broker = '127.0.0.1'
port = 1883
topic = "rfid"
# generate client ID with pub prefix randomly
client_id = f'rfid-{random.randint(0, 100)}'


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
        id = ""
        for value in bytearray(msg.payload):
            id = id + str(value)
        # print(id)
        global selectedUser
        from dbmanager import getUserThresholds
        newUser = getUserThresholds(int(id))
        if newUser is not None:
            selectedUser = newUser
        # print(selectedUser)
    client.subscribe(topic)
    client.on_message = on_message

def run():
    client = connect_mqtt()
    subscribe(client)
    client.loop_start()
