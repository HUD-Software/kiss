

from .node import Node

class LinkerFeatureArgsNode(Node):
    """Represents the 'args' block inside a linker feature with arguments.

    args:
      min: 1
      max: ~
      separator: ","
      pattern: "*.lib"
    """
    pass


class LinkerFeatureNode(Node):
    """Represents a single linker feature entry.

    - name: LINK
      description: Link with library
      args: ...
      flags: [/link {args}]
    """
    pass


class LinkerFeatureRuleNode(Node):
    """Represents a feature rule (only-one or incompatible)."""
    pass


class LinkerNode(Node):
    """Represents a linker entry (abstract or concrete).

    e.g. msvc-linker, link, lld-link
    """
    pass
