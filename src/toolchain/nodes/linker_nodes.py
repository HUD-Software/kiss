from __future__ import annotations
import copy
from toolchain.nodes.feature_node import FeatureNodeList, FeatureRuleNodeList, FeatureStrList, merge_feature_list
from toolchain.nodes.property import  StrList, merge_str_list

class LinkerNode:
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
        self.name = name
        self.is_abstract = False
        self.extends = None
        self.feature_list = FeatureNodeList()
        self.feature_rule_list = FeatureRuleNodeList()
    
    def __eq__(self, other):
        if not isinstance(other, LinkerNode):
            return NotImplemented
        return self.name == other.name

    def __hash__(self):
        return hash(self.name)
    
    def merge_with(self, parent: LinkerNode):
        if not parent:
            return copy.deepcopy(self)
        """Merge list without applying modifier or dispatching top to bottom hierarchy """
        assert type(parent) is type(self), "Type mismatch"
        result = LinkerNode(self.name)
        result.is_abstract = self.is_abstract
        result.extends = self.extends
        # Apply modifier during merge before merging the feature list
        # We want to merge feature list according the rules, we must merge feature rule with parent 
        # but also resolve modifier to validate
        result.feature_rule_list = self.feature_rule_list.merge_with(parent.feature_rule_list).apply_modifiers()
        result.feature_list = self.feature_list.merge_with(parent.feature_list, result.feature_rule_list)
        return result
    
    def apply_modifiers(self) -> LinkerNode:
        """Apply list modifier"""
        result  = LinkerNode(self.name)
        result.is_abstract = self.is_abstract
        result.extends = self.extends
        result.feature_rule_list = copy.deepcopy(self.feature_rule_list)
        result.feature_list = self.feature_list.apply_modifiers(result.feature_rule_list)
        return result
        
    def dispatch(self) -> LinkerNode:
        """ 
        Dispatch properties from top to bottom hierarchy
        """
        result = LinkerNode(self.name)
        result.is_abstract = self.is_abstract
        result.extends = self.extends
        result.feature_list = copy.deepcopy(self.feature_list)
        result.feature_rule_list = copy.deepcopy(self.feature_rule_list)
        return result

    def resolve_extends(self, parent: LinkerNode) -> LinkerNode:
        if parent:
            assert parent.name == self.extends
            node = self.merge_with(parent)
        else:
            node = copy.deepcopy(self)
        node = node.dispatch()
        #node = node.apply_modifiers()
        return node
        
class LinkerSpecificOverrideNode:
    """Represents a per-linker override inside a 'linkers:' node.
    
    linkers:
      lld-link : # LinkerSpecificOverrideNode
        enable-features: []
        add-flags: []
      link : # LinkerSpecificOverrideNode
        enable-features: []
        add-flags: []
      ...

    """
    def __init__(self, name : str):
        self.name = name
        self.flags = StrList()
        self.features = FeatureStrList ()

    def __eq__(self, other):
        if not isinstance(other, LinkerSpecificOverrideNode):
            return NotImplemented
        return self.name == other.name

    def __hash__(self):
        return hash(self.name)
   
    def apply_modifiers(self, linker_feature_rules: FeatureRuleNodeList) -> LinkerSpecificOverrideNode:
        result = LinkerSpecificOverrideNode(self.name)
        result.flags = self.flags.apply_modifiers()
        result.features = self.features.apply_modifiers(linker_feature_rules)
        return result
    
    def merge_with(self, parent: LinkerSpecificOverrideNode, linker_feature_rules: FeatureRuleNodeList) -> LinkerSpecificOverrideNode:
        result = LinkerSpecificOverrideNode(self.name)
        result.flags = merge_str_list(self.flags, parent.flags)
        result.features = merge_feature_list(self.features, parent.features, linker_feature_rules)
        return result
        
class LinkersOverrideNode:
    """Represents the 'linkers:' block.
    Contains global enable-features + per-linker overrides 'LinkerSpecificOverrideNode' nodes.

    linkers: # LinkersOverrideNode
      enable-features: []
      add-flags: []
      lld-link : 
        enable-features: []
        add-flags: []
      link:
        enable-features: []
        add-flags: []
      ...
    """
    def __init__(self):
        self.common_linker = LinkerSpecificOverrideNode("")
        self.linker_overrides = dict[str, LinkerSpecificOverrideNode]()

    def merge_with(self, parent: LinkersOverrideNode, linkers : dict[str, LinkerNode]):
        result = LinkersOverrideNode()

        # Merge common linker with the parent common linker without feature rule list
        # We can't use feature rule list because it is bound too the linker itself.
        # We just merge with all know linker after and validate the merge here
        # We could wait for the dispatch step, but if we do it now, we can have better understanding of where the bad merge appears
        result.common_linker = self.common_linker.merge_with(parent.common_linker, FeatureRuleNodeList())
        for linker in linkers.values():
            features = merge_feature_list(
                self.common_linker.features,
                parent.common_linker.features,
                linker.feature_rule_list
            )
            linker.feature_rule_list.validate(features.apply_modifiers(linker.feature_rule_list).values)

        # Merge linker overrides
        # - Merge if present in parent and self
        # - If not present in parent, keep it
        # - Add parent that are not in self
        for linker_override_name, linker_override in self.linker_overrides.items():
            if linker_override_name in parent.linker_overrides:
                result.linker_overrides[linker_override_name] = linker_override.merge_with(parent.linker_overrides[linker_override_name], linkers[linker_override_name].feature_rule_list)
            else:
                result.linker_overrides[linker_override_name] = copy.deepcopy(linker_override)

        for parent_linker_override_name, parent_linker_override in parent.linker_overrides.items():
            if not parent_linker_override_name in self.linker_overrides:
                result.linker_overrides[parent_linker_override_name] = copy.deepcopy(parent_linker_override)
                
        return result
    
    def apply_modifiers(self, linkers : dict[str, LinkerNode]) -> LinkersOverrideNode:
        result = LinkersOverrideNode()
        result.common_linker = self.common_linker.apply_modifiers(FeatureRuleNodeList())
        for linker in linkers.values():
            result.common_linker.apply_modifiers(linker.feature_rule_list)
                
        for linker_override_name, linker_override in self.linker_overrides.items():
            result.linker_overrides[linker_override_name] = linker_override.apply_modifiers(linkers[linker_override_name].feature_rule_list)
        return result
        

    def dispatch(self, linkers : dict[str, LinkerNode]) -> LinkersOverrideNode:
        result = LinkersOverrideNode()
        result.common_linker = copy.deepcopy(self.common_linker)
        for linker_override_name, linker_override in self.linker_overrides.items():
            if linker_override_name in linkers:
                result.linker_overrides[linker_override_name] = linker_override.merge_with(result.common_linker, linkers[linker_override_name].feature_rule_list)
        return result


def merge_linkers_override_node(child: LinkersOverrideNode, parent: LinkersOverrideNode, linkers : dict[str, LinkerNode] ):
    if child and parent:
        return child.merge_with(parent, linkers)
    elif child:
        return copy.deepcopy(child)
    elif parent:
        return copy.deepcopy(parent)