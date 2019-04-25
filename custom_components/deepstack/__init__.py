"""
This component provides support for Home Automation Manager (HAM).
For more details about this component, please refer to the documentation at
https://home-assistant.io/components/edgeos/
"""
from .const import *
from .deep_stack import (DeepStack)


def setup(hass, config):
    """Set up an Home Automation Manager component."""
    conf = config.get(DOMAIN, {})

    data = DeepStack(hass, conf)

    hass.data[DATA_DEEP_STACK] = data

    return data.is_initialized
