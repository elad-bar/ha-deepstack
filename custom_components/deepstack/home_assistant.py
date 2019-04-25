import logging
import voluptuous as vol

from homeassistant.const import (CONF_HOST, CONF_PORT, ATTR_NAME, CONF_SSL)
from homeassistant.helpers import config_validation as cv
from homeassistant.components.image_processing import (CONF_CONFIDENCE)

from .const import *

_LOGGER = logging.getLogger(__name__)

CONFIG_SCHEMA = vol.Schema({
    DOMAIN: vol.Schema({
        vol.Required(CONF_HOST): cv.string,
        vol.Optional(CONF_SSL): cv.boolean,
        vol.Required(CONF_PORT): cv.port,
        vol.Optional(CONF_UNKNOWN_DIRECTORY): cv.string,
        vol.Optional(CONF_ADMIN_KEY, default=''): cv.string,
        vol.Optional(CONF_API_KEY, default=''): cv.string
    }),
}, extra=vol.ALLOW_EXTRA)

SERVICE_REGISTER_FACE_SCHEMA = vol.Schema({
    vol.Required(ATTR_NAME): cv.string,
    vol.Required(FILE_PATH): cv.string,
})

SERVICE_DELETE_FACE_SCHEMA = vol.Schema({
    vol.Required(ATTR_NAME): cv.string
})

SERVICE_DISPLAY_RESPONSE_TIME_SCHEMA = vol.Schema({
    vol.Required(ATTR_ENABLED): cv.boolean,
})

SERVICE_CHANGE_CONFIDENCE_LEVEL_SCHEMA = vol.Schema({
    vol.Required(CONF_CONFIDENCE): vol.All(vol.Coerce(float), vol.Range(min=0, max=100))
})


class HomeAssistant:
    def __init__(self, hass, allow_backup_restore):
        self._hass = hass
        self._allow_backup_restore = allow_backup_restore

    def initialize(self, service_change_confidence_level, service_display_response_time,
                   service_register_face, service_list_faces, service_delete_face):
        self._hass.services.register(DOMAIN, SERVICE_CHANGE_CONFIDENCE_LEVEL, service_change_confidence_level,
                                     schema=SERVICE_CHANGE_CONFIDENCE_LEVEL_SCHEMA)

        self._hass.services.register(DOMAIN, SERVICE_DISPLAY_RESPONSE_TIME, service_display_response_time,
                                     schema=SERVICE_DISPLAY_RESPONSE_TIME_SCHEMA)

        self._hass.services.register(DOMAIN, SERVICE_REGISTER_FACE, service_register_face,
                                     schema=SERVICE_REGISTER_FACE_SCHEMA)

        if self._allow_backup_restore:
            self._hass.services.register(DOMAIN, SERVICE_LIST_FACES, service_list_faces)
            self._hass.services.register(DOMAIN, SERVICE_DELETE_FACE, service_delete_face,
                                         schema=SERVICE_DELETE_FACE_SCHEMA)

    def is_valid_file_path(self, file_path):
        """Check that a file_path points to a valid file."""
        result = False

        try:
            cv.isfile(file_path)

            result = self._hass.config.is_allowed_path(file_path)
        except vol.Invalid:
            _LOGGER.error(f'Invalid file path: {file_path}')

        return result

    def is_valid_directory_path(self, directory_path):
        """Check that a file_path points to a valid file."""
        result = False

        try:
            cv.isdir(directory_path)

            result = self._hass.config.is_allowed_path(directory_path)
        except vol.Invalid:
            _LOGGER.error(f'Invalid directory path: {directory_path}')

        return result

    def fire_event(self, name, data):
        _LOGGER.info(f'Firing event: {name} with the following data: {data}')

        self._hass.async_add_job(self._hass.bus.async_fire, name, data)

    def path_builder(self, file_name):
        path = self._hass.config.path(file_name)

        return path

    def display_message(self, message):
        _LOGGER.info(f'Display message: {message}')

        self._hass.components.persistent_notification.create(message,
                                                             title=NOTIFICATION_FACE_LIST,
                                                             notification_id=NOTIFICATION_FACE_LIST)
