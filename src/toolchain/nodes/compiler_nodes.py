
from toolchain.nodes.property import Property, PropertyBool, PropertyDict, PropertyStr, PropertyStrList
from toolchain.parsers.parse_utils import parse_property

class CompilerLinkerOverrideNode(PropertyDict):
    """Represents a per-linker feature override inside a compiler feature.
    e.g. link: { enable-features: [OPT_LEVEL_0] }
    """
    pass

class CompilerFeatureLinkersNode(PropertyDict):
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

    # @classmethod
    # def from_yaml_dict(cls, yaml: dict):
    #     node = cls(name=yaml["name"], inheritable=True)

    #     for key, value in yaml.items():
    #         if key == "name":
    #             continue
    #         if key == "features" and isinstance(value, list):
    #             node.add_property(PropertyDict(key, [
    #                 CompilerFeatureNode.from_yaml_dict(f) for f in value
    #             ]))
    #             continue
    #         if key == "feature-rules" and isinstance(value, list):
    #             node.add_property(PropertyDict("feature-rules", [
    #                 CompilerFeatureRuleNode.from_yaml_dict(r) for r in value
    #             ]))
    #             continue
    #         prop = parse_property(key, value)
    #         if prop:
    #             node.add_property(prop)
    #     return node

    @property
    def supported_linkers(self) -> list[str]:
        prop = self.get_property_as("supported_linkers", PropertyStrList)
        return prop.values if prop else None
    
    @property
    def is_abstract(self) -> bool :
        prop = self.get_property_as("is_abstract", PropertyBool)
        return prop.value if prop else False
    
    @property
    def default_linker_name(self) -> str | None:
        prop = self.get_property_as("default-linker", PropertyStr)
        return prop.value if prop else None
    
    
    