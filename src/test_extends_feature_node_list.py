#   features:
#     - name:
#       description:
#       flags: [] # Add/remove flags
#       features: [] # Add/remove features
#       args:
#         min: 1
#         max: ~
#         separator: ","
#         pattern: "*.lib"

from test_common import create_feature_node, create_feature_rule_node_list, create_feature_rule_node_list, create_feature_str_list, create_incompatible_rule, create_only_one_rule, create_str_list, create_feature_node_list
from toolchain.nodes.feature_node import FeatureNodeList, FeatureRuleNodeIncompatible, FeatureRuleNodeList, FeatureRuleNodeOnlyOne

def test_extends_empty():
    # No feature rule
    result = FeatureNodeList().resolve_extends(FeatureNodeList(), FeatureRuleNodeList())
    assert result.is_empty()

    # only one feature rule
    onlyone_rule = create_only_one_rule("A", "desc a", ["L0_F3", "L1_F3", "L2_F3"])
    feature_rule_list = create_feature_rule_node_list([onlyone_rule])
    result = FeatureNodeList().resolve_extends(FeatureNodeList(), feature_rule_list)
    assert result.is_empty()

    # incompatible feature rule
    feature_rule_list = FeatureRuleNodeList()
    incompatible_rule = create_incompatible_rule("B", "desc b", "L00", ["L0_F3", "L1_F3", "L2_F3"])
    feature_rule_list.add_feature_rule(incompatible_rule)
    result = FeatureNodeList().resolve_extends(FeatureNodeList(), feature_rule_list)
    assert result.is_empty()

    # only one  and incompatible feature rule
    feature_rule_list = create_feature_rule_node_list([onlyone_rule, incompatible_rule])
    result = FeatureNodeList().resolve_extends(FeatureNodeList(), feature_rule_list)
    assert result.is_empty()

def test_extends_child_empty_no_rules_1():
    # level 0 feature list
    level_0_feature_list = FeatureNodeList()

    # Level 1 feature list
    feature_level_1_a_flags = create_str_list(False, ["L1_A_1", "L1_A_2"], ["L1_A_1", "L1_A_3"] )
    feature_level_1_a_features = create_feature_str_list(False, ["L1_A_F1", "L1_A_F2", "L1_A_F3"], ["L1_A_F1"] )
    feature_level_1_b_flags = create_str_list(False, ["L1_B_1", "L1_B_2"], ["L1_B_1", "L1_B_3"] )
    feature_level_1_b_features = create_feature_str_list(False, ["L1_B_F1", "L1_B_F2", "L1_B_F3"], ["L1_B_F1"] )
    level_1_feature_list = create_feature_node_list([create_feature_node("level 1 A", "feature A", feature_level_1_a_flags, feature_level_1_a_features),
                                                     create_feature_node("level 1 B", "feature B", feature_level_1_b_flags, feature_level_1_b_features)])

    # Extends
    level_0_feature_list = level_0_feature_list.resolve_extends(FeatureNodeList(), FeatureRuleNodeList())
    result = level_1_feature_list.resolve_extends(level_0_feature_list, FeatureRuleNodeList())
    
    assert len(result.features) == 2
    feature = result.get_by_name("level 1 A")
    assert feature
    assert feature.name == "level 1 A"
    assert feature.description == "feature A"
    assert feature.flags.override == False
    assert feature.flags.values == set(["L1_A_2"])
    assert feature.features.override == False
    assert feature.features.values == set(["L1_A_F2", "L1_A_F3"])
    feature = result.get_by_name("level 1 B")
    assert feature
    assert feature.name == "level 1 B"
    assert feature.description == "feature B"
    assert feature.flags.override == False
    assert feature.flags.values == set(["L1_B_2"])
    assert feature.features.override == False
    assert feature.features.values == set(["L1_B_F2", "L1_B_F3"])

def test_extends_child_empty_no_rules_2():
    # level 0 feature list
    level_0_feature_list = FeatureNodeList()

    # Level 1 feature list
    feature_level_1_a_flags = create_str_list(True, ["L1_A_1", "L1_A_2"], ["L1_A_1", "L1_A_3"] )
    feature_level_1_a_features = create_feature_str_list(True, ["L1_A_F1", "L1_A_F2", "L1_A_F3"], ["L1_A_F1"] )
    feature_level_1_b_flags = create_str_list(True, ["L1_B_1", "L1_B_2"], ["L1_B_1", "L1_B_3"] )
    feature_level_1_b_features = create_feature_str_list(True, ["L1_B_F1", "L1_B_F2", "L1_B_F3"], ["L1_B_F1"] )
    level_1_feature_list = create_feature_node_list([create_feature_node("level 1 A", "feature A", feature_level_1_a_flags, feature_level_1_a_features),
                                                     create_feature_node("level 1 B", "feature B", feature_level_1_b_flags, feature_level_1_b_features)])

    # Extends
    level_0_feature_list = level_0_feature_list.resolve_extends(FeatureNodeList(), FeatureRuleNodeList())
    result = level_1_feature_list.resolve_extends(level_0_feature_list, FeatureRuleNodeList())
    
    assert len(result.features) == 2
    feature = result.get_by_name("level 1 A")
    assert feature
    assert feature.name == "level 1 A"
    assert feature.description == "feature A"
    assert feature.flags.override == True
    assert feature.flags.values == set(["L1_A_2"])
    assert feature.features.override == True
    assert feature.features.values == set(["L1_A_F2", "L1_A_F3"])
    feature = result.get_by_name("level 1 B")
    assert feature
    assert feature.name == "level 1 B"
    assert feature.description == "feature B"
    assert feature.flags.override == True
    assert feature.flags.values == set(["L1_B_2"])
    assert feature.features.override == True
    assert feature.features.values == set(["L1_B_F2", "L1_B_F3"])

def test_extends_parent_empty_no_rules_1():
    # Level 0 feature list
    feature_level_0_a_flags = create_str_list(False, ["L0_A_1", "L0_A_2"], ["L0_A_1", "L0_A_3"] )
    feature_level_0_a_features = create_feature_str_list(False, ["L0_A_F1", "L0_A_F2", "L0_A_F3"], ["L0_A_F1"] )
    feature_level_0_b_flags = create_str_list(False, ["L0_B_1", "L0_B_2"], ["L0_B_1", "L0_B_3"] )
    feature_level_0_b_features = create_feature_str_list(False, ["L0_B_F1", "L0_B_F2", "L0_B_F3"], ["L0_B_F1"] )
    level_0_feature_list = create_feature_node_list([create_feature_node("level 0 A", "feature A", feature_level_0_a_flags, feature_level_0_a_features),
                                                     create_feature_node("level 0 B", "feature B", feature_level_0_b_flags, feature_level_0_b_features)])

    # level 1 feature list
    level_1_feature_list = FeatureNodeList()

    
    # Extends
    level_0_feature_list = level_0_feature_list.resolve_extends(FeatureNodeList(), FeatureRuleNodeList())
    result = level_1_feature_list.resolve_extends(level_0_feature_list, FeatureRuleNodeList())
    
    assert len(result.features) == 2
    feature = result.get_by_name("level 0 A")
    assert feature
    assert feature.name == "level 0 A"
    assert feature.description == "feature A"
    assert feature.flags.override == False
    assert feature.flags.values == set(["L0_A_2"])
    assert feature.features.override == False
    assert feature.features.values == set(["L0_A_F2", "L0_A_F3"])
    feature = result.get_by_name("level 0 B")
    assert feature
    assert feature.name == "level 0 B"
    assert feature.description == "feature B"
    assert feature.flags.override == False
    assert feature.flags.values == set(["L0_B_2"])
    assert feature.features.override == False
    assert feature.features.values == set(["L0_B_F2", "L0_B_F3"])

def test_extends_parent_empty_no_rules_2():
    # Level 0 feature list
    feature_level_0_a_flags = create_str_list(True, ["L0_A_1", "L0_A_2"], ["L0_A_1", "L0_A_3"] )
    feature_level_0_a_features = create_feature_str_list(True, ["L0_A_F1", "L0_A_F2", "L0_A_F3"], ["L0_A_F1"] )
    feature_level_0_b_flags = create_str_list(True, ["L0_B_1", "L0_B_2"], ["L0_B_1", "L0_B_3"] )
    feature_level_0_b_features = create_feature_str_list(True, ["L0_B_F1", "L0_B_F2", "L0_B_F3"], ["L0_B_F1"] )
    level_0_feature_list = create_feature_node_list([create_feature_node("level 0 A", "feature A", feature_level_0_a_flags, feature_level_0_a_features),
                                                     create_feature_node("level 0 B", "feature B", feature_level_0_b_flags, feature_level_0_b_features)])

    # level 1 feature list
    level_1_feature_list = FeatureNodeList()

    
    # Extends
    level_0_feature_list = level_0_feature_list.resolve_extends(FeatureNodeList(), FeatureRuleNodeList())
    result = level_1_feature_list.resolve_extends(level_0_feature_list, FeatureRuleNodeList())
    
    assert len(result.features) == 2
    feature = result.get_by_name("level 0 A")
    assert feature
    assert feature.name == "level 0 A"
    assert feature.description == "feature A"
    assert feature.flags.override == False
    assert feature.flags.values == set(["L0_A_2"])
    assert feature.features.override == False
    assert feature.features.values == set(["L0_A_F2", "L0_A_F3"])
    feature = result.get_by_name("level 0 B")
    assert feature
    assert feature.name == "level 0 B"
    assert feature.description == "feature B"
    assert feature.flags.override == False
    assert feature.flags.values == set(["L0_B_2"])
    assert feature.features.override == False
    assert feature.features.values == set(["L0_B_F2", "L0_B_F3"])

def test_extends_no_rules_no_merge_1():
    # level 0 feature list
    feature_level_0_a_flags = create_str_list(False, ["L0_A_1", "L0_A_2"], ["L0_A_1", "L0_A_3"] )
    feature_level_0_a_features = create_feature_str_list(False, ["L0_A_F1", "L0_A_F2", "L0_A_F3"], ["L0_A_F1"] )
    feature_level_0_b_flags = create_str_list(False, ["L0_B_1", "L0_B_2"], ["L0_B_1", "L0_B_3"] )
    feature_level_0_b_features = create_feature_str_list(False, ["L0_B_F1", "L0_B_F2", "L0_B_F3"], ["L0_B_F1"] )
    level_0_feature_list = create_feature_node_list([create_feature_node("level 0 A", "feature A", feature_level_0_a_flags, feature_level_0_a_features),
                                                        create_feature_node("level 0 B", "feature B", feature_level_0_b_flags, feature_level_0_b_features)])

    # Level 1 feature list
    feature_level_1_a_flags = create_str_list(False, ["L1_A_1", "L1_A_2"], ["L1_A_1", "L1_A_3"] )
    feature_level_1_a_features = create_feature_str_list(False, ["L1_A_F1", "L1_A_F2", "L1_A_F3"], ["L1_A_F1"] )
    feature_level_1_b_flags = create_str_list(False, ["L1_B_1", "L1_B_2"], ["L1_B_1", "L1_B_3"] )
    feature_level_1_b_features = create_feature_str_list(False, ["L1_B_F1", "L1_B_F2", "L1_B_F3"], ["L1_B_F1"] )
    level_1_feature_list = create_feature_node_list([create_feature_node("level 1 A", "feature A", feature_level_1_a_flags, feature_level_1_a_features),
                                                     create_feature_node("level 1 B", "feature B", feature_level_1_b_flags, feature_level_1_b_features)])

    # Extends
    level_0_feature_list = level_0_feature_list.resolve_extends(FeatureNodeList(), FeatureRuleNodeList())
    result = level_1_feature_list.resolve_extends(level_0_feature_list, FeatureRuleNodeList())
    
    assert len(result.features) == 4
    feature = result.get_by_name("level 0 A")
    assert feature
    assert feature.name == "level 0 A"
    assert feature.description == "feature A"
    assert feature.flags.override == False
    assert feature.flags.values == set(["L0_A_2"])
    assert feature.features.override == False
    assert feature.features.values == set(["L0_A_F2", "L0_A_F3"])
    feature = result.get_by_name("level 0 B")
    assert feature
    assert feature.name == "level 0 B"
    assert feature.description == "feature B"
    assert feature.flags.override == False
    assert feature.flags.values == set(["L0_B_2"])
    assert feature.features.override == False
    assert feature.features.values == set(["L0_B_F2", "L0_B_F3"])

    feature = result.get_by_name("level 1 A")
    assert feature
    assert feature.name == "level 1 A"
    assert feature.description == "feature A"
    assert feature.flags.override == False
    assert feature.flags.values == set(["L1_A_2"])
    assert feature.features.override == False
    assert feature.features.values == set(["L1_A_F2", "L1_A_F3"])
    feature = result.get_by_name("level 1 B")
    assert feature
    assert feature.name == "level 1 B"
    assert feature.description == "feature B"
    assert feature.flags.override == False
    assert feature.flags.values == set(["L1_B_2"])
    assert feature.features.override == False
    assert feature.features.values == set(["L1_B_F2", "L1_B_F3"])

def test_extends_no_rules_no_merge_2():
    # level 0 feature list
    feature_level_0_a_flags = create_str_list(True, ["L0_A_1", "L0_A_2"], ["L0_A_1", "L0_A_3"] )
    feature_level_0_a_features = create_feature_str_list(True, ["L0_A_F1", "L0_A_F2", "L0_A_F3"], ["L0_A_F1"] )
    feature_level_0_b_flags = create_str_list(True, ["L0_B_1", "L0_B_2"], ["L0_B_1", "L0_B_3"] )
    feature_level_0_b_features = create_feature_str_list(True, ["L0_B_F1", "L0_B_F2", "L0_B_F3"], ["L0_B_F1"] )
    level_0_feature_list = create_feature_node_list([create_feature_node("level 0 A", "feature A", feature_level_0_a_flags, feature_level_0_a_features),
                                                     create_feature_node("level 0 B", "feature B", feature_level_0_b_flags, feature_level_0_b_features)])

    # Level 1 feature list
    feature_level_1_a_flags = create_str_list(False, ["L1_A_1", "L1_A_2"], ["L1_A_1", "L1_A_3"] )
    feature_level_1_a_features = create_feature_str_list(False, ["L1_A_F1", "L1_A_F2", "L1_A_F3"], ["L1_A_F1"] )
    feature_level_1_b_flags = create_str_list(False, ["L1_B_1", "L1_B_2"], ["L1_B_1", "L1_B_3"] )
    feature_level_1_b_features = create_feature_str_list(False, ["L1_B_F1", "L1_B_F2", "L1_B_F3"], ["L1_B_F1"] )
    level_1_feature_list = create_feature_node_list([create_feature_node("level 1 A", "feature A", feature_level_1_a_flags, feature_level_1_a_features),
                                                     create_feature_node("level 1 B", "feature B", feature_level_1_b_flags, feature_level_1_b_features)])

    # Extends
    level_0_feature_list = level_0_feature_list.resolve_extends(FeatureNodeList(), FeatureRuleNodeList())
    result = level_1_feature_list.resolve_extends(level_0_feature_list, FeatureRuleNodeList())
    
    assert len(result.features) == 4
    feature = result.get_by_name("level 0 A")
    assert feature
    assert feature.name == "level 0 A"
    assert feature.description == "feature A"
    assert feature.flags.override == False
    assert feature.flags.values == set(["L0_A_2"])
    assert feature.features.override == False
    assert feature.features.values == set(["L0_A_F2", "L0_A_F3"])
    feature = result.get_by_name("level 0 B")
    assert feature
    assert feature.name == "level 0 B"
    assert feature.description == "feature B"
    assert feature.flags.override == False
    assert feature.flags.values == set(["L0_B_2"])
    assert feature.features.override == False
    assert feature.features.values == set(["L0_B_F2", "L0_B_F3"])

    feature = result.get_by_name("level 1 A")
    assert feature
    assert feature.name == "level 1 A"
    assert feature.description == "feature A"
    assert feature.flags.override == False
    assert feature.flags.values == set(["L1_A_2"])
    assert feature.features.override == False
    assert feature.features.values == set(["L1_A_F2", "L1_A_F3"])
    feature = result.get_by_name("level 1 B")
    assert feature
    assert feature.name == "level 1 B"
    assert feature.description == "feature B"
    assert feature.flags.override == False
    assert feature.flags.values == set(["L1_B_2"])
    assert feature.features.override == False
    assert feature.features.values == set(["L1_B_F2", "L1_B_F3"])

def test_extends_no_rules_no_merge_3():
    # level 0 feature list
    feature_level_0_a_flags = create_str_list(False, ["L0_A_1", "L0_A_2"], ["L0_A_1", "L0_A_3"] )
    feature_level_0_a_features = create_feature_str_list(False, ["L0_A_F1", "L0_A_F2", "L0_A_F3"], ["L0_A_F1"] )
    feature_level_0_b_flags = create_str_list(False, ["L0_B_1", "L0_B_2"], ["L0_B_1", "L0_B_3"] )
    feature_level_0_b_features = create_feature_str_list(False, ["L0_B_F1", "L0_B_F2", "L0_B_F3"], ["L0_B_F1"] )
    level_0_feature_list = create_feature_node_list([create_feature_node("level 0 A", "feature A", feature_level_0_a_flags, feature_level_0_a_features),
                                                        create_feature_node("level 0 B", "feature B", feature_level_0_b_flags, feature_level_0_b_features)])

    # Level 1 feature list
    feature_level_1_a_flags = create_str_list(True, ["L1_A_1", "L1_A_2"], ["L1_A_1", "L1_A_3"] )
    feature_level_1_a_features = create_feature_str_list(True, ["L1_A_F1", "L1_A_F2", "L1_A_F3"], ["L1_A_F1"] )
    feature_level_1_b_flags = create_str_list(True, ["L1_B_1", "L1_B_2"], ["L1_B_1", "L1_B_3"] )
    feature_level_1_b_features = create_feature_str_list(True, ["L1_B_F1", "L1_B_F2", "L1_B_F3"], ["L1_B_F1"] )
    level_1_feature_list = create_feature_node_list([create_feature_node("level 1 A", "feature A", feature_level_1_a_flags, feature_level_1_a_features),
                                                     create_feature_node("level 1 B", "feature B", feature_level_1_b_flags, feature_level_1_b_features)])

    # Extends
    level_0_feature_list = level_0_feature_list.resolve_extends(FeatureNodeList(), FeatureRuleNodeList())
    result = level_1_feature_list.resolve_extends(level_0_feature_list, FeatureRuleNodeList())
    
    assert len(result.features) == 4
    feature = result.get_by_name("level 0 A")
    assert feature
    assert feature.name == "level 0 A"
    assert feature.description == "feature A"
    assert feature.flags.override == False
    assert feature.flags.values == set(["L0_A_2"])
    assert feature.features.override == False
    assert feature.features.values == set(["L0_A_F2", "L0_A_F3"])
    feature = result.get_by_name("level 0 B")
    assert feature
    assert feature.name == "level 0 B"
    assert feature.description == "feature B"
    assert feature.flags.override == False
    assert feature.flags.values == set(["L0_B_2"])
    assert feature.features.override == False
    assert feature.features.values == set(["L0_B_F2", "L0_B_F3"])

    feature = result.get_by_name("level 1 A")
    assert feature
    assert feature.name == "level 1 A"
    assert feature.description == "feature A"
    assert feature.flags.override == True
    assert feature.flags.values == set(["L1_A_2"])
    assert feature.features.override == True
    assert feature.features.values == set(["L1_A_F2", "L1_A_F3"])
    feature = result.get_by_name("level 1 B")
    assert feature
    assert feature.name == "level 1 B"
    assert feature.description == "feature B"
    assert feature.flags.override == True
    assert feature.flags.values == set(["L1_B_2"])
    assert feature.features.override == True
    assert feature.features.values == set(["L1_B_F2", "L1_B_F3"])

def test_extends_no_rules_no_merge_4():
    # level 0 feature list
    feature_level_0_a_flags = create_str_list(True, ["L0_A_1", "L0_A_2"], ["L0_A_1", "L0_A_3"] )
    feature_level_0_a_features = create_feature_str_list(True, ["L0_A_F1", "L0_A_F2", "L0_A_F3"], ["L0_A_F1"] )
    feature_level_0_b_flags = create_str_list(True, ["L0_B_1", "L0_B_2"], ["L0_B_1", "L0_B_3"] )
    feature_level_0_b_features = create_feature_str_list(True, ["L0_B_F1", "L0_B_F2", "L0_B_F3"], ["L0_B_F1"] )
    level_0_feature_list = create_feature_node_list([create_feature_node("level 0 A", "feature A", feature_level_0_a_flags, feature_level_0_a_features),
                                                     create_feature_node("level 0 B", "feature B", feature_level_0_b_flags, feature_level_0_b_features)])

    # Level 1 feature list
    feature_level_1_a_flags = create_str_list(True, ["L1_A_1", "L1_A_2"], ["L1_A_1", "L1_A_3"] )
    feature_level_1_a_features = create_feature_str_list(True, ["L1_A_F1", "L1_A_F2", "L1_A_F3"], ["L1_A_F1"] )
    feature_level_1_b_flags = create_str_list(True, ["L1_B_1", "L1_B_2"], ["L1_B_1", "L1_B_3"] )
    feature_level_1_b_features = create_feature_str_list(True, ["L1_B_F1", "L1_B_F2", "L1_B_F3"], ["L1_B_F1"] )
    level_1_feature_list = create_feature_node_list([create_feature_node("level 1 A", "feature A", feature_level_1_a_flags, feature_level_1_a_features),
                                                     create_feature_node("level 1 B", "feature B", feature_level_1_b_flags, feature_level_1_b_features)])

    # Extends
    level_0_feature_list = level_0_feature_list.resolve_extends(FeatureNodeList(), FeatureRuleNodeList())
    result = level_1_feature_list.resolve_extends(level_0_feature_list, FeatureRuleNodeList())
    
    assert len(result.features) == 4
    feature = result.get_by_name("level 0 A")
    assert feature
    assert feature.name == "level 0 A"
    assert feature.description == "feature A"
    assert feature.flags.override == False
    assert feature.flags.values == set(["L0_A_2"])
    assert feature.features.override == False
    assert feature.features.values == set(["L0_A_F2", "L0_A_F3"])
    feature = result.get_by_name("level 0 B")
    assert feature
    assert feature.name == "level 0 B"
    assert feature.description == "feature B"
    assert feature.flags.override == False
    assert feature.flags.values == set(["L0_B_2"])
    assert feature.features.override == False
    assert feature.features.values == set(["L0_B_F2", "L0_B_F3"])

    feature = result.get_by_name("level 1 A")
    assert feature
    assert feature.name == "level 1 A"
    assert feature.description == "feature A"
    assert feature.flags.override == True
    assert feature.flags.values == set(["L1_A_2"])
    assert feature.features.override == True
    assert feature.features.values == set(["L1_A_F2", "L1_A_F3"])
    feature = result.get_by_name("level 1 B")
    assert feature
    assert feature.name == "level 1 B"
    assert feature.description == "feature B"
    assert feature.flags.override == True
    assert feature.flags.values == set(["L1_B_2"])
    assert feature.features.override == True
    assert feature.features.values == set(["L1_B_F2", "L1_B_F3"])

def test_extends_no_rules_merge_1():
    # level 0 feature list
    feature_level_0_a_flags = create_str_list(False, ["L0_A_1", "L0_A_2"], ["L0_A_1", "L0_A_3"] )
    feature_level_0_a_features = create_feature_str_list(False, ["L0_A_F1", "L0_A_F2", "L0_A_F3"], ["L0_A_F1"] )
    feature_level_0_b_flags = create_str_list(False, ["L0_B_1", "L0_B_2"], ["L0_B_1", "L0_B_3"] )
    feature_level_0_b_features = create_feature_str_list(False, ["L0_B_F1", "L0_B_F2", "L0_B_F3"], ["L0_B_F1"] )
    level_0_feature_list = create_feature_node_list([create_feature_node("level 0 A", "feature A", feature_level_0_a_flags, feature_level_0_a_features),
                                                     create_feature_node("level 0 B", "feature B", feature_level_0_b_flags, feature_level_0_b_features)])

    # Level 1 feature list
    feature_level_1_a_flags = create_str_list(False, ["L1_A_1", "L1_A_2"], ["L1_A_1", "L1_A_3"] )
    feature_level_1_a_features = create_feature_str_list(False, ["L1_A_F1", "L1_A_F2", "L1_A_F3"], ["L1_A_F1"] )
    feature_level_1_b_flags = create_str_list(False, ["L1_B_1", "L1_B_2"], ["L1_B_1", "L1_B_3"] )
    feature_level_1_b_features = create_feature_str_list(False, ["L1_B_F1", "L1_B_F2", "L1_B_F3"], ["L1_B_F1"] )
    level_1_feature_list = create_feature_node_list([create_feature_node("level 0 A", "feature A", feature_level_1_a_flags, feature_level_1_a_features),
                                                     create_feature_node("level 1 B", "feature B", feature_level_1_b_flags, feature_level_1_b_features)])

    # Extends
    level_0_feature_list = level_0_feature_list.resolve_extends(FeatureNodeList(), FeatureRuleNodeList())
    result = level_1_feature_list.resolve_extends(level_0_feature_list, FeatureRuleNodeList())
    
    assert len(result.features) == 3
    feature = result.get_by_name("level 0 A")
    assert feature
    assert feature.name == "level 0 A"
    assert feature.description == "feature A"
    assert feature.flags.override == False
    assert feature.flags.values == set(["L0_A_2", "L1_A_2"])
    assert feature.features.override == False
    assert feature.features.values == set(["L0_A_F2", "L0_A_F3", "L1_A_F2", "L1_A_F3"])
    feature = result.get_by_name("level 0 B")
    assert feature
    assert feature.name == "level 0 B"
    assert feature.description == "feature B"
    assert feature.flags.override == False
    assert feature.flags.values == set(["L0_B_2"])
    assert feature.features.override == False
    assert feature.features.values == set(["L0_B_F2", "L0_B_F3"])

    feature = result.get_by_name("level 1 B")
    assert feature
    assert feature.name == "level 1 B"
    assert feature.description == "feature B"
    assert feature.flags.override == False
    assert feature.flags.values == set(["L1_B_2"])
    assert feature.features.override == False
    assert feature.features.values == set(["L1_B_F2", "L1_B_F3"])

def test_extends_no_rules_merge_2():
    # level 0 feature list
    feature_level_0_a_flags = create_str_list(True, ["L0_A_1", "L0_A_2"], ["L0_A_1", "L0_A_3"] )
    feature_level_0_a_features = create_feature_str_list(True, ["L0_A_F1", "L0_A_F2", "L0_A_F3"], ["L0_A_F1"] )
    feature_level_0_b_flags = create_str_list(True, ["L0_B_1", "L0_B_2"], ["L0_B_1", "L0_B_3"] )
    feature_level_0_b_features = create_feature_str_list(True, ["L0_B_F1", "L0_B_F2", "L0_B_F3"], ["L0_B_F1"] )
    level_0_feature_list = create_feature_node_list([create_feature_node("level 0 A", "feature A", feature_level_0_a_flags, feature_level_0_a_features),
                                                     create_feature_node("level 0 B", "feature B", feature_level_0_b_flags, feature_level_0_b_features)])

    # Level 1 feature list
    feature_level_1_a_flags = create_str_list(False, ["L1_A_1", "L1_A_2"], ["L1_A_1", "L1_A_3"] )
    feature_level_1_a_features = create_feature_str_list(False, ["L1_A_F1", "L1_A_F2", "L1_A_F3"], ["L1_A_F1"] )
    feature_level_1_b_flags = create_str_list(False, ["L1_B_1", "L1_B_2"], ["L1_B_1", "L1_B_3"] )
    feature_level_1_b_features = create_feature_str_list(False, ["L1_B_F1", "L1_B_F2", "L1_B_F3"], ["L1_B_F1"] )
    level_1_feature_list = create_feature_node_list([create_feature_node("level 0 A", "feature A", feature_level_1_a_flags, feature_level_1_a_features),
                                                     create_feature_node("level 1 B", "feature B", feature_level_1_b_flags, feature_level_1_b_features)])

    # Extends
    level_0_feature_list = level_0_feature_list.resolve_extends(FeatureNodeList(), FeatureRuleNodeList())
    result = level_1_feature_list.resolve_extends(level_0_feature_list, FeatureRuleNodeList())
    
    assert len(result.features) == 3
    feature = result.get_by_name("level 0 A")
    assert feature
    assert feature.name == "level 0 A"
    assert feature.description == "feature A"
    assert feature.flags.override == False
    assert feature.flags.values == set(["L0_A_2", "L1_A_2"])
    assert feature.features.override == False
    assert feature.features.values == set(["L0_A_F2", "L0_A_F3", "L1_A_F2", "L1_A_F3"])
    feature = result.get_by_name("level 0 B")
    assert feature
    assert feature.name == "level 0 B"
    assert feature.description == "feature B"
    assert feature.flags.override == False
    assert feature.flags.values == set(["L0_B_2"])
    assert feature.features.override == False
    assert feature.features.values == set(["L0_B_F2", "L0_B_F3"])

    feature = result.get_by_name("level 1 B")
    assert feature
    assert feature.name == "level 1 B"
    assert feature.description == "feature B"
    assert feature.flags.override == False
    assert feature.flags.values == set(["L1_B_2"])
    assert feature.features.override == False
    assert feature.features.values == set(["L1_B_F2", "L1_B_F3"])

def test_extends_no_rules_merge_3():
    # level 0 feature list
    feature_level_0_a_flags = create_str_list(False, ["L0_A_1", "L0_A_2"], ["L0_A_1", "L0_A_3"] )
    feature_level_0_a_features = create_feature_str_list(False, ["L0_A_F1", "L0_A_F2", "L0_A_F3"], ["L0_A_F1"] )
    feature_level_0_b_flags = create_str_list(False, ["L0_B_1", "L0_B_2"], ["L0_B_1", "L0_B_3"] )
    feature_level_0_b_features = create_feature_str_list(False, ["L0_B_F1", "L0_B_F2", "L0_B_F3"], ["L0_B_F1"] )
    level_0_feature_list = create_feature_node_list([create_feature_node("level 0 A", "feature A", feature_level_0_a_flags, feature_level_0_a_features),
                                                     create_feature_node("level 0 B", "feature B", feature_level_0_b_flags, feature_level_0_b_features)])

    # Level 1 feature list
    feature_level_1_a_flags = create_str_list(True, ["L1_A_1", "L1_A_2"], ["L1_A_1", "L1_A_3"] )
    feature_level_1_a_features = create_feature_str_list(True, ["L1_A_F1", "L1_A_F2", "L1_A_F3"], ["L1_A_F1"] )
    feature_level_1_b_flags = create_str_list(True, ["L1_B_1", "L1_B_2"], ["L1_B_1", "L1_B_3"] )
    feature_level_1_b_features = create_feature_str_list(True, ["L1_B_F1", "L1_B_F2", "L1_B_F3"], ["L1_B_F1"] )
    level_1_feature_list = create_feature_node_list([create_feature_node("level 0 A", "feature A", feature_level_1_a_flags, feature_level_1_a_features),
                                                     create_feature_node("level 1 B", "feature B", feature_level_1_b_flags, feature_level_1_b_features)])

    # Extends
    level_0_feature_list = level_0_feature_list.resolve_extends(FeatureNodeList(), FeatureRuleNodeList())
    result = level_1_feature_list.resolve_extends(level_0_feature_list, FeatureRuleNodeList())
    
    assert len(result.features) == 3
    feature = result.get_by_name("level 0 A")
    assert feature
    assert feature.name == "level 0 A"
    assert feature.description == "feature A"
    assert feature.flags.override == True
    assert feature.flags.values == set(["L1_A_2"])
    assert feature.features.override == True
    assert feature.features.values == set(["L1_A_F2", "L1_A_F3"])
    feature = result.get_by_name("level 0 B")
    assert feature
    assert feature.name == "level 0 B"
    assert feature.description == "feature B"
    assert feature.flags.override == False
    assert feature.flags.values == set(["L0_B_2"])
    assert feature.features.override == False
    assert feature.features.values == set(["L0_B_F2", "L0_B_F3"])

    feature = result.get_by_name("level 1 B")
    assert feature
    assert feature.name == "level 1 B"
    assert feature.description == "feature B"
    assert feature.flags.override == True
    assert feature.flags.values == set(["L1_B_2"])
    assert feature.features.override == True
    assert feature.features.values == set(["L1_B_F2", "L1_B_F3"])

def test_extends_no_rules_merge_4():
    # level 0 feature list
    feature_level_0_a_flags = create_str_list(True, ["L0_A_1", "L0_A_2"], ["L0_A_1", "L0_A_3"] )
    feature_level_0_a_features = create_feature_str_list(True, ["L0_A_F1", "L0_A_F2", "L0_A_F3"], ["L0_A_F1"] )
    feature_level_0_b_flags = create_str_list(True, ["L0_B_1", "L0_B_2"], ["L0_B_1", "L0_B_3"] )
    feature_level_0_b_features = create_feature_str_list(True, ["L0_B_F1", "L0_B_F2", "L0_B_F3"], ["L0_B_F1"] )
    level_0_feature_list = create_feature_node_list([create_feature_node("level 0 A", "feature A", feature_level_0_a_flags, feature_level_0_a_features),
                                                     create_feature_node("level 0 B", "feature B", feature_level_0_b_flags, feature_level_0_b_features)])

    # Level 1 feature list
    feature_level_1_a_flags = create_str_list(True, ["L1_A_1", "L1_A_2"], ["L1_A_1", "L1_A_3"] )
    feature_level_1_a_features = create_feature_str_list(True, ["L1_A_F1", "L1_A_F2", "L1_A_F3"], ["L1_A_F1"] )
    feature_level_1_b_flags = create_str_list(True, ["L1_B_1", "L1_B_2"], ["L1_B_1", "L1_B_3"] )
    feature_level_1_b_features = create_feature_str_list(True, ["L1_B_F1", "L1_B_F2", "L1_B_F3"], ["L1_B_F1"] )
    level_1_feature_list = create_feature_node_list([create_feature_node("level 0 A", "feature A", feature_level_1_a_flags, feature_level_1_a_features),
                                                     create_feature_node("level 1 B", "feature B", feature_level_1_b_flags, feature_level_1_b_features)])

    # Extends
    level_0_feature_list = level_0_feature_list.resolve_extends(FeatureNodeList(), FeatureRuleNodeList())
    result = level_1_feature_list.resolve_extends(level_0_feature_list, FeatureRuleNodeList())
    
    assert len(result.features) == 3
    feature = result.get_by_name("level 0 A")
    assert feature
    assert feature.name == "level 0 A"
    assert feature.description == "feature A"
    assert feature.flags.override == True
    assert feature.flags.values == set(["L1_A_2"])
    assert feature.features.override == True
    assert feature.features.values == set(["L1_A_F2", "L1_A_F3"])
    feature = result.get_by_name("level 0 B")
    assert feature
    assert feature.name == "level 0 B"
    assert feature.description == "feature B"
    assert feature.flags.override == False
    assert feature.flags.values == set(["L0_B_2"])
    assert feature.features.override == False
    assert feature.features.values == set(["L0_B_F2", "L0_B_F3"])

    feature = result.get_by_name("level 1 B")
    assert feature
    assert feature.name == "level 1 B"
    assert feature.description == "feature B"
    assert feature.flags.override == True
    assert feature.flags.values == set(["L1_B_2"])
    assert feature.features.override == True
    assert feature.features.values == set(["L1_B_F2", "L1_B_F3"])

def test_extends_child_only_one_rule():
   pass

def test_extends_parent_incompatible_rule():
    pass

def test_extends_child_rules():
    pass

def test_extends_feature_node_list() :
    test_extends_empty()

    test_extends_child_empty_no_rules_1()
    test_extends_child_empty_no_rules_2()
    test_extends_parent_empty_no_rules_1()
    test_extends_parent_empty_no_rules_2()

    test_extends_no_rules_no_merge_1()
    test_extends_no_rules_no_merge_2()
    test_extends_no_rules_no_merge_3()
    test_extends_no_rules_no_merge_4()
    
    test_extends_no_rules_merge_1()
    test_extends_no_rules_merge_2()
    test_extends_no_rules_merge_3()
    test_extends_no_rules_merge_4()


    test_extends_onlyone_rule_merge_1()