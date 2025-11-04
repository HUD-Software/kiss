from enum import Enum

class PlatformTarget(str, Enum):
    x86_64_pc_windows_msvc = "x86_64-pc-windows-msvc"

    def default_target():
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
                return PlatformTarget.x86_64_pc_windows_msvc