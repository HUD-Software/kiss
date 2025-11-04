from config import Config


def config_to_cmake_config(config: Config):
    match config:
        case Config.debug:
            return "Debug"
        case Config.release:
            return "Release"