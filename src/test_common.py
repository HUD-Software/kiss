from toolchain.nodes.feature_node import FeatureArgsNode, FeatureNode, FeatureNodeList, FeatureRuleNode, FeatureRuleNodeIncompatible, FeatureRuleNodeList, FeatureRuleNodeOnlyOne, FeatureStrList
from toolchain.nodes.linker_nodes import LinkerSpecificOverrideNode, LinkersOverrideNode
from toolchain.nodes.property import StrList


def create_str_list(values, add_modifiers: list[str], remove_modifiers: list[str]) -> StrList:
    str_list = StrList()
    if isinstance(values, bool):
        str_list.override = values
    else:
        for value in values:
            str_list.override = True
            str_list.add_value(value)
    for modifier in add_modifiers:
        str_list.add_value(modifier)
    for modifier in remove_modifiers:
        str_list.add_modifier_remove(modifier)
    return str_list

def create_specific_linker_override_node(name: str, flags: StrList, features: FeatureStrList) -> LinkerSpecificOverrideNode:
    linker_node = LinkerSpecificOverrideNode(name)
    linker_node.flags = flags
    linker_node.features = features
    return linker_node

def create_test_linker_node(common_flag: StrList, specificflags: LinkerSpecificOverrideNode) -> LinkersOverrideNode:
    linker_node = LinkersOverrideNode()
    if common_flag:
        linker_node.common_linker.flags = common_flag
    if specificflags:
        linker_node.linker_overrides[specificflags.name] = specificflags
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

def create_feature_str_list(values, add_modifiers: list[str], remove_modifiers: list[str]):
    feature_str_list = FeatureStrList()
    if isinstance(values, bool):
        feature_str_list.str_list.override = values
    else:
        for value in values:
            feature_str_list.str_list.override = True
            feature_str_list.str_list.add_value(value)
    for modifier in add_modifiers:
        feature_str_list.str_list.add_value(modifier)
    for modifier in remove_modifiers:
        feature_str_list.str_list.add_modifier_remove(modifier)
    return feature_str_list
