import yaml
from toolchain.nodes.property import (
    PropertyDict, PropertyStr, PropertyStrList,
    PropertyNodeList,
)
from toolchain.nodes.compiler_nodes import (
    CompilerLinkerOverrideNode, CompilerNode, CompilerFeatureNode, CompilerFeatureLinkersNode, CompilerFeatureRuleNode
)
from toolchain.parsers.parse_utils import parse_property


def parse_feature_linkers(name: str, data: dict) -> CompilerFeatureLinkersNode:
    """Parse the 'linkers:' block inside a compiler feature.

    linkers:
      enable-features: []
      link:
        enable-features: [OPT_LEVEL_0]
      lld-link:
        enable-features: [OPT_LEVEL_0]
    """
    node     = CompilerFeatureLinkersNode(name, data)
    overrides = PropertyDict("overrides")

    for key, value in data.items():
        prop = parse_property(key, value)
        if prop:
            node.add_property(prop)
        elif isinstance(value, dict):
            override = CompilerLinkerOverrideNode(key)
            for override_key, override_value in value.items():
                prop = parse_property(override_key, override_value)
                if prop:
                    override.add_property(prop)
            overrides.add_property(override)
    if overrides.properties:
        node.add_property(overrides)
    return node


def yaml_parse_feature_rule(data: dict) -> CompilerFeatureRuleNode:
    """Parse a single feature rule (only-one or incompatible)."""

    if "only-one" in data:
        node = CompilerFeatureRuleNode(data["only-one"])
        node.add_property(PropertyStr("type", "only-one"))
        node.add_property(PropertyStrList("features", data.get("features", [])))
    elif "incompatible" in data:
        node = CompilerFeatureRuleNode(data["incompatible"])
        node.add_property(PropertyStr("type", "incompatible"))
        node.add_property(PropertyStr("feature", data["feature"]))
        node.add_property(PropertyStrList("with", data.get("with", [])))
    else:
        raise ValueError(f"Unknown feature rule: {data}")
    return node


def yaml_parse_compiler_feature(data: dict) -> CompilerFeatureNode:
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
            node.add_property(parse_feature_linkers(key, value))
            continue
        
        prop = parse_property(key, value)
        if prop:
            node.add_property(prop)
    return node


def yaml_parse_compiler(data: dict) -> CompilerNode:
    """Parse a single compiler entry."""
    
    node = CompilerNode(data["name"])

    for key, value in data.items():
        if key == "name":
            continue
        if key == "features" and isinstance(value, list):
            features = PropertyDict(key)
            for f in value:
                features.add_property(yaml_parse_compiler_feature(f))
            if features.properties:
                node.add_property(features)
            continue
        if key == "feature-rules" and isinstance(value, list):
            feature_rules = PropertyDict("feature-rules")
            for fr in value:
                feature_rules.add_property(yaml_parse_feature_rule(fr))
            if feature_rules.properties:
                node.add_property(feature_rules)
            continue
        
        prop = parse_property(key, value)
        if prop:
            node.add_property(prop)

    return node


def load_compilers(path: str) -> dict[str, CompilerNode]:
    with open(path, encoding="utf-8") as f:
        data = yaml.safe_load(f)
    compilers = {}
    for c in data.get("compilers", []):
        compiler = yaml_parse_compiler(c)
        compilers[compiler.name] = compiler
    return compilers

    #return [yaml_parse_compiler(c) for c in data.get("compilers", [])]
