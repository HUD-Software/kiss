import yaml
from toolchain.nodes.feature_node import FeatureNodeList, FeatureRuleNodeList
from toolchain.nodes.property import PropertyDict
from toolchain.nodes.linker_nodes import LinkerNode, LinkerSpecificOverrideNode, LinkersOverrideNode
from toolchain.parsers.feature_parser import yaml_parse_feature, yaml_parse_feature_rule
from toolchain.parsers.parse_utils import parse_property


def yaml_parse_linkers_overrides(name: str, data: dict) -> LinkersOverrideNode:
    """Parse the 'linkers:' block inside a compiler feature.

    linkers:
      enable-features: []
      link:
        enable-features: [OPT_LEVEL_0]
      lld-link:
        enable-features: [OPT_LEVEL_0]
    """
    node     = LinkersOverrideNode(name, data)
    overrides = PropertyDict("overrides")

    for key, value in data.items():
        prop = parse_property(key, value)
        if prop:
            node.add_property(prop)
        elif isinstance(value, dict):
            override = LinkerSpecificOverrideNode(key)
            for override_key, override_value in value.items():
                prop = parse_property(override_key, override_value)
                if prop:
                    override.add_property(prop)
            overrides.add_property(override)
    if overrides.properties:
        node.add_property(overrides)
    return node


def yaml_parse_linker(data: dict) -> LinkerNode:
    node = LinkerNode(data["name"])
    for key, value in data.items():
        if key == "name":
            continue
        if key == FeatureNodeList.NAME and isinstance(value, list):
            features = FeatureNodeList()
            for f in value:
                features.add_property(yaml_parse_feature(f))
            if features.properties:
                node.add_property(features)
            continue
        if key == FeatureRuleNodeList.NAME and isinstance(value, list):
            feature_rules = FeatureRuleNodeList()
            for fr in value:
                feature_rules.add_property(yaml_parse_feature_rule(fr))
            if feature_rules.properties:
                node.add_property(feature_rules)
            continue
        
        prop = parse_property(key, value)
        if prop:
            node.add_property(prop)
    return node


def load_linkers(path: str) -> dict[str, LinkerNode]:
    with open(path, encoding="utf-8") as f:
        data = yaml.safe_load(f)

    linkers = {}
    for l in data.get("linkers", []):
        linker = yaml_parse_linker(l)
        linkers[linker.name] = linker
    return linkers

