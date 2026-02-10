from pathlib import Path
import console

class TargetInfo:
    def __init__(self, name: str, arch:str, vendor:str, os:str, env:str):
        # The target name
        self.name = name
        # The arch of the target
        self.arch = arch
        # The vendor of the target
        self.vendor = vendor
        # The os of the target
        self.os = os
        # The env of the target
        self.env = env
        # Size of the pointer
        self.pointer_width = int
        # Endianness ( little or big )
        self.endianness = str

    def __hash__(self) -> int:
        return hash(self.name)

    def __eq__(self, other) -> bool:
        if not isinstance(other, TargetInfo):
            return NotImplemented
        return self.name == other.name
 
    def _build_repr(self) -> str:
        lines = [
            f"{self.__class__.__name__} : {self.name}",
            f"  - arch : {self.arch}",
            f"  - vendor : {self.vendor}",
            f"  - os : {self.os}",
            f"  - env : {self.env}",
            f"  - pointer_width : {self.pointer_width}",
            f"  - endianness : {self.endianness}"
        ]
        return "\n".join(lines)

    def __repr__(self) -> str:
        return self._build_repr()

    def __str__(self) -> str:
        return self._build_repr()
    
class TargetInfoList:
    def __init__(self):
        self.targets : set[TargetInfo] = set()

    def __iter__(self):
        return iter(self.targets)
    
    def __len__(self):
        return len(self.targets)
    
    def __contains__(self, item) -> bool:
        if isinstance(item, TargetInfo):
            return item in self.targets
        if isinstance(item, str):
            return any(t.name == item for t in self.targets)
        return False

    def add(self, target:TargetInfo):
        self.targets.add(target)

    def get(self, name: str) -> TargetInfo | None:
        for t in self.targets:
            if t.name == name:
                return t
        return None


################################################
# List of targets loaded by files
################################################
class TargetInfoRegistry:
    def __init__(self):
        self.targets = TargetInfoList()
    
    def __contains__(self, target_name: str) -> bool:
        return target_name in self.targets

    def __iter__(self):
        return iter(self.targets)
    
    def get(self, target_name: str) -> TargetInfo | None:
        return self.targets.get(target_name)
    
    def register_compiler(self, target: TargetInfo):
        existing_target = self.targets.get(target.name)
        if existing_target:
            console.print_error(f"⚠️  Warning: Compiler already registered: {existing_target.name} in {str(existing_target.file)}")
            exit(1)
        self.targets.add(target)


TargetInfoRegistry = TargetInfoRegistry()
