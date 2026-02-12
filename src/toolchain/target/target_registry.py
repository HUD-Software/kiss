import os
import platform
import struct
import subprocess
import console

class Target:
    def __init__(self, name: str, arch:str, vendor:str, os:str, abi:str):
        # The compiler name
        self.name = name
        # The arch of the compiler
        self.arch = arch
        # The vendor of the compiler
        self.vendor = vendor
        # The os of the compiler
        self.os = os
        # The abi of the compiler
        self.abi = abi
        # Size of the pointer
        self.pointer_width = int
        # Endianness ( little or big )
        self.endianness = str
    
    def is_windows_os(self) -> bool:
        return self.os == "windows"
    
    def is_linux_os(self) -> bool:
        return self.os == "linux"
    
    def is_msvc_abi(self) -> bool:
        return self.abi == "msvc"
    
    def is_gnu_abi(self) -> bool: 
        return self.abi == "gnu"
    
    def is_x86_64(self) -> bool:
        return self.arch == "x86_64"
    
    def is_i686(self) -> bool:
        return self.arch == "i686"

    def is_aarch64(self) -> bool:
        return self.arch == "aarch64"
    
    def is_arm(self) -> bool:
        return self.arch == "arm"
    
    @classmethod
    def default_target_name(cls):
        if not hasattr(cls, "_default_target_name"):
            ARCH_MAP = {
                "amd64": "x86_64",
                "x86_64": "x86_64",
                "i386": "i686",
                "i686": "i686",
                "x86": "i686",
                "arm64": "aarch64",
                "aarch64": "aarch64",
                "arm": "arm",
                "armv7l": "arm",
                "armv6l": "arm",
            }

            system = platform.system()
            arch = ""
            vendor = ""
            os_name = ""
            abi = ""
            
            if system == "Windows":
                arch = os.environ.get("PROCESSOR_ARCHITECTURE", "").lower()
                arch_w6432 = os.environ.get("PROCESSOR_ARCHITEW6432", "").lower()
                if arch_w6432:
                    arch = arch_w6432
                vendor = "pc"
                os_name = "windows"
                abi = "msvc"
            elif system in ("Linux", "Darwin"):
                try:
                    arch = subprocess.check_output(["uname", "-m"]).decode().strip().lower()
                except Exception:
                    pointer_size = struct.calcsize("P") * 8
                    arch = "x86_64" if pointer_size == 64 else "i686"

                if system == "Linux":
                    vendor = "unknown"
                    os_name = "linux"
                    abi = "gnu"
                elif system == "Darwin":
                    vendor = "apple"
                    os_name = "darwin"
                    abi = ""
            else:
                pointer_size = struct.calcsize("P") * 8
                arch = "x86_64" if pointer_size == 64 else "i686"
                vendor = "unknown"
                os_name = system.lower()
                abi = "gnu"

            arch = ARCH_MAP.get(arch, arch)

            if abi:
                target_name = f"{arch}-{vendor}-{os_name}-{abi}"
            else:
                target_name = f"{arch}-{vendor}-{os_name}"

            cls._default_target_name = target_name
        return cls._default_target_name
    def _build_repr(self) -> str:
        lines = [
            f"Target: {self.name}",
            f"  - arch: {self.arch}",
            f"  - vendor: {self.vendor}",
            f"  - os: {self.os}",
            f"  - abi: {self.abi}",
            f"  - endianness: {self.endianness}",
            f"  - pointer width: {self.pointer_width}"
        ]
        return "\n".join(lines)

    def __repr__(self) -> str:
        return self._build_repr()

    def __str__(self) -> str:
        return self._build_repr()
    
class TargetList:
    def __init__(self):
        self.targets : set[Target] = set()

    def __iter__(self):
        return iter(self.targets)
    
    def __len__(self):
        return len(self.targets)
    
    def __contains__(self, item) -> bool:
        if isinstance(item, Target):
            return item in self.targets
        if isinstance(item, str):
            return any(t.name == item for t in self.targets)
        return False

    def add(self, target:Target):
        self.targets.add(target)

    def get(self, target_name: str) -> Target | None:
        for t in self.targets:
            if t.name == target_name:
                return t
        return None



################################################
# List of targets loaded by files
################################################
class TargetRegistry:
    def __init__(self):
        self.targets = TargetList()
    
    def __contains__(self, target_name: str) -> bool:
        return target_name in self.targets

    def __iter__(self):
        return iter(self.targets)
    
    def get(self, target_name: str) -> Target | None:
        return self.targets.get(target_name)
    
    def register_compiler(self, target: Target):
        existing_target = self.targets.get(target.name)
        if existing_target:
            console.print_error(f"Error: Target '{existing_target.name}' already registered {str(existing_target.file)}")
            exit(1)
        self.targets.add(target)


TargetRegistry = TargetRegistry()
