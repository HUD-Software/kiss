from toolchain.nodes.feature_node import FeatureArgsNode, FeatureNode, FeatureNodeList, FeatureRuleNode, FeatureRuleNodeList
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

def yaml_parse_feature_rule(data: dict) -> FeatureRuleNode:
    """Parse a single feature rule (only-one or incompatible)."""

    if "only-one" in data:
        node = FeatureRuleNode(data["only-one"])
        node.add_property(PropertyStr("type", "only-one"))
        node.add_property(PropertyStrList("features", data.get("features", [])))
    elif "incompatible" in data:
        node = FeatureRuleNode(data["incompatible"])
        node.add_property(PropertyStr("type", "incompatible"))
        node.add_property(PropertyStr("feature", data["feature"]))
        node.add_property(PropertyStrList("with", data.get("with", [])))
    else:
        raise ValueError(f"Unknown feature rule: {data}")
    return node


