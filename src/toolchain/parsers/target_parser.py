import yaml
from toolchain.nodes.property import PropertyDict, PropertyNodeList
from toolchain.nodes.target_nodes import (
    TargetNode, TargetLinkerNode,
    TargetCompilerOverrideNode, TargetCompilerFeatureOverrideNode,
)
from toolchain.parsers.parse_utils import parse_property


def parse_target_linkers(data: dict) -> TargetLinkerNode:
    node = TargetLinkerNode(name="linkers")
    for k, v in data.items():
        prop = parse_property(k, v)
        if prop:
            node.add_property(prop)
    return node


def parse_target_compiler_feature_override(data: dict) -> TargetCompilerFeatureOverrideNode:
    node = TargetCompilerFeatureOverrideNode(name=data["name"])
    for key, value in data.items():
        if key == "name":
            continue
        if key == "linkers" and isinstance(value, dict):
            node.add_property(PropertyNodeList("linkers", [parse_target_linkers(value)]))
            continue
        prop = parse_property(key, value)
        if prop:
            node.add_property(prop)
    return node


def parse_target_compiler_override(name: str, data: dict) -> TargetCompilerOverrideNode:
    node = TargetCompilerOverrideNode(name=name)
    if "features" in data:
        features = [parse_target_compiler_feature_override(f) for f in data["features"]]
        node.add_property(PropertyNodeList("features", features))
    return node


def parse_target(data: dict) -> TargetNode:
    node = TargetNode(name=data["name"])
    for key, value in data.items():
        if key == "name":
            continue
        if key == "linkers" and isinstance(value, dict):
            node.add_property(PropertyNodeList("linkers", [parse_target_linkers(value)]))
            continue
        if key == "compilers" and isinstance(value, dict):
            overrides = {k: parse_target_compiler_override(k, v or {}) for k, v in value.items()}
            node.add_property(PropertyDict("overrides", overrides))
            continue
        prop = parse_property(key, value)
        if prop:
            node.add_property(prop)
    return node


def load_targets(path: str) -> list[TargetNode]:
    with open(path, encoding="utf-8") as f:
        data = yaml.safe_load(f)
    return [parse_target(t) for t in data.get("targets", [])]
