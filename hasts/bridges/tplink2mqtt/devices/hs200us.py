#!/usr/bin/env python3

### IMPORTS ###
from .tplinkdevice import TPLinkDevice

### GLOBALS ###

### FUNCTIONS ###

### CLASSES ###
class HS200US(TPLinkDevice):
    """
    TPLink HS200(US)
    In-wall light switch
    1 output, no dimming
    no energy monitoring
    """
    def __init__(self, mqtt_client, kasa_device, always_publish = False):
        super().__init__(mqtt_client, kasa_device, always_publish)
        # self.logger = logging.getLogger(type(self).__name__)
        self.logger.debug("Inputs - mqtt_client: %s, device: %s", mqtt_client, kasa_device)
        # FIXME: Does super().__init__(...) use the correct __name__ for the logger?
        self._previous_output = False

    async def _check_outputs(self):
        self.logger.debug("Checking outputs")
        if self.always_publish or (self._kasa_device.is_on != self._previous_output):
            # State changed, so update previous and emit a message
            self._previous_output = self._kasa_device.is_on
            # Should the MAC address have the ':' characters removed?
            await self._mqtt_client.publish(
                "hasts/switch/{}/0/state".format(self.mac),
                "on" if self._kasa_device.is_on else "off"
            )

    async def _handle_message(self, message):
        self.logger.debug("received message: %s", message)
        # FIXME: handle payloads

    async def register_coroutines(self):
        # FIXME: Can refactory this to be a nice data structure that the base class processes.
        self.logger.debug("Registering coroutines")
        await self._mqtt_client.register_topic_coroutine(
            "hasts/switch/{}/0/change_state".format(self.mac),
            self._handle_message
        )

    async def unregister_coroutines(self):
        # FIXME: Can refactory this to be a nice data structure that the base class processes.
        self.logger.debug("Unregistering coroutines")
        await self._mqtt_client.unregister_topic_coroutine(
            "hasts/switch/{}/0/change_state".format(self.mac),
            self._handle_message
        )
