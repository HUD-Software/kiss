from enum import Enum
import platform

import console

class PlatformTarget(str, Enum):
    # <architecture>-<vendor>-<os>-<abi>
    x86_64_pc_windows_msvc = "x86_64-pc-windows-msvc" # Windows x86_64
    x86_64_unkwown_linux_gnu  = "x86_64-unknown-linux-gnu" # Linux x86_64
    x86_64_pc_windows_gnu = "x86_64-pc-windows-gnu" # Windows GNU / MinGW


    @classmethod
    def default_target(cls):
        if hasattr(cls, "_default_target"):
            return cls._default_target

        # Architecture
        match platform.machine():
            case "AMD64" | "x86_64":
                arch = "x86_64"
            case value:
                console.print_error(f"machine type not supported: {value}")
                raise RuntimeError

        # OS
        match platform.system():
            case "Windows":
                cls._default_target = cls.x86_64_pc_windows_msvc
            case "Linux":
                cls._default_target = cls.x86_64_unkwown_linux_gnu
            case value:
                console.print_error(f"OS not supported: {value}")
                raise RuntimeError

        return cls._default_target
