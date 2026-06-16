import yaml
from toolchain.nodes.profile_nodes import ProfileNode, ProfileSpecificOverrideNode, ProfilesOverrideNode
from toolchain.nodes.property import PropertyDict
from toolchain.parsers.compiler_parser import yaml_parse_compilers_overrides
from toolchain.parsers.linker_parser import yaml_parse_linkers_overrides
from toolchain.parsers.parse_utils import parse_property
from toolchain.parsers.project_type_parser import yaml_parse_project_types_overrides

def yaml_parse_profile_overrides(name: str, data: dict) -> ProfilesOverrideNode:
    """Parse a 'profiles:' block inside a target entry.

    Handles a dict of profile-specific overrides, each containing compiler
    and linker configuration scoped to that profile. This is the deepest
    specialization layer in the resolution pipeline, capable of expressing
    intersections like "clangcl + dyn + release on x86_64 only" when combined
    with the project-type overrides nested inside each profile.

    Expected structure:
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
    
    node     = ProfilesOverrideNode(name, data)
    overrides = PropertyDict("overrides")

    for key, value in data.items():
        prop = parse_property(key, value)
        if prop:
            node.add_property(prop)
        elif isinstance(value, dict):
            override = ProfileSpecificOverrideNode(key)
            for override_key, override_value in value.items():
                if override_key == "compilers" and isinstance(override_value, dict):
                    override.add_property(yaml_parse_compilers_overrides(override_key, override_value))
                elif override_key == "linkers" and isinstance(override_value, dict):
                    override.add_property(yaml_parse_linkers_overrides(override_key, override_value))
                else:
                    prop = parse_property(override_key, override_value)
                    if prop:
                        override.add_property(prop)
            overrides.add_property(override)
    if overrides.properties:
        node.add_property(overrides)
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
    node = ProfileNode(name=data["name"])
    for key, value in data.items():
        if key == "name":
            continue
        if key == "compilers" and isinstance(value, dict):
            compiler_node = yaml_parse_compilers_overrides(key, value)
            node.add_property(compiler_node)
            continue
        if key == "linkers" and isinstance(value, dict):
            linker_node = yaml_parse_linkers_overrides(key, value)
            node.add_property(linker_node)
            continue
        if key == "project-types" and isinstance(value, dict):
            project_types = yaml_parse_project_types_overrides(key, value)
            node.add_property(project_types)
            continue
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
