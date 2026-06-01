from .node import Node

class ProfileCompilerOverrideNode(Node):
    """Represents a compiler-specific override block inside a profile.

    msvc-compiler:
      enable-features: [OPT_LEVEL_0, WINDOWS_DLL_RUNTIME_DEBUG]
      defines: []
    """
    pass


class ProfileLinkerOverrideNode(Node):
    """Represents a linker-specific override block inside a profile.

    msvc-linker:
      enable-features: [REMOVE_DEAD_CODE]
    """
    pass


class ProfileCompilersNode(Node):
    """Represents the 'compilers:' block inside a profile.

    compilers:
      enable-features: []
      defines: [KISS_DEBUG]
      msvc-compiler:
        enable-features: [OPT_LEVEL_0]
    """
    pass


class ProfileLinkerNode(Node):
    """Represents the 'linkers:' block inside a profile.

    linkers:
      enable-features: [ENABLE_INCREMENTAL_LINK]
      msvc-linker:
        enable-features: []
    """
    pass


class ProfileProjectNode(Node):
    """Represents a project-type override block inside a profile.

    dyn:
      compilers:
        enable-features: [DYNAMIC_LIBRARY_DEBUG]
      linkers:
        enable-features: []
    """
    pass


class ProfileNode(Node):
    """Represents a profile entry.

    - name: debug
      description: ...
      extends: ...
      compilers: ...
      linkers: ...
      projects: ...
    """
    pass
