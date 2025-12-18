from enum import Enum

class PlatformTarget(str, Enum):
    x86_64_pc_windows_msvc = "x86_64-pc-windows-msvc"

    @classmethod
    def default_target(cls):
        if not getattr(cls, "_default_target", None):
            import platform
            import console
            match platform.machine():
                case "AMD64":
                    machine = "x86_64"
                case _ as value:
                    console.print_error(f"machine type not supported : {value}")

            match platform.system():
                case "Windows":
                    system = "pc-windows-msvc"
                case _ as value:
                    console.print_error(f"machine type not supported : {value}")

            match [machine, system]:
                case ["x86_64", "pc-windows-msvc"]:
                    cls._default_target = PlatformTarget.x86_64_pc_windows_msvc
        return cls._default_target