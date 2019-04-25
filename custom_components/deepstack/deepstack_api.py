import sys
import logging
import shutil
import requests

from .const import *

_LOGGER = logging.getLogger(__name__)


class DeepStackAPI:
    """Perform a face classification."""

    def __init__(self, host, port, ssl, api_key, admin_key, path_builder):
        """Init with the API key and model id."""
        protocol = PROTOCOLS[ssl]

        deepstack_url = f'{protocol}://{host}:{port}'

        self._api_key = api_key
        self._admin_key = admin_key

        self._face_detect_url = f'{deepstack_url}{ENDPOINT_DETECTION}'

        self._face_recognize_url = f'{deepstack_url}{ENDPOINT_FACE_RECOGNIZE}'
        self._face_register_url = f'{deepstack_url}{ENDPOINT_FACE_REGISTER}'
        self._face_delete_url = f'{deepstack_url}{ENDPOINT_FACE_DELETE}'
        self._face_list_url = f'{deepstack_url}{ENDPOINT_FACE_LIST}'

        self._backup_url = f'{deepstack_url}{ENDPOINT_BACKUP}'
        self._restore_url = f'{deepstack_url}{ENDPOINT_RESTORE}'

        self._backup_path = path_builder(BACKUP_FILE)
        self._connected = False
        self._timeout = DEFAULT_TIMEOUT

    def change_time_out(self, timeout):
        self._timeout = timeout

    @property
    def is_connected(self):
        return self._connected

    def enrich_data(self, data=None):
        if data is None:
            data = {}

        if self._api_key is not None:
            data[CONF_API_KEY] = self._api_key

        return data

    def enrich_admin_data(self, data=None):
        if data is None:
            data = {}

        if self._admin_key is not None:
            data[CONF_ADMIN_KEY] = self._admin_key

        return data

    def recognize(self, image):
        """Post an image to the classifier."""
        failure_error_message = f'Failed to recognize faces in the image, URL: {self._face_recognize_url}'

        response = []

        connected = False

        try:
            data = self.enrich_data()

            response_data = requests.post(self._face_recognize_url, files={IMAGE: image}, data=data, timeout=self._timeout)

            response_data.raise_for_status()

            json = response_data.json()

            if PREDICTIONS in json:
                response = json[PREDICTIONS]

                connected = True
            else:
                _LOGGER.error(f'{failure_error_message}, Invalid response: {json}')

        except requests.exceptions.ConnectionError as cex:
            _LOGGER.error(f'{failure_error_message}, Communication error: {cex}')

        except Exception as ex:
            exc_type, exc_obj, tb = sys.exc_info()
            line_number = tb.tb_lineno

            _LOGGER.error(f'{failure_error_message}, Error: {ex}, Line: {line_number}')
        finally:
            self._connected = connected

        return response

    def detect(self, image):
        """Post an image to the classifier."""
        failure_error_message = f'Failed to detect object in the image, URL: {self._face_detect_url}'

        response = []

        connected = False

        try:
            data = self.enrich_data()

            response_data = requests.post(self._face_detect_url, files={IMAGE: image}, data=data, timeout=self._timeout)

            response_data.raise_for_status()

            json = response_data.json()

            if PREDICTIONS in json:
                response = json[PREDICTIONS]

                connected = True
            else:
                _LOGGER.error(f'{failure_error_message}, Invalid response: {json}')

        except requests.exceptions.ConnectionError as cex:
            _LOGGER.error(f'{failure_error_message}, Communication error: {cex}')

        except Exception as ex:
            exc_type, exc_obj, tb = sys.exc_info()
            line_number = tb.tb_lineno

            _LOGGER.error(f'{failure_error_message}, Error: {ex}, Line: {line_number}')
        finally:
            self._connected = connected

        return response

    def register_face(self, name, file_path):
        """ Register a name to a file. """
        failure_error_message = f'Failed to register face for {name}, URL: {self._face_register_url}'
        try:
            data = self.enrich_data({USER_ID: name})

            with open(file_path, "rb") as image:
                response = requests.post(self._face_register_url, files={IMAGE: image.read()}, data=data)

            response.raise_for_status()

            if response.json()[SUCCESS]:
                _LOGGER.info(f'Register face for {name} using file {file_path}')
            else:
                error = response.json()[ERROR]

                _LOGGER.warning(f'{failure_error_message}, Error message: {error}')

        except requests.exceptions.ConnectionError as cex:
            _LOGGER.error(f'{failure_error_message}, Communication error: {cex}')
        except Exception as ex:
            exc_type, exc_obj, tb = sys.exc_info()
            line_number = tb.tb_lineno

            _LOGGER.error(f'{failure_error_message}, from file: {file_path}, Error: {ex}, Line: {line_number}')

    def delete_face(self, name):
        try:
            _LOGGER.info(f'Deleting face of: {name}')

            data = self.enrich_data({USER_ID: name})

            response = requests.post(self._face_delete_url, data=data, timeout=self._timeout)

            response.raise_for_status()

            json = response.json()

            _LOGGER.info(f'Face ({name}) deleting result for: {json}')
        except Exception as ex:
            exc_type, exc_obj, tb = sys.exc_info()
            line_number = tb.tb_lineno

            _LOGGER.error(f'Delete face failed, URL: {self._face_delete_url}, Error: {ex}, Line: {line_number}')

    def list_faces(self):
        faces = None
        try:
            data = self.enrich_data()

            response = requests.post(self._face_list_url, data, timeout=self._timeout)

            response.raise_for_status()

            faces = response.json()[FACES]

            _LOGGER.info(f'Following faces are listed: {faces}')
        except Exception as ex:
            exc_type, exc_obj, tb = sys.exc_info()
            line_number = tb.tb_lineno

            _LOGGER.error(f'Restore failed, URL: {self._face_list_url}, Error: {ex}, Line: {line_number}')

        return faces

    def backup(self):
        try:
            _LOGGER.info('Backing up...')

            request_data = self.enrich_admin_data()

            data = requests.post(self._backup_url, stream=True, data=request_data)

            with open(self._backup_path, "wb") as file:
                shutil.copyfileobj(data.raw, file)

            del data

            _LOGGER.info(f'Backup store to: {self._backup_path}')
        except Exception as ex:
            exc_type, exc_obj, tb = sys.exc_info()
            line_number = tb.tb_lineno

            _LOGGER.error(f'Backup failed, URL: {self._backup_url}, Error: {ex}, Line: {line_number}')

    def restore(self):
        try:
            _LOGGER.info(f'Restoring from: {self._backup_path}')

            request_data = self.enrich_admin_data()

            image_data = open(self._backup_path, "rb").read()

            response = requests.post(self._restore_url, files={"file": image_data}, data=request_data)

            response.raise_for_status()

            _LOGGER.info(f'Restore result: {response.json()}')
        except Exception as ex:
            exc_type, exc_obj, tb = sys.exc_info()
            line_number = tb.tb_lineno

            _LOGGER.error(f'Restore failed, URL: {self._restore_url}, Error: {ex}, Line: {line_number}')
