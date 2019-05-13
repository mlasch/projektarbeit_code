#!/usr/bin/env python3

from random import randint
from time import sleep
from struct import pack

import paho.mqtt.client as mqtt

from planning.position import Emitter

if __name__ == '__main__':
    client = mqtt.Client('emitter-'+''.join(str(randint(0,9)) for _ in range(5)))
    client.connect('192.168.6.235', port=1883, keepalive=60, bind_address="")

    emitter = Emitter(1700, 2800, 0)

    for x, y, theta in emitter.emit():
        payload = pack("!fff", x, y, theta)
        client.publish("position", payload=payload, qos=0, retain=False)
        print("send {} {} {} {}".format(x,y,theta, payload))
        sleep(0.08)
