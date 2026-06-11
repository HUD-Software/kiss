
from toolchain.nodes.feature_node import FeatureNode, FeatureRuleNode
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


class CompilerNode(PropertyDict):
    """Represents a compiler entry (abstract or concrete).
    e.g. msvc-compiler, cl, clangcl
    """

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
    
    
    