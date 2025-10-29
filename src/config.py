from enum import Enum

class Config(str, Enum):
    debug = "debug"
    release = "release"