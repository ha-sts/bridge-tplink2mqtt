#!/usr/bin/env python3

### IMPORTS ###
import logging
import asyncio
import asyncio_mqtt

### GLOBALS ###

### FUNCTIONS ###

### CLASSES ###
class MqttClient:
    def __init__(self, host = "localhost", port = 1883, user = None, password = None):
        self.logger = logging.getLogger(type(self).__name__)
        self.logger.debug("Inputs - host: %s, port: %s, user: %s, password: %s", host, port, user, password)
        self.host = host
        self.port = int(port)
        self.user = user
        self.password = password
        self._client = None
        self._running = False
        self._stop = False
        self.reconnect_interval = 3

    async def run(self):
        while not self._stop:
            try:
                async with asyncio_mqtt.Client(
                    hostname = self.host,
                    port = self.port,
                    username = self.user,
                    password = self.password
                ) as client:
                    self._client = client
                    self._running = True
                    async with client.unfiltered_messages() as messages:
                        await client.subscribe("hasts/#")
                        async for message in messages:
                            # Call a method to check topics and route commands
                            self.logger.debug("message: %s", message)
            except asyncio_mqtt.MqttError as error:
                self.logger.warning("MQTT Error: %s")
                if self.reconnect_interval > 0:
                    self.logger.info("Reconnecting in %d seconds", self.reconnect_interval)
                    await asyncio.sleep(self.reconnect_interval)
                else:
                    # Not reconnecting, so stop the loop
                    self._stop = True

    async def publish(self, topic, payload):
        tmp_client = await self._get_client()
        # NOTE: There are more options available:
        #       https://github.com/sbtinstruments/asyncio-mqtt/blob/d1c75369bcfcf3b4e6631d2bc228509e9160fd9c/asyncio_mqtt/client.py#L389
        await tmp_client.publish(topic = topic, payload = payload)

    async def _get_client(self):
        # Check to see if the client is created
        if self._client is None or not self._running:
            # FIXME: What's the best way to start this if the client isn't running?  Or should it just throw an error?
            pass
        return self._client
