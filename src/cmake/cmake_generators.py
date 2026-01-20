

# Enumeration of the project type that is supported
from enum import Enum

from platform_target import PlatformTarget



class CMakeGenerator(str, Enum):
    Ninja = "Ninja"
    UnixMakefiles = "Unix Makefiles"
    VisualStudio = "Visual Studio"

    def __str__(self):
        return self.name

    @classmethod
    def default_generator(cls, platform_target: PlatformTarget):
        if not getattr(cls, "default_generator_", None):
            match platform_target:
                case PlatformTarget.x86_64_pc_windows_msvc:
                    cls.default_generator_ = CMakeGenerator.VisualStudio
                case PlatformTarget.x86_64_unknown_linux_gnu:
                    cls.default_generator_ = CMakeGenerator.UnixMakefiles
        return cls.default_generator_
    
    @classmethod
    def available_generator_for_platform_target(cls, platform_target: PlatformTarget) -> list[str]: 
        return _TARGET_TO_GENERATORS[platform_target]


_TARGET_TO_GENERATORS: dict[PlatformTarget, list[str]] = {
    PlatformTarget.x86_64_pc_windows_msvc: [CMakeGenerator.VisualStudio, CMakeGenerator.Ninja],
    PlatformTarget.x86_64_pc_windows_gnu: [CMakeGenerator.Ninja, CMakeGenerator.UnixMakefiles],
    PlatformTarget.x86_64_unknown_linux_gnu: [CMakeGenerator.Ninja, CMakeGenerator.UnixMakefiles],
}
    
  