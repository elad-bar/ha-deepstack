from datetime import timedelta
VERSION = '1.0.7'

DEFAULT_TIMEOUT = 10

DOMAIN = 'deepstack'
DATA_DEEP_STACK = f'{DOMAIN}_data'

DEEP_STACK_FACE_RECOGNITION = 'DeepStack Face Recognition'
DEEP_STACK_FACE_DETECTION = 'DeepStack Face Detection'

FILE_PATH = 'file_path'
SERVICE_REGISTER_FACE = 'register_face'
SERVICE_CHANGE_DETECT_FIRST = 'change_detected_first'
SERVICE_DISPLAY_RESPONSE_TIME = 'display_response_time'
SERVICE_CHANGE_CONFIDENCE_LEVEL = 'change_confidence_level'
SERVICE_LIST_FACES = 'list_faces'
SERVICE_DELETE_FACE = 'delete_face'

ATTR_CONNECTED = 'connected'
ATTR_MATCHED_FACES = 'matched_faces'
ATTR_TOTAL_MATCHED_FACES = 'total_matched_faces'
ATTR_RESPONSE_TIME_SEC = 'response time (sec)'

USER_ID = 'userid'
UNKNOWN = 'unknown'
SUCCESS = 'success'
ERROR = 'error'
IMAGE = 'image'
PREDICTIONS = 'predictions'
FACES = 'faces'
LABEL = 'label'
COUNT = 'count'
TARGETS = 'targets'

CONF_FACE_RECOGNITION = 'face_recognition'
CONF_OBJECT_DETECTION = 'object_detection'

CONF_DETECT_FIRST = 'detect_first'
CONF_TARGETS = 'targets'

ATTR_ENABLED = 'enabled'

ATTR_CAMERA_NAME = 'name'

DASHED_DATE_FORMAT = '%Y-%m-%d %H-%M-%S'

CONF_UNKNOWN_DIRECTORY = 'unknown_directory'

EVENT_UNKNOWN_FACE_DETECT = f'{DOMAIN}.unknown_face_detected'
EVENT_DETECT_OBJECT = f'{DOMAIN}.object_detected'

IMAGE_TIMEOUT = timedelta(seconds=5)

PROTOCOLS = {
    True: "https",
    False: "http"
}

ENDPOINT_BASE = '/v1/vision/'
ENDPOINT_BASE_FACE = f'{ENDPOINT_BASE}face/'

ENDPOINT_BACKUP = f'{ENDPOINT_BASE}backup'
ENDPOINT_RESTORE = f'{ENDPOINT_BASE}restore'

ENDPOINT_FACE_DELETE = f'{ENDPOINT_BASE_FACE}delete'
ENDPOINT_FACE_LIST = f'{ENDPOINT_BASE_FACE}list'
ENDPOINT_FACE_REGISTER = f'{ENDPOINT_BASE_FACE}register'
ENDPOINT_FACE_RECOGNIZE = f'{ENDPOINT_BASE_FACE}recognize'

ENDPOINT_DETECTION = f'{ENDPOINT_BASE}detection'

BACKUP_FILE = "backup-deepstack.zip"

NOTIFICATION_FACE_LIST = 'DeepStack trained faces'

CONF_ADMIN_KEY = 'admin_key'
CONF_API_KEY = 'api_key'

TARGET_PERSON = 'person'

SUPPORTED_TARGETS = [
    TARGET_PERSON,
    'bicycle',
    'car',
    'motorcycle',
    'airplane',
    'bus',
    'train',
    'truck',
    'boat',
    'traffic light',
    'fire hydrant',
    'stop_sign',
    'parking meter',
    'bench',
    'bird',
    'cat',
    'dog',
    'horse',
    'sheep',
    'cow',
    'elephant',
    'bear',
    'zebra',
    'giraffe',
    'backpack',
    'umbrella',
    'handbag',
    'tie',
    'suitcase',
    'frisbee',
    'skis',
    'snowboard',
    'sports ball',
    'kite',
    'baseball bat',
    'baseball glove',
    'skateboard',
    'surfboard',
    'tennis racket',
    'bottle',
    'wine glass',
    'cup',
    'fork',
    'knife',
    'spoon',
    'bowl',
    'banana',
    'apple',
    'sandwich',
    'orange',
    'broccoli',
    'carrot',
    'hot dog',
    'pizza',
    'donot',
    'cake',
    'chair',
    'couch',
    'potted plant',
    'bed',
    'dining table',
    'toilet',
    'tv',
    'laptop',
    'mouse',
    'remote',
    'keyboard',
    'cell phone',
    'microwave',
    'oven',
    'toaster',
    'sink',
    'refrigerator',
    'book',
    'clock',
    'vase',
    'scissors',
    'teddy bear',
    'hair dryer',
    'toothbrush'
]
