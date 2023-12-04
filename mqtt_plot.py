# python3.6

import random
import json
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
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

fig, ax = plt.subplots()
line_temp, = ax.plot([], [], label='Temperature')
line_hum, = ax.plot([], [], label='Humidity')
ax.set_xlabel('Time')
ax.set_ylabel('Value')
ax.set_title('Temperature and Humidity Data')
ax.legend()

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
        payload = json.loads(msg.payload.decode())
        if msg.topic == "dht11/temp":
            temperature_data.append(payload)
        elif msg.topic == "dht11/hum":
            humidity_data.append(payload)

    for topic in topics:
        client.subscribe(topic)
    client.on_message = on_message

def update_plot(frame):
    line_temp.set_data(range(len(temperature_data)), temperature_data)
    line_hum.set_data(range(len(humidity_data)), humidity_data)
    ax.relim()
    ax.autoscale_view()

def run():
    client = connect_mqtt()
    subscribe(client, topics)
    client.loop_start()

    ani = FuncAnimation(fig, update_plot, interval=1000)  # Update every 1000 milliseconds (1 second)

    plt.show()

    client.loop_stop()

if __name__ == '__main__':
    run()
