import yaml
from ..nodes.node import PropertyStr, PropertyStrList, PropertyNodeList, PropertyNodeDict
from ..nodes.target_nodes import (
    TargetNode, TargetLinkerNode,
    TargetCompilerOverrideNode, TargetCompilerFeatureOverrideNode
)


def parse_target_linkers(linkers_data: dict) -> TargetLinkerNode:
    """Parse the 'linkers:' block inside a target.

    linkers:
      enable-features: [TARGET_X64]
    """
    node = TargetLinkerNode(name="linkers")

    if "enable-features" in linkers_data:
        node.add_property(PropertyStrList("enable-features", linkers_data["enable-features"] or []))

    return node


def parse_target_compiler_feature_override(feature_data: dict) -> TargetCompilerFeatureOverrideNode:
    """Parse a feature override for a specific compiler inside a target.

    - name: ASAN
      linkers:
        enable-features: [LINK:msvcrt.lib]
    """
    node = TargetCompilerFeatureOverrideNode(name=feature_data["name"])

    if "linkers" in feature_data:
        linkers_data = feature_data["linkers"]
        linker_node = TargetLinkerNode(name="linkers")
        if "enable-features" in linkers_data:
            linker_node.add_property(PropertyStrList("enable-features", linkers_data["enable-features"] or []))
        node.add_property(PropertyNodeList("linkers", [linker_node]))

    return node


def parse_target_compiler_override(name: str, compiler_data: dict) -> TargetCompilerOverrideNode:
    """Parse a compiler-specific override block inside a target.

    clangcl:
      features:
        - name: ASAN
          linkers:
            enable-features: [LINK:msvcrt.lib]
    """
    node = TargetCompilerOverrideNode(name=name)

    if "features" in compiler_data:
        features = [parse_target_compiler_feature_override(f) for f in compiler_data["features"]]
        node.add_property(PropertyNodeList("features", features))

    return node


def parse_target(target_data: dict) -> TargetNode:
    """Parse a single target entry.

    - name: x86_64-pc-windows-msvc
      arch: x86_64
      vendor: pc
      os: windows
      abi: msvc
      pointer-width: 64
      endianness: little
      supported-compilers: [clangcl, cl]
      default-compiler: cl
      linkers: ...
      compilers: ...
    """
    node = TargetNode(name=target_data["name"])

    for field in ("arch", "vendor", "os", "abi", "endianness", "default-compiler"):
        if field in target_data:
            node.add_property(PropertyStr(field, str(target_data[field])))

    if "pointer-width" in target_data:
        node.add_property(PropertyStr("pointer-width", str(target_data["pointer-width"])))

    if "supported-compilers" in target_data:
        node.add_property(PropertyStrList("supported-compilers", target_data["supported-compilers"] or []))

    if "linkers" in target_data:
        linkers_node = parse_target_linkers(target_data["linkers"])
        node.add_property(PropertyNodeList("linkers", [linkers_node]))

    if "compilers" in target_data:
        overrides = {}
        for compiler_name, compiler_data in target_data["compilers"].items():
            overrides[compiler_name] = parse_target_compiler_override(compiler_name, compiler_data or {})
        node.add_property(PropertyNodeDict("compiler-overrides", overrides))

    return node
