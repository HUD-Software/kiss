from __future__ import annotations
from toolchain.nodes.feature_node import FeatureNodeList, FeatureRuleNodeList
from toolchain.nodes.property import PropertyBool, PropertyDict, Property

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
        prop = self.properties.get_property_as("is_abstract", PropertyBool)
        return prop.value if prop else False
    
    @property
    def features(self) -> FeatureNodeList:
        prop = self.properties.get_property_as(FeatureNodeList.NAME, FeatureNodeList)
        return prop
    
    @property
    def feature_rules(self) -> FeatureRuleNodeList:
        prop = self.properties.get_property_as(FeatureRuleNodeList.NAME, FeatureRuleNodeList)
        return prop
    
    def get_property(self, name: str) -> Property | None:
        return self.properties.get_property(name)
    
    def add_property(self, property):
        self.properties.add_property(property)

    def clone(self) -> LinkerNode:
        cloned  = LinkerNode(self.name)
        cloned.properties = self._properties.clone()
        return cloned
    
    def merge_with_parent(self, parent):
        assert type(parent) is type(self), "Type mismatch"
        merged = LinkerNode(self.name)
        merged._properties = self.properties.merge_with_parent(parent.properties)
        return merged
    
    def dispatch_globals(self) -> LinkerNode:
        dispatched = LinkerNode(self.name)
        for property_name, property in self.properties.items():
            if property_name == FeatureNodeList.NAME or property_name == FeatureRuleNodeList.NAME:
                property = property.dispatch_globals()
            dispatched.add_property(property)
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
    pass

class LinkersOverrideNode(Property):
    """Represents the 'linkers:' block.
    Contains global enable-features + per-linker overrides 'LinkerSpecificOverrideNode' nodes.

    linkers: # LinkersOverrideNode
      lld-link : 
        enable-features: []
      ...
    """
    pass

