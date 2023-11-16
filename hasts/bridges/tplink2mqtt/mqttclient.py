#!/usr/bin/env python3

### IMPORTS ###
import logging
import asyncio
import aiomqtt

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
                async with aiomqtt.Client(
                    hostname = self.host,
                    port = self.port,
                    username = self.user,
                    password = self.password
                ) as client:
                    self._client = client
                    self._running = True
                    async with client.messages() as messages:
                        await client.subscribe("hasts/#")
                        async for message in messages:
                            # Call a method to check topics and route commands
                            self.logger.debug("Received message:")
                            self.logger.debug("  topic: %s", message.topic)
                            self.logger.debug("  payload: %s", message.payload)
                            self.logger.debug("  qos: %s", message.qos)
                            await self._relay_message_to_topic_coroutines(message)
            except aiomqtt.MqttError as error:
                self.logger.warning("MQTT Error: %s", error)
                if self.reconnect_interval > 0:
                    self.logger.info("Reconnecting in %d seconds", self.reconnect_interval)
                    await asyncio.sleep(self.reconnect_interval)
                else:
                    # Not reconnecting, so stop the loop
                    self._stop = True

    async def register_topic_coroutine(self, topic, coroutine):
        # Register a coroutine (async function) to get tasked when a message matching the topic arrives
        self.logger.info("Registering topic: %s", topic)
        self._topic_coroutines.append({
            "topic": topic,
            "coroutine": coroutine
        })
        self.logger.debug("Current Coroutine List: %s", self._topic_coroutines)

    async def unregister_topic_coroutine(self, topic, coroutine):
        # Unregister a coroutine
        self.logger.info("Unregistering topic: %s", topic)
        for item in self._topic_coroutines:
            if item['topic'] == topic and item['coroutine'] == coroutine:
                self._topic_coroutines.remove(item)

    async def _relay_message_to_topic_coroutines(self, message):
        # Send the received message to any registered coroutines with a matching topic
        self.logger.debug("Relaying message: %s", message)
        for item in self._topic_coroutines:
            self.logger.debug("  checking item: %s", item)
            if item['topic'] == message.topic:
                self.logger.debug("  item matched")
                tmp_coro = item['coroutine']
                # NOTE: This should probably store the task object into a list,
                #       then have some regular process come through and clean up
                #       the completed tasks.  For now, just going to await the
                #       handling of the message.  This means only one message
                #       will be handled at a time, but that should be fine for
                #       now.
                # asyncio.create_task(tmp_coro(message))
                tmp_task = asyncio.create_task(tmp_coro(message))
                self.logger.debug("  created task: %s", tmp_task)
                await tmp_task

    async def publish(self, topic, payload):
        self.logger.info("Publishing topic: %s, payload: %s", topic, payload)
        #tmp_client = await self._get_client()
        # NOTE: There are more options available:
        #       https://sbtinstruments.github.io/aiomqtt/publishing-a-message.html
        # NOTE: Setting retain on all messages being sent.  This is needed for the "state" topics to allow instant
        #       status update when starting or restarting various managers, such as Home Assistant.
        await self._client.publish(topic = topic, payload = payload, retain = True)
