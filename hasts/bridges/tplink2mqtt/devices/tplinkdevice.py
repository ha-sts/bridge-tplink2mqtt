#!/usr/bin/env python3

### IMPORTS ###
import logging

### GLOBALS ###

### FUNCTIONS ###

### CLASSES ###
class TPLinkDevice:
    """
    This class will have to maintain a copy of the state of the device outputs
    in order to be able to detect a change and issue an MQTT message with the
    new state.

    This class will also have to detect a timeout so a status message about the
    device can be issued.

    A "heartbeat" method will need to be called every minute or five to get an
    update from the device and compare the current state to the previous state.

    This class will need to subscribe to control messages in order to receive
    commands to "turn on" and "turn off" the switches (output relays).  Since
    the different device types have different outputs, it will likely be
    required to sub-class this with specifics about the different device types.
    """
    def __init__(self, mqtt_client, kasa_device, always_publish = False):
        self.logger = logging.getLogger(type(self).__name__)
        self.logger.debug("Inputs - mqtt_client: %s, device: %s", mqtt_client, kasa_device)
        self._mqtt_client = mqtt_client
        self._kasa_device = kasa_device
        # FIXME: Are these safe enough to convert to properties that access the
        #        _kasa_device?
        # FIXME: Can the _kasa_device handle reconnections, either manually or
        #        automagically?
        self.host = self._kasa_device.host
        self.mac = self._kasa_device.mac
        self.always_publish = always_publish

    async def _check_outputs(self):
        raise NotImplementedError

    async def _check_energy(self):
        # By default, there's no energy metering.
        pass

    async def heartbeat(self):
        self.logger.debug("Heartbeat")
        # Try a device update.
        # FIXME: Record offline state if there's a timeout.  Issue a status message.
        # FIXME: If the previous state was offline and the device becomes responsive,
        #        record online state and issue a status message.
        await self._kasa_device.update()
        # If the new state of the output(s) is different than the old state,
        # issue a state message
        await self._check_outputs()
        # If there's any energy metering, get those values and issue the correct messages.
        await self._check_energy()
