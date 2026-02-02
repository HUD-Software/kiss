import console
from toolchain.compiler import CompilerList

class Target:
    def __init__(self, name: str, arch:str, vendor:str, os:str, env:str):
        # The compiler name
        self.name = name
        # The arch of the compiler
        self.arch = arch
        # The vendor of the compiler
        self.vendor = vendor
        # The os of the compiler
        self.os = os
        # The env of the compiler
        self.env = env
        # List of profiles
        self.suppported_compilers = CompilerList()

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


# class TargetRegistry:
#     def __init__(self):
#         self.targets = TargetList()
    
#     def __contains__(self, name: str) -> bool:
#         return name in self.targets

#     def __iter__(self):
#         return iter(self.targets)
    
#     def register_target(self, target: Target):
#         existing_target = self.targets.get(target.name)
#         if existing_target:
#             console.print_error(f"⚠️  Warning: Target already registered: {existing_target.name} in {str(existing_target.file)}")
#             exit(1)
#         self.targets.add(target)


# TargetRegistry = TargetRegistry()


