import yaml
from toolchain.nodes.compiler_nodes import CompilersOverrideNode
from toolchain.nodes.linker_nodes import LinkersOverrideNode
from toolchain.nodes.project_type_nodes import ProjectTypeNode, ProjectTypeSpecificOverrideNode, ProjectTypesOverrideNode
from toolchain.nodes.property import PropertyDict
from toolchain.parsers.compiler_parser import yaml_parse_compilers_overrides
from toolchain.parsers.linker_parser import yaml_parse_linkers_overrides
from toolchain.parsers.parse_utils import parse_property

def yaml_parse_project_types_overrides(data: dict) -> ProjectTypesOverrideNode:
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
    node = ProjectTypesOverrideNode()
    for key, value in data.items():
        prop = parse_property(key, value)
        if prop:
            node.add_property(prop)
        elif isinstance(value, dict):
            override = ProjectTypeSpecificOverrideNode(key)
            for key_p, value_p in value.items():
                match key_p:
                    case CompilersOverrideNode.NAME:
                        override.compilers = yaml_parse_compilers_overrides(value_p)
                    case LinkersOverrideNode.NAME:
                        override.linkers = yaml_parse_linkers_overrides(value_p)
                    case _:
                        prop = parse_property(key_p, value_p)
                        if prop:
                            node.add_property(prop)
            node.add_project_type(override)
    return node

def yaml_parse_project_type(data: dict) -> ProjectTypeNode:
    """Parse a project type entry (bin, lib, dyn or custom).

    - name: my_bin
      description: Executable binary
      extends: ...
      compilers: ...
      linkers: ...
    """
    # Project type need 'name'
    name = data.get("name")
    if not name or not isinstance(name, str):
        raise ValueError("Missing 'name' for profile as string")
    
    # Create the project type and load informations
    node = ProjectTypeNode(name)
    for key, value in data.items():
        match key:
            case "name":
                continue
            case CompilersOverrideNode.NAME:
                node.compilers = yaml_parse_compilers_overrides(value)
            case LinkersOverrideNode.NAME:
                node.linkers = yaml_parse_linkers_overrides(value)
            case _:
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

