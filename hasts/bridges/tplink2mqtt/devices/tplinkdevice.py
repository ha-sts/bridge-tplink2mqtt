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
        # FIXME: Can the _kasa_device handle reconnections, either manually or
        #        automagically?
        self.host = self._kasa_device.host
        self.mac = self._kasa_device.mac
        self.always_publish = always_publish
        self._previous_outputs = []
        self._previous_outputs.append(False)

    async def _check_outputs(self):
        self.logger.warning("Checking outputs for unknown device type: %s", self._kasa_device.model)
        # NOTE: This assumes that the device is a "single switch", which is a generic mode supported by the kasa library
        if self.always_publish or (self._kasa_device.is_on != self._previous_outputs[0]):
            # State changed, so update previous and emit a message
            self._previous_outputs[0] = self._kasa_device.is_on
            # Should the MAC address have the ':' characters removed?
            await self._mqtt_client.publish(
                "hasts/switch/{}/0/state".format(self.mac),
                "on" if self._kasa_device.is_on else "off"
            )

    async def _check_energy(self):
        # By default, there's no energy metering.
        pass

    async def _handle_message(self, message):
        self.logger.warning("Handling message for unknown device type: %s", self._kasa_device.model)
        self.logger.debug("received message: %s", message)
        tmp_payload = message.payload.decode('utf-8')
        if tmp_payload == 'on':
            # Send the turn on command
            await self._kasa_device.turn_on()
        elif tmp_payload == 'off':
            # Send the turn off command
            await self._kasa_device.turn_off()
        # Run the heartbeat to update the state.
        await self.heartbeat()

    async def register_coroutines(self):
        self.logger.debug("Registering coroutines for unknown device type: %s", self._kasa_device.model)
        await self._mqtt_client.register_topic_coroutine(
            "hasts/switch/{}/0/change_state".format(self.mac),
            self._handle_message
        )

    async def unregister_coroutines(self):
        self.logger.debug("Unregistering coroutines for unknown device type: %s", self._kasa_device.model)
        await self._mqtt_client.unregister_topic_coroutine(
            "hasts/switch/{}/0/change_state".format(self.mac),
            self._handle_message
        )

    async def heartbeat(self):
        self.logger.info("Heartbeat")
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
