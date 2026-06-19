import yaml
from toolchain.nodes.linker_nodes import LinkersOverrideNode
from toolchain.nodes.target_nodes import TargetNode
from toolchain.parsers.compiler_parser import yaml_parse_compilers_overrides
from toolchain.parsers.linker_parser import yaml_parse_linkers_overrides
from toolchain.parsers.parse_utils import parse_property


def yaml_parse_target(data: dict) -> TargetNode:
    node = TargetNode(name=data["name"])
    for key, value in data.items():
        if key == "name":
            continue
        if key == LinkersOverrideNode.NAME:
            node.add_property(yaml_parse_linkers_overrides(value))
            continue
        if key == "compilers" and isinstance(value, dict):
            node.add_property(yaml_parse_compilers_overrides(value))
            continue
        prop = parse_property(key, value)
        if prop:
            node.add_property(prop)
    return node


def load_targets(path: str) ->  dict[str, TargetNode]:
    with open(path, encoding="utf-8") as f:
        data = yaml.safe_load(f)
    
    targets = {}
    for t in data.get("targets", []):
        target = yaml_parse_target(t)
        targets[target.name] = target
    return targets
