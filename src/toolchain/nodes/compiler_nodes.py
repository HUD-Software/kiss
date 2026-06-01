from toolchain.nodes.node import Node


class CompilerLinkerOverrideNode(Node):
    """Represents a per-linker feature override inside a compiler feature.
    e.g. link: { enable-features: [OPT_LEVEL_0] }
    """
    pass


class CompilerFeatureLinkerNode(Node):
    """Represents the 'linkers:' block inside a compiler feature.
    Contains global enable-features + per-linker overrides.
    """
    pass


class CompilerFeatureNode(Node):
    """Represents a single compiler feature entry.
    e.g. - name: OPT_LEVEL_0
           flags: [/Od]
           enable-features: [DEBUG_INFO]
           linkers: ...
    """
    pass


class CompilerFeatureRuleNode(Node):
    """Represents a feature rule (only-one or incompatible)."""
    pass


class CompilerNode(Node):
    """Represents a compiler entry (abstract or concrete).
    e.g. msvc-compiler, cl, clangcl
    """
    pass
