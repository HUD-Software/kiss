import yaml
from toolchain.nodes.compiler_nodes import CompilersOverrideNode
from toolchain.nodes.linker_nodes import LinkersOverrideNode
from toolchain.nodes.profile_nodes import ProfileNode, ProfileSpecificOverrideNode, ProfilesOverrideNode
from toolchain.nodes.project_type_nodes import ProjectTypesOverrideNode
from toolchain.nodes.property import PropertyDict
from toolchain.parsers.compiler_parser import yaml_parse_compilers_overrides
from toolchain.parsers.linker_parser import yaml_parse_linkers_overrides
from toolchain.parsers.parse_utils import parse_property
from toolchain.parsers.project_type_parser import yaml_parse_project_types_overrides

def yaml_parse_profiles_overrides(data: dict) -> ProfilesOverrideNode:
    """Parse a 'profiles:' block inside a target entry.

    Handles a dict of profile-specific overrides, each containing compiler
    and linker configuration scoped to that profile. This is the deepest
    specialization layer in the resolution pipeline, capable of expressing
    intersections like "clangcl + dyn + release on x86_64 only" when combined
    with the project-type overrides nested inside each profile.

    profiles:
        release:                      # → ProfileSpecificOverrideNode
            compilers:
            enable-features: [...]
            clangcl:
                enable-features: [...]
            linkers:
            enable-features: [...]
            project-types:
            dyn:
                compilers:
                enable-features: [...]
        debug:                        # → ProfileSpecificOverrideNode
            compilers:
            enable-features: [...]
    """
    node = ProfilesOverrideNode()
    for key, value in data.items():
        prop = parse_property(key, value)
        if prop:
            node.add_property(prop)
        elif isinstance(value, dict):
            override = ProfileSpecificOverrideNode(key)
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
                    case _:
                        prop = parse_property(key, value)
                        if prop:
                            override.add_property(prop)
            node.add_project_type(override)
    return node


def yaml_parse_profile(data: dict) -> ProfileNode:
    """Parse a single profile entry from profiles.yaml.

    Handles the top-level keys of a profile, dispatching each to its
    dedicated parser. Unknown keys are parsed as generic properties.

    Expected structure:
      - name: release
        description: ...
        extends: ...
        compilers:        # → yaml_parse_compilers_overrides()
          enable-features: [...]
          defines: [...]
          msvc-compiler:
            enable-features: [...]
        linkers:          # → yaml_parse_linkers_overrides()
          enable-features: [...]
          msvc-linker:
            enable-features: [...]
        project-types:    # → yaml_parse_project_types_overrides()
          dyn:
            compilers:
              enable-features: [...]
            linkers:
              enable-features: [...]
    """
    # Profile need 'name'
    name = data.get("name")
    if not name or not isinstance(name, str):
        raise ValueError("Missing 'name' for profile as string")
    
    # Create the profile and load informations
    node = ProfileNode(data["name"])
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
            case _:
                prop = parse_property(key, value)
                if prop:
                    node.add_property(prop)
    return node


def load_profiles(path: str) -> list[ProfileNode]:
    with open(path, encoding="utf-8") as f:
        data = yaml.safe_load(f)

    profiles = {}
    for p in data.get("profiles", []):
        profile = yaml_parse_profile(p)
        profiles[profile.name] = profile
    return profiles
