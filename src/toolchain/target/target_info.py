class TargetInfo:
    def __init__(self, name: str, arch:str, vendor:str, os:str, abi:str):
        # The target name
        self.name = name
        # The arch of the target
        self.arch = arch
        # The vendor of the target
        self.vendor = vendor
        # The os of the target
        self.os = os
        # The abi of the target
        self.abi = abi
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
            f"  - abi : {self.abi}",
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


