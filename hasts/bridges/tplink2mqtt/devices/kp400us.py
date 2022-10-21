#!/usr/bin/env python3

### IMPORTS ###
from .tplinkdevice import TPLinkDevice

### GLOBALS ###

### FUNCTIONS ###

### CLASSES ###
class KP400US(TPLinkDevice):
    """
    TPLink KP400(US)
    Switched plugs on short cord
    2 outputs, no dimming
    no energy monitoring
    """
    def __init__(self, mqtt_client, kasa_device, always_publish = False):
        super().__init__(mqtt_client, kasa_device, always_publish)
        # self.logger = logging.getLogger(type(self).__name__)
        self.logger.debug("Inputs - mqtt_client: %s, device: %s", mqtt_client, kasa_device)
        # FIXME: Does super().__init__(...) use the correct __name__ for the logger?
        self._previous_output_0 = False
        self._previous_output_1 = False

    async def _check_outputs(self):
        self.logger.debug("Checking outputs")
        # First Plug
        if self.always_publish or (self._kasa_device.get_plug_by_index(0).is_on != self._previous_output_0):
            # State changed, so update previous and emit a message
            self._previous_output_0 = self._kasa_device.get_plug_by_index(0).is_on
            # Should the MAC address have the ':' characters removed?
            await self._mqtt_client.publish(
                "hasts/switch/{}/0/state".format(self.mac),
                "on" if self._kasa_device.get_plug_by_index(0).is_on else "off"
            )
        # Second Plug
        if self.always_publish or (self._kasa_device.get_plug_by_index(1).is_on != self._previous_output_1):
            # State changed, so update previous and emit a message
            self._previous_output_1 = self._kasa_device.get_plug_by_index(1).is_on
            # Should the MAC address have the ':' characters removed?
            await self._mqtt_client.publish(
                "hasts/switch/{}/1/state".format(self.mac),
                "on" if self._kasa_device.get_plug_by_index(1).is_on else "off"
            )

    async def _handle_message_0(self, message):
        self.logger.debug("received message: %s", message)
        # FIXME: handle payloads

    async def _handle_message_1(self, message):
        self.logger.debug("received message: %s", message)
        # FIXME: handle payloads

    async def register_coroutines(self):
        self.logger.debug("Registering coroutines")
        self._mqtt_client.register_topic_coroutine(
            "hasts/switch/{}/0/change_state".format(self.mac),
            self._handle_message_0
        )
        self._mqtt_client.register_topic_coroutine(
            "hasts/switch/{}/1/change_state".format(self.mac),
            self._handle_message_1
        )

    async def unregister_coroutines(self):
        self.logger.debug("Unregistering coroutines")
        self._mqtt_client.unregister_topic_coroutine(
            "hasts/switch/{}/0/change_state".format(self.mac),
            self._handle_message_0
        )
        self._mqtt_client.unregister_topic_coroutine(
            "hasts/switch/{}/1/change_state".format(self.mac),
            self._handle_message_1
        )
