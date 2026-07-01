import yaml
from toolchain.nodes.feature_node import FeatureNodeList, FeatureRuleNodeList
from toolchain.nodes.property import PropertyDict
from toolchain.nodes.linker_nodes import LinkerNode, LinkerSpecificOverrideNode, LinkersOverrideNode
from toolchain.parsers.feature_parser import yaml_parse_feature, yaml_parse_feature_rule
from toolchain.parsers.parse_utils import parse_property


def yaml_parse_linkers_overrides(data: dict) -> LinkersOverrideNode:
    """Parse the 'linkers:' block inside a compiler feature.

    linkers:
      enable-features: []
      link:
        enable-features: [OPT_LEVEL_0]
      lld-link:
        enable-features: [OPT_LEVEL_0]
    """
    node = LinkersOverrideNode()
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
            node.add_linker(override)
    return node
    


def yaml_parse_linker(data: dict) -> LinkerNode:
    # Linker need 'name'
    name = data.get("name")
    if not name or not isinstance(name, str):
        raise ValueError("Missing 'name' for linker as string")
    
    
    # Create the linker and load informations
    node = LinkerNode(name)
    for key, value in data.items():
        match key:
            case "name":
                pass
            case FeatureNodeList.NAME:
                feature_list = FeatureNodeList()
                for f in value:
                    feature_list.add_feature(yaml_parse_feature(f))
                if feature_list.features:
                    node.feature_list = feature_list
            case FeatureRuleNodeList.NAME:
                feature_rule_list = FeatureRuleNodeList()
                for fr in value:
                    feature_rule_list.add_feature_rule(yaml_parse_feature_rule(fr))
                if feature_rule_list.feature_rules:
                    node.feature_rule_list = feature_rule_list
            case _:
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

