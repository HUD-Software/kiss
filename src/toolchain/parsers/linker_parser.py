from toolchain.nodes.linker_nodes import LinkerFeatureRuleNode, LinkerFeatureArgsNode, LinkerFeatureNode, LinkerNode
from toolchain.nodes.node import PropertyBool, PropertyNodeList, PropertyStr, PropertyStrList


def parse_linker_feature_args(args_data: dict) -> LinkerFeatureArgsNode:
    """Parse the 'args:' block inside a linker feature.

    args:
      min: 1
      max: ~
      separator: ","
      pattern: "*.lib"
    """
    node = LinkerFeatureArgsNode(name="args")

    if "min" in args_data:
        node.add_property(PropertyStr("min", str(args_data["min"])))
    if "max" in args_data and args_data["max"] is not None:
        node.add_property(PropertyStr("max", str(args_data["max"])))
    if "separator" in args_data:
        node.add_property(PropertyStr("separator", args_data["separator"]))
    if "pattern" in args_data:
        node.add_property(PropertyStr("pattern", args_data["pattern"]))

    return node


def parse_linker_feature(feature_data: dict) -> LinkerFeatureNode:
    """Parse a single linker feature entry.

    - name: LINK
      description: Link with library
      args:
        min: 1
        max: ~
        separator: ","
        pattern: "*.lib"
      flags: [/link {args}]
    """
    node = LinkerFeatureNode(name=feature_data["name"])

    if "description" in feature_data:
        node.add_property(PropertyStr("description", feature_data["description"]))

    if "flags" in feature_data:
        node.add_property(PropertyStrList("flags", feature_data["flags"] or []))

    if "enable-features" in feature_data:
        node.add_property(PropertyStrList("enable-features", feature_data["enable-features"] or []))

    if "args" in feature_data:
        args_node = parse_linker_feature_args(feature_data["args"])
        node.add_property(PropertyNodeList("args", [args_node]))

    return node


def parse_feature_rule(rule_data: dict) -> LinkerFeatureRuleNode:
    """Parse a single feature rule (only-one or incompatible).

    - only-one: optimization
      features: [OPT_LEVEL_0, OPT_LEVEL_3]

    - incompatible: no_opt
      feature: OPT_LEVEL_0
      with: [LTO]
    """
    if "only-one" in rule_data:
        node = LinkerFeatureRuleNode(name=rule_data["only-one"])
        node.add_property(PropertyStr("type", "only-one"))
        node.add_property(PropertyStrList("features", rule_data.get("features", [])))
    elif "incompatible" in rule_data:
        node = LinkerFeatureRuleNode(name=rule_data["incompatible"])
        node.add_property(PropertyStr("type", "incompatible"))
        node.add_property(PropertyStr("feature", rule_data["feature"]))
        node.add_property(PropertyStrList("with", rule_data.get("with", [])))
    else:
        raise ValueError(f"Unknown feature rule type: {rule_data}")

    return node


def parse_linker(linker_data: dict) -> LinkerNode:
    """Parse a single linker entry.

    - name: msvc-linker
      is_abstract: true
      extends: ...
      features: [...]
      feature-rules: [...]
    """
    node = LinkerNode(name=linker_data["name"])

    if "is_abstract" in linker_data:
        node.add_property(PropertyBool("is_abstract", linker_data["is_abstract"]))

    if "extends" in linker_data:
        node.add_property(PropertyStr("extends", linker_data["extends"]))

    if "features" in linker_data and linker_data["features"]:
        features = [parse_linker_feature(f) for f in linker_data["features"]]
        node.add_property(PropertyNodeList("features", features))

    if "feature-rules" in linker_data:
        rules = [parse_feature_rule(r) for r in linker_data["feature-rules"]]
        node.add_property(PropertyNodeList("feature-rules", rules))

    return node
