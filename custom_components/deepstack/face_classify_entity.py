import sys
import logging
import voluptuous as vol

from homeassistant.core import split_entity_id
from homeassistant.components.image_processing import (ImageProcessingFaceEntity)
from homeassistant.helpers import config_validation as cv

from .const import *

_LOGGER = logging.getLogger(__name__)

SERVICE_CHANGE_DETECT_FIRST_SCHEMA = vol.Schema({
    vol.Required(ATTR_ENABLED): cv.boolean,
})


class FaceClassifyEntity(ImageProcessingFaceEntity):
    """Perform a face classification."""

    def __init__(self, hass, data, camera_entity_id, name, detected_first):
        """Init with the API key and model id."""
        super().__init__()

        self.hass = hass
        self.timeout = IMAGE_TIMEOUT.seconds

        self._camera_entity_id = camera_entity_id
        self._data = data

        self._matched_faces_description = None
        self._response_time = None
        self._detected_first = detected_first
        self._last_result = {
            ATTR_CONNECTED: False
        }

        if name:
            self._name = f'{DEEP_STACK_FACE_RECOGNITION} {name}'
        else:
            camera_name = split_entity_id(camera_entity_id)[1]
            self._name = f'{DEEP_STACK_FACE_RECOGNITION} {camera_name}'

        def service_change_detect_first(service):
            """Handle for services."""
            enabled = service.data.get(ATTR_ENABLED, False)
            self._detected_first = enabled

        hass.services.register(DOMAIN, SERVICE_CHANGE_DETECT_FIRST, service_change_detect_first,
                               schema=SERVICE_CHANGE_DETECT_FIRST_SCHEMA)

    def process_image(self, image):
        """Process an image."""
        try:
            _LOGGER.debug(f'Starting to recognize image of {self._name}')

            self._last_result = self._data.recognize(image, self._camera_entity_id, self._name, self._detected_first)

            self.total_faces = self._last_result.get(ATTR_TOTAL_MATCHED_FACES, 0)
            self.faces = self._last_result.get(FACES, [])

        except Exception as ex:
            exc_type, exc_obj, tb = sys.exc_info()
            line_number = tb.tb_lineno

            _LOGGER.error(f'Failed to process image ({self._name}), Error: {ex}, Line: {line_number}')

    @property
    def camera_entity(self):
        """Return camera entity id from process pictures."""
        return self._camera_entity_id

    @property
    def name(self):
        """Return the name of the sensor."""
        return self._name

    @property
    def device_state_attributes(self):
        """Return the classifier attributes."""

        attrs = {
            ATTR_MATCHED_FACES: self._last_result.get(ATTR_MATCHED_FACES, []),
            ATTR_TOTAL_MATCHED_FACES: self._last_result.get(ATTR_TOTAL_MATCHED_FACES, 0),
            ATTR_CONNECTED: self._last_result.get(ATTR_CONNECTED, False)
        }

        if self._data.display_response_time:
            attrs[ATTR_RESPONSE_TIME_SEC] = self._last_result.get(ATTR_RESPONSE_TIME_SEC, 0)

        return attrs
