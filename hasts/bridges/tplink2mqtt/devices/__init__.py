#!/usr/bin/env python3

### IMPORTS ###
from .tplinkdevice import TPLinkDevice
from .hs200us import HS200US
from .kp400us import KP400US

### GLOBALS ###
MODEL_DICT = {
    "HS200(US)": HS200US,
    "KP400(US)": KP400US
}

### FUNCTIONS ###
def get_device_class(model_str):
    # Lookup the correct device class based on the model number.
    if model_str in MODEL_DICT:
        return MODEL_DICT[model_str]
    return TPLinkDevice

### CLASSES ###
