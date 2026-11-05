# - name:
#     description:
#     flags: [] # Add/remove flags
#     features: [] # Add/remove features
#     args:
#       min: 1
#       max: ~
#       separator: ","
#       pattern: "*.lib"


from unittest import result

from test_common import create_feature_str_list, create_str_list
from toolchain.nodes.feature_node import FeatureNode, FeatureRuleNodeList

def test_extends_empty_1():
    # feature level 0
    feature_level_0 = FeatureNode("level_0")
    feature_level_0.description = "feature level 0"
    feature_level_0.flags = create_str_list(False, ["L0_1", "L0_2"], ["L0_1", "L0_3"] )
    feature_level_0.features = create_feature_str_list(False, ["L0_F1", "L0_F2"], ["L0_F1", "L0_F3"] )

    result = feature_level_0.resolve_extends(FeatureNode("root"), FeatureRuleNodeList())

    assert result.name == "level_0"
    assert result.description == "feature level 0"
    assert result.flags.override == False
    assert result.flags.values == set(["L0_2"])
    assert result.flags.remove_modifiers.values == set([])
    assert result.features.override == False
    assert result.features.values == set(["L0_F2"])
    assert result.features.remove_modifiers.values == set([])

def test_extends_empty_2():
    # feature level 0
    feature_level_0 = FeatureNode("level_0")
    feature_level_0.description = "feature level 0"
    feature_level_0.flags = create_str_list(True, ["L0_1", "L0_2"], ["L0_1", "L0_3"] )
    feature_level_0.features = create_feature_str_list(True, ["L0_F1", "L0_F2"], ["L0_F1", "L0_F3"] )

    result = feature_level_0.resolve_extends(FeatureNode("root"), FeatureRuleNodeList())

    assert result.name == "level_0"
    assert result.description == "feature level 0"
    assert result.flags.override == True
    assert result.flags.values == set(["L0_2"])
    assert result.flags.remove_modifiers.values == set([])
    assert result.features.override == True
    assert result.features.values == set(["L0_F2"])
    assert result.features.remove_modifiers.values == set([])

def test_extends_no_rules_1():
    # feature level 0
    feature_level_0 = FeatureNode("level_0")
    feature_level_0.description = "feature level 0"
    feature_level_0.flags = create_str_list(False, ["L0_1", "L0_2"], ["L0_1", "L0_3"] )
    feature_level_0.features = create_feature_str_list(False, ["L0_F1", "L0_F2"], ["L0_F1", "L0_F3"] )

    feature_level_0 = feature_level_0.resolve_extends(FeatureNode("root"), FeatureRuleNodeList())

    # feature level 1
    feature_level_1 = FeatureNode("level_1")
    feature_level_1.description = "feature level 1"
    feature_level_1.flags = create_str_list(False, ["L1_1", "L1_2"], ["L1_1", "L1_3"] )
    feature_level_1.features = create_feature_str_list(False, ["L1_F1", "L1_F2"], ["L1_F1", "L1_F3"] )

    feature_level_1 = feature_level_1.resolve_extends(feature_level_0, FeatureRuleNodeList())

    assert feature_level_1.name == "level_1"
    assert feature_level_1.description == "feature level 1"
    assert feature_level_1.flags.override == False
    assert feature_level_1.flags.values == set(["L0_2", "L1_2"])
    assert feature_level_1.flags.remove_modifiers.values == set([])
    assert feature_level_1.features.override == False
    assert feature_level_1.features.values == set(["L0_F2", "L1_F2"])
    assert feature_level_1.features.remove_modifiers.values == set([])

    # feature level 2
    feature_level_2 = FeatureNode("level_2")
    feature_level_2.description = "feature level 2"
    feature_level_2.flags = create_str_list(False, ["L2_1", "L2_2"], ["L2_1", "L2_3"] )
    feature_level_2.features = create_feature_str_list(False, ["L2_F1", "L2_F2"], ["L2_F1", "L2_F3"] )

    feature_level_2 = feature_level_2.resolve_extends(feature_level_1, FeatureRuleNodeList())

    assert feature_level_2.name == "level_2"
    assert feature_level_2.description == "feature level 2"
    assert feature_level_2.flags.override == False
    assert feature_level_2.flags.values == set(["L0_2", "L1_2", "L2_2"])
    assert feature_level_2.flags.remove_modifiers.values == set([])
    assert feature_level_2.features.override == False
    assert feature_level_2.features.values == set(["L0_F2", "L1_F2", "L2_F2"])
    assert feature_level_2.features.remove_modifiers.values == set([])

def test_extends_no_rules_2():
    # feature level 0
    feature_level_0 = FeatureNode("level_0")
    feature_level_0.description = "feature level 0"
    feature_level_0.flags = create_str_list(False, ["L0_1", "L0_2"], ["L0_1", "L0_3"] )
    feature_level_0.features = create_feature_str_list(False, ["L0_F1", "L0_F2"], ["L0_F1", "L0_F3"] )

    feature_level_0 = feature_level_0.resolve_extends(FeatureNode("root"), FeatureRuleNodeList())

    # feature level 1
    feature_level_1 = FeatureNode("level_1")
    feature_level_1.description = "feature level 1"
    feature_level_1.flags = create_str_list(True, ["L1_1", "L1_2"], ["L1_1", "L1_3"] )
    feature_level_1.features = create_feature_str_list(True, ["L1_F1", "L1_F2"], ["L1_F1", "L1_F3"] )

    feature_level_1 = feature_level_1.resolve_extends(feature_level_0, FeatureRuleNodeList())

    assert feature_level_1.name == "level_1"
    assert feature_level_1.description == "feature level 1"
    assert feature_level_1.flags.override == True
    assert feature_level_1.flags.values == set(["L1_2"])
    assert feature_level_1.flags.remove_modifiers.values == set([])
    assert feature_level_1.features.override == True
    assert feature_level_1.features.values == set(["L1_F2"])
    assert feature_level_1.features.remove_modifiers.values == set([])

    # feature level 2
    feature_level_2 = FeatureNode("level_2")
    feature_level_2.description = "feature level 2"
    feature_level_2.flags = create_str_list(False, ["L2_1", "L2_2"], ["L2_1", "L2_3"] )
    feature_level_2.features = create_feature_str_list(False, ["L2_F1", "L2_F2"], ["L2_F1", "L2_F3"] )

    feature_level_2 = feature_level_2.resolve_extends(feature_level_1, FeatureRuleNodeList())

    assert feature_level_2.name == "level_2"
    assert feature_level_2.description == "feature level 2"
    assert feature_level_2.flags.override == False
    assert feature_level_2.flags.values == set(["L1_2", "L2_2"])
    assert feature_level_2.flags.remove_modifiers.values == set([])
    assert feature_level_2.features.override == False
    assert feature_level_2.features.values == set(["L1_F2", "L2_F2"])
    assert feature_level_2.features.remove_modifiers.values == set([])

def test_extends_no_rules_3():
    # feature level 0
    feature_level_0 = FeatureNode("level_0")
    feature_level_0.description = "feature level 0"
    feature_level_0.flags = create_str_list(False, ["L0_1", "L0_2"], ["L0_1", "L0_3"] )
    feature_level_0.features = create_feature_str_list(False, ["L0_F1", "L0_F2"], ["L0_F1", "L0_F3"] )

    feature_level_0 = feature_level_0.resolve_extends(FeatureNode("root"), FeatureRuleNodeList())

    # feature level 1
    feature_level_1 = FeatureNode("level_1")
    feature_level_1.description = "feature level 1"
    feature_level_1.flags = create_str_list(False, ["L1_1", "L1_2"], ["L1_1", "L1_3"] )
    feature_level_1.features = create_feature_str_list(False, ["L1_F1", "L1_F2"], ["L1_F1", "L1_F3"] )

    feature_level_1 = feature_level_1.resolve_extends(feature_level_0, FeatureRuleNodeList())

    assert feature_level_1.name == "level_1"
    assert feature_level_1.description == "feature level 1"
    assert feature_level_1.flags.override == False
    assert feature_level_1.flags.values == set(["L0_2", "L1_2"])
    assert feature_level_1.flags.remove_modifiers.values == set([])
    assert feature_level_1.features.override == False
    assert feature_level_1.features.values == set(["L0_F2", "L1_F2"])
    assert feature_level_1.features.remove_modifiers.values == set([])

    # feature level 2
    feature_level_2 = FeatureNode("level_2")
    feature_level_2.description = "feature level 2"
    feature_level_2.flags = create_str_list(True, ["L2_1", "L2_2"], ["L2_1", "L2_3"] )
    feature_level_2.features = create_feature_str_list(True, ["L2_F1", "L2_F2"], ["L2_F1", "L2_F3"] )

    feature_level_2 = feature_level_2.resolve_extends(feature_level_1, FeatureRuleNodeList())

    assert feature_level_2.name == "level_2"
    assert feature_level_2.description == "feature level 2"
    assert feature_level_2.flags.override == True
    assert feature_level_2.flags.values == set(["L2_2"])
    assert feature_level_2.flags.remove_modifiers.values == set([])
    assert feature_level_2.features.override == True
    assert feature_level_2.features.values == set(["L2_F2"])
    assert feature_level_2.features.remove_modifiers.values == set([])

def test_extends_no_rules_4():
    # feature level 0
    feature_level_0 = FeatureNode("level_0")
    feature_level_0.description = "feature level 0"
    feature_level_0.flags = create_str_list(False, ["L0_1", "L0_2"], ["L0_1", "L0_3"] )
    feature_level_0.features = create_feature_str_list(False, ["L0_F1", "L0_F2"], ["L0_F1", "L0_F3"] )

    feature_level_0 = feature_level_0.resolve_extends(FeatureNode("root"), FeatureRuleNodeList())

    # feature level 1
    feature_level_1 = FeatureNode("level_1")
    feature_level_1.description = "feature level 1"
    feature_level_1.flags = create_str_list(True, ["L1_1", "L1_2"], ["L1_1", "L1_3"] )
    feature_level_1.features = create_feature_str_list(True, ["L1_F1", "L1_F2"], ["L1_F1", "L1_F3"] )

    feature_level_1 = feature_level_1.resolve_extends(feature_level_0, FeatureRuleNodeList())

    assert feature_level_1.name == "level_1"
    assert feature_level_1.description == "feature level 1"
    assert feature_level_1.flags.override == True
    assert feature_level_1.flags.values == set(["L1_2"])
    assert feature_level_1.flags.remove_modifiers.values == set([])
    assert feature_level_1.features.override == True
    assert feature_level_1.features.values == set(["L1_F2"])
    assert feature_level_1.features.remove_modifiers.values == set([])

    # feature level 2
    feature_level_2 = FeatureNode("level_2")
    feature_level_2.description = "feature level 2"
    feature_level_2.flags = create_str_list(True, ["L2_1", "L2_2"], ["L2_1", "L2_3"] )
    feature_level_2.features = create_feature_str_list(True, ["L2_F1", "L2_F2"], ["L2_F1", "L2_F3"] )

    feature_level_2 = feature_level_2.resolve_extends(feature_level_1, FeatureRuleNodeList())

    assert feature_level_2.name == "level_2"
    assert feature_level_2.description == "feature level 2"
    assert feature_level_2.flags.override == True
    assert feature_level_2.flags.values == set(["L2_2"])
    assert feature_level_2.flags.remove_modifiers.values == set([])
    assert feature_level_2.features.override == True
    assert feature_level_2.features.values == set(["L2_F2"])
    assert feature_level_2.features.remove_modifiers.values == set([])

def test_extends_feature_node() :
    test_extends_empty_1()
    test_extends_empty_2()
    test_extends_no_rules_1()
    test_extends_no_rules_2()
    test_extends_no_rules_3()
    test_extends_no_rules_4()