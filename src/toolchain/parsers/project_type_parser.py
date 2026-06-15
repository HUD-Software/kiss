import yaml
from toolchain.nodes.project_type_nodes import ProjectSpecificOverrideNode, ProjectTypeNode, ProjectsOverrideNode
from toolchain.nodes.property import PropertyDict
from toolchain.parsers.compiler_parser import yaml_parse_compilers_overrides
from toolchain.parsers.linker_parser import yaml_parse_linkers_overrides
from toolchain.parsers.parse_utils import parse_property

def yaml_parse_project_types_overrides(name: str, data: dict) -> ProjectsOverrideNode:
    """Parse the 'project-types:' block inside a profile entry.

    Handles a dict of project-type-specific overrides, each containing
    compiler and linker configuration scoped to that project type.

    project-types:
      dyn:
        compilers:
          enable-features: [DYNAMIC_LIBRARY_DEBUG]
          defines: []
          msvc-compiler:
            enable-features: []
            defines: []
        linkers:
          enable-features: []
          msvc-linker:
            enable-features: []
    """
    node     = ProjectsOverrideNode(name, data)
    overrides = PropertyDict("overrides")

    for key, value in data.items():
        prop = parse_property(key, value)
        if prop:
            node.add_property(prop)
        elif isinstance(value, dict):
            override = ProjectSpecificOverrideNode(key)
            for override_key, override_value in value.items():
                prop = parse_property(override_key, override_value)
                if prop:
                    override.add_property(prop)
            overrides.add_property(override)
    if overrides.properties:
        node.add_property(overrides)
    return node

def yaml_parse_project_type(data: dict) -> ProjectTypeNode:
    """Parse a project type entry (bin, lib, dyn or custom).

    - name: my_bin
      description: Executable binary
      extends: ...
      compilers: ...
      linkers: ...
    """
    node = ProjectTypeNode(data["name"])
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
        prop = parse_property(key, value)
        if prop:
            node.add_property(prop)
    return node


def load_project_types(path: str) -> dict[str, ProjectTypeNode]:
    with open(path, encoding="utf-8") as f:
        data = yaml.safe_load(f)

    project_types = {}
    for p in data.get("project-types", []):
        project_type = yaml_parse_project_type(p)
        project_types[project_type.name] = project_type
    return project_types

