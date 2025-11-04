from enum import Enum

class Compiler(str, Enum):
    cl = "cl"
    clang = "clang"

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
                return Compiler.cl

