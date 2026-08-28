import yaml
from toolchain.nodes.feature_node import FeatureNodeList, FeatureRuleNodeList
from toolchain.nodes.linker_nodes import LinkerNode, LinkerSpecificOverrideNode, LinkersOverrideNode
from toolchain.parsers.feature_parser import  yaml_parse_feature_list, yaml_parse_feature_rule_list
from toolchain.parsers.parse_utils import parse_property, try_parse_list_modifier

def yaml_parse_linker_specific_overrides(name: str, data: dict) -> LinkerSpecificOverrideNode:
    linker = LinkerSpecificOverrideNode(name)
    for key, value in data.items():
        if try_parse_list_modifier("flags", linker.flags, key, value):
            continue
        elif try_parse_list_modifier("features", linker.features.str_list, key, value):
            continue
        else:    
            raise ValueError(f"'{key}:{value}' is not a valid key ({name})")
    return linker

def yaml_parse_linkers_overrides(data: dict) -> LinkersOverrideNode:
    """Parse the 'linkers:' block inside a compiler feature.

    linkers:
      enable-features: []
      add-flags:[]
      link:
        add-flags:[]
        enable-features: [OPT_LEVEL_0]
      lld-link:
        add-flags:[]
        enable-features: [OPT_LEVEL_0]
    """
    node = LinkersOverrideNode()
    for key, value in data.items():
        if isinstance(value, dict):
            linker = yaml_parse_linker_specific_overrides(key, value)
            node.linkers.add(linker)
        else:
            if try_parse_list_modifier("flags", node.common_linker.flags, key, value):
                continue
            elif try_parse_list_modifier("features", node.common_linker.features.str_list, key, value):
                continue
            else:    
                raise ValueError(f"'{key}:{value}' is not a valid key")
                
    
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
            case "feature-rules":
                feature_rule_list = yaml_parse_feature_rule_list(value)
                if not feature_rule_list.is_empty():
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
    if data:
        for l in data.get("linkers", []):
            linker = yaml_parse_linker(l)
            linkers[linker.name] = linker
    return linkers

