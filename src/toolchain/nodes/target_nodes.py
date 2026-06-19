from __future__ import annotations
from .property import Property, PropertyDict, PropertyStr, PropertyStrList


class TargetNode(Property):
    """Represents a build target definition in targets.yaml.

    A target describes a fully-qualified compilation platform using a triple-like
    convention (e.g. 'x86_64-pc-windows-msvc'), combining architecture, vendor,
    OS and ABI. It is the most specific layer in the resolution pipeline:

        linker → compiler → target → project-type → profile

    As such, it can specialize compiler and linker configuration at every level,
    making it the only layer capable of expressing intersections like
    "clangcl + dyn + release on x86_64 only".

    Key attributes:
    - arch: target architecture (x86_64, i686, aarch64, arm)
    - vendor: platform vendor (pc, unknown)
    - os: operating system (windows, linux, macos, none)
    - abi: binary interface (msvc, gnu, musl, none)
    - pointer-width: 32 or 64 bits
    - endianness: little or big
    - supported-compilers: list of compiler names compatible with this target
    - default-compiler: compiler selected when multiple supported compilers are available
    - compilers: compiler-side overrides scoped to this target, optionally
                 specialized per compiler (e.g. clangcl:)
    - linkers: linker-side overrides scoped to this target, optionally
               specialized per linker (e.g. msvc-linker:)
    - project-types: compiler/linker overrides scoped to a specific project type,
                     optionally specialized per compiler and per linker
                     (e.g. project-types.dyn.compilers.clangcl:)
    - profiles: compiler/linker overrides scoped to a specific profile, optionally
                specialized per compiler, per linker and per project-type
                (e.g. profiles.release.project-types.dyn.compilers.clangcl:)
    """
    def __init__(self, name : str):
        super().__init__(name)
        self._properties = PropertyDict()
    
    @property
    def properties(self) -> PropertyDict:
        return self._properties
    
    @property
    def default_compiler_name(self) -> str | None:
        return self.get_property_as("default-compiler", PropertyStr) or self.supported_compiler_names[0]

    @property
    def supported_compiler_names(self) -> list[str]:
        prop = self.get_property_as("supported-compilers", PropertyStrList)
        return prop.values if prop else []
    

    def get_property(self, name: str) -> Property | None:
        return self.properties.get_property(name)
    
    def add_property(self, property):
        self.properties.add_property(property)

    def clone(self) -> TargetNode:
        cloned  = TargetNode(self.name)
        cloned.properties = self._properties.clone()
        return cloned
    
    def merge_with_parent(self, parent):
        assert type(parent) is type(self), "Type mismatch"
        merged = TargetNode(self.name)
        merged._properties = self.properties.merge_with_parent(parent.properties)
        return merged
    
    def dispatch_globals(self) -> TargetNode:
        dispatched = TargetNode(self.name)
        for property in self.properties.values():
            property = property.dispatch_globals()
            dispatched.add_property(property)
        return dispatched