import yaml
from toolchain.nodes.feature_node import FeatureNodeList, FeatureRuleNodeList
from toolchain.nodes.property import PropertyDict
from toolchain.nodes.linker_nodes import LinkerNode, LinkerSpecificOverrideNode, LinkersOverrideNode
from toolchain.parsers.feature_parser import  yaml_parse_feature_list, yaml_parse_feature_rule_list
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
            linker_specific = LinkerSpecificOverrideNode(key)
            for override_key, override_value in value.items():
                match override_key:
                    case FeatureNodeList.NAME:
                        linker_specific.feature_list = yaml_parse_feature_list(override_value)
                    case FeatureRuleNodeList.NAME:
                        linker_specific.feature_rule_list = yaml_parse_feature_rule_list(override_value)
                    case _:
                        prop = parse_property(override_key, override_value)
                        if prop:
                            linker_specific.add_property(prop)
            node.add_linker(linker_specific)
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
            case "features":
                node.feature_list = yaml_parse_feature_list(value)
            case FeatureRuleNodeList.NAME:
                feature_rule_list = yaml_parse_feature_rule_list(value)
                if feature_rule_list.feature_rules:
                    node.feature_rule_list = feature_rule_list
            case "is_abstract":
                if not isinstance(value, bool):
                    raise ValueError(f"'is_abstract' must be a boolean value ({name})")
                node.is_abstract = value
            case "extends":
                if not isinstance(value, str):
                    raise ValueError(f"'extends' must be a string value ({name})")
                node.extends = value
            case _:
                raise ValueError(f"'{key}:{value}' is not a valid key ({name})")
    return node


def load_linkers(path: str) -> dict[str, LinkerNode]:
    with open(path, encoding="utf-8") as f:
        data = yaml.safe_load(f)

    linkers = {}
    for l in data.get("linkers", []):
        linker = yaml_parse_linker(l)
        linkers[linker.name] = linker
    return linkers

