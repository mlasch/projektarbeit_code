import math
import json
import time

def emitter_thread_circle(socketio):
    phi = 0
    while True:

        if phi >= 360:
            phi = 0
        else:
            phi += 3

        x = 100*math.cos(phi/360*2*math.pi) + 300
        y = 100*math.sin(phi/360*2*math.pi) + 300

        theta = (phi)/360*2*math.pi

        #x = randint(100, 600)
        #y = randint(100, 400)

        #print(x,y)

        position = {
            "pos": {"x": x, "y": y},
            "theta": theta
        }

        socketio.emit("json", json.dumps(position), namespace='/position')  # send to all clients in the namespace

        time.sleep(1/4)

def emitter_thread(socketio):
    emitter_thread_circle(socketio)
