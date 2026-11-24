from __future__ import annotations
import copy
from result import Err, Ok, Result
from toolchain.nodes.feature_node import FeatureNodeList, FeatureRuleNodeList, FeatureStrList, InvalidExtends, ValidationError, resolve_extends_feature_list
from toolchain.nodes.property import  StrList, resolve_extends_str_list

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
    
    def resolve_extends(self, parent: LinkerNode) -> Result[LinkerNode, ValidationError]:
        result = LinkerNode(self.name)
        result.is_abstract = self.is_abstract
        result.extends = self.extends   
        
        if not parent:
            result.feature_rule_list = self.feature_rule_list.resolve_extends(FeatureRuleNodeList())
            match self.feature_list.resolve_extends(FeatureNodeList(), result.feature_rule_list):
                case Err() as err:
                    return err
                case Ok(feature_list):
                    result.feature_list = feature_list
        else:
            result.feature_rule_list = self.feature_rule_list.resolve_extends(parent.feature_rule_list)
            match self.feature_list.resolve_extends(parent.feature_list, result.feature_rule_list):
                case Err() as err:
                    return err
                case Ok(feature_list):
                    result.feature_list = feature_list
        return Ok(result)
        
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

    def resolve_extends(self, parent: LinkerSpecificOverrideNode | None, linker_feature_rules: FeatureRuleNodeList) -> Result[LinkerSpecificOverrideNode, ValidationError]:
        if parent:
            if(self.name != parent.name):
                return Err(InvalidExtends(self.name, parent.name))

        parent_flags = parent.flags if parent else StrList()
        parent_features = parent.features if parent else FeatureStrList()

        result = LinkerSpecificOverrideNode(self.name)
        result.flags = resolve_extends_str_list(self.flags, parent_flags)
        match resolve_extends_feature_list(self.features,parent_features, linker_feature_rules):
            case Err() as err:
                return err
            case Ok(feature_list):
                result.features = feature_list
        return Ok(result)
    
    def apply_remove(self):
        result = LinkerSpecificOverrideNode(self.name)
        result.flags = self.flags.apply_remove()
        result.features = self.features.apply_remove()
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

    def resolve_extends(self, parent: LinkersOverrideNode | None,  linkers : dict[str, LinkerNode]) -> Result[LinkersOverrideNode, ValidationError]:
        result = LinkersOverrideNode()
        
        # Apply all `remove` modifiers of the common part first, so that the linker-specific
        # overrides (LinkerSpecificOverrideNode) are then resolved against an already-cleaned base.
        # We deliberately avoid `resolve_extends` here: it would consume the `remove` modifiers,
        # which the extends resolution of the linker overrides still needs.
        self_common_linker_remove_applied = self.common_linker.apply_remove()

        if parent:
            def merge_str_list_with_parent(self_str_list: StrList, self_common_str_list: StrList, parent_str_list: StrList):
                # If self common or self str list override ignore parent
                # Merge list the common
                override = self_common_str_list.override or self_str_list.override
                # If common list don't have values we merge with parent
                base = self_common_str_list if override else resolve_extends_str_list(self_common_str_list, parent_str_list)
                return resolve_extends_str_list(self_str_list, base)
                
            def merge_feature_str_list_with_parent(self_feature_str_list: FeatureStrList, self_common_feature_str_list: FeatureStrList, parent_feature_str_list: FeatureStrList, feature_rules: FeatureRuleNodeList) -> Result[FeatureStrList, ValidationError]:
                # If self common or self feature str list override ignore parent
                # Merge list the common
                if self_common_feature_str_list.override or self_feature_str_list.override:
                    base = self_common_feature_str_list
                # If common list don't have values we merge with parent
                else:
                    match resolve_extends_feature_list(self_common_feature_str_list, parent_feature_str_list, feature_rules):
                        case Err() as err:
                            return err
                        case Ok(base):
                            pass
                return resolve_extends_feature_list(self_feature_str_list, base, feature_rules)
                        
            # Merge all self linker override with common and parent
            for linker_override_name, linker_override in self.linker_overrides.items():
                result_override = LinkerSpecificOverrideNode(linker_override_name)
                parent_linker_override = parent.linker_overrides.get(linker_override_name)

                # Merge flags
                # If the parent have a specific linker, merge with it else merge with common
                parent_linker_flags = (parent_linker_override.flags if parent_linker_override else None) or parent.common_linker.flags
                result_override.flags = merge_str_list_with_parent(linker_override.flags, self_common_linker_remove_applied.flags, parent_linker_flags)

                # Merge features
                parent_linker_features = (parent_linker_override.features if parent_linker_override else None) or parent.common_linker.features
                linker_feature_rules = rules.feature_rule_list if (rules := linkers.get(linker_override_name)) else FeatureRuleNodeList()
                match merge_feature_str_list_with_parent(linker_override.features, self_common_linker_remove_applied.features, parent_linker_features, linker_feature_rules):
                    case Err() as err:
                        return err
                    case Ok(feature_list):
                            result_override.features = feature_list

                result.linker_overrides[linker_override_name] = result_override
                
            # Copy all parent linker override that are not in self
            for linker_override_name, parent_linker_override in parent.linker_overrides.items():
                if linker_override_name not in self.linker_overrides:
                    result_override = LinkerSpecificOverrideNode(linker_override_name)
                    result_override.flags.remove_modifiers = copy.deepcopy(parent_linker_override.flags.remove_modifiers)
                    result_override.features.remove_modifiers = copy.deepcopy(parent_linker_override.features.remove_modifiers)
    
                    # Extends flags
                    extended_common_flags = resolve_extends_str_list(self_common_linker_remove_applied.flags, parent_linker_override.flags)
                    result_override.flags = resolve_extends_str_list(result_override.flags, extended_common_flags)
                    
                    
                    # Extends features
                    linker_feature_rules = rules.feature_rule_list if (rules := linkers.get(linker_override_name)) else FeatureRuleNodeList()
                    match resolve_extends_feature_list(self_common_linker_remove_applied.features, parent_linker_override.features, linker_feature_rules):
                        case Err() as err:
                            return err
                        case Ok(feature_list):
                            match resolve_extends_feature_list(result_override.features, feature_list, linker_feature_rules):
                                case Err() as err:
                                    return err
                                case Ok(feature_list):
                                    result_override.features = feature_list
                    result.linker_overrides[linker_override_name] = result_override
        else:
            for linker_override_name, linker_override in self.linker_overrides.items():
                result_override = LinkerSpecificOverrideNode(linker_override_name)
                # Remove flags specified in common if no value is specified in linker override
                result_override.flags = resolve_extends_str_list(linker_override.flags, self_common_linker_remove_applied.flags)         
                # Remove features specified in common if no value is specified in linker override
                linker_feature_rules = rules.feature_rule_list if (rules := linkers.get(linker_override_name)) else FeatureRuleNodeList()
                match resolve_extends_feature_list(linker_override.features, self_common_linker_remove_applied.features, linker_feature_rules):
                    case Err() as err:
                        return err
                    case Ok(feature_list):
                        result_override.features = feature_list
                result.linker_overrides[linker_override_name] = result_override

        result.common_linker = self_common_linker_remove_applied
        return Ok(result)