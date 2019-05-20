#!/usr/bin/env python3

import math
import argparse

from random import randint
from time import sleep
from struct import pack

import paho.mqtt.client as mqtt

from planning.position import Emitter

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Robot position simulator')
    parser.add_argument('hostname', metavar='HOST', help='Hostname of the MQTT broker')
    args = parser.parse_args()


    client = mqtt.Client('emitter-'+''.join(str(randint(0,9)) for _ in range(5)))
    #client.connect('localhost', port=1883, keepalive=60, bind_address="")
    client.connect(args.hostname, port=1883, keepalive=60, bind_address="")

    emitter = Emitter(1700, 2800, 0)

    for x, y, theta in emitter.emit():
        x = 4000.0
        y = 2000.0
        ctl_forward = 0
        ctl_side = 0
        theta = -math.pi/2

        payload = pack("!fffff", x, y, theta, ctl_forward, ctl_side)
        client.publish("position", payload=payload, qos=0, retain=False)
        print("send {} {} {} {}".format(x,y,theta, payload))
        sleep(0.5)
