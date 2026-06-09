from toolchain.nodes.property import PropertyDict


class SourceNode(PropertyDict):
    """Represents a source file entry.

    - src/main.cpp
    """
    pass


class DependencyNode(PropertyDict):
    """Represents a dependency entry.

    - my_lib
    - fmt
    """
    pass


class KissProjectTypeNode(PropertyDict):
    """Represents a project entry in kiss.yaml (bin, lib, dyn or custom type).

    - name: my_bin
      version: 0.1.0
      sources:
        - src/main.cpp
      dependencies:
        - my_lib
    """
    pass


class KissWorkspaceNode(PropertyDict):
    """Represents the root of kiss.yaml.

    Contains all project entries grouped by type,
    plus optional custom profiles and project types.
    """
    pass
