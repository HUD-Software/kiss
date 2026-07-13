import yaml
from toolchain.nodes.compiler_nodes import CompilersOverrideNode
from toolchain.nodes.linker_nodes import LinkersOverrideNode
from toolchain.nodes.profile_nodes import ProfilesOverrideNode
from toolchain.nodes.project_type_nodes import ProjectTypesOverrideNode
from toolchain.nodes.target_nodes import TargetNode
from toolchain.parsers.compiler_parser import yaml_parse_compilers_overrides
from toolchain.parsers.linker_parser import yaml_parse_linkers_overrides
from toolchain.parsers.parse_utils import parse_property
from toolchain.parsers.profile_parser import yaml_parse_profiles_overrides
from toolchain.parsers.project_type_parser import yaml_parse_project_types_overrides


def yaml_parse_target(data: dict) -> TargetNode:

    # Target need 'name'
    name = data.get("name")
    if not name or not isinstance(name, str):
        raise ValueError("Missing 'name' for target as string")
    
    # Create the profile and load informations
    node = TargetNode(data["name"])
    for key, value in data.items():
        match key:
            case "name":
                continue
            case CompilersOverrideNode.NAME:
                node.compilers = yaml_parse_compilers_overrides(value)
            case LinkersOverrideNode.NAME:
                node.linkers = yaml_parse_linkers_overrides(value)
            case ProjectTypesOverrideNode.NAME:
                node.project_types = yaml_parse_project_types_overrides(value)
            case ProfilesOverrideNode.NAME:
                node.profiles = yaml_parse_profiles_overrides(value)
            case _:
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
