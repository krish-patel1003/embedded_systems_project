# python3.6

import random
import json
import matplotlib.pyplot as plt
from paho.mqtt import client as mqtt_client

broker = 'broker.cosmos.deepak.codes'
port = 1883
topics = ["dht11/hum", "dht11/temp"]
# Generate a Client ID with the subscribe prefix.
client_id = f'subscribe-{random.randint(0, 100)}'
# username = 'emqx'
# password = 'public'

temperature_data = []
humidity_data = []


def connect_mqtt() -> mqtt_client:
    def on_connect(client, userdata, flags, rc):
        if rc == 0:
            print("Connected to MQTT Broker!")
        else:
            print("Failed to connect, return code %d\n", rc)

    client = mqtt_client.Client(client_id)
    # client.username_pw_set(username, password)
    client.on_connect = on_connect
    client.connect(broker, port)
    return client


def subscribe(client: mqtt_client, topics: list):
    def on_message(client, userdata, msg):
        print(f"Received `{msg.payload.decode()}` from `{msg.topic}` topic")
        payload = json.loads(msg.payload.decode())
        if msg.topic == "dht11/temp":
            temperature_data.append(payload)
        elif msg.topic == "dht11/hum":
            humidity_data.append(payload)

    for topic in topics:
        client.subscribe(topic)
    client.on_message = on_message


def plot_chart():
    plt.plot(temperature_data, label='Temperature')
    plt.plot(humidity_data, label='Humidity')
    plt.xlabel('Time')
    plt.ylabel('Value')
    plt.title('Temperature and Humidity Data')
    plt.legend()
    plt.show()


def run():
    client = connect_mqtt()
    subscribe(client, topics)
    client.loop_start()

    try:
        while True:
            plot_chart()
    except KeyboardInterrupt:
        print("Stopping...")

    client.loop_stop()


if __name__ == '__main__':
    run()
