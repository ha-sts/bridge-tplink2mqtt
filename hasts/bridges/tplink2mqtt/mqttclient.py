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
        self._topic_coroutines = []

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
                            self.logger.debug("Received message:")
                            self.logger.debug("  topic: %s", message.topic)
                            self.logger.debug("  payload: %s", message.payload)
                            self.logger.debug("  qos: %s", message.qos)
                            await self._relay_message_to_topic_coroutines(message)
            except asyncio_mqtt.MqttError as error:
                self.logger.warning("MQTT Error: %s", error)
                if self.reconnect_interval > 0:
                    self.logger.info("Reconnecting in %d seconds", self.reconnect_interval)
                    await asyncio.sleep(self.reconnect_interval)
                else:
                    # Not reconnecting, so stop the loop
                    self._stop = True

    async def register_topic_coroutine(self, topic, coroutine):
        # Register a coroutine (async function) to get tasked when a message matching the topic arrives
        # FIXME: Support wildcard paths in the future
        self.logger.info("Registering topic: %s", topic)
        self._topic_coroutines.append({
            "topic": topic,
            "coroutine": coroutine
        })

    async def unregister_topic_coroutine(self, topic, coroutine):
        # Unregister a coroutine
        # FIXME: Support wildcards?
        # FIXME: Should this be 'unregister_coroutine' that would remove all references to the coroutine?
        self.logger.info("Unregistering topic: %s", topic)
        for item in self._topic_coroutines:
            if item['topic'] == topic and item['coroutine'] == coroutine:
                self._topic_coroutines.remove(item)

    async def _relay_message_to_topic_coroutines(self, message):
        # Send the received message to any registered coroutines with a matching topic
        for item in self._topic_coroutines:
            # FIXME: Support wildcard paths in the future
            if item['topic'] == message.topic:
                tmp_coro = item['coroutine']
                asyncio.create_task(tmp_coro(message))

    async def publish(self, topic, payload):
        self.logger.info("Publishing topic: %s, payload: %s", topic, payload)
        #tmp_client = await self._get_client()
        # NOTE: There are more options available:
        #       https://github.com/sbtinstruments/asyncio-mqtt/blob/master/asyncio_mqtt/client.py#L389
        await self._client.publish(topic = topic, payload = payload)

    # async def _get_client(self):
    #     # Check to see if the client is created
    #     if self._client is None or not self._running:
    #         # Start the client or raise an exception
    #         pass
    #     return self._client
