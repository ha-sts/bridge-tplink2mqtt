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
        self.devices = {}
        self.always_publish = always_publish

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
        if kasa_device.mac in self.devices:
            # Device exists, check the host name
            if kasa_device.host == self.devices[kasa_device.mac].host:
                # Same device, same host, all is well, so do nothing
                return
            # Remove the device from the list
            self.logger.debug("Host value changed, updating known list.")
            await self._remove_device(kasa_device.mac)
        # Device not in list, so create
        await self._create_device(kasa_device)

    async def _create_device(self, kasa_device):
        self.logger.debug("Inputs - kasa_device: %s", kasa_device)
        dev_class = get_device_class(kasa_device.model)
        self.logger.debug("dev_class: %s", dev_class)
        self.devices[kasa_device.mac] = dev_class(self._mqtt_client, kasa_device, self.always_publish)
        await self.devices[kasa_device.mac].register_coroutines()
        self.logger.debug("self.devices: %s", self.devices)

    async def _remove_device(self, tp_device_mac):
        self.logger.debug("Inputs - tp_device_mac: %s", tp_device_mac)
        await self.devices[tp_device_mac].unregister_coroutines()
        del self.devices[tp_device_mac]
        self.logger.debug("self.devices: %s", self.devices)

    async def _handle_command(self, message):
        self.logger.debug("received command message: %s", message)
        tmp_payload = message.payload.decode('utf-8')
        if tmp_payload == 'discover':
            # Run the device discovery process, then run the heartbeat to update all of the devices
            await self.discover_devices()
            await self.heartbeat()

    async def register_coroutines(self):
        # This should be called after the creation of this class to enable listening for messages.
        await self._mqtt_client.register_topic_coroutine("hasts/service/tplink2mqtt/control", self._handle_command)

    async def heartbeat(self):
        for dev in self.devices.values():
            asyncio.create_task(dev.heartbeat())
