#!/usr/bin/env python3

import os
import logging
import time
import math
import argparse

from random import randint
from json import dumps, loads

import eventlet
from flask import Flask, copy_current_request_context, request, jsonify
from flask.logging import default_handler
from flask_socketio import SocketIO, emit, send
from flask_mqtt import Mqtt

from planning import Floorplan
from planning.position import position_handler, checkpoint_handler

from time import sleep

logger = logging.getLogger('server')
logger.setLevel(logging.DEBUG)
logger.addHandler(default_handler)

parser = argparse.ArgumentParser(description='Robot position simulator')
parser.add_argument('hostname', metavar='HOST', help='Hostname of the MQTT broker')
args = parser.parse_args()

eventlet.monkey_patch()

app = Flask(__name__, static_folder='map-server/static')

app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app)

app.config['MQTT_BROKER_URL'] = args.hostname
app.config['MQTT_BROKER_PORT'] = 1883
app.config['MQTT_REFRESH_TIME'] = 1.0
mqtt = Mqtt()

floorplan = Floorplan("CAD Files/li27.dxf")
#floorplan = Floorplan("CAD Files/polygon_convex_example.dxf")
clients = []

@app.route('/')
def index():
    return app.send_static_file('index.html')

@app.route('/floorplan')
def get_floorplan():
    floorplan.load_map()
    obstacles = list(floorplan.get_obstacles())

    #obstacles = [[(0,100), (0,0), (400,0), (400, 100)],
    #            [(300,400),(300,300),(400,300),(400,400)],
    #            [(-200,-100),(-200,-200),(0, -200),(0, -50)] ]
    data = {'obstacles': obstacles,
            'area': {'x': 1000, 'y': 1000}      # area in world coordinates
            }

    return jsonify(data)

@app.route('/plan', methods=['POST'])
def path_planner():
    print("POST:", request.json)

    floorplan.path_planner((request.json['x'], request.json['y']))

    return jsonify({'checkpoints': []})

@app.route('/checkpoints', methods=['POST'])
def checkpoints_handler():
    data = checkpoint_handler(request.json)
    mqtt.publish('path', data)

    print("Published", data, len(data))


    return jsonify(success=True)

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
        try:
            result = position_handler(message.payload)
        except ValueError:
            result = None

        if result:
            floorplan.update_pos((result['pos'], result['theta']))
            socketio.emit('json', dumps(result), namespace='/position')

if __name__ == '__main__':
    logger.log(logging.INFO, "Connecting to MQTT broker at {}:{}".format(
        app.config['MQTT_BROKER_URL'],app.config['MQTT_BROKER_PORT']))
    mqtt.init_app(app)
    mqtt.subscribe('position')

    socketio.run(app, host='0.0.0.0', log_output=True)
