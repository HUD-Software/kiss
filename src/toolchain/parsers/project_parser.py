import yaml
from toolchain.nodes.node import Node, PropertyNodeDict, PropertyNodeList, PropertyStrList
from toolchain.nodes.project_type_nodes import ProjectTypeNode, ProjectTypeCompilerNode, ProjectTypeLinkerNode
from toolchain.parsers.parse_utils import parse_property

def parse_project_compilers(name: str, data: dict) -> ProjectTypeCompilerNode:
    node     = ProjectTypeCompilerNode(name)
    overrides: dict = {}

    for key, value in data.items():
        prop = parse_property(key, value)
        if prop:
            node.add_property(prop)
        elif isinstance(value, dict):
            override = ProjectTypeCompilerNode(name=key)
            for key, value in value.items():
                prop = parse_property(key, value)
                if prop:
                    override.add_property(prop)
            overrides[key] = override
    if overrides:
        node.add_property(PropertyNodeDict("overrides", overrides))
    return node

def parse_project_linkers(data: dict) -> ProjectTypeLinkerNode:
    node     = ProjectTypeLinkerNode("linkers")
    overrides: dict = {}

    for key, value in data.items():
        prop = parse_property(key, value)
        if prop:
            node.add_property(prop)
        elif isinstance(value, dict):
            override = ProjectTypeLinkerNode(name=key)
            for key, value in value.items():
                prop = parse_property(key, value)
                if prop:
                    override.add_property(prop)
            overrides[key] = override
    if overrides:
        node.add_property(PropertyNodeDict("linkers", overrides))


def parse_project(data: dict) -> ProjectTypeNode:
    node = ProjectTypeNode(name=data["name"])
    for key, value in data.items():
        if key == "name":
            continue
        if key == "compilers" and isinstance(value, dict):
            compiler_node = parse_project_compilers(key, value)
            node.add_property(compiler_node)
            continue
        # if key == "linkers" and isinstance(value, dict):
        #     linker_node = parse_project_linkers(value)
        #     node.add_property(PropertyNodeList(key, [linker_node]))
        #     continue
        prop = parse_property(key, value)
        if prop:
            node.add_property(prop)
    return node


def load_projects(path: str) -> list[ProjectTypeNode]:
    with open(path, encoding="utf-8") as f:
        data = yaml.safe_load(f)
    return [parse_project(p) for p in data.get("projects", [])]
