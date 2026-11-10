
# linkers:
#     lld-link : # LinkerSpecificOverrideNode
#     enable-features: []
#     add-flags: []

from test_common import create_feature_rule_node_list, create_feature_str_list, create_only_one_rule, create_specific_linker_override_node, create_str_list
from toolchain.nodes.feature_node import FeatureRuleNodeList, FeatureStrList
from toolchain.nodes.linker_nodes import LinkerSpecificOverrideNode
from toolchain.nodes.property import StrList


def test_extends_empty():
    parent_specific_node = LinkerSpecificOverrideNode("A")
    child_specific_node = LinkerSpecificOverrideNode("A")
    result = child_specific_node.resolve_extends(parent_specific_node, FeatureRuleNodeList()).unwrap()
    assert result.name == "A"
    assert result.flags.is_empty()
    assert result.features.is_empty()

def test_extends_empty_failed():
    parent_specific_node = LinkerSpecificOverrideNode("B")
    child_specific_node = LinkerSpecificOverrideNode("A")
    assert child_specific_node.resolve_extends(parent_specific_node, FeatureRuleNodeList()).is_err()

def test_extends_no_parent_1():
    child_specific_node = create_specific_linker_override_node("A",
                                                                   create_str_list(False, ["C_0", "C_1", "C_2"], ["C_1"]),
                                                                   create_feature_str_list(False, ["C_F0", "C_F1", "C_F2"], ["C_F1"]))
    # Extends
    result = child_specific_node.resolve_extends(None, FeatureRuleNodeList()).unwrap()
    
    assert result.name == "A"
    assert result.flags.override == False
    assert result.flags.values == set(["C_0", "C_2"])
    assert result.flags.remove_modifiers.values == set([])
    assert result.features.override == False
    assert result.features.values == set(["C_F0", "C_F2"])
    assert result.features.remove_modifiers.values == set([])

def test_extends_no_parent_2():
    child_specific_node = create_specific_linker_override_node("A",
                                                                create_str_list(True, ["C_0", "C_1", "C_2"], ["C_1"]),
                                                                create_feature_str_list(True, ["C_F0", "C_F1", "C_F2"], ["C_F1"]))
    # Extends
    result = child_specific_node.resolve_extends(None, FeatureRuleNodeList()).unwrap()
    
    assert result.name == "A"
    assert result.flags.override == True
    assert result.flags.values == set(["C_0", "C_2"])
    assert result.flags.remove_modifiers.values == set([])
    assert result.features.override == True
    assert result.features.values == set(["C_F0", "C_F2"])
    assert result.features.remove_modifiers.values == set([])

def test_extends_no_child_1():
    parent_specific_node = create_specific_linker_override_node("A",
                                                                create_str_list(False, ["P_0", "P_1", "P_2"], ["P_1"]),
                                                                create_feature_str_list(False, ["P_F0", "P_F1", "P_F2"], ["P_F1"]))
    # Extends
    parent_specific_node = parent_specific_node.resolve_extends(None, FeatureRuleNodeList()).unwrap()
    result = LinkerSpecificOverrideNode("A").resolve_extends(parent_specific_node, FeatureRuleNodeList()).unwrap()
    
    assert result.name == "A"
    assert result.flags.override == False
    assert result.flags.values == set(["P_0", "P_2"])
    assert result.flags.remove_modifiers.values == set([])
    assert result.features.override == False
    assert result.features.values == set(["P_F0", "P_F2"])
    assert result.features.remove_modifiers.values == set([])

def test_extends_no_child_2():
    parent_specific_node = create_specific_linker_override_node("A",
                                                                create_str_list(True, ["P_0", "P_1", "P_2"], ["P_1"]),
                                                                create_feature_str_list(True, ["P_F0", "P_F1", "P_F2"], ["P_F1"]))
    # Extends
    parent_specific_node = parent_specific_node.resolve_extends(None, FeatureRuleNodeList()).unwrap()
    result = LinkerSpecificOverrideNode("A").resolve_extends(parent_specific_node, FeatureRuleNodeList()).unwrap()
    
    assert result.name == "A"
    assert result.flags.override == False
    assert result.flags.values == set(["P_0", "P_2"])
    assert result.flags.remove_modifiers.values == set([])
    assert result.features.override == False
    assert result.features.values == set(["P_F0", "P_F2"])
    assert result.features.remove_modifiers.values == set([])

def test_extends_no_rules_1():
    level_0_node = create_specific_linker_override_node("A",
                                                        create_str_list(False, ["LV0_0", "LV0_1", "LV0_2"], ["LV0_1"]),
                                                        create_feature_str_list(False, ["LV0_F0", "LV0_F1", "LV0_F2"], ["LV0_F1"]))

    level_1_node = create_specific_linker_override_node("A",
                                                        create_str_list(False, ["LV1_0", "LV1_1", "LV1_2"], ["LV1_1"]),
                                                        create_feature_str_list(False, ["LV1_F0", "LV1_F1", "LV1_F2"], ["LV1_F1"]))

    level_2_node = create_specific_linker_override_node("A",
                                                        create_str_list(False, ["LV2_0", "LV2_1", "LV2_2"], ["LV2_1"]),
                                                        create_feature_str_list(False, ["LV2_F0", "LV2_F1", "LV2_F2"], ["LV2_F1"]))
    # Extends
    level_0_node = level_0_node.resolve_extends(None, FeatureRuleNodeList()).unwrap()
    assert level_0_node.name == "A"
    assert level_0_node.flags.override == False
    assert level_0_node.flags.values == set(["LV0_0", "LV0_2"])
    assert level_0_node.flags.remove_modifiers.values == set([])
    assert level_0_node.features.override == False
    assert level_0_node.features.values == set(["LV0_F0", "LV0_F2"])
    assert level_0_node.features.remove_modifiers.values == set([])

    level_1_node = level_1_node.resolve_extends(level_0_node, FeatureRuleNodeList()).unwrap()
    assert level_1_node.name == "A"
    assert level_1_node.flags.override == False
    assert level_1_node.flags.values == set(["LV1_0", "LV1_2", "LV0_0", "LV0_2"])
    assert level_1_node.flags.remove_modifiers.values == set([])
    assert level_1_node.features.override == False
    assert level_1_node.features.values == set(["LV1_F0", "LV1_F2", "LV0_F0", "LV0_F2"])
    assert level_1_node.features.remove_modifiers.values == set([])

    level_2_node = level_2_node.resolve_extends(level_1_node, FeatureRuleNodeList()).unwrap()
    assert level_2_node.name == "A"
    assert level_2_node.flags.override == False
    assert level_2_node.flags.values == set(["LV2_0", "LV2_2", "LV1_0", "LV1_2", "LV0_0", "LV0_2"])
    assert level_2_node.flags.remove_modifiers.values == set([])
    assert level_2_node.features.override == False
    assert level_2_node.features.values == set(["LV2_F0", "LV2_F2", "LV1_F0", "LV1_F2", "LV0_F0", "LV0_F2"])
    assert level_2_node.features.remove_modifiers.values == set([])


def test_extends_rules_1():
    level_0_node = create_specific_linker_override_node("A",
                                                            create_str_list(False, ["LV0_0", "LV0_1", "LV0_2"], ["LV0_1"]),
                                                            create_feature_str_list(False, ["LV0_F0", "LV0_F1", "LV0_F2"], ["LV0_F1"]))
    
    level_1_node = create_specific_linker_override_node("A",
                                                        create_str_list(False, ["LV1_0", "LV1_1", "LV1_2"], ["LV1_1"]),
                                                        create_feature_str_list(False, ["LV1_F0", "LV1_F1", "LV1_F2"], ["LV1_F1"]))

    level_2_node = create_specific_linker_override_node("A",
                                                        create_str_list(False, ["LV2_0", "LV2_1", "LV2_2"], ["LV2_1"]),
                                                        create_feature_str_list(False, ["LV2_F0", "LV2_F1", "LV2_F2"], ["LV2_F1"]))

    # Rule only one 1 replace "LV0_0" in level_0 with 'LV1_0" in level_1
    onlyone_rule_1 = create_only_one_rule("one rule 1", "one rule 1", ["LV0_F0", "LV1_F0"])
    # Rule only one 2 replace "LV1_0" in level_0 with 'LV2_0" in level_2
    onlyone_rule_2 = create_only_one_rule("one rule 2", "one rule 2", ["LV1_F0", "LV2_F0"])
    feature_rule_list = create_feature_rule_node_list([onlyone_rule_1, onlyone_rule_2])

    # Extends
    level_0_node = level_0_node.resolve_extends(None, feature_rule_list).unwrap()
    assert level_0_node.name == "A"
    assert level_0_node.flags.override == False
    assert level_0_node.flags.values == set(["LV0_0", "LV0_2"])
    assert level_0_node.flags.remove_modifiers.values == set([])
    assert level_0_node.features.override == False
    assert level_0_node.features.values == set(["LV0_F0", "LV0_F2"])
    assert level_0_node.features.remove_modifiers.values == set([])

    level_1_node = level_1_node.resolve_extends(level_0_node, feature_rule_list).unwrap()
    assert level_1_node.name == "A"
    assert level_1_node.flags.override == False
    assert level_1_node.flags.values == set(["LV1_0", "LV1_2", "LV0_0", "LV0_2"])
    assert level_1_node.flags.remove_modifiers.values == set([])
    assert level_1_node.features.override == False
    assert level_1_node.features.values == set(["LV1_F0", "LV1_F2", "LV0_F2"])
    assert level_1_node.features.remove_modifiers.values == set([])

    level_2_node = level_2_node.resolve_extends(level_1_node, feature_rule_list).unwrap()
    assert level_2_node.name == "A"
    assert level_2_node.flags.override == False
    assert level_2_node.flags.values == set(["LV2_0", "LV2_2", "LV1_0", "LV1_2", "LV0_0", "LV0_2"])
    assert level_2_node.flags.remove_modifiers.values == set([])
    assert level_2_node.features.override == False
    assert level_2_node.features.values == set(["LV2_F0", "LV2_F2", "LV1_F2", "LV0_F2"])
    assert level_2_node.features.remove_modifiers.values == set([])

def test_extends_linker_specific_override_node() :
    test_extends_empty()
    test_extends_empty_failed()
    test_extends_no_parent_1()
    test_extends_no_parent_2()
    test_extends_no_child_1()
    test_extends_no_child_2()
    test_extends_no_rules_1()
    test_extends_rules_1()