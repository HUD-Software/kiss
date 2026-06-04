from toolchain.nodes.node import Node, PropertyBool, PropertyStr


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

    @property
    def is_abstract(self) -> bool :
        prop = self.get_property_as("is_abstract", PropertyBool)
        return prop.value if prop else False
    
    @property
    def default_linker_name(self) -> str | None:
        prop = self.get_property_as("default-linker", PropertyStr)
        return prop.value if prop else None
    

    # def merge_with_parent(self, parent: 'CompilerNode') -> 'CompilerNode':
    #     result = CompilerNode(self.name)
    #     for name, prop in self.properties.items():
    #         parent_prop = parent.get_property(name)
    #         if not parent_prop:
    #             result.add_property(prop.clone())
    #         else:
    #             result.add_property(prop.merge_with_parent(parent_prop))
    #     return result
            
                



   

