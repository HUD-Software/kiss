import yaml
from toolchain.nodes.node import PropertyDict
from toolchain.nodes.project_type_nodes import ProjectTypeCompilerOverrideNode, ProjectTypeLinkerOverrideNode, ProjectTypeNode, ProjectTypeCompilerNode, ProjectTypeLinkerNode
from toolchain.parsers.parse_utils import parse_property

def parse_project_compilers(name: str, data: dict) -> ProjectTypeCompilerNode:
    node     = ProjectTypeCompilerNode(name)
    overrides: dict = {}

    for key, value in data.items():
        prop = parse_property(key, value)
        if prop:
            node.add_property(prop)
        elif isinstance(value, dict):
            override = ProjectTypeCompilerOverrideNode(key)
            for prop_key, prop_value in value.items():
                prop = parse_property(prop_key, prop_value)
                if prop:
                    override.add_property(prop)
            overrides[key] = override
    if overrides:
        node.add_property(PropertyDict("overrides", overrides))
    return node

def parse_project_linkers(name: str, data: dict) -> ProjectTypeLinkerNode:
    node     = ProjectTypeLinkerNode(name)
    overrides: dict = {}

    for key, value in data.items():
        prop = parse_property(key, value)
        if prop:
            node.add_property(prop)
        elif isinstance(value, dict):
            override = ProjectTypeLinkerOverrideNode(key)
            for prop_key, prop_value in value.items():
                prop = parse_property(prop_key, prop_value)
                if prop:
                    override.add_property(prop)
            overrides[key] = override
    if overrides:
        node.add_property(PropertyDict("overrides", overrides))
    return node

def parse_project(data: dict) -> ProjectTypeNode:
    node = ProjectTypeNode(data["name"])
    for key, value in data.items():
        if key == "name":
            continue
        if key == "compilers" and isinstance(value, dict):
            compiler_node = parse_project_compilers(key, value)
            node.add_property(compiler_node)
            continue
        if key == "linkers" and isinstance(value, dict):
            linker_node = parse_project_linkers(key, value)
            node.add_property(linker_node)
            continue
        prop = parse_property(key, value)
        if prop:
            node.add_property(prop)
    return node


def load_projects(path: str) -> list[ProjectTypeNode]:
    with open(path, encoding="utf-8") as f:
        data = yaml.safe_load(f)
    return [parse_project(p) for p in data.get("projects", [])]
