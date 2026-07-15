from __future__ import annotations
import copy
from toolchain.nodes.feature_node import FeatureNode, FeatureNodeList, FeatureRuleNodeList
from toolchain.nodes.property import PropertyBool, PropertyDict, Property
from typing import TypeVar, Type
T = TypeVar("T", bound=Property)

class LinkerNode(Property):
    """Represents a linker definition in linkers.yaml.

    A linker node can be abstract (base template, e.g. 'msvc-linker') or concrete
    (e.g. 'link', 'lld-link'). Concrete linkers can extend an abstract one via 'extends',
    inheriting its features and feature-rules while adding or overriding their own.

    Key attributes:
    - is_abstract: if True, this node is a base template and cannot be used directly
    - features: linker flags grouped by named capability (e.g. LTO, TARGET_X64)
    - feature_rules: constraints between features (only-one and incompatible)

    Some features support parameterized arguments (e.g. LINK accepts one or more
    .lib filenames separated by commas), contrasting with simple flag-based features.
    Linker features can also be activated indirectly by compiler features via their
    'linkers' sub-key in compilers.yaml.
    """
    def __init__(self, name : str):
        super().__init__(name)
        self._properties = PropertyDict()
        self.feature_list = FeatureNodeList()
        self.feature_rule_list = FeatureRuleNodeList()
      
    @property
    def properties(self) -> PropertyDict:
        return self._properties
    
    @property
    def is_abstract(self) -> bool :
        prop = self.get_property_as("is_abstract", PropertyBool)
        return prop.value if prop else False
    
    def get_property(self, name: str) -> Property | None:
        return self.properties.get_property(name)
    
    def add_property(self, property):
        self.properties.add_property(property)

    def get_property_as(self, name: str, prop_type: Type[T]) -> T | None:
        return self.properties.get_property_as(name, prop_type)
        
    def merge_with(self, parent: LinkerNode):
        if not parent:
            return copy.deepcopy(self)
        """Merge list without applying modifier or dispatching top to bottom hierarchy """
        assert type(parent) is type(self), "Type mismatch"
        merged = LinkerNode(self.name)
        merged._properties = self.properties.merge_with(parent.properties)
        merged.feature_rule_list = self.feature_rule_list.merge_with(parent.feature_rule_list)
        merged.feature_list = self.feature_list.merge_with(parent.feature_list)
        return merged
    
    def apply_modifiers(self) -> LinkerNode:
        """Apply list modifier"""
        applied  = LinkerNode(self.name)
        applied._properties = self.properties.apply_modifiers()
        applied.feature_list = self.feature_list.apply_modifiers()
        applied.feature_rule_list = copy.deepcopy(self.feature_rule_list)
        return applied
        
    def dispatch(self) -> LinkerNode:
        """ 
        Dispatch properties from top to bottom hierarchy
        """
        dispatched = LinkerNode(self.name)
        dispatched._properties = copy.deepcopy(self.properties)
        dispatched.feature_list = self.feature_list.dispatch()
        dispatched.feature_rule_list = copy.deepcopy(self.feature_rule_list)
        return dispatched
        
class LinkerSpecificOverrideNode(Property):
    """Represents a per-linker override inside a 'linkers:' node.
    
    linkers:
      lld-link : # LinkerSpecificOverrideNode
        enable-features: []
      link : # LinkerSpecificOverrideNode
        enable-features: []
      ...

    """
    def __init__(self, name : str):
      super().__init__(name)
      self._properties = PropertyDict()
      self.feature_list = FeatureNodeList()
      self.feature_rule_list = FeatureRuleNodeList()

    @property
    def properties(self) -> PropertyDict:
        return self._properties
    
    def get_property(self, name: str) -> Property | None:
        return self.properties.get_property(name)
    
    def add_property(self, property):
        self.properties.add_property(property)

    def apply_modifiers(self) -> LinkerSpecificOverrideNode:
        result = LinkerSpecificOverrideNode(self.name)
        result._properties = self.properties.apply_modifiers()
        result.feature_list = self.feature_list.apply_modifiers()
        result.feature_rule_list = self.feature_rule_list.apply_modifiers()
        return result
    
    def merge_with(self, other: LinkerSpecificOverrideNode, parent_list_name_to_ignore: set[str] = None) -> LinkerSpecificOverrideNode:
        if not other:
            return copy.deepcopy(self)
        assert self.name == other.name, "Name mismatch"
        result = LinkerSpecificOverrideNode(self.name)
        result._properties = self.properties.merge_with(other.properties, parent_list_name_to_ignore)
        result.feature_list = self.feature_list.merge_with(other.feature_list)
        result.feature_rule_list = self.feature_rule_list.merge_with(other.feature_rule_list)
        return result
    
    def dispatch(self, properties : PropertyDict) -> LinkerSpecificOverrideNode:
        result = LinkerSpecificOverrideNode(self.name)
        result._properties = self.properties.dispatch(properties)
        result.feature_list = self.feature_list.dispatch()
        result.feature_rule_list = self.feature_rule_list.dispatch()
        return result
    
class LinkersOverrideNode(Property):
    """Represents the 'linkers:' block.
    Contains global enable-features + per-linker overrides 'LinkerSpecificOverrideNode' nodes.

    linkers: # LinkersOverrideNode
      enable-features: []
      lld-link : 
        enable-features: []
      link:
        enable-features: []
      ...
    """

    NAME = "linkers"
    def __init__(self, name : str= NAME):
        super().__init__(name)
        self._properties = PropertyDict()
        self._linkers = dict[str, LinkerSpecificOverrideNode]()

    @property
    def properties(self) -> PropertyDict:
        return self._properties

    def get_property(self, name: str) -> Property | None:
        return self.properties.get_property(name)
    
    def add_property(self, property):
        self.properties.add_property(property)
    
    def add_linker(self, linker:LinkerSpecificOverrideNode):
        self._linkers[linker.name] = linker

    def merge_with(self, other: LinkersOverrideNode, parent_list_name_to_ignore: set[str] = None):
        if not other:
            return copy.deepcopy(self)
        result = LinkersOverrideNode(self.name)
        result._properties = self.properties.merge_with(other.properties, parent_list_name_to_ignore)
        
        if parent_list_name_to_ignore:
            parent_list_name_to_ignore.update(self.properties.explicit_list_names())
        else :
            parent_list_name_to_ignore = self.properties.explicit_list_names()

        for linker in self._linkers.values():
            other_linker = other._linkers.get(linker.name)
            if other_linker: # linker in both
                result.add_linker(linker.merge_with(other_linker, parent_list_name_to_ignore))
            else: # linker only in self
                result.add_linker(copy.deepcopy(linker))
        
        for linker_name, other_linker in other._linkers.items():
            if linker_name not in self._linkers: # Only in parents
                self_linker = LinkerSpecificOverrideNode(other_linker.name)
                result.add_linker(self_linker.merge_with(other_linker, parent_list_name_to_ignore))

        return result
    
    def apply_modifiers(self) -> LinkersOverrideNode:
        result = LinkersOverrideNode(self.name)
        result._properties = self.properties.apply_modifiers()
        for linker in self._linkers.values():
            result.add_linker(linker.apply_modifiers())
        return result

    def dispatch(self, properties: PropertyDict) -> LinkersOverrideNode:
        result = LinkersOverrideNode(self.name)
        result._properties = self.properties.dispatch(properties)
        for linker in self._linkers.values():
            result.add_linker(linker.dispatch(result.properties))
        return result