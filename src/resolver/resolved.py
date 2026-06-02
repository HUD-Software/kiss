from dataclasses import dataclass, field


@dataclass
class ResolvedFlags:
    """
    Final result of the resolution pipeline for one project.
    Ready to be consumed by a generator.
    """
    project_name:    str
    project_type:    str                  # bin, lib, dyn, ...
    profile:         str                  # debug, release, asan, ...
    compiler:        str                  # cl, clangcl, ...
    linker:          str                  # link, lld-link, ...

    # Compiler
    compiler_flags:  list[str] = field(default_factory=list)
    defines:         list[str] = field(default_factory=list)

    # Linker
    linker_flags:    list[str] = field(default_factory=list)

    # Active feature names (for debug/info purposes)
    active_compiler_features: list[str] = field(default_factory=list)
    active_linker_features:   list[str] = field(default_factory=list)

    def summary(self) -> str:
        lines = [
            f"Project  : {self.project_name} ({self.project_type})",
            f"Profile  : {self.profile}",
            f"Compiler : {self.compiler}",
            f"Linker   : {self.linker}",
            f"",
            f"Compiler features : {self.active_compiler_features}",
            f"Compiler flags    : {self.compiler_flags}",
            f"Defines           : {self.defines}",
            f"",
            f"Linker features   : {self.active_linker_features}",
            f"Linker flags      : {self.linker_flags}",
        ]
        return "\n".join(lines)
