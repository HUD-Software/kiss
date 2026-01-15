from enum import Enum
from platform_target import PlatformTarget

class Compiler(str, Enum):
    cl = "cl"
    clang = "clang"
    gcc = "gcc"
    
    @classmethod
    def default_compiler(cls, platform_target: PlatformTarget):
        if not getattr(cls, "default_compiler_", None):
            match platform_target:
                case PlatformTarget.x86_64_pc_windows_msvc:
                    cls.default_compiler_ = Compiler.cl
                case PlatformTarget.x86_64_unkwown_linux_gnu:
                    cls.default_compiler_ = Compiler.gcc
        return cls.default_compiler_
