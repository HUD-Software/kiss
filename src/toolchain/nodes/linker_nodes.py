from __future__ import annotations
import copy
from toolchain.nodes.feature_node import FeatureNodeList, FeatureRuleNodeList
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
      
    @property
    def properties(self) -> PropertyDict:
        return self._properties
    
    @property
    def is_abstract(self) -> bool :
        prop = self.get_property_as("is_abstract", PropertyBool)
        return prop.value if prop else False
    
    @property
    def features(self) -> FeatureNodeList:
        prop = self.get_property_as(FeatureNodeList.NAME, FeatureNodeList)
        return prop
     
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
        
    # def clone(self) -> LinkerNode:
    #     cloned  = LinkerNode(self.name)
    #     cloned._properties = self._properties.clone()
    #     return cloned
    
    def resolve_extends(self, parent):
        assert type(parent) is type(self), "Type mismatch"
        merged = LinkerNode(self.name)
        merged._properties = self.properties.resolve_extends(parent.properties)
        return merged
    
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

    @property
    def properties(self) -> PropertyDict:
        return self._properties
    
    def get_property(self, name: str) -> Property | None:
        return self.properties.get_property(name)
    
    def add_property(self, property):
        self.properties.add_property(property)

    # def clone(self) -> LinkerSpecificOverrideNode:
    #     cloned  = LinkerSpecificOverrideNode(self.name)
    #     cloned._properties = self._properties.clone()
    #     return cloned
    
    def merge_with_properties(self, properties):
        merged = LinkerSpecificOverrideNode(self.name)
        merged._properties = self.properties.merge_with_properties(properties)
        return merged
    
    def resolve_extends(self, parent):
        assert type(parent) is type(self), "Type mismatch"
        return self.merge_with_properties(parent.properties)

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

    def resolve_extends(self, parent):
        assert type(parent) is type(self), "Type mismatch"
        merged = LinkersOverrideNode(self.name)
        
        # Merge global properties under 'linkers.'
        merged._properties = self.properties.resolve_extends(parent.properties)

        # loop through all linkers: 'link', 'lld-link', etc...
        # Merge if parent is in self, add if not in self
        for parent_linker_name, parent_linker in parent._linkers.items():
            self_linker = self._linkers.get(parent_linker_name)
            if self_linker is not None:
                merged.add_linker(self_linker.resolve_extends(parent_linker))
            else:
                merged.add_linker(copy.deepcopy(parent_linker))
   
        # Add 'linkers' that are not in parent
        for self_linker in self._linkers:
            if self_linker not in parent._linkers:
                merged.add_linker(copy.deepcopy(parent_linker))

        return merged
    
    def merge_with_properties(self, properties: PropertyDict):
        merged = LinkersOverrideNode(self.name)
        # Merge global properties in 'linkers:'
        merged._properties = self.properties.merge_with_properties(properties)
        # Merge newly merged glabl properties to each 'linker'
        for linker in self._linkers.values():
            merged.add_linker(linker.merge_with_properties(merged._properties))
        return merged