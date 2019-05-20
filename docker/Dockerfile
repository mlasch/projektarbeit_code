FROM debian:buster-slim

RUN apt-get update && apt-get install \
	-y --no-install-recommends mosquitto

ADD etc/ /etc/

EXPOSE 1883

CMD ["mosquitto", "-c", "/etc/mosquitto/mosquitto.conf"]
