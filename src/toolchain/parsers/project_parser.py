import yaml
from ..nodes.node import PropertyStr, PropertyBool, PropertyStrList, PropertyNodeList
from ..nodes.project_nodes import ProjectNode, ProjectCompilersNode, ProjectLinkerNode


def parse_project_compilers(compilers_data: dict) -> ProjectCompilersNode:
    """Parse the 'compilers:' block inside a project type.

    compilers:
      enable-features: []
      defines: [KISS_BIN]
    """
    node = ProjectCompilersNode(name="compilers")

    if "enable-features" in compilers_data:
        node.add_property(PropertyStrList("enable-features", compilers_data["enable-features"] or []))
    if "defines" in compilers_data:
        node.add_property(PropertyStrList("defines", compilers_data["defines"] or []))

    return node


def parse_project_linkers(linkers_data: dict) -> ProjectLinkerNode:
    """Parse the 'linkers:' block inside a project type.

    linkers:
      enable-features: []
    """
    node = ProjectLinkerNode(name="linkers")

    if "enable-features" in linkers_data:
        node.add_property(PropertyStrList("enable-features", linkers_data["enable-features"] or []))

    return node


def parse_project(project_data: dict) -> ProjectNode:
    """Parse a single project type entry.

    - name: bin
      description: Executable binary
      extends: ...
      compilers:
        enable-features: []
        defines: [KISS_BIN]
      linkers:
        enable-features: []
    """
    node = ProjectNode(name=project_data["name"])

    if "description" in project_data:
        node.add_property(PropertyStr("description", project_data["description"]))

    if "extends" in project_data:
        node.add_property(PropertyStr("extends", project_data["extends"]))

    if "compilers" in project_data:
        compilers_node = parse_project_compilers(project_data["compilers"])
        node.add_property(PropertyNodeList("compilers", [compilers_node]))

    if "linkers" in project_data:
        linkers_node = parse_project_linkers(project_data["linkers"])
        node.add_property(PropertyNodeList("linkers", [linkers_node]))

    return node
