import yaml
from toolchain.nodes.node import (
    PropertyDict, PropertyStr, PropertyStrList,
    PropertyNodeList,
)
from toolchain.nodes.compiler_nodes import (
    CompilerLinkerOverrideNode, CompilerNode, CompilerFeatureNode, CompilerFeatureLinkerNode, CompilerFeatureRuleNode
)
from toolchain.parsers.parse_utils import parse_property


def parse_linker_overrides(name: str, data: dict) -> CompilerFeatureLinkerNode:
    """Parse the 'linkers:' block inside a compiler feature.

    linkers:
      enable-features: []
      link:
        enable-features: [OPT_LEVEL_0]
      lld-link:
        enable-features: [OPT_LEVEL_0]
    """
    node     = CompilerFeatureLinkerNode(name)
    overrides: dict = {}

    for key, value in data.items():
        prop = parse_property(key, value)
        if prop:
            node.add_property(prop)
        elif isinstance(value, dict):
            override = CompilerFeatureLinkerNode(key)
            for key, value in value.items():
                prop = parse_property(key, value)
                if prop:
                    override.add_property(prop)
            overrides[key] = override
    if overrides:
        node.add_property(PropertyDict("overrides", overrides))
    return node

    # node     = CompilerFeatureLinkerNode(name="linkers")
    # overrides: dict = {}

    # for key, value in data.items():
    #     if key == "enable-features":
    #         node.add_property(PropertyStrList("enable-features", value or []))
    #     elif isinstance(value, dict):
    #         override = CompilerLinkerOverrideNode(name=key)
    #         for k, v in value.items():
    #             prop = parse_property(k, v)
    #             if prop:
    #                 override.add_property(prop)
    #         overrides[key] = override

    # if overrides:
    #     node.add_property(PropertyDict("overrides", overrides))

    # return node


def parse_feature_rule(data: dict) -> CompilerFeatureRuleNode:
    """Parse a single feature rule (only-one or incompatible)."""

    if "only-one" in data:
        node = CompilerFeatureRuleNode(name=data["only-one"])
        node.add_property(PropertyStr("type", "only-one"))
        node.add_property(PropertyStrList("features", data.get("features", [])))
    elif "incompatible" in data:
        node = CompilerFeatureRuleNode(name=data["incompatible"])
        node.add_property(PropertyStr("type", "incompatible"))
        node.add_property(PropertyStr("feature", data["feature"]))
        node.add_property(PropertyStrList("with", data.get("with", [])))
    else:
        raise ValueError(f"Unknown feature rule: {data}")
    return node


def parse_compiler_feature(data: dict) -> CompilerFeatureNode:
    """Parse a single compiler feature entry.

    - name: OPT_LEVEL_0
      description: No optimization
      flags: [/Od]
      enable-features: [DEBUG_INFO]
      append-flags: [...]         # optional
      remove-flags: [...]         # optional
      linkers:
        enable-features: []
        link:
          enable-features: [OPT_LEVEL_0]
    """
    node = CompilerFeatureNode(data["name"])

    for key, value in data.items():
        if key == "name":
            continue
        if key == "linkers" and isinstance(value, dict):
            linker_prop = parse_linker_overrides(key, value)
            node.add_property(linker_prop)
            continue
        prop = parse_property(key, value)
        if prop:
            node.add_property(prop)
    return node


def parse_compiler(data: dict) -> CompilerNode:
    """Parse a single compiler entry."""

    node = CompilerNode(data["name"])
    for key, value in data.items():
        if key == "name":
            continue
        if key == "features" and isinstance(value, list):
            node.add_property(PropertyNodeList("features", [parse_compiler_feature(f) for f in value]))
            continue
        if key == "feature-rules" and isinstance(value, list):
            node.add_property(PropertyNodeList("feature-rules", [parse_feature_rule(r) for r in value]))
            continue
        prop = parse_property(key, value)
        if prop:
            node.add_property(prop)

    return node


def load_compilers(path: str) -> list[CompilerNode]:
    with open(path, encoding="utf-8") as f:
        data = yaml.safe_load(f)
    return [parse_compiler(c) for c in data.get("compilers", [])]
