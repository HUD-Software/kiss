

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
    def available_generator_for_platform_target(cls, target: Target) -> list[str]: 
        if target.is_windows_os(): 
            if target.is_msvc_abi():
                return [CMakeGenerator.VisualStudio, CMakeGenerator.Ninja]
            elif target.is_gnu_abi(): 
                return [CMakeGenerator.Ninja, CMakeGenerator.UnixMakefiles]
        elif target.is_linux_os() or target.is_macos(): 
            return [CMakeGenerator.Ninja, CMakeGenerator.UnixMakefiles]
