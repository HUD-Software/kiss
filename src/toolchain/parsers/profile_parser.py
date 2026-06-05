import yaml
from toolchain.nodes.node import PropertyNodeDict, PropertyNodeList
from toolchain.nodes.profile_nodes import ProfileCompilerOverrideNode, ProfileCompilersNode, ProfileLinkerNode, ProfileLinkerOverrideNode, ProfileNode, ProfileProjectTypeNode
from toolchain.parsers.parse_utils import parse_property

RESERVED_COMPILER = {"enable-features", "defines"}
RESERVED_LINKER   = {"enable-features"}


def parse_compiler_override(name: str, data: dict) -> ProfileCompilerOverrideNode:
    node = ProfileCompilerOverrideNode(name=name)
    for k, v in data.items():
        prop = parse_property(k, v)
        if prop:
            node.add_property(prop)
    return node


def parse_linker_override(name: str, data: dict) -> ProfileLinkerOverrideNode:
    node = ProfileLinkerOverrideNode(name=name)
    for k, v in data.items():
        prop = parse_property(k, v)
        if prop:
            node.add_property(prop)
    return node


def parse_profile_compilers(data: dict) -> ProfileCompilersNode:
    node      = ProfileCompilersNode(name="compilers")
    overrides = {}
    for key, value in data.items():
        if key in RESERVED_COMPILER or key.startswith("append-") or key.startswith("remove-"):
            prop = parse_property(key, value)
            if prop:
                node.add_property(prop)
        elif isinstance(value, dict):
            overrides[key] = parse_compiler_override(key, value)
    if overrides:
        node.add_property(PropertyNodeDict("overrides", overrides))
    return node


def parse_profile_linkers(data: dict) -> ProfileLinkerNode:
    node      = ProfileLinkerNode(name="linkers")
    overrides = {}
    for key, value in data.items():
        if key in RESERVED_LINKER or key.startswith("append-") or key.startswith("remove-"):
            prop = parse_property(key, value)
            if prop:
                node.add_property(prop)
        elif isinstance(value, dict):
            overrides[key] = parse_linker_override(key, value)
    if overrides:
        node.add_property(PropertyNodeDict("overrides", overrides))
    return node


def parse_profile_project(name: str, data: dict) -> ProfileProjectTypeNode:
    node = ProfileProjectTypeNode(name=name)
    if "compilers" in data:
        node.add_property(PropertyNodeList("compilers", [parse_profile_compilers(data["compilers"])]))
    if "linkers" in data:
        node.add_property(PropertyNodeList("linkers",   [parse_profile_linkers(data["linkers"])]))
    return node


def parse_profile(data: dict) -> ProfileNode:
    node = ProfileNode(name=data["name"])
    for key, value in data.items():
        if key == "name":
            continue
        if key == "compilers" and isinstance(value, dict):
            node.add_property(PropertyNodeList("compilers", [parse_profile_compilers(value)]))
            continue
        if key == "linkers" and isinstance(value, dict):
            node.add_property(PropertyNodeList("linkers", [parse_profile_linkers(value)]))
            continue
        if key == "projects" and isinstance(value, dict):
            projects = {k: parse_profile_project(k, v or {}) for k, v in value.items()}
            node.add_property(PropertyNodeDict("projects", projects))
            continue
        prop = parse_property(key, value)
        if prop:
            node.add_property(prop)
    return node


def load_profiles(path: str) -> list[ProfileNode]:
    with open(path, encoding="utf-8") as f:
        data = yaml.safe_load(f)
    return [parse_profile(p) for p in data.get("profiles", [])]
