"""
Component that will perform facial detection and identification via deepstack.

For more details about this platform, please refer to the documentation at
https://home-assistant.io/components/image_processing.deepstack_object
"""
import logging

from homeassistant.core import split_entity_id
from homeassistant.components.image_processing import (ImageProcessingEntity)

from .const import *

_LOGGER = logging.getLogger(__name__)


class ObjectClassifyEntity(ImageProcessingEntity):
    """Perform a face classification."""

    def __init__(self, hass, data, camera_entity_id, name, targets):
        """Init with the API key and model id."""
        super().__init__()

        self._targets = targets

        self.hass = hass
        self.timeout = IMAGE_TIMEOUT.seconds

        self._camera_entity_id = camera_entity_id
        self._data = data

        if name:
            self._name = f'{DEEP_STACK_FACE_DETECTION} {name}'
        else:
            camera_name = split_entity_id(camera_entity_id)[1]
            self._name = f'{DEEP_STACK_FACE_DETECTION} {camera_name}'

        self._state = None
        self._predictions = {}

    def process_image(self, image):
        """Process an image."""
        _LOGGER.debug(f'Starting to detect objects in image of {self._name}')
        response = self._data.detect(image, self._targets)

        self._state = response.get(COUNT)
        self._predictions = response.get(TARGETS)

    @property
    def camera_entity(self):
        """Return camera entity id from process pictures."""
        return self._camera_entity_id

    @property
    def state(self):
        """Return the state of the entity."""
        return self._state

    @property
    def name(self):
        """Return the name of the sensor."""
        return self._name

    @property
    def device_state_attributes(self):
        """Return device specific state attributes."""
        attr = {
            CONF_TARGETS: self._targets,
            PREDICTIONS: self._predictions
        }

        return attr
