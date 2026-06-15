import yaml
from toolchain.nodes.property import PropertyStr, PropertyStrList, PropertyNodeList, PropertyNodeDict
from toolchain.parsers.profile_parser import parse_profile
from toolchain.parsers.project_type_parser import parse_project
from .nodes.workspace_nodes import KissWorkspaceNode, KissProjectTypeNode, SourceNode, DependencyNode


# Built-in project types that kiss knows about natively
BUILTIN_PROJECT_TYPES = {"bin", "lib", "dyn"}


def parse_kiss_project(name: str, project_data: dict) -> KissProjectTypeNode:
    """Parse a single project entry in kiss.yaml.

    - name: my_bin
      version: 0.1.0
      sources:
        - src/main.cpp
      dependencies:
        - my_lib
    """
    node = KissProjectTypeNode(name=name)

    if "version" in project_data:
        node.add_property(PropertyStr("version", project_data["version"]))

    if "sources" in project_data:
        sources = [SourceNode(name=s) for s in (project_data["sources"] or [])]
        node.add_property(PropertyNodeList("sources", sources))

    if "dependencies" in project_data:
        deps = [DependencyNode(name=d) for d in (project_data["dependencies"] or [])]
        node.add_property(PropertyNodeList("dependencies", deps))

    return node


def load_workspace(path: str) -> KissWorkspaceNode:
    """Load and parse kiss.yaml, returning a KissWorkspaceNode.

    kiss.yaml structure:
      profiles:        # optional custom profiles
      project-types:   # optional custom project types
      bin:             # list of binary projects
      lib:             # list of static library projects
      dyn:             # list of dynamic library projects
      <custom-type>:   # list of custom project type entries
    """
    with open(path, encoding="utf-8") as f:
        data = yaml.safe_load(f)

    workspace = KissWorkspaceNode(name=str(path))

    # Optional custom profiles
    if "profiles" in data:
        custom_profiles = [parse_profile(p) for p in data["profiles"]]
        workspace.add_property(PropertyNodeList("profiles", custom_profiles))

    # Optional custom project types
    if "project-types" in data:
        custom_projects = [parse_project(p) for p in data["project-types"]]
        workspace.add_property(PropertyNodeList("project-types", custom_projects))

    # All project entries (built-in types + custom types)
    # We collect all keys that are not reserved metadata keys
    reserved_keys = {"profiles", "project-types"}
    projects_by_type: dict[str, list] = {}

    for key, entries in data.items():
        if key in reserved_keys or not isinstance(entries, list):
            continue
        parsed = [parse_kiss_project(entry["name"], entry) for entry in entries]
        projects_by_type[key] = parsed

    if projects_by_type:
        type_dict = {}
        for type_name, project_list in projects_by_type.items():
            from toolchain.nodes.property import PropertyDict
            container = PropertyDict(name=type_name)
            container.add_property(PropertyNodeList("entries", project_list))
            type_dict[type_name] = container
        workspace.add_property(PropertyNodeDict("project-entries", type_dict))

    return workspace
