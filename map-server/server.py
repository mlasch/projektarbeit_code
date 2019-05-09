#!/usr/bin/env python3

import sys
if '../floorplan' not in sys.path:
    sys.path.append('../floorplan')

import os
import logging
import time
import math

from random import randint
from json import dumps

from flask import Flask, copy_current_request_context, request
from flask_socketio import SocketIO, emit, send
from threading import Thread

from planning import Floorplan

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app, async_mode="threading")

def emitter_thread():
    phi = 0
    while True:

        if phi >= 360:
            phi = 0
        else:
            phi += 3

        x = 100*math.cos(phi/360*2*math.pi) + 300
        y = 100*math.sin(phi/360*2*math.pi) + 300


        #x = randint(100, 600)
        #y = randint(100, 400)

        print(x,y)

        position = {
            "pos": {"x": x, "y": y}
        }

        socketio.emit("json", dumps(position), namespace='/position')  # send to all clients in the namespace

        time.sleep(0.1)

@app.route('/')
def index():
    return app.send_static_file('index.html')

@socketio.on('connect', namespace='/position')
def test_connect():
    print("New client connected")

@socketio.on('disconnect', namespace='/position')
def handle_disconnect():
    print('Client disconnected')

if __name__ == '__main__':
    t1 = Thread(target=emitter_thread)
    #t1 = socketio.start_background_task(emitter_thread)
    print("bla")
    t1.start()
    socketio.run(app, log_output=False)
