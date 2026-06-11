from toolchain.nodes.property import PropertyDict

class FeatureArgsNode(PropertyDict):
    """Represents the 'args' block inside a feature with arguments.
    args:
      min: 1
      max: ~
      separator: ","
      pattern: "*.lib"
    """
    pass

class FeatureNode(PropertyDict):
    """Represents a single compiler feature entry.
    e.g. - name: OPT_LEVEL_0
           flags: [/Od]
           enable-features: [DEBUG_INFO]
           args: ...
    """
    pass

class FeatureRuleNode(PropertyDict):
    """Represents a feature rule (only-one or incompatible)."""
    pass