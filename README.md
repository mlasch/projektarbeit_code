# Path Planning

This repository contains examples to explore different ideas to implement 2D path planning.

## Install dependencies

Install `python3-venv` package

```
$ sudo apt install python3-venv python3-dev libsdl-dev libsdl-image1.2-dev libsdl-mixer1.2-dev libsdl-ttf2.0-dev
```

For shapely
```
$ sudo apt install libgeos-dev
```

Create a virtual environment for `python3`

```
$ python3 -m venv .venv
```

Install requirements from the file

```
$ source .venv/bin/activate
(.venv)$ pip3 install wheel
(.venv)$ pip3 install -r requirements.txt
```

Check shapely speedups:
```
>>> from shapely import speedups
>>> speedups.enabled
```

### Message Broker

Install the message broker locally:

```
$ sudo apt install mosquitto mosquitto-clients
```
or run it inside a Docker container:

```
$ cd docker
$ docker build -t mqtt-broker .
```

```
$ docker run -p 1883:1883 -t mqtt-broker
```

List the installed Docker images with `docker image ls` or `docker system df` in either case sometimes it's necessary to reset the environment: `docker system prune`  

Tagging the Docker image after building: `docker tag 3b6b527f221b mqtt-broker`
