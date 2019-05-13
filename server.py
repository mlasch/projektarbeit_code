#!/usr/bin/env python3

import os
import logging
import time
import math

from random import randint
from json import dumps

from flask import Flask, copy_current_request_context, request, jsonify
from flask_socketio import SocketIO, emit, send
from threading import Thread

from planning import Floorplan
from planning.position import emitter_thread

app = Flask(__name__, static_folder='map-server/static')
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app, async_mode="threading")

floorplan = Floorplan("CAD Files/li27_example.dxf")

clients = []
t1 = Thread(target=emitter_thread, args=(socketio,))

@app.route('/')
def index():
    return app.send_static_file('index.html')

@app.route('/floorplan')
def get_floorplan():
    data = list(floorplan.get_obstacles())

    return jsonify(data)

@socketio.on('connect', namespace='/position')
def test_connect():
    clients.append(request.sid)
    print("New client connected")

@socketio.on('disconnect', namespace='/position')
def handle_disconnect():
    clients.remove(request.sid)
    print('Client disconnected')

if __name__ == '__main__':
    t1.start()
    socketio.run(app, host='0.0.0.0', log_output=False)
