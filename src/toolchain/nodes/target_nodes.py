from .property import PropertyDict, PropertyStr, PropertyStrList


class TargetLinkerNode(PropertyDict):
    """Represents the 'linkers:' block inside a target.

    linkers:
      enable-features: [TARGET_X64]
    """
    pass


class TargetCompilerOverrideNode(PropertyDict):
    """Represents a compiler-specific override block inside a target.

    clangcl:
      features:
        - name: ASAN
          linkers:
            enable-features: [LINK:msvcrt.lib]
    """
    pass


class TargetCompilerFeatureOverrideNode(PropertyDict):
    """Represents a feature override for a specific compiler inside a target.

    - name: ASAN
      linkers:
        enable-features: [LINK:msvcrt.lib]
    """
    pass


class TargetNode(PropertyDict):
    """Represents a build target entry.

    - name: x86_64-pc-windows-msvc
      arch: x86_64
      vendor: pc
      os: windows
      abi: msvc
      pointer-width: 64
      endianness: little
      supported-compilers: [clangcl, cl]
      default-compiler: cl
      linkers: ...
      compilers: ...
    """

    @property
    def default_compiler_name(self) -> str | None:
        return self.get_property_as("default-compiler", PropertyStr) or self.supported_compiler_names[0]

    @property
    def supported_compiler_names(self) -> list[str]:
        prop = self.get_property_as("supported-compilers", PropertyStrList)
        return prop.values if prop else []