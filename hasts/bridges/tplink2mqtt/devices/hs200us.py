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
    def __init__(self, mqtt_client, kasa_device):
        super().__init__(mqtt_client, kasa_device)
        # self.logger = logging.getLogger(type(self).__name__)
        self.logger.debug("Inputs - mqtt_client: %s, device: %s", mqtt_client, kasa_device)
        # FIXME: Does super().__init__(...) use the correct __name__ for the logger?
        self._previous_output = False

    async def _check_outputs(self):
        self.logger.debug("Checking outputs")
        if self._kasa_device.is_on != self._previous_output:
            # State changed, so update previous and emit a message
            self._previous_output = self._kasa_device.is_on
            # Should the MAC address have the ':' characters removed?
            await self._mqtt_client.publish(
                "hasts/switch/{}/0/state".format(self.mac),
                "on" if self._kasa_device.is_on else "off"
            )

    # hasts/switch/{mac}/0/change_state -> "on" or "off"
