#!/usr/bin/env python3

### IMPORTS ###
import asyncio
import logging
import kasa

### GLOBALS ###
TARGET_NETWORK_BROADCAST = "172.17.255.255" # Broadcast address for 172.17.0.0/16 CIDR Network

### FUNCTIONS ###

### CLASSES ###
class TPLinkDevice:
    pass

class TPLinkDeviceManager:
    def __init__(self, tnba = None):
        self.logger = logging.getLogger(type(self).__name__)
        self.logger.debug("Inputs - tnba: %s", tnba)
        self.target_network_broadcast_address = tnba
        self.devices = []

    async def discover_devices(self):
        # This method runs the kasa library discovery mechanism with a callback
        # to check and (if needed) create the TPLinkDevice object
        self.logger.debug("Discovering Devices")
        await kasa.Discover.discover(
            target = self.target_network_broadcast_address,
            on_discovered = self._device_discovered
        )

    async def _device_discovered(self, device):
        self.logger.debug("Device Discovered: %s", device)
        # Check to see if the discovered device is already in the devices list.
        # Note: This could be more efficiently performed using a dictionary, but
        #       the likelyhood of that many devices on a given network is low.
        # for item in self.devices:
        #     # If mac addresses are the same
        #     if device.mac == item.mac:
        #         # Same device, make sure IP is still the same
        #         if device.
        # if not, add to the devices list

### MAIN ###
def main():
    log_format = "%(asctime)s:%(levelname)s:%(name)s.%(funcName)s: %(message)s"
    logging.basicConfig(format = log_format, level = logging.DEBUG)

    loop = asyncio.get_event_loop()

    tpldm = TPLinkDeviceManager(TARGET_NETWORK_BROADCAST)

    task_discovery = loop.create_task(tpldm.discover_devices())

    loop.run_forever()

if __name__ == "__main__":
    main()
