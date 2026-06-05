from toolchain.nodes.node import PropertyDict, PropertyBool, PropertyStr


class CompilerLinkerOverrideNode(PropertyDict):
    """Represents a per-linker feature override inside a compiler feature.
    e.g. link: { enable-features: [OPT_LEVEL_0] }
    """
    pass


class CompilerFeatureLinkerNode(PropertyDict):
    """Represents the 'linkers:' block inside a compiler feature.
    Contains global enable-features + per-linker overrides.
    """
    pass


class CompilerFeatureNode(PropertyDict):
    """Represents a single compiler feature entry.
    e.g. - name: OPT_LEVEL_0
           flags: [/Od]
           enable-features: [DEBUG_INFO]
           linkers: ...
    """
    pass


class CompilerFeatureRuleNode(PropertyDict):
    """Represents a feature rule (only-one or incompatible)."""
    pass


class CompilerNode(PropertyDict):
    """Represents a compiler entry (abstract or concrete).
    e.g. msvc-compiler, cl, clangcl
    """
    
    @property
    def is_abstract(self) -> bool :
        prop = self.get_property_as("is_abstract", PropertyBool)
        return prop.value if prop else False
    
    @property
    def default_linker_name(self) -> str | None:
        prop = self.get_property_as("default-linker", PropertyStr)
        return prop.value if prop else None
    