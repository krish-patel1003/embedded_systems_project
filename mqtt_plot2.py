# python3.6

import random
import json
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from matplotlib.widgets import Button
from paho.mqtt import client as mqtt_client
import time

broker = 'broker.cosmos.deepak.codes'
port = 1883
topics = ["dht11/hum", "dht11/temp"]
pub_topic = "dht11/led"
client_id = f'subscribe-{random.randint(0, 100)}'
led_status = False

temperature_data = []
humidity_data = []

fig_temp, ax_temp = plt.subplots()
fig_hum, ax_hum = plt.subplots()

line_temp, = ax_temp.plot([], [], label='Temperature (°C)')
line_hum, = ax_hum.plot([], [], label='Humidity (%)')

ax_temp.set_xlabel('Time')
ax_temp.set_ylabel('Temperature (°C)')
ax_temp.set_title('Temperature Data')
ax_temp.legend()

ax_hum.set_xlabel('Time')
ax_hum.set_ylabel('Humidity (%)')
ax_hum.set_title('Humidity Data')
ax_hum.legend()

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
    
    # Adjusting temperature y-axis scale
    ax_temp.set_ylim(min(temperature_data) - 2, max(temperature_data) + 2)
    
    # Adjusting humidity y-axis scale
    ax_hum.set_ylim(min(humidity_data) - 5, max(humidity_data) + 5)
    
    ax_temp.relim()
    ax_temp.autoscale_view()

    ax_hum.relim()
    ax_hum.autoscale_view()

def publish(client):

    global led_status
    led_status = not led_status
    msg = f"messages: {led_status}"
    result = client.publish(pub_topic, msg)
    # result: [0, 1]
    status = result[0]
    if status == 0:
        print(f"Send `{msg}` to topic `{pub_topic}`")
    else:
        print(f"Failed to send message to topic {pub_topic}")
    


def on_button_click(event, client):
    print("Button clicked.")
    publish(client)


def add_button(fig, ax, label, callback):
    button_ax = plt.axes([0.85, 0.02, 0.1, 0.05])  # Adjust position and size of the button
    button = Button(button_ax, label)
    button.on_clicked(callback)

def run():
    client = connect_mqtt()
    subscribe(client, topics)
    client.loop_start()

    ani_temp = FuncAnimation(fig_temp, update_plot, interval=1000)  # Update every 1000 milliseconds (1 second)
    
    # Add a button to the temperature plot
    add_button(fig_temp, ax_temp, 'Run Code', on_button_click(client=client))

    plt.show()

    client.loop_stop()

if __name__ == '__main__':
    run()
