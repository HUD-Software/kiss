from toolchain.nodes.feature_node import FeatureArgsNode, FeatureNode, FeatureNodeList, FeatureRuleNode
from toolchain.nodes.property import PropertyStr, PropertyStrList
from toolchain.parsers.parse_utils import parse_property


from typing import Type, TypeVar
T = TypeVar("T", bound="FeatureNode")

def yaml_parse_feature(data: dict, node_cls: Type[T] = FeatureNode) -> T:

    # Feature need 'name'
    name = data.get("name")
    if not name or not isinstance(name, str):
        raise ValueError("Missing 'name' for feature as string")

    # Create the feature and load informations
    node = node_cls(data["name"])
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

    # node = FeatureNode(data["name"])
    # for key, value in data.items():
    #     if key == "name":
    #         continue
    #     if key == "args" and isinstance(value, dict):
    #         arg_node = FeatureArgsNode(key)
    #         for key, value in data.items():
    #             prop = parse_property(key, value if value is not None else "")
    #             if prop:
    #                 arg_node.add_property(prop)
    #         node.add_property(arg_node)
    #         continue
    #     prop = parse_property(key, value)
    #     if prop:
    #         node.add_property(prop)
    # return node


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


