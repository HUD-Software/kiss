from .node import Node


class ProjectCompilersNode(Node):
    """Represents the 'compilers:' block inside a project type.

    compilers:
      enable-features: []
      defines: [KISS_BIN]
    """
    pass


class ProjectLinkerNode(Node):
    """Represents the 'linkers:' block inside a project type.

    linkers:
      enable-features: []
    """
    pass


class ProjectNode(Node):
    """Represents a project type entry (bin, lib, dyn or custom).

    - name: bin
      description: Executable binary
      extends: ...
      compilers: ...
      linkers: ...
    """
    pass
