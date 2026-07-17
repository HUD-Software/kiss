from toolchain.nodes.feature_node import FeatureArgsNode, FeatureNode, FeatureNodeList, FeatureRuleNode, FeatureRuleNodeIncompatible, FeatureRuleNodeList, FeatureRuleNodeOnlyOne
from toolchain.nodes.property import StrList
from typing import TypeVar

from toolchain.parsers.parse_utils import try_parse_list_modifier
T = TypeVar("T", bound="FeatureNode")


def yaml_parse_feature_list(data: dict) -> FeatureNodeList:
    feature_list = FeatureNodeList()
    for f in data:
        feature_list.add_feature(yaml_parse_feature(f))
    return feature_list


def yaml_parse_feature_rule_list(data:dict) -> FeatureRuleNodeList:
    feature_rule_list = FeatureRuleNodeList()
    for fr in data:
        feature_rule_list.add_feature_rule(yaml_parse_feature_rule(fr))
    return feature_rule_list

def yaml_parse_feature_args(data:dict, feature_name:str) -> FeatureArgsNode:
    args = FeatureArgsNode()
    for key, value in data.items():
        match key:
            case "min":
                if not isinstance(value, int):
                    raise ValueError(f"'min' must be a integer value ({feature_name})")
                args.min = value
            case "max":
                if value is not None and not isinstance(value, int):
                    raise ValueError(f"'max' must be a integer value ({feature_name})")
                args.max = value
            case "separator":
                if not isinstance(value, str):
                    raise ValueError(f"'separator' must be a string value ({feature_name})")
                args.separator = value
            case _:
                raise ValueError(f"'{key}: {value}' is not a valid key ({feature_name})")
    return args

def yaml_parse_feature(data: dict) -> FeatureNode:
    # Feature need 'name'
    name = data.get("name")
    if not name or not isinstance(name, str):
        raise ValueError("Missing 'name' for feature as string")

    # optional description
    description = data.get("description", "")
    if description and not isinstance(description, str):
        raise ValueError("'description' for feature must be a string")
    
    # Create the feature and load informations
    node = FeatureNode(name)
    for key, value in data.items():
        match key:
            case "name":
                pass
            case "description":
                if not isinstance(value, str):
                    raise ValueError(f"'description' must be a string value ({name})")
                node.description = value
            case "args":
                if not isinstance(value, dict):
                    raise ValueError(f"'args' must be a composed values -> {value} in ({name})")
                node.args = yaml_parse_feature_args(value, name)
            case _:
                if try_parse_list_modifier("flags", node.flags, key, value):
                    continue
                else:    
                    raise ValueError(f"'{key}:{value}' is not a valid key ({name})")
    return node

ALLOWED_RULE_KINDS = {FeatureRuleNodeOnlyOne.RULE_NAME, FeatureRuleNodeIncompatible.RULE_NAME}
def yaml_parse_feature_rule(data: dict) -> FeatureRuleNode:
    """Parse a single feature rule (only-one or incompatible)."""
    kind = next(iter(data))
    if kind not in ALLOWED_RULE_KINDS:
        raise ValueError(
            f"Unknown feature rule '{kind}', expected one of {sorted(ALLOWED_RULE_KINDS)}"
        )
    
    # Is it 'only-one' rule?
    if FeatureRuleNodeOnlyOne.RULE_NAME in data:
        name = None
        feature_names = StrList()
        for key, value in data.items():
            match key:
                case FeatureRuleNodeOnlyOne.RULE_NAME:
                    if not value or not isinstance(value, str):
                        raise ValueError(f"{FeatureRuleNodeOnlyOne.RULE_NAME!r} of feature rule must be a string")
                    name = value
                case _:
                    if try_parse_list_modifier("features", feature_names, key, value):
                        continue
                    else:    
                        raise ValueError(f"'{key}:{value}' is not a valid key ({name})")
                    
        if not name:
            raise ValueError(f"Missing {FeatureRuleNodeIncompatible.RULE_NAME!r} as string for feature rule")
        if feature_names.is_empty():
            raise ValueError(f"Missing 'incompatible_with' as list of string for feature rule {FeatureRuleNodeIncompatible.RULE_NAME!r}")
  
        return FeatureRuleNodeOnlyOne(name, feature_names)

    # Is it 'incompatible' rule?
    elif FeatureRuleNodeIncompatible.RULE_NAME in data:
        name = None
        feature = None
        incompatible_with = StrList()
        for key, value in data.items():
            match key:
                case FeatureRuleNodeIncompatible.RULE_NAME:
                    if not value or not isinstance(value, str):
                        raise ValueError(f"{FeatureRuleNodeIncompatible.RULE_NAME!r} of feature rule must be a string")
                    name = value
                case "feature":
                    if not value or not isinstance(value, str):
                        raise ValueError(f"'feature' of feature rule must be a string")
                    feature = value
                case _:
                    if try_parse_list_modifier("with", incompatible_with, key, value):
                        continue
                    else:    
                        raise ValueError(f"'{key}:{value}' is not a valid key ({name})")
                    
        if not name:
            raise ValueError(f"Missing {FeatureRuleNodeIncompatible.RULE_NAME!r} as string for feature rule")
        if not feature:
            raise ValueError(f"Missing 'feature' as string for feature rule {FeatureRuleNodeIncompatible.RULE_NAME!r}")
        if incompatible_with.is_empty():
            raise ValueError(f"Missing 'incompatible_with' as list of string for feature rule {FeatureRuleNodeIncompatible.RULE_NAME!r}")
        
        return FeatureRuleNodeIncompatible(name,
                                           feature,
                                           incompatible_with)
    
    else:
        raise ValueError(f"Unknown feature rule: {data}")


