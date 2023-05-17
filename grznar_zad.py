import json
import tkinter as tk
import tkinter.font as tkfont
import paho.mqtt.client as mqtt
import threading
import serial
import threading

broker_address = "demo.thingsboard.io" 
access_token = "tCo5ZrWi1XnImHpej2AP"
broker_port = 1883

serial_com = 'COM7'
serial_boudrate = 115200

ser = serial.Serial(serial_com, serial_boudrate)

def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("Connected to MQTT broker")
    else:
        print(f"Connection failed with error code {rc}")

def on_publish(client, userdata, mid):
    print("Data published successfully")

def read():
    while True:
        if ser.in_waiting > 0:
            data = ser.readline().decode('utf-8').rstrip()
            try:
                json_data = json.loads(data)
                publish_data(json_data)
                update_labels(json_data)
            except json.JSONDecodeError:
                print("Data: ", data)
                pass

def publish_data(data):
    client.publish(topic, json.dumps(data, separators=(',', ':')))

def update_labels(data):
    aX = data.get('aX')
    aY = data.get('aY')
    aZ = data.get('aZ')
    gX = data.get('gX')
    gY = data.get('gY')
    gZ = data.get('gZ')
    temp = data.get('temp')
    angX = data.get('angX')
    angY = data.get('AngY')

    val_temp.config(text=f'{temp} °C')
    val_g.config(text=f'aX: {aX}, aY: {aY}, aZ: {aZ}')
    val_a.config(text=f'gX: {gX}, gY: {gY}, gZ: {gZ}')
    val_ang.config(text=f'angX: {angX}°, angY: {angY}°')

def send_command(command):
    ser.write(command.encode())

def start_stop():
    global start
    if start % 2 == 0:
        send_command("Start")
        start_button.config(text="Stop")
    else:
        send_command("Stop")
        start_button.config(text="Start")
    start += 1

root = tk.Tk()
root.title("Gyroscop zadanie Matej Grznar")
root.geometry("520x250")
root.resizable(False, False)

start = 0
start_button = tk.Button(root, text="Start", command=start_stop)
start_button.grid(row=0, column=0, columnspan=2, pady=10, padx=10, sticky="nesw")

display_font = tkfont.Font(family="segmental", size=20, weight="normal")

val_g = tk.Label(root, text='gX: --, gY: --, gZ: --', font=display_font)
val_g.grid(row=1, column=0, columnspan=2, pady=10)
val_a = tk.Label(root, text='aX: --, aY: --, aZ: --', font=display_font)
val_a.grid(row=2, column=0, columnspan=2, pady=10)
val_temp = tk.Label(root, text='-- °C', font=display_font)
val_temp.grid(row=3, column=0, columnspan=2)
val_ang = tk.Label(root, text='angX: --°, angY: --°', font=display_font)
val_ang.grid(row=4, column=0, columnspan=2, pady=10)

root.columnconfigure(0, weight=1)
root.columnconfigure(1, weight=1)

client = mqtt.Client()
client.username_pw_set(access_token)
client.on_connect = on_connect
client.on_publish = on_publish
client.connect(broker_address, broker_port)
topic = "v1/devices/me/telemetry"

t = threading.Thread(target=read)
t.daemon = True
t.start()
root.mainloop()