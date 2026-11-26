from toolchain.nodes.compiler_nodes import CompilerFeatureNode, CompilerFeatureNodeList
from toolchain.nodes.feature_node import FeatureArgsNode, FeatureNode, FeatureNodeList, FeatureRuleNode, FeatureRuleNodeIncompatible, FeatureRuleNodeList, FeatureRuleNodeOnlyOne, FeatureStrList
from toolchain.nodes.linker_nodes import LinkerSpecificOverrideNode, LinkersOverrideNode
from toolchain.nodes.property import StrList


def create_str_list(override: bool, values: list[str], remove_modifiers: list[str]) -> StrList:
    str_list = StrList()
    str_list.override = override
    for modifier in values:
        str_list.add_value(modifier)
    for modifier in remove_modifiers:
        str_list.add_modifier_remove(modifier)
    return str_list

def create_specific_linker_override_node(name: str, flags: StrList, features: FeatureStrList) -> LinkerSpecificOverrideNode:
    linker_node = LinkerSpecificOverrideNode(name)
    linker_node.flags = flags
    linker_node.features = features
    return linker_node

def create_linker_override_node(common_flag: StrList | None, common_features: FeatureStrList | None, specificlinker: LinkerSpecificOverrideNode | None) -> LinkersOverrideNode:
    linker_node = LinkersOverrideNode()
    if common_flag:
        linker_node.common_linker.flags = common_flag
    if common_features:
        linker_node.common_linker.features = common_features
    if specificlinker:
        linker_node.linker_overrides[specificlinker.name] = specificlinker
    return linker_node

def create_feature_rule_node_list(feature_rule_list : list[FeatureRuleNode]):
    feature_node_rule_list = FeatureRuleNodeList()
    for feature_rule in feature_rule_list:
        feature_node_rule_list.add_feature_rule(feature_rule)
    return feature_node_rule_list

def create_feature_node(name: str, description = "", flags = StrList(), features = FeatureStrList(), args = FeatureArgsNode()):
    feature = FeatureNode(name)
    feature.description = description
    feature.flags = flags
    feature.features = features
    feature.args = args
    return feature

def create_feature_node_list(features : list[FeatureNode]):
    feature_list = FeatureNodeList()
    for feature in features:
        feature_list.add_feature(feature)
    return feature_list

def create_only_one_rule(name: str, description: str, feature_names):
    if isinstance(feature_names, StrList):
        return FeatureRuleNodeOnlyOne(name, description, feature_names)
    elif isinstance(feature_names, list):
        l = StrList()
        for feature_name in feature_names:
            l.add_value(feature_name)
        return FeatureRuleNodeOnlyOne(name, description, l)
    raise ValueError("Invalid feature_names type")

def create_incompatible_rule(name: str, description: str, feature: str, feature_names):
    if isinstance(feature_names, StrList):
        return FeatureRuleNodeIncompatible(name, description, feature, feature_names)
    elif isinstance(feature_names, list):
        l = StrList()
        for feature_name in feature_names:
            l.add_value(feature_name)
        return FeatureRuleNodeIncompatible(name, description, feature, l)
    raise ValueError("Invalid feature_names type")

def create_feature_str_list(override: bool, values: list[str], remove_modifiers: list[str]) -> FeatureStrList:
    feature_str_list = FeatureStrList()
    feature_str_list.str_list.override = override
    for modifier in values:
        feature_str_list.str_list.add_value(modifier)
    for modifier in remove_modifiers:
        feature_str_list.str_list.add_modifier_remove(modifier)
    return feature_str_list

def create_compiler_feature_node(name: str, description = "", flags = StrList(), features = FeatureStrList(), linkers = LinkersOverrideNode(), args = FeatureArgsNode()):
    feature = CompilerFeatureNode(name)
    feature.description = description
    feature.flags = flags
    feature.features = features
    feature.args = args
    feature.linkers = linkers
    return feature

def create_compiler_feature_node_list(features : list[CompilerFeatureNode]):
    feature_list = CompilerFeatureNodeList()
    for feature in features:
        feature_list.add_feature(feature)
    return feature_list


def create_linker_override_node_1() -> LinkersOverrideNode :
    """  
    linkers:
      flags: [C1, C2] # Override = False
      remove-flags: [C1, C3]
      features: [CF1, CF2] # Override = False
      remove-features: [CF1, CF3]
        ld:
          flags: [LD1, C3, LD2] # Override = False
          remove-flags: [LD2] 
          features: [LDF1, CF3, LDF2] # Override = False
          remove-features: [LDF2] 
    """
    common_flag = create_str_list(False, ["C1", "C2"], ["C1", "C3"])
    common_features = create_feature_str_list(False, ["CF1", "CF2"], ["CF1", "CF3"])
    ld_flags = create_str_list(False, ["LD1", "C3", "LD2"], ["LD2"])
    ld_features = create_feature_str_list(False, ["LDF1", "CF3", "LDF2"], ["LDF2"])
    ld_linker = create_specific_linker_override_node("ld", ld_flags, ld_features)
    linker_override_node = create_linker_override_node(common_flag, common_features, ld_linker)

    assert linker_override_node.common_linker.flags.override == False
    assert linker_override_node.common_linker.flags.values == set(["C1", "C2"])
    assert linker_override_node.common_linker.flags.remove_modifiers.values == set(["C1", "C3"])
    assert linker_override_node.common_linker.features.override == False
    assert linker_override_node.common_linker.features.values == set(["CF1", "CF2"])
    assert linker_override_node.common_linker.features.remove_modifiers.values == set(["CF1", "CF3"])
    ld = linker_override_node.linker_overrides.get("ld")
    assert ld
    assert ld.flags.override == False
    assert ld.flags.values == set(["LD1", "C3", "LD2"])
    assert ld.flags.remove_modifiers.values == set(["LD2"]) 
    assert ld.features.override == False
    assert ld.features.values == set(["LDF1", "CF3", "LDF2"])
    assert ld.features.remove_modifiers.values == set(["LDF2"]) 
    return linker_override_node