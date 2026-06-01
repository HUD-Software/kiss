import yaml
from ..nodes.node import PropertyStr, PropertyBool, PropertyStrList, PropertyNodeList, PropertyNodeDict
from ..nodes.profile_nodes import (
    ProfileNode, ProfileCompilersNode, ProfileLinkerNode,
    ProfileProjectNode, ProfileCompilerOverrideNode, ProfileLinkerOverrideNode
)


# Keys that are reserved in the compilers/linkers block and are not compiler/linker names
RESERVED_COMPILER_KEYS = {"enable-features", "defines"}
RESERVED_LINKER_KEYS = {"enable-features"}


def parse_compiler_override(name: str, data: dict) -> ProfileCompilerOverrideNode:
    """Parse a compiler-specific override block.

    msvc-compiler:
      enable-features: [OPT_LEVEL_0, WINDOWS_DLL_RUNTIME_DEBUG]
      defines: []
    """
    node = ProfileCompilerOverrideNode(name=name)

    if "enable-features" in data:
        node.add_property(PropertyStrList("enable-features", data["enable-features"] or []))
    if "defines" in data:
        node.add_property(PropertyStrList("defines", data["defines"] or []))

    return node


def parse_linker_override(name: str, data: dict) -> ProfileLinkerOverrideNode:
    """Parse a linker-specific override block.

    msvc-linker:
      enable-features: [REMOVE_DEAD_CODE]
    """
    node = ProfileLinkerOverrideNode(name=name)

    if "enable-features" in data:
        node.add_property(PropertyStrList("enable-features", data["enable-features"] or []))

    return node


def parse_profile_compilers(compilers_data: dict) -> ProfileCompilersNode:
    """Parse the 'compilers:' block inside a profile.

    compilers:
      enable-features: []
      defines: [KISS_DEBUG]
      msvc-compiler:
        enable-features: [OPT_LEVEL_0]
        defines: []
    """
    node = ProfileCompilersNode(name="compilers")

    if "enable-features" in compilers_data:
        node.add_property(PropertyStrList("enable-features", compilers_data["enable-features"] or []))
    if "defines" in compilers_data:
        node.add_property(PropertyStrList("defines", compilers_data["defines"] or []))

    # Per-compiler overrides
    overrides = {}
    for key, value in compilers_data.items():
        if key not in RESERVED_COMPILER_KEYS and isinstance(value, dict):
            overrides[key] = parse_compiler_override(key, value)

    if overrides:
        node.add_property(PropertyNodeDict("compiler-overrides", overrides))

    return node


def parse_profile_linkers(linkers_data: dict) -> ProfileLinkerNode:
    """Parse the 'linkers:' block inside a profile.

    linkers:
      enable-features: [ENABLE_INCREMENTAL_LINK]
      msvc-linker:
        enable-features: []
    """
    node = ProfileLinkerNode(name="linkers")

    if "enable-features" in linkers_data:
        node.add_property(PropertyStrList("enable-features", linkers_data["enable-features"] or []))

    # Per-linker overrides
    overrides = {}
    for key, value in linkers_data.items():
        if key not in RESERVED_LINKER_KEYS and isinstance(value, dict):
            overrides[key] = parse_linker_override(key, value)

    if overrides:
        node.add_property(PropertyNodeDict("linker-overrides", overrides))

    return node


def parse_profile_project(name: str, project_data: dict) -> ProfileProjectNode:
    """Parse a project-type override block inside a profile.

    dyn:
      compilers:
        enable-features: [DYNAMIC_LIBRARY_DEBUG]
        defines: []
        msvc-compiler:
          enable-features: []
      linkers:
        enable-features: []
        msvc-linker:
          enable-features: []
    """
    node = ProfileProjectNode(name=name)

    if "compilers" in project_data:
        compilers_node = parse_profile_compilers(project_data["compilers"])
        node.add_property(PropertyNodeList("compilers", [compilers_node]))

    if "linkers" in project_data:
        linkers_node = parse_profile_linkers(project_data["linkers"])
        node.add_property(PropertyNodeList("linkers", [linkers_node]))

    return node


def parse_profile(profile_data: dict) -> ProfileNode:
    """Parse a single profile entry.

    - name: debug
      description: ...
      extends: debug
      compilers: ...
      linkers: ...
      projects:
        dyn: ...
    """
    node = ProfileNode(name=profile_data["name"])

    if "description" in profile_data:
        node.add_property(PropertyStr("description", profile_data["description"]))

    if "extends" in profile_data:
        node.add_property(PropertyStr("extends", profile_data["extends"]))

    if "compilers" in profile_data:
        compilers_node = parse_profile_compilers(profile_data["compilers"])
        node.add_property(PropertyNodeList("compilers", [compilers_node]))

    if "linkers" in profile_data:
        linkers_node = parse_profile_linkers(profile_data["linkers"])
        node.add_property(PropertyNodeList("linkers", [linkers_node]))

    if "projects" in profile_data:
        projects = {}
        for proj_name, proj_data in profile_data["projects"].items():
            projects[proj_name] = parse_profile_project(proj_name, proj_data or {})
        node.add_property(PropertyNodeDict("projects", projects))

    return node
