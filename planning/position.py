import math
import json
import time

from struct import unpack, pack

def position_handler(payload):
    if len(payload) > 20:
        print("Payload length missmatch")
        raise ValueError

    x, y, theta, joy_x, joy_y = unpack("!fffff", payload)

    position = {
        "pos": {"x": x, "y": y},
        "joystick": {"x": joy_x, "y": joy_y},
        "theta": theta
    }

    return position

def checkpoint_handler(checkpoints):
    data = b""

    for checkpoint in checkpoints:
        print("TEST", checkpoint)
        data += pack("!ff", checkpoint['x'], checkpoint['y'])

    return data

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

class Emitter():
    def __init__(self, x, y, theta):
        self.x = x
        self.y = y
        self.theta = theta

    def emit(self):
        UP = 1
        DOWN = 2
        TURN1 = 3
        TURN2 = 4
        state = DOWN

        while True:
            if state == DOWN:
                if self.y > 2800:
                    state = TURN2
                else:
                    self.y += 8

            elif state == UP:
                if self.y < 600:
                    state = TURN1
                else:
                    self.y -= 8

            elif state == TURN1:
                if self.theta > math.pi:
                    state = DOWN
                else:

                    self.theta += 2*math.pi/360*2

            elif state == TURN2:
                if self.theta <= 0:
                    state = UP
                else:

                    self.theta -= 2*math.pi/360*2

            yield self.x, self.y, self.theta


def emitter_thread(socketio):
    #emitter_thread_circle(socketio)

    emitter = Emitter(1700, 2800, 0)
    for x,y,theta in emitter.emit():
        position = {
            "pos": {"x": x, "y": y},
            "theta": theta
        }

        socketio.emit("json", json.dumps(position), namespace='/position')  # send to all clients in the namespace
        time.sleep(1/20)
