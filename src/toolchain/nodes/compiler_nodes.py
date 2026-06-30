
from __future__ import annotations
import copy
from toolchain.nodes.feature_node import FeatureNode, FeatureNodeList, FeatureRuleNodeList
from toolchain.nodes.linker_nodes import LinkersOverrideNode
from toolchain.nodes.property import Property, PropertyBool, PropertyDict, PropertyStr, PropertyStrList
from typing import TypeVar, Type
T = TypeVar("T", bound=Property)

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
        self._feature_list = FeatureNodeList()
        
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
    
    @property
    def feature_list(self) -> FeatureNodeList:
        return self._feature_list
    
    @feature_list.setter
    def feature_list(self, feature_list):
        self._feature_list = feature_list

    @property
    def feature_rules(self) -> FeatureRuleNodeList:
        prop = self.get_property_as(FeatureRuleNodeList.NAME, FeatureRuleNodeList)
        return prop
    
    def get_property(self, name: str) -> Property | None:
        return self.properties.get_property(name)
    
    def add_property(self, property):
        self.properties.add_property(property)
    
    def get_property_as(self, name: str, prop_type: Type[T]) -> T | None:
        return self.properties.get_property_as(name, prop_type)

    def merge_with(self, parent: CompilerNode):
        """Merge list without applying modifier or dispatching top to bottom hierarchy """
        assert type(parent) is type(self), "Type mismatch"
        merged = CompilerNode(self.name)
        merged._properties = self.properties.merge_with(parent.properties)
        merged._feature_list = self._feature_list.merge_with(parent._feature_list)
        return merged
    
    def apply_modifiers(self) -> CompilerNode:
        """Apply list modifier"""
        applied  = CompilerNode(self.name)
        applied._properties = self.properties.apply_modifiers()
        applied._feature_list = self._feature_list.apply_modifiers()
        return applied
        
    def dispatch(self) -> CompilerNode:
        """ 
        Dispatch properties from top to bottom hierarchy
        """
        dispatched = CompilerNode(self.name)
        dispatched._properties = copy.deepcopy(self.properties)
        dispatched.feature_list = self.feature_list.dispatch()
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
    
    def resolve_extends(self, parent):
        assert type(parent) is type(self), "Type mismatch"
        merged = CompilerSpecificOverrideNode(self.name)
        merged._properties = self.properties.resolve_extends(parent.properties)
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

    def resolve_extends(self, parent):
        assert type(parent) is type(self), "Type mismatch"
        merged = CompilersOverrideNode(self.name)
        merged._properties = self.properties.resolve_extends(parent.properties)
        return merged

class CompilerFeatureNode(FeatureNode):

    def __init__(self, name:str):
        super().__init__(name)
        # The 'linkers:' node
        self.linkers : LinkersOverrideNode = None

    def merge_with(self, other: CompilerFeatureNode):
        merged = CompilerFeatureNode(self.name)
        merged._properties = self.properties.merge_with(other.properties)
        if other.linkers:
            if self.linkers:
                merged.linkers = self.linkers.merge_with(other.linkers)
            else:
                merged.linkers = copy.deepcopy(other.linkers)
        return merged
    
    def apply_modifiers(self) -> FeatureNodeList:
        result = CompilerFeatureNode(self.name)
        result._properties = self.properties.apply_modifiers()
        if self.linkers:
            result.linkers = self.linkers.apply_modifiers()
        return result

    def dispatch(self) -> CompilerFeatureNode:
        result = CompilerFeatureNode(self.name)
        result._properties = copy.deepcopy(self.properties)
        if self.linkers:
            result.linkers = self.linkers.dispatch(result.properties)
        return result