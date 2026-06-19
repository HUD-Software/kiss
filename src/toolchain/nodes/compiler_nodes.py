
from __future__ import annotations
from toolchain.nodes.feature_node import FeatureNode, FeatureNodeList, FeatureRuleNode, FeatureRuleNodeList
from toolchain.nodes.property import Property, PropertyBool, PropertyDict, PropertyStr, PropertyStrList
from toolchain.parsers.parse_utils import parse_property


class CompilerNode(Property):
    """Represents a compiler definition in compilers.yaml.

    A compiler node can be abstract (base template, e.g. 'msvc-compiler') or concrete
    (e.g. 'cl', 'clangcl'). Concrete compilers can extend an abstract one via 'extends',
    inheriting its features and feature-rules while adding or overriding their own.

    Key attributes:
    - supported_linkers: list of linker names compatible with this compiler
    - default_linker: preferred linker when multiple supported linkers are available
    - is_abstract: if True, this node is a base template and cannot be used directly
    - features: compiler flags grouped by named capability (e.g. OPT_LEVEL_2, ASAN)
    - feature_rules: constraints between features (only-one and incompatible)

    Features can cascade to the linker layer via their 'linkers' sub-key,
    enabling linker-specific features when a given compiler feature is activated.
    """
    def __init__(self, name : str):
        super().__init__(name)
        self._properties = PropertyDict()
    
    @property
    def properties(self) -> PropertyDict:
        return self._properties
    
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
    
    def get_property(self, name: str) -> Property | None:
        return self.properties.get_property(name)
    
    def add_property(self, property):
        self.properties.add_property(property)

    def clone(self) -> CompilerNode:
        cloned  = CompilerNode(self.name)
        cloned.properties = self._properties.clone()
        return cloned
    
    def merge_with_parent(self, parent):
        assert type(parent) is type(self), "Type mismatch"
        merged = CompilerNode(self.name)
        merged._properties = self.properties.merge_with_parent(parent.properties)
        return merged
    
    def dispatch_globals(self) -> CompilerNode:
        dispatched = CompilerNode(self.name)
        for property_name, property in self.properties.items():
            if property_name == FeatureNodeList.NAME or property_name == FeatureRuleNodeList.NAME:
                property = property.dispatch_globals()
            dispatched.add_property(property)
        return dispatched
    
class CompilerSpecificOverrideNode(Property):
    """Represents a per-compiler override inside a 'compilers:' node.

    compilers:
      gcc : # CompilerSpecificOverrideNode
        enable-features: []
        defines: []
      ...
    """
    def __init__(self, name : str):
      super().__init__(name)
      self._properties = PropertyDict()

    @property
    def properties(self) -> PropertyDict:
        return self._properties
    
    def get_property(self, name: str) -> Property | None:
        return self.properties.get_property(name)
    
    def add_property(self, property):
        self.properties.add_property(property)

    def clone(self) -> CompilerSpecificOverrideNode:
        cloned  = CompilerSpecificOverrideNode(self.name)
        cloned._properties = self._properties.clone()
        return cloned
    
    def merge_with_parent(self, parent):
        assert type(parent) is type(self), "Type mismatch"
        merged = CompilerSpecificOverrideNode(self.name)
        merged._properties = self.properties.merge_with_parent(parent.properties)
        return merged
    

class CompilersOverrideNode(Property):
    """Represents the 'compilers:' block.
    Contains global enable-features + per-compiler overrides 'CompilerSpecificOverrideNode' nodes.

    compilers: # CompilersOverrideNode
      gcc : 
        enable-features: []
        defines: []
      ...
    """
    NAME = "compilers"
    def __init__(self, name : str= NAME):
      super().__init__(name)
      self._properties = PropertyDict()

    @property
    def properties(self) -> PropertyDict:
        return self._properties
    
    def get_property(self, name: str) -> Property | None:
        return self.properties.get_property(name)
    
    def add_property(self, property):
        self.properties.add_property(property)

    def clone(self) -> CompilersOverrideNode:
        cloned  = CompilersOverrideNode(self.name)
        cloned._properties = self._properties.clone()
        return cloned
    
    def merge_with_parent(self, parent):
        assert type(parent) is type(self), "Type mismatch"
        merged = CompilersOverrideNode(self.name)
        merged._properties = self.properties.merge_with_parent(parent.properties)
        return merged


class CompilerFeatureNode(FeatureNode):
    def dispatch_globals(self) -> FeatureNodeList:
        dispatched = super().clone()
        return dispatched