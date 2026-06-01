from toolchain.nodes.compiler_nodes import CompilerFeatureLinkerNode, CompilerFeatureNode, CompilerFeatureRuleNode, CompilerLinkerOverrideNode, CompilerNode
from toolchain.nodes.node import PropertyBool, PropertyNodeDict, PropertyNodeList, PropertyStr, PropertyStrList


def parse_linker_overrides(linkers_data: dict) -> CompilerFeatureLinkerNode:
    """Parse the 'linkers:' block inside a compiler feature.

    linkers:
      enable-features: []       # global, for all linkers
      link:
        enable-features: [...]  # specific to 'link' linker
      lld-link:
        enable-features: [...]  # specific to 'lld-link' linker
    """
    node = CompilerFeatureLinkerNode(name="linkers")

    for key, value in linkers_data.items():
        if key == "enable-features":
            node.add_property(PropertyStrList("enable-features", value or []))
        else:
            # Per-linker override block (e.g. link:, lld-link:)
            override = CompilerLinkerOverrideNode(name=key)
            if isinstance(value, dict):
                if "enable-features" in value:
                    override.add_property(PropertyStrList("enable-features", value["enable-features"] or []))
            node.add_property(PropertyNodeDict("linker-overrides", {}) if "linker-overrides" not in node.properties else node.get_property("linker-overrides"))
            # Add this override into the dict property
            overrides_prop = node.get_property("linker-overrides")
            if overrides_prop is None:
                overrides_prop = PropertyNodeDict("linker-overrides", {})
                node.add_property(overrides_prop)
            overrides_prop.entries[key] = override

    return node


def parse_compiler_feature(feature_data: dict) -> CompilerFeatureNode:
    """Parse a single feature entry inside a compiler.

    - name: OPT_LEVEL_0
      description: No optimization
      flags: [/Od]
      enable-features: [DEBUG_INFO]
      linkers:
        enable-features: []
        link:
          enable-features: [OPT_LEVEL_0]
    """
    node = CompilerFeatureNode(name=feature_data["name"])

    if "description" in feature_data:
        node.add_property(PropertyStr("description", feature_data["description"]))

    if "flags" in feature_data:
        node.add_property(PropertyStrList("flags", feature_data["flags"] or []))

    if "enable-features" in feature_data:
        node.add_property(PropertyStrList("enable-features", feature_data["enable-features"] or []))

    if "linkers" in feature_data:
        linker_node = parse_linker_overrides(feature_data["linkers"])
        node.add_property(PropertyNodeList("linkers", [linker_node]))

    return node


def parse_feature_rule(rule_data: dict) -> CompilerFeatureRuleNode:
    """Parse a single feature rule (only-one or incompatible).

    - only-one: optimization
      features: [OPT_LEVEL_0, OPT_LEVEL_1, ...]

    - incompatible: no_opt
      feature: OPT_LEVEL_0
      with: [LTO, OMIT_FRAME_POINTER]
    """
    if "only-one" in rule_data:
        node = CompilerFeatureRuleNode(name=rule_data["only-one"])
        node.add_property(PropertyStr("type", "only-one"))
        node.add_property(PropertyStrList("features", rule_data.get("features", [])))
    elif "incompatible" in rule_data:
        node = CompilerFeatureRuleNode(name=rule_data["incompatible"])
        node.add_property(PropertyStr("type", "incompatible"))
        node.add_property(PropertyStr("feature", rule_data["feature"]))
        node.add_property(PropertyStrList("with", rule_data.get("with", [])))
    else:
        raise ValueError(f"Unknown feature rule type: {rule_data}")

    return node


def parse_compiler(compiler_data: dict) -> CompilerNode:
    """Parse a single compiler entry.

    - name: msvc-compiler
      is_abstract: true
      supported-linkers: [link, lld-link]
      default-linker: link
      extends: ...
      features: [...]
      feature-rules: [...]
    """
    node = CompilerNode(name=compiler_data["name"])

    if "is_abstract" in compiler_data:
        node.add_property(PropertyBool("is_abstract", compiler_data["is_abstract"]))

    if "extends" in compiler_data:
        node.add_property(PropertyStr("extends", compiler_data["extends"]))

    if "supported-linkers" in compiler_data:
        node.add_property(PropertyStrList("supported-linkers", compiler_data["supported-linkers"] or []))

    if "default-linker" in compiler_data:
        node.add_property(PropertyStr("default-linker", compiler_data["default-linker"]))

    if "features" in compiler_data:
        features = [parse_compiler_feature(f) for f in compiler_data["features"]]
        node.add_property(PropertyNodeList("features", features))

    if "feature-rules" in compiler_data:
        rules = [parse_feature_rule(r) for r in compiler_data["feature-rules"]]
        node.add_property(PropertyNodeList("feature-rules", rules))

    return node
