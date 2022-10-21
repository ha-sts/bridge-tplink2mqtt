#!/usr/bin/env python3

### IMPORTS ###
import asyncio
import logging

from hasts.bridges.tplink2mqtt import TPLinkDeviceManager

### GLOBALS ###
TARGET_NETWORK_BROADCAST = "172.17.255.255" # Broadcast address for 172.17.0.0/16 CIDR Network

### FUNCTIONS ###

### CLASSES ###
class HeartbeatTickler:
    def __init__(self):
        self.logger = logging.getLogger(type(self).__name__)
        self._corofuncs = []
        self._stop = False

    def add_corofunc(self, corofunc):
        # NOTE: The coroutine generating method supplied should not require arguments
        #       For later improvement: https://stackoverflow.com/a/65755581
        self._corofuncs.append(corofunc)

    def stop(self):
        self._stop = True

    async def run(self):
        while not self._stop:
            cororuns = []
            for i in self._corofuncs:
                cororuns.append(i())
            await asyncio.gather(*cororuns)
            await asyncio.sleep(300) # Every five minutes for now.

### MAIN ###
def main():
    log_format = "%(asctime)s:%(levelname)s:%(name)s.%(funcName)s: %(message)s"
    logging.basicConfig(format = log_format, level = logging.DEBUG)

    loop = asyncio.get_event_loop()

    tpldm = TPLinkDeviceManager(mqtt_client = "", tnba = TARGET_NETWORK_BROADCAST)
    hbt = HeartbeatTickler()
    hbt.add_corofunc(tpldm.heartbeat)

    task_discovery = loop.create_task(tpldm.discover_devices())
    task_tickler = loop.create_task(hbt.run())

    loop.run_forever()

    # FIXME: Should make this catch the keyboard interrupt (and possibly others)
    #        and make this shutdown gracefully, waiting for tasks and then
    #        disconnecting MQTT

if __name__ == "__main__":
    main()
