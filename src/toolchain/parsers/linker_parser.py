import yaml
from toolchain.nodes.node import PropertyStr, PropertyStrList, PropertyNodeList
from toolchain.nodes.linker_nodes import LinkerNode, LinkerFeatureNode, LinkerFeatureArgsNode, LinkerFeatureRuleNode
from toolchain.parsers.parse_utils import parse_property


def parse_linker_feature_args(data: dict) -> LinkerFeatureArgsNode:
    node = LinkerFeatureArgsNode(name="args")
    for key, value in data.items():
        prop = parse_property(key, value if value is not None else "")
        if prop:
            node.add_property(prop)
    return node


def parse_feature_rule(data: dict) -> LinkerFeatureRuleNode:
    if "only-one" in data:
        node = LinkerFeatureRuleNode(name=data["only-one"])
        node.add_property(PropertyStr("type", "only-one"))
        node.add_property(PropertyStrList("features", data.get("features", [])))
    elif "incompatible" in data:
        node = LinkerFeatureRuleNode(name=data["incompatible"])
        node.add_property(PropertyStr("type", "incompatible"))
        node.add_property(PropertyStr("feature", data["feature"]))
        node.add_property(PropertyStrList("with", data.get("with", [])))
    else:
        raise ValueError(f"Unknown feature rule: {data}")
    return node


def parse_linker_feature(data: dict) -> LinkerFeatureNode:
    node = LinkerFeatureNode(name=data["name"])
    for key, value in data.items():
        if key == "name":
            continue
        if key == "args" and isinstance(value, dict):
            node.add_property(PropertyNodeList("args", [parse_linker_feature_args(value)]))
            continue
        prop = parse_property(key, value)
        if prop:
            node.add_property(prop)
    return node


def parse_linker(data: dict) -> LinkerNode:
    node = LinkerNode(name=data["name"])
    for key, value in data.items():
        if key == "name":
            continue
        if key == "features" and isinstance(value, list):
            node.add_property(PropertyNodeList("features", [parse_linker_feature(f) for f in (value or [])]))
            continue
        if key == "feature-rules" and isinstance(value, list):
            node.add_property(PropertyNodeList("feature-rules", [parse_feature_rule(r) for r in value]))
            continue
        prop = parse_property(key, value)
        if prop:
            node.add_property(prop)
    return node


def load_linkers(path: str) -> list[LinkerNode]:
    with open(path) as f:
        data = yaml.safe_load(f)
    return [parse_linker(l) for l in data.get("linkers", [])]
