from __future__ import annotations
from toolchain.nodes.feature_node import FeatureNodeList, FeatureRuleNodeList
from toolchain.nodes.property import PropertyBool, PropertyDict

class LinkerNode(PropertyDict):
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
    

    def dispatch_globals(self) -> LinkerNode:
       # Linker have no specialisation.
       # Unlike compiler or profile, we don't have compiler block with global to dispatch to specifics
       # like in compilers we have:
       # - name: OPT_LEVEL_0
       #   description: No optimization # Description of the feature
       #   flags: [/Od]
       #   enable-features: [DEBUG_INFO]
       #   linkers:
       #     enable-features: []
       #     link:
       #       enable-features: [OPT_LEVEL_0]
       #     lld-link:
       #       enable-features: [OPT_LEVEL_0]
       #
       pass 
        

class LinkerSpecificOverrideNode(PropertyDict):
  
    """Represents a per-linker override inside a 'linkers:' node.
    
    linkers:
      lld-link : # LinkerSpecificOverrideNode
        enable-features: []
      link : # LinkerSpecificOverrideNode
        enable-features: []
      ...

    """
    pass

class LinkersOverrideNode(PropertyDict):
    """Represents the 'linkers:' block.
    Contains global enable-features + per-linker overrides 'LinkerSpecificOverrideNode' nodes.

    linkers: # LinkersOverrideNode
      lld-link : 
        enable-features: []
      ...
    """
    pass

