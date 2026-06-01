from .node import Node


class TargetLinkerNode(Node):
    """Represents the 'linkers:' block inside a target.

    linkers:
      enable-features: [TARGET_X64]
    """
    pass


class TargetCompilerOverrideNode(Node):
    """Represents a compiler-specific override block inside a target.

    clangcl:
      features:
        - name: ASAN
          linkers:
            enable-features: [LINK:msvcrt.lib]
    """
    pass


class TargetCompilerFeatureOverrideNode(Node):
    """Represents a feature override for a specific compiler inside a target.

    - name: ASAN
      linkers:
        enable-features: [LINK:msvcrt.lib]
    """
    pass


class TargetNode(Node):
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
    pass
