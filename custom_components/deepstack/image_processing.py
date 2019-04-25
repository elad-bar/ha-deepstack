"""
Component that will perform facial recognition via deepstack.

For more details about this platform, please refer to the documentation at
https://home-assistant.io/components/image_processing.deepstack_face
"""
import logging
import voluptuous as vol
import homeassistant.helpers.config_validation as cv
from homeassistant.const import (CONF_SCAN_INTERVAL)
from homeassistant.components.image_processing import (PLATFORM_SCHEMA, CONF_SOURCE,
                                                       CONF_ENTITY_ID, CONF_NAME)

from .const import *
from .face_classify_entity import FaceClassifyEntity
from .object_classify_entity import ObjectClassifyEntity

_LOGGER = logging.getLogger(__name__)
DEPENDENCIES = [DOMAIN]

FACE_RECOGNITION_SCHEMA = vol.Schema({
    vol.Required(ATTR_ENABLED): cv.boolean,
    vol.Optional(CONF_DETECT_FIRST, default=False): cv.boolean,
})

OBJECT_DETECTION_SCHEMA = vol.Schema({
    vol.Required(ATTR_ENABLED): cv.boolean,
    vol.Optional(CONF_TARGETS, default=[TARGET_PERSON]): vol.All(cv.ensure_list, [vol.In(SUPPORTED_TARGETS)])
})

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend({
    vol.Optional(CONF_FACE_RECOGNITION): FACE_RECOGNITION_SCHEMA,
    vol.Optional(CONF_OBJECT_DETECTION): OBJECT_DETECTION_SCHEMA
})


def setup_platform(hass, config, add_devices, discovery_info=None):
    """Set up the classifier."""
    all_cameras = config.get(CONF_SOURCE)
    scan_interval = config.get(CONF_SCAN_INTERVAL, timedelta(seconds=DEFAULT_TIMEOUT))

    face_recognition = config.get(CONF_FACE_RECOGNITION, {})
    allow_face_recognition = face_recognition.get(ATTR_ENABLED, False)
    detect_first = face_recognition.get(CONF_DETECT_FIRST, False)

    object_detection = config.get(CONF_OBJECT_DETECTION, {})
    allow_object_detection = object_detection.get(ATTR_ENABLED, False)
    object_detection_targets = object_detection.get(CONF_TARGETS, [TARGET_PERSON])

    _LOGGER.info(f'Initializing with following configuration: {config}, discovery_info: {discovery_info}')

    data = hass.data[DATA_DEEP_STACK]

    timeout = scan_interval.total_seconds()

    if allow_face_recognition and detect_first:
        timeout = (timeout / 2) - 0.1
    else:
        timeout = timeout - 0.1

    data.change_api_timeout(timeout)

    for camera in all_cameras:
        camera_name = camera.get(CONF_NAME)
        camera_entity_id = camera.get(CONF_ENTITY_ID)

        if allow_face_recognition:
            face_entity = FaceClassifyEntity(hass, data, camera_entity_id, camera_name, detect_first)

            data.add_processor(face_entity)

        if allow_object_detection:
            face_entity = ObjectClassifyEntity(hass, data, camera_entity_id, camera_name, object_detection_targets)

            data.add_processor(face_entity)

    add_devices(data.processors)
