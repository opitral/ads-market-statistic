from enum import Enum
from config_reader import config


class Endpoint(Enum):
    BASE_URL = config.API_BASE_URL + "/api"
    GROUP = f"{BASE_URL}/group"
    POST = f"{BASE_URL}/post"

    def __str__(self):
        return self.value


class PostStatus(Enum):
    PUBLISHED = "PUBLISHED"
