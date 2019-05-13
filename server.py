#!/usr/bin/env python3

import os
import logging
import time
import math

from random import randint
from json import dumps

import eventlet
from flask import Flask, copy_current_request_context, request, jsonify
from flask_socketio import SocketIO, emit, send
from flask_mqtt import Mqtt

from planning import Floorplan
from planning.position import position_handler

eventlet.monkey_patch()

app = Flask(__name__, static_folder='map-server/static')

app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app)

app.config['MQTT_BROKER_URL'] = '192.168.6.235'
app.config['MQTT_BROKER_PORT'] = 1883
app.config['MQTT_REFRESH_TIME'] = 1.0
mqtt = Mqtt(app)

floorplan = Floorplan("CAD Files/li27_example.dxf")

clients = []
#t1 = Thread(target=emitter_thread, args=(socketio,))

@app.route('/')
def index():
    return app.send_static_file('index.html')

@app.route('/floorplan')
def get_floorplan():
    data = list(floorplan.get_obstacles())

    return jsonify(data)

@socketio.on('connect', namespace='/position')
def handle_connect():
    clients.append(request.sid)
    print("New client connected")

@socketio.on('disconnect', namespace='/position')
def handle_disconnect():
    clients.remove(request.sid)
    print('Client disconnected')

@mqtt.on_message()
def handle_mqtt_message(client, userdata, message):
    if message.topic == 'position':
        result = position_handler(message.payload)

        if result:
            print(result)
            socketio.emit('json', result, namespace='/position')

if __name__ == '__main__':
    #t1.start()
    mqtt.subscribe('position')

    socketio.run(app, host='0.0.0.0', log_output=True)
