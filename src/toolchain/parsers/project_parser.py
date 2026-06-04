import yaml
from toolchain.nodes.node import PropertyNodeList
from toolchain.nodes.project_type_nodes import ProjectTypeNode, ProjectTypeCompilersNode, ProjectTypeLinkerNode
from toolchain.parsers.parse_utils import parse_property


def parse_project_compilers(data: dict) -> ProjectTypeCompilersNode:
    node = ProjectTypeCompilersNode(name="compilers")
    for k, v in data.items():
        prop = parse_property(k, v)
        if prop:
            node.add_property(prop)
    return node


def parse_project_linkers(data: dict) -> ProjectTypeLinkerNode:
    node = ProjectTypeLinkerNode(name="linkers")
    for k, v in data.items():
        prop = parse_property(k, v)
        if prop:
            node.add_property(prop)
    return node


def parse_project(data: dict) -> ProjectTypeNode:
    node = ProjectTypeNode(name=data["name"])
    for key, value in data.items():
        if key == "name":
            continue
        if key == "compilers" and isinstance(value, dict):
            node.add_property(PropertyNodeList("compilers", [parse_project_compilers(value)]))
            continue
        if key == "linkers" and isinstance(value, dict):
            node.add_property(PropertyNodeList("linkers", [parse_project_linkers(value)]))
            continue
        prop = parse_property(key, value)
        if prop:
            node.add_property(prop)
    return node


def load_projects(path: str) -> list[ProjectTypeNode]:
    with open(path, encoding="utf-8") as f:
        data = yaml.safe_load(f)
    return [parse_project(p) for p in data.get("projects", [])]
