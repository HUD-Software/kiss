from enum import Enum

class Config(str, Enum):
    debug = "debug"
    release = "release"

class Compiler(str, Enum):
    cl = "cl"
    clang = "clang"
