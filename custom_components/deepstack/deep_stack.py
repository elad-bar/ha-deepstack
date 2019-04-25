import sys
import logging
import time

from datetime import datetime
from homeassistant.util import slugify
from homeassistant.const import (CONF_HOST, CONF_PORT, ATTR_NAME, ATTR_ENTITY_ID, CONF_SSL)
from homeassistant.components.image_processing import (CONF_CONFIDENCE, DEFAULT_CONFIDENCE, EVENT_DETECT_FACE)

from .deepstack_api import DeepStackAPI
from .home_assistant import HomeAssistant
from .const import *

_LOGGER = logging.getLogger(__name__)


class DeepStack:
    def __init__(self, hass, config):
        host = config.get(CONF_HOST)
        port = config.get(CONF_PORT)
        ssl = config.get(CONF_SSL, False)
        admin_key = config.get(CONF_ADMIN_KEY)
        api_key = config.get(CONF_API_KEY)

        allow_backup_restore = admin_key is not None

        self._ha = HomeAssistant(hass, allow_backup_restore)
        self._api = DeepStackAPI(host, port, ssl, api_key, admin_key, self._ha.path_builder)
        self._is_api_connected = False
        self._is_initialized = False
        self._confidence = config.get(CONF_CONFIDENCE, DEFAULT_CONFIDENCE)
        self._unknown_directory = config.get(CONF_UNKNOWN_DIRECTORY, '')
        self._display_response_time = False
        self._allow_save_unknown_faces = self._ha.is_valid_directory_path(self._unknown_directory)
        self._processors = []

        def service_register_face(service):
            """Handle for services."""
            self.register(service.data)

        def service_display_response_time(service):
            """Handle for services."""
            enabled = service.data.get(ATTR_ENABLED, False)

            self._display_response_time = enabled

        def service_change_confidence_level(service):
            """Handle for services."""
            confidence_level = service.data.get(CONF_CONFIDENCE, self._confidence)

            self._confidence = confidence_level

        def service_list_faces(event_time):
            """Handle for services."""
            _LOGGER.debug(f'List faces called at: {event_time}')
            self.list_faces()

        def service_delete_face(service):
            """Handle for services."""
            self.delete_face(service.data)

        self._ha.initialize(service_change_confidence_level, service_display_response_time, service_register_face,
                            service_list_faces, service_delete_face)

        self._is_initialized = True

    @property
    def is_initialized(self):
        return self._is_initialized

    @property
    def processors(self):
        return self._processors

    @property
    def is_api_connected(self):
        return self._is_api_connected

    @property
    def confidence(self):
        return self._confidence

    @property
    def display_response_time(self):
        return self._display_response_time

    def add_processor(self, processor):
        self._processors.append(processor)

    def change_api_timeout(self, scan_interval):
        self._api.change_time_out(scan_interval)

    def list_faces(self):
        faces = self.get_registered_faces()

        faces_message = ', '.join(faces)

        message = f'Following faces found: {faces_message}'

        self._ha.display_message(message)

    def detect(self, image, camera_entity_id, targets, fire_event_on_detection=True):
        result = {
            COUNT: 0,
            TARGETS: []
        }

        if self.is_initialized:
            count = None
            target_list = {}

            predictions = self._api.detect(image)

            if predictions is not None:
                count = 0
                for prediction in predictions:
                    label = prediction.get(LABEL)
                    if label in targets:
                        target_count = 0

                        if label in target_list:
                            target_count = int(target_list[label])

                        target_list[label] = target_count + 1
                        count = count + 1

            result[COUNT] = count
            result[TARGETS] = target_list

            if count > 0 and fire_event_on_detection:
                event_data = {
                    ATTR_ENTITY_ID: camera_entity_id,
                    TARGETS: target_list
                }

                self._ha.fire_event(EVENT_DETECT_OBJECT, event_data)

            _LOGGER.debug(f'Detect result: {result}')

        else:
            _LOGGER.info(f'Detect called before fully initialized')

        return result

    def recognize(self, image, camera_entity_id, camera_name, detect_first):
        result = {
            FACES: [],
            ATTR_TOTAL_MATCHED_FACES: 0,
            ATTR_MATCHED_FACES: None,
            ATTR_RESPONSE_TIME_SEC: None
        }

        try:
            start_time = time.time()

            if self.is_initialized:
                faces = []
                matched_faces = []
                person_detected = True

                if detect_first:
                    person_detected = self.is_person_detected(image, camera_entity_id)
                else:
                    _LOGGER.debug(f'Skip person detection')

                if person_detected:
                    predictions = self._api.recognize(image)
                    unknown_faces = []

                    for prediction in predictions:
                        confidence = prediction.get(CONF_CONFIDENCE, 0)
                        confidence = round(confidence * 100, 1)

                        user_id = prediction.get(USER_ID)

                        face = {
                            USER_ID: user_id,
                            CONF_CONFIDENCE: confidence,
                            ATTR_ENTITY_ID: camera_entity_id,
                            ATTR_CAMERA_NAME: camera_name
                        }

                        faces.append(face)

                        if bool(user_id == UNKNOWN):
                            unknown_faces.append(face)

                            _LOGGER.debug(f'Unknown face found')
                        else:
                            matched_face_details = f'{user_id}: {confidence}'
                            _LOGGER.info(f'{matched_face_details} identified')

                            matched_faces.append(matched_face_details)

                            self.face_identified(face)

                    result[FACES] = faces
                    result[ATTR_TOTAL_MATCHED_FACES] = len(faces)
                    result[ATTR_MATCHED_FACES] = ', '.join(matched_faces)

                    unknown_faces_count = len(unknown_faces)

                    if unknown_faces_count > 0:
                        _LOGGER.info(f'{unknown_faces_count} Unknown faces found')

                        self.unknown_faces_detected(image, camera_entity_id, camera_name)

            else:
                _LOGGER.info(f'Recognize called before fully initialized')

            result[ATTR_RESPONSE_TIME_SEC] = round(time.time() - start_time, 1)
            result[ATTR_CONNECTED] = self.is_api_connected

        except Exception as ex:
            exc_type, exc_obj, tb = sys.exc_info()
            line_number = tb.tb_lineno

            _LOGGER.error(f'Failed to process image ({camera_name}), Error: {ex}, Line: {line_number}')

        _LOGGER.debug(f'Recognize result: {result}')

        return result

    def register(self, service_data):
        name = service_data.get(ATTR_NAME)
        image_path = service_data.get(FILE_PATH)

        is_valid_file_path = self._ha.is_valid_file_path(image_path)

        if is_valid_file_path:
            self._api.register_face(name, image_path)

        faces = self.get_registered_faces()
        faces_message = ', '.join(faces)

        message = f'{name} was registered, available faces: {faces_message}'

        self._ha.display_message(message)

    def delete_face(self, service_data):
        name = service_data.get(ATTR_NAME)

        self._api.delete_face(name)

        faces = self.get_registered_faces()
        faces_message = ', '.join(faces)

        message = f'{name} was deleted, available faces: {faces_message}'

        self._ha.display_message(message)

    def get_registered_faces(self):
        faces = self._api.list_faces()

        return faces

    def is_person_detected(self, image, camera_entity_id):
        result = False

        detect_result = self.detect(image, camera_entity_id, [TARGET_PERSON])

        person_data = detect_result.get(TARGETS, {})
        persons_found = person_data.get(TARGET_PERSON, 0)

        if persons_found > 0:
            result = True

        _LOGGER.debug(f'Person detection API result: {detect_result}, Final decision: {result}')

        return result

    def save_unknown_faces(self, image, camera_entity_id):
        file_path = None

        if self._allow_save_unknown_faces:
            current_date = slugify(datetime.now().strftime(DASHED_DATE_FORMAT))

            base_file_path = f'{self._unknown_directory}/{slugify(camera_entity_id)}_{current_date}'
            file_path = f'{base_file_path}.jpg'

            with open(file_path, 'wb') as img_file:
                img_file.write(image)

        return file_path

    def face_identified(self, face):
        confidence = face.get(CONF_CONFIDENCE, 0)

        if confidence >= self._confidence:
            self._ha.fire_event(EVENT_DETECT_FACE, face)

    def unknown_faces_detected(self, image, camera_entity_id, camera_name):
        file_path = self.save_unknown_faces(image, camera_entity_id)

        event_data = {
            ATTR_ENTITY_ID: camera_entity_id,
            ATTR_CAMERA_NAME: camera_name,
            FILE_PATH: file_path
        }

        self._ha.fire_event(EVENT_UNKNOWN_FACE_DETECT, event_data)
