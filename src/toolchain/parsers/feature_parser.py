from toolchain.nodes.feature_node import FeatureArgsNode, FeatureNode, FeatureNodeList, FeatureRuleNodeIncompatible, FeatureRuleNodeList, FeatureRuleNodeOnlyOne
from toolchain.nodes.property import StrList
from toolchain.parsers.parse_utils import try_parse_list_modifier

def yaml_parse_feature_list(data: dict) -> FeatureNodeList:
    feature_list = FeatureNodeList()
    for f in data:
        feature_list.add_feature(yaml_parse_feature(f))
    return feature_list


def yaml_parse_feature_rule_list(data:dict) -> FeatureRuleNodeList:
    ALLOWED_RULE_KINDS = {FeatureRuleNodeOnlyOne.RULE_NAME, 
                          FeatureRuleNodeIncompatible.RULE_NAME}
    
    feature_rule_list = FeatureRuleNodeList()
    if data:
        for fr in data:    
            kind = next(iter(fr))
            if kind not in ALLOWED_RULE_KINDS:
                raise ValueError(
                    f"Unknown feature rule '{kind}', expected one of {sorted(ALLOWED_RULE_KINDS)}"
                )
            
            # Is it 'only-one' rule?
            match kind:
                case FeatureRuleNodeOnlyOne.RULE_NAME:
                    feature_rule_list.add_feature_rule(yaml_parse_feature_rule_only_one(fr))
                case FeatureRuleNodeIncompatible.RULE_NAME:
                    feature_rule_list.add_feature_rule(yaml_parse_feature_rule_incompatible(fr))
                case _:
                    raise ValueError(f"Unknown feature rule: {data}")
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
                elif try_parse_list_modifier("features", node.features.str_list, key, value):
                    continue
                else:    
                    raise ValueError(f"'{key}:{value}' is not a valid key ({name})")
    return node



def yaml_parse_feature_rule_only_one(data: dict) -> FeatureRuleNodeOnlyOne:
    name = None
    description = ""
    feature_names = StrList()
    for key, value in data.items():
        match key:
            case FeatureRuleNodeOnlyOne.RULE_NAME:
                if not value or not isinstance(value, str):
                    raise ValueError(f"{FeatureRuleNodeOnlyOne.RULE_NAME!r} of feature rule must be a string")
                name = value
            case "description":
                if not value or not isinstance(value, str):
                    raise ValueError(f"'description' of feature rule must be a string")
                description = value
            case _:
                if try_parse_list_modifier("features", feature_names, key, value):
                    continue
                else:    
                    raise ValueError(f"'{key}:{value}' is not a valid key ({name})")
                
    if not name:
        raise ValueError(f"Missing {FeatureRuleNodeOnlyOne.RULE_NAME!r} as string for feature rule")
    if not feature_names.is_user_defined_values() and not feature_names.is_user_defined_modifiers():
        raise ValueError(f"Missing 'features' or 'add/enable' modifier as list of string for feature rule {FeatureRuleNodeOnlyOne.RULE_NAME!r}")

    return FeatureRuleNodeOnlyOne(name, description, feature_names)

def yaml_parse_feature_rule_incompatible(data: dict) -> FeatureRuleNodeIncompatible:
    name = None
    feature = None
    description = ""
    incompatible_with = StrList()
    for key, value in data.items():
        match key:
            case FeatureRuleNodeIncompatible.RULE_NAME:
                if not value or not isinstance(value, str):
                    raise ValueError(f"{FeatureRuleNodeIncompatible.RULE_NAME!r} of feature rule must be a string")
                name = value
            case "description":
                if not value or not isinstance(value, str):
                    raise ValueError(f"'description' of feature rule must be a string")
                description = value
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
    if not incompatible_with.is_user_defined_values() and not incompatible_with.is_user_defined_modifiers():
        raise ValueError(f"Missing 'incompatible_with' as list of string for feature rule {FeatureRuleNodeIncompatible.RULE_NAME!r}")
    
    return FeatureRuleNodeIncompatible(name, description, feature, incompatible_with)