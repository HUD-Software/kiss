

# Enumeration of the project type that is supported
from enum import Enum
import platform
from typing import Self

from toolchain import Toolchain, Target

class CMakeGenerator(str, Enum):
    Ninja = "Ninja"
    UnixMakefiles = "Unix Makefiles"
    VisualStudio = "Visual Studio"

    def __str__(self):
        return self.name

    @classmethod
    def default_generator(cls, toolchain: Toolchain):
        if not getattr(cls, "default_generator_", None):
            match toolchain.target.name:
                case "x86_64-pc-windows-msvc":
                    cls.default_generator_ = CMakeGenerator.VisualStudio
                case "x86_64-unknown-linux-gnu":
                    cls.default_generator_ = CMakeGenerator.UnixMakefiles
        return cls.default_generator_
    
    @classmethod
    def available_generator_for_platform_target(cls, target: Target) -> list[str]: 
        return _TARGET_TO_GENERATORS.get(target.name, [])

_TARGET_TO_GENERATORS: dict[str, list[type]] = {
    "x86_64-pc-windows-msvc": [CMakeGenerator.VisualStudio, CMakeGenerator.Ninja],
    "x86_64-pc-windows-gnu": [CMakeGenerator.Ninja, CMakeGenerator.UnixMakefiles],
    "x86_64-unknown-linux-gnu": [CMakeGenerator.Ninja, CMakeGenerator.UnixMakefiles],
}
  