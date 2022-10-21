#!/usr/bin/env python3

### IMPORTS ###
import logging
import asyncio_mqtt

### GLOBALS ###

### FUNCTIONS ###

### CLASSES ###
class MqttClient:
    def __init__(self, host = "localhost", port = 1883, user = None, password = None):
        self.logger = logging.getLogger(type(self).__name__)
        self.logger.debug("Inputs - host: %s, port: %s, user: %s, password: %s", host, port, user, password)
        self._host = host
        self._port = port
        self._user = user
        self._password = password
        self._client = None

    async def publish(self, topic, payload):
        tmp_client = await self._get_client()
        # NOTE: There are more options available:
        #       https://github.com/sbtinstruments/asyncio-mqtt/blob/d1c75369bcfcf3b4e6631d2bc228509e9160fd9c/asyncio_mqtt/client.py#L389
        await tmp_client.publish(topic = topic, payload = payload)

    async def _get_client(self):
        # Check to see if the client is created
        if self._client is None:
            self._client = asyncio_mqtt.Client(
                hostname = self._host,
                port = self._port,
                username = self._user,
                password = self._password
            )
            # FIXME: Some sort of reconnection mechanism...
            await self._client.connect()
        return self._client
