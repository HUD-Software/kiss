from enum import Enum

class Config(str, Enum):
    debug = "debug"
    release = "release"

    def default_config():
        return Config.debug