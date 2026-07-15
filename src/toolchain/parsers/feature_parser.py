from toolchain.nodes.feature_node import FeatureArgsNode, FeatureNode, FeatureNodeList, FeatureRuleNode, FeatureRuleNodeIncompatible, FeatureRuleNodeList, FeatureRuleNodeOnlyOne
from toolchain.nodes.property import PropertyStr, PropertyStrList
from toolchain.parsers.parse_utils import parse_property


from typing import Type, TypeVar
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


def yaml_parse_feature(data: dict, node_cls: Type[T] = FeatureNode) -> T:
    # Feature need 'name'
    name = data.get("name")
    if not name or not isinstance(name, str):
        raise ValueError("Missing 'name' for feature as string")

    # optional description
    description = data.get("description", "")
    if description and not isinstance(description, str):
        raise ValueError("'description' for feature must be a string")
    
    # Create the feature and load informations
    node = node_cls(name)
    for key, value in data.items():
        match key:
            case "name":
                pass
            case FeatureArgsNode.NAME:
                args = FeatureArgsNode()
                for args_key, args_value in value.items():
                    args.add_property(parse_property(args_key, args_value if args_value is not None else ""))
                if args.properties:
                    node.add_property(args)
            case _:
                prop = parse_property(key, value)
                if prop:
                    node.add_property(prop)
    return node

ALLOWED_RULE_KINDS = {FeatureRuleNodeOnlyOne.NAME, FeatureRuleNodeIncompatible.NAME}
def yaml_parse_feature_rule(data: dict) -> FeatureRuleNode:
    """Parse a single feature rule (only-one or incompatible)."""
    kind = next(iter(data))
    if kind not in ALLOWED_RULE_KINDS:
        raise ValueError(
            f"Unknown feature rule '{kind}', expected one of {sorted(ALLOWED_RULE_KINDS)}"
        )
    
    # Is it 'only-one' rule?
    if FeatureRuleNodeOnlyOne.NAME in data:
        # Read 'only-one' name
        name = data.get(FeatureRuleNodeOnlyOne.NAME)
        if not name or not isinstance(name, str):
            raise ValueError(f"Missing {FeatureRuleNodeOnlyOne.NAME!r} as string for feature rule")
        
        # Read 'features'
        features = data.get("features")
        if not features or not isinstance(features, list) or not all(isinstance(f, str) for f in features):
            raise ValueError(f"Missing 'features' as list of string for feature rule {FeatureRuleNodeOnlyOne.NAME!r}")
        return FeatureRuleNodeOnlyOne(name, PropertyStrList("features", features))

    # Is it 'incompatible' rule?
    elif FeatureRuleNodeIncompatible.NAME in data:
        # Read 'incompatible' name
        name = data.get(FeatureRuleNodeIncompatible.NAME)
        if not name or not isinstance(name, str):
            raise ValueError(f"Missing {FeatureRuleNodeIncompatible.NAME!r} as string for feature rule")
        
        # Read 'feature'
        feature = data.get("feature")
        if not feature or not isinstance(feature, str):
            raise ValueError(f"Missing 'feature' as string for feature rule {FeatureRuleNodeIncompatible.NAME!r}")
        
         # Read 'with'
        incompatible_with = data.get("with")
        if not incompatible_with or not isinstance(incompatible_with, list) or not all(isinstance(f, str) for f in incompatible_with):
            raise ValueError(f"Missing 'incompatible_with' as list of string for feature rule {FeatureRuleNodeIncompatible.NAME!r}")
        
        return FeatureRuleNodeIncompatible(name,
                                           PropertyStr("feature", feature),
                                           PropertyStrList("with", incompatible_with))
    
    else:
        raise ValueError(f"Unknown feature rule: {data}")


