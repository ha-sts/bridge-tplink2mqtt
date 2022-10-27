#!/usr/bin/env python3

### IMPORTS ###
import asyncio
import logging
import kasa

from .devices import get_device_class

### GLOBALS ###

### FUNCTIONS ###

### CLASSES ###
class TPLinkDeviceManager:
    def __init__(self, mqtt_client, tnba = None, always_publish = False):
        self.logger = logging.getLogger(type(self).__name__)
        self.logger.debug("Inputs - mqtt_client: %s, tnba: %s", mqtt_client, tnba)
        self._mqtt_client = mqtt_client
        self.target_network_broadcast_address = tnba
        self.devices = []
        self.always_publish = always_publish
        # Register the command handler
        self._mqtt_client.register_topic_coroutine("hasts/service/tplink2mqtt", self._handle_command)

    async def discover_devices(self):
        # This method runs the kasa library discovery mechanism with a coroutine
        # to check and (if needed) create the TPLinkDevice object
        self.logger.debug("Discovering devices")
        await kasa.Discover.discover(
            target = self.target_network_broadcast_address,
            on_discovered = self._device_discovered
        )

    async def _device_discovered(self, kasa_device):
        self.logger.info("Device Discovered: %s", kasa_device)
        # Check to see if the discovered device is already in the devices list.
        # Note: This could be more efficiently performed using a dictionary, but
        #       the likelyhood of that many devices on a given network is low.
        found = False
        for item in self.devices:
            # If mac addresses are the same
            if kasa_device.mac == item.mac:
                self.logger.debug("Found device in known list.")
                found = True
                # Same device, make sure hostname or IP address is still the same
                if kasa_device.host != item.host:
                    # Replace the device in the list
                    self.logger.debug("Host value changed, updating known list.")
                    await self._remove_device(item)
                    await self._create_device(kasa_device)
        # if not, add to the devices list
        if not found:
            await self._create_device(kasa_device)

    async def _create_device(self, kasa_device):
        self.logger.debug("Inputs - kasa_device: %s", kasa_device)
        dev_class = get_device_class(kasa_device.model)
        self.logger.debug("dev_class: %s", dev_class)
        tmp_dev = dev_class(self._mqtt_client, kasa_device, self.always_publish)
        await tmp_dev.register_coroutines()
        self.devices.append(tmp_dev)
        self.logger.debug("self.devices: %s", self.devices)

    async def _remove_device(self, tp_device):
        self.logger.debug("Inputs - tp_device: %s", tp_device)
        self.devices.remove(tp_device)
        await tp_device.unregister_coroutines()
        self.logger.debug("self.devices: %s", self.devices)

    async def _handle_command(self, message):
        self.logger.debug("received command message: %s", message)
        tmp_payload = message.payload.decode('utf-8')
        if tmp_payload == 'discover':
            # Run the device discovery process, then run the heartbeat to update all of the devices
            await self.discover_devices()
            await self.heartbeat()

    async def heartbeat(self):
        for i in self.devices:
            asyncio.create_task(i.heartbeat())
