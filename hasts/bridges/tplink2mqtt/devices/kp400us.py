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
    def __init__(self, mqtt_client, kasa_device):
        super().__init__(mqtt_client, kasa_device)
        # self.logger = logging.getLogger(type(self).__name__)
        self.logger.debug("Inputs - mqtt_client: %s, device: %s", mqtt_client, kasa_device)
        # FIXME: Does super().__init__(...) use the correct __name__ for the logger?
        self._previous_output_0 = False
        self._previous_output_1 = False

    async def _check_outputs(self):
        self.logger.debug("Checking outputs")
        # First Plug
        if self._kasa_device.get_plug_by_index(0).is_on != self._previous_output_0:
            # State changed, so update previous and emit a message
            self._previous_output_0 = self._kasa_device.get_plug_by_index(0).is_on
            # Should the MAC address have the ':' characters removed?
            await self._mqtt_client.publish(
                "hasts/switch/{}/0/state".format(self.mac),
                "on" if self._kasa_device.get_plug_by_index(0).is_on else "off"
            )
        # Second Plug
        if self._kasa_device.get_plug_by_index(1).is_on != self._previous_output_1:
            # State changed, so update previous and emit a message
            self._previous_output_1 = self._kasa_device.get_plug_by_index(1).is_on
            # Should the MAC address have the ':' characters removed?
            await self._mqtt_client.publish(
                "hasts/switch/{}/1/state".format(self.mac),
                "on" if self._kasa_device.get_plug_by_index(1).is_on else "off"
            )
