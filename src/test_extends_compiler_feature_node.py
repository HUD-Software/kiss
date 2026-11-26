# - name:
#     description:
#     flags: [] # Add/remove flags
#     features: [] # Add/remove features
#     args:
#       min: 1
#       max: ~
#       separator: ","
#       pattern: "*.lib"
#     linkers:
#       features: []
#       linker-name:
#         features: []
from test_common import create_feature_rule_node_list, create_feature_str_list, create_linker_override_node, create_linker_override_node_1, create_only_one_rule, create_str_list
from toolchain.nodes.compiler_nodes import CompilerFeatureNode
from toolchain.nodes.feature_node import FeatureRuleNodeList

def test_extends_parent_empty_1():
    # feature level 0
    feature_level_0 = CompilerFeatureNode("level 0")
    feature_level_0.description = "feature level 0"
    feature_level_0.flags = create_str_list(False, ["L0_1", "L0_2"], ["L0_1", "L0_3"] )
    feature_level_0.features = create_feature_str_list(False, ["L0_F1", "L0_F2", "L0_F3"], ["L0_F1"] )
    feature_level_0.linkers = create_linker_override_node(None, None, None)

    result = feature_level_0.resolve_extends(CompilerFeatureNode("root"), {}, FeatureRuleNodeList()).unwrap()

    assert result.name == "level 0"
    assert result.description == "feature level 0"
    assert result.flags.override == False
    assert result.flags.values == set(["L0_2"])
    assert result.flags.remove_modifiers.values == set(["L0_1", "L0_3"])
    assert result.features.override == False
    assert result.features.values == set(["L0_F2", "L0_F3"])
    assert result.features.remove_modifiers.values == set( ["L0_F1"])
    assert result.linkers.common_linker.features.is_empty()
    assert result.linkers.common_linker.flags.is_empty()
    assert len(result.linkers.linker_overrides) == 0

def test_extends_parent_empty_2():
    # feature level 0
    feature_level_0 = CompilerFeatureNode("level 0")
    feature_level_0.description = "feature level 0"
    feature_level_0.flags = create_str_list(True, ["L0_1", "L0_2"], ["L0_1", "L0_3"] )
    feature_level_0.features = create_feature_str_list(True, ["L0_F1", "L0_F2", "L0_F3"], ["L0_F1"] )
    feature_level_0.linkers = create_linker_override_node(None, None, None)

    result = feature_level_0.resolve_extends(CompilerFeatureNode("root"), {},FeatureRuleNodeList()).unwrap()

    assert result.name == "level 0"
    assert result.description == "feature level 0"
    assert result.flags.override == True
    assert result.flags.values == set(["L0_2"])
    assert result.flags.remove_modifiers.values == set(["L0_1", "L0_3"] )
    assert result.features.override == True
    assert result.features.values == set(["L0_F2", "L0_F3"])
    assert result.features.remove_modifiers.values == set( ["L0_F1"])
    assert result.linkers.common_linker.features.is_empty()
    assert result.linkers.common_linker.flags.is_empty()
    assert len(result.linkers.linker_overrides) == 0

def test_extends_parent_empty_linker_override_1():
    # feature level 0
    feature_level_0 = CompilerFeatureNode("level 0")
    feature_level_0.description = "feature level 0"
    feature_level_0.flags = create_str_list(False, ["L0_1", "L0_2"], ["L0_1", "L0_3"] )
    feature_level_0.features = create_feature_str_list(False, ["L0_F1", "L0_F2", "L0_F3"], ["L0_F1"] )
    feature_level_0.linkers = create_linker_override_node_1()

    result = feature_level_0.resolve_extends(CompilerFeatureNode("root"), {}, FeatureRuleNodeList()).unwrap()

    assert result.name == "level 0"
    assert result.description == "feature level 0"
    assert result.flags.override == False
    assert result.flags.values == set(["L0_2"])
    assert result.flags.remove_modifiers.values == set(["L0_1", "L0_3"])
    assert result.features.override == False
    assert result.features.values == set(["L0_F2", "L0_F3"])
    assert result.features.remove_modifiers.values == set( ["L0_F1"])
    assert result.linkers.common_linker.flags.override == False
    assert result.linkers.common_linker.flags.values == set(["C2"])
    assert result.linkers.common_linker.flags.remove_modifiers.values == set(["C1", "C3"])
    assert result.linkers.common_linker.features.override == False
    assert result.linkers.common_linker.features.values == set(["CF2"])
    assert result.linkers.common_linker.features.remove_modifiers.values == set(["CF1", "CF3"])
    ld = result.linkers.linker_overrides.get("ld")
    assert ld
    assert ld.flags.override == False
    assert ld.flags.values == set(["C2", "C3", "LD1"])
    assert ld.flags.remove_modifiers.values == set(["LD2"]) 
    assert ld.features.override == False
    assert ld.features.values == set(["CF2", "CF3", "LDF1"])
    assert ld.features.remove_modifiers.values == set(["LDF2"]) 

def test_extends_parent_empty_linker_override_2():
    # feature level 0
    feature_level_0 = CompilerFeatureNode("level 0")
    feature_level_0.description = "feature level 0"
    feature_level_0.flags = create_str_list(True, ["L0_1", "L0_2"], ["L0_1", "L0_3"] )
    feature_level_0.features = create_feature_str_list(True, ["L0_F1", "L0_F2", "L0_F3"], ["L0_F1"] )
    feature_level_0.linkers = create_linker_override_node_1()

    result = feature_level_0.resolve_extends(CompilerFeatureNode("root"), {},FeatureRuleNodeList()).unwrap()

    assert result.name == "level 0"
    assert result.description == "feature level 0"
    assert result.flags.override == True
    assert result.flags.values == set(["L0_2"])
    assert result.flags.remove_modifiers.values == set(["L0_1", "L0_3"] )
    assert result.features.override == True
    assert result.features.values == set(["L0_F2", "L0_F3"])
    assert result.features.remove_modifiers.values == set( ["L0_F1"])
    assert result.linkers.common_linker.flags.override == False
    assert result.linkers.common_linker.flags.values == set(["C2"])
    assert result.linkers.common_linker.flags.remove_modifiers.values == set(["C1", "C3"])
    assert result.linkers.common_linker.features.override == False
    assert result.linkers.common_linker.features.values == set(["CF2"])
    assert result.linkers.common_linker.features.remove_modifiers.values == set(["CF1", "CF3"])
    ld = result.linkers.linker_overrides.get("ld")
    assert ld
    assert ld.flags.override == False
    assert ld.flags.values == set(["C2", "C3", "LD1"])
    assert ld.flags.remove_modifiers.values == set(["LD2"]) 
    assert ld.features.override == False
    assert ld.features.values == set(["CF2", "CF3", "LDF1"])
    assert ld.features.remove_modifiers.values == set(["LDF2"]) 

def test_extends_no_rules_1():
    # feature level 0
    feature_level_0 = CompilerFeatureNode("level 0")
    feature_level_0.description = "feature level 0"
    feature_level_0.flags = create_str_list(False, ["L0_1", "L0_2"], ["L0_1", "L0_3"] )
    feature_level_0.features = create_feature_str_list(False, ["L0_F1", "L0_F2", "L0_F3"], ["L0_F1"] )
    feature_level_0.linkers = create_linker_override_node(None, None, None)

    feature_level_0 = feature_level_0.resolve_extends(CompilerFeatureNode("root"), {},FeatureRuleNodeList()).unwrap()

    # feature level 1
    feature_level_1 = CompilerFeatureNode("level_1")
    feature_level_1.description = "feature level 1"
    feature_level_1.flags = create_str_list(False, ["L1_1", "L1_2"], ["L1_1", "L1_3"] )
    feature_level_1.features = create_feature_str_list(False, ["L1_F1", "L1_F2", "L1_F3"], ["L1_F1"] )
    feature_level_1.linkers = create_linker_override_node(None, None, None)

    feature_level_1 = feature_level_1.resolve_extends(feature_level_0, {}, FeatureRuleNodeList()).unwrap()

    assert feature_level_1.name == "level_1"
    assert feature_level_1.description == "feature level 1"
    assert feature_level_1.flags.override == False
    assert feature_level_1.flags.values == set(["L0_2", "L1_2"])
    assert feature_level_1.flags.remove_modifiers.values == set(["L1_1", "L1_3"] )
    assert feature_level_1.features.override == False
    assert feature_level_1.features.values == set(["L0_F2", "L0_F3", "L1_F2", "L1_F3"])
    assert feature_level_1.features.remove_modifiers.values == set(["L1_F1"] )
    assert feature_level_1.linkers.common_linker.features.is_empty()
    assert feature_level_1.linkers.common_linker.flags.is_empty()
    assert len(feature_level_1.linkers.linker_overrides) == 0

    # feature level 2
    feature_level_2 = CompilerFeatureNode("level_2")
    feature_level_2.description = "feature level 2"
    feature_level_2.flags = create_str_list(False, ["L2_1", "L2_2"], ["L2_1", "L2_3"] )
    feature_level_2.features = create_feature_str_list(False, ["L2_F1", "L2_F2", "L2_F3"], ["L2_F1"] )
    feature_level_2.linkers = create_linker_override_node(None, None, None)

    feature_level_2 = feature_level_2.resolve_extends(feature_level_1, {}, FeatureRuleNodeList()).unwrap()

    assert feature_level_2.name == "level_2"
    assert feature_level_2.description == "feature level 2"
    assert feature_level_2.flags.override == False
    assert feature_level_2.flags.values == set(["L0_2", "L1_2", "L2_2"])
    assert feature_level_2.flags.remove_modifiers.values == set( ["L2_1", "L2_3"] )
    assert feature_level_2.features.override == False
    assert feature_level_2.features.values == set(["L0_F2", "L0_F3", "L1_F2", "L1_F3", "L2_F2", "L2_F3"])
    assert feature_level_2.features.remove_modifiers.values == set( ["L2_F1"])
    assert feature_level_2.linkers.common_linker.features.is_empty()
    assert feature_level_2.linkers.common_linker.flags.is_empty()
    assert len(feature_level_2.linkers.linker_overrides) == 0

def test_extends_no_rules_2():
    # feature level 0
    feature_level_0 = CompilerFeatureNode("level 0")
    feature_level_0.description = "feature level 0"
    feature_level_0.flags = create_str_list(False, ["L0_1", "L0_2"], ["L0_1", "L0_3"] )
    feature_level_0.features = create_feature_str_list(False, ["L0_F1", "L0_F2", "L0_F3"], ["L0_F1"] )
    feature_level_0.linkers = create_linker_override_node(None, None, None)

    feature_level_0 = feature_level_0.resolve_extends(CompilerFeatureNode("root"), {}, FeatureRuleNodeList()).unwrap()

    # feature level 1
    feature_level_1 = CompilerFeatureNode("level_1")
    feature_level_1.description = "feature level 1"
    feature_level_1.flags = create_str_list(True, ["L1_1", "L1_2"], ["L1_1", "L1_3"] )
    feature_level_1.features = create_feature_str_list(True, ["L1_F1", "L1_F2", "L1_F3"], ["L1_F1"] )
    feature_level_1.linkers = create_linker_override_node(None, None, None)

    feature_level_1 = feature_level_1.resolve_extends(feature_level_0, {}, FeatureRuleNodeList()).unwrap()

    assert feature_level_1.name == "level_1"
    assert feature_level_1.description == "feature level 1"
    assert feature_level_1.flags.override == True
    assert feature_level_1.flags.values == set(["L1_2"])
    assert feature_level_1.flags.remove_modifiers.values == set(["L1_1", "L1_3"] )
    assert feature_level_1.features.override == True
    assert feature_level_1.features.values == set(["L1_F2", "L1_F3"])
    assert feature_level_1.features.remove_modifiers.values == set(["L1_F1"])
    assert feature_level_1.linkers.common_linker.features.is_empty()
    assert feature_level_1.linkers.common_linker.flags.is_empty()
    assert len(feature_level_1.linkers.linker_overrides) == 0


    # feature level 2
    feature_level_2 = CompilerFeatureNode("level_2")
    feature_level_2.description = "feature level 2"
    feature_level_2.flags = create_str_list(False, ["L2_1", "L2_2"], ["L2_1", "L2_3"] )
    feature_level_2.features = create_feature_str_list(False, ["L2_F1", "L2_F2", "L2_F3"], ["L2_F1"] )
    feature_level_2.linkers = create_linker_override_node(None, None, None)

    feature_level_2 = feature_level_2.resolve_extends(feature_level_1, {}, FeatureRuleNodeList()).unwrap()

    assert feature_level_2.name == "level_2"
    assert feature_level_2.description == "feature level 2"
    assert feature_level_2.flags.override == False
    assert feature_level_2.flags.values == set(["L1_2", "L2_2"])
    assert feature_level_2.flags.remove_modifiers.values == set(["L2_1", "L2_3"])
    assert feature_level_2.features.override == False
    assert feature_level_2.features.values == set(["L1_F2", "L1_F3", "L2_F2", "L2_F3"])
    assert feature_level_2.features.remove_modifiers.values == set(["L2_F1"])
    assert feature_level_2.linkers.common_linker.features.is_empty()
    assert feature_level_2.linkers.common_linker.flags.is_empty()
    assert len(feature_level_2.linkers.linker_overrides) == 0


def test_extends_no_rules_3():
    # feature level 0
    feature_level_0 = CompilerFeatureNode("level 0")
    feature_level_0.description = "feature level 0"
    feature_level_0.flags = create_str_list(False, ["L0_1", "L0_2"], ["L0_1", "L0_3"] )
    feature_level_0.features = create_feature_str_list(False, ["L0_F1", "L0_F2", "L0_F3"], ["L0_F1"] )
    feature_level_0.linkers = create_linker_override_node(None, None, None)

    feature_level_0 = feature_level_0.resolve_extends(CompilerFeatureNode("root"), {},FeatureRuleNodeList()).unwrap()

    # feature level 1
    feature_level_1 = CompilerFeatureNode("level_1")
    feature_level_1.description = "feature level 1"
    feature_level_1.flags = create_str_list(False, ["L1_1", "L1_2"], ["L1_1", "L1_3"] )
    feature_level_1.features = create_feature_str_list(False, ["L1_F1", "L1_F2", "L1_F3"], ["L1_F1"] )
    feature_level_1.linkers = create_linker_override_node(None, None, None)

    feature_level_1 = feature_level_1.resolve_extends(feature_level_0,{}, FeatureRuleNodeList()).unwrap()

    assert feature_level_1.name == "level_1"
    assert feature_level_1.description == "feature level 1"
    assert feature_level_1.flags.override == False
    assert feature_level_1.flags.values == set(["L0_2", "L1_2"])
    assert feature_level_1.flags.remove_modifiers.values == set(["L1_1", "L1_3"])
    assert feature_level_1.features.override == False
    assert feature_level_1.features.values == set(["L0_F2", "L0_F3", "L1_F2", "L1_F3"])
    assert feature_level_1.features.remove_modifiers.values == set(["L1_F1"])
    assert feature_level_1.linkers.common_linker.features.is_empty()
    assert feature_level_1.linkers.common_linker.flags.is_empty()
    assert len(feature_level_1.linkers.linker_overrides) == 0

    # feature level 2
    feature_level_2 = CompilerFeatureNode("level_2")
    feature_level_2.description = "feature level 2"
    feature_level_2.flags = create_str_list(True, ["L2_1", "L2_2"], ["L2_1", "L2_3"] )
    feature_level_2.features = create_feature_str_list(True, ["L2_F1", "L2_F2", "L2_F3"], ["L2_F1"] )
    feature_level_2.linkers = create_linker_override_node(None, None, None)

    feature_level_2 = feature_level_2.resolve_extends(feature_level_1, {},FeatureRuleNodeList()).unwrap()

    assert feature_level_2.name == "level_2"
    assert feature_level_2.description == "feature level 2"
    assert feature_level_2.flags.override == True
    assert feature_level_2.flags.values == set(["L2_2"])
    assert feature_level_2.flags.remove_modifiers.values == set( ["L2_1", "L2_3"] )
    assert feature_level_2.features.override == True
    assert feature_level_2.features.values == set(["L2_F2", "L2_F3"])
    assert feature_level_2.features.remove_modifiers.values == set(["L2_F1"])
    assert feature_level_2.linkers.common_linker.features.is_empty()
    assert feature_level_2.linkers.common_linker.flags.is_empty()
    assert len(feature_level_2.linkers.linker_overrides) == 0

def test_extends_no_rules_4():
    # feature level 0
    feature_level_0 = CompilerFeatureNode("level 0")
    feature_level_0.description = "feature level 0"
    feature_level_0.flags = create_str_list(False, ["L0_1", "L0_2"], ["L0_1", "L0_3"] )
    feature_level_0.features = create_feature_str_list(False, ["L0_F1", "L0_F2", "L0_F3"], ["L0_F1"] )
    feature_level_0.linkers = create_linker_override_node(None, None, None)

    feature_level_0 = feature_level_0.resolve_extends(CompilerFeatureNode("root"),{}, FeatureRuleNodeList()).unwrap()

    # feature level 1
    feature_level_1 = CompilerFeatureNode("level_1")
    feature_level_1.description = "feature level 1"
    feature_level_1.flags = create_str_list(True, ["L1_1", "L1_2"], ["L1_1", "L1_3"] )
    feature_level_1.features = create_feature_str_list(True, ["L1_F1", "L1_F2", "L1_F3"], ["L1_F1"] )
    feature_level_1.linkers = create_linker_override_node(None, None, None)

    feature_level_1 = feature_level_1.resolve_extends(feature_level_0,{}, FeatureRuleNodeList()).unwrap()

    assert feature_level_1.name == "level_1"
    assert feature_level_1.description == "feature level 1"
    assert feature_level_1.flags.override == True
    assert feature_level_1.flags.values == set(["L1_2"])
    assert feature_level_1.flags.remove_modifiers.values == set( ["L1_1", "L1_3"])
    assert feature_level_1.features.override == True
    assert feature_level_1.features.values == set(["L1_F2", "L1_F3"])
    assert feature_level_1.features.remove_modifiers.values == set(["L1_F1"] )
    assert feature_level_1.linkers.common_linker.features.is_empty()
    assert feature_level_1.linkers.common_linker.flags.is_empty()
    assert len(feature_level_1.linkers.linker_overrides) == 0

    # feature level 2
    feature_level_2 = CompilerFeatureNode("level_2")
    feature_level_2.description = "feature level 2"
    feature_level_2.flags = create_str_list(True, ["L2_1", "L2_2"], ["L2_1", "L2_3"] )
    feature_level_2.features = create_feature_str_list(True, ["L2_F1", "L2_F2", "L2_F3"], ["L2_F1"] )
    feature_level_2.linkers = create_linker_override_node(None, None, None)

    feature_level_2 = feature_level_2.resolve_extends(feature_level_1,{}, FeatureRuleNodeList()).unwrap()

    assert feature_level_2.name == "level_2"
    assert feature_level_2.description == "feature level 2"
    assert feature_level_2.flags.override == True
    assert feature_level_2.flags.values == set(["L2_2"])
    assert feature_level_2.flags.remove_modifiers.values == set(["L2_1", "L2_3"])
    assert feature_level_2.features.override == True
    assert feature_level_2.features.values == set(["L2_F2", "L2_F3"])
    assert feature_level_2.features.remove_modifiers.values == set(["L2_F1"])
    assert feature_level_2.linkers.common_linker.features.is_empty()
    assert feature_level_2.linkers.common_linker.flags.is_empty()
    assert len(feature_level_2.linkers.linker_overrides) == 0

def test_extends_1():
    onlyone_rule = create_only_one_rule("one rule F3", "OnlyOne F3", ["L0_F3", "L1_F3", "L2_F3"])
    feature_rule_list = create_feature_rule_node_list([onlyone_rule])
       
    # feature level 0
    feature_level_0 = CompilerFeatureNode("level 0")
    feature_level_0.description = "feature level 0"
    feature_level_0.flags = create_str_list(False, ["L0_1", "L0_2"], ["L0_1", "L0_3"] )
    feature_level_0.features = create_feature_str_list(False, ["L0_F1", "L0_F2", "L0_F3"], ["L0_F1"] )
    feature_level_0.linkers = create_linker_override_node(None, None, None)

    feature_level_0 = feature_level_0.resolve_extends(CompilerFeatureNode("root"), {},feature_rule_list).unwrap()

    # feature level 1
    feature_level_1 = CompilerFeatureNode("level_1")
    feature_level_1.description = "feature level 1"
    feature_level_1.flags = create_str_list(False, ["L1_1", "L1_2"], ["L1_1", "L1_3"] )
    feature_level_1.features = create_feature_str_list(False, ["L1_F1", "L1_F2", "L1_F3"], ["L1_F1"] )
    feature_level_1.linkers = create_linker_override_node(None, None, None)

    feature_level_1 = feature_level_1.resolve_extends(feature_level_0,{}, feature_rule_list).unwrap()

    assert feature_level_1.name == "level_1"
    assert feature_level_1.description == "feature level 1"
    assert feature_level_1.flags.override == False
    assert feature_level_1.flags.values == set(["L0_2", "L1_2"])
    assert feature_level_1.flags.remove_modifiers.values == set(["L1_1", "L1_3"])
    assert feature_level_1.features.override == False
    assert feature_level_1.features.values == set(["L0_F2", "L1_F2", "L1_F3"])
    assert feature_level_1.features.remove_modifiers.values == set(["L1_F1"])
    assert feature_level_1.linkers.common_linker.features.is_empty()
    assert feature_level_1.linkers.common_linker.flags.is_empty()
    assert len(feature_level_1.linkers.linker_overrides) == 0

    # feature level 2
    feature_level_2 = CompilerFeatureNode("level_2")
    feature_level_2.description = "feature level 2"
    feature_level_2.flags = create_str_list(False, ["L2_1", "L2_2"], ["L2_1", "L2_3"] )
    feature_level_2.features = create_feature_str_list(False, ["L2_F1", "L2_F2", "L2_F3"], ["L2_F1"] )
    feature_level_2.linkers = create_linker_override_node(None, None, None)
    feature_level_2 = feature_level_2.resolve_extends(feature_level_1, {},feature_rule_list).unwrap()

    assert feature_level_2.name == "level_2"
    assert feature_level_2.description == "feature level 2"
    assert feature_level_2.flags.override == False
    assert feature_level_2.flags.values == set(["L0_2", "L1_2", "L2_2"])
    assert feature_level_2.flags.remove_modifiers.values == set(["L2_1", "L2_3"])
    assert feature_level_2.features.override == False
    assert feature_level_2.features.values == set(["L0_F2", "L1_F2", "L2_F2", "L2_F3"])
    assert feature_level_2.features.remove_modifiers.values == set(["L2_F1"])
    assert feature_level_2.linkers.common_linker.features.is_empty()
    assert feature_level_2.linkers.common_linker.flags.is_empty()
    assert len(feature_level_2.linkers.linker_overrides) == 0

def test_extends_2():
    onlyone_rule = create_only_one_rule("one rule F3", "OnlyOne F3", ["L0_F3", "L1_F3", "L2_F3"])
    feature_rule_list = create_feature_rule_node_list([onlyone_rule])
       
    # feature level 0
    feature_level_0 = CompilerFeatureNode("level 0")
    feature_level_0.description = "feature level 0"
    feature_level_0.flags = create_str_list(True, ["L0_1", "L0_2"], ["L0_1", "L0_3"] )
    feature_level_0.features = create_feature_str_list(True, ["L0_F1", "L0_F2", "L0_F3"], ["L0_F1"] )
    feature_level_0.linkers = create_linker_override_node(None, None, None)

    feature_level_0 = feature_level_0.resolve_extends(CompilerFeatureNode("root"), {},feature_rule_list).unwrap()

    # feature level 1
    feature_level_1 = CompilerFeatureNode("level_1")
    feature_level_1.description = "feature level 1"
    feature_level_1.flags = create_str_list(False, ["L1_1", "L1_2"], ["L1_1", "L1_3"] )
    feature_level_1.features = create_feature_str_list(False, ["L1_F1", "L1_F2", "L1_F3"], ["L1_F1"] )
    feature_level_1.linkers = create_linker_override_node(None, None, None)

    feature_level_1 = feature_level_1.resolve_extends(feature_level_0, {},feature_rule_list).unwrap()

    assert feature_level_1.name == "level_1"
    assert feature_level_1.description == "feature level 1"
    assert feature_level_1.flags.override == False
    assert feature_level_1.flags.values == set(["L0_2", "L1_2"])
    assert feature_level_1.flags.remove_modifiers.values == set(["L1_1", "L1_3"])
    assert feature_level_1.features.override == False
    assert feature_level_1.features.values == set(["L0_F2", "L1_F2", "L1_F3"])
    assert feature_level_1.features.remove_modifiers.values == set(["L1_F1"])
    assert feature_level_1.linkers.common_linker.features.is_empty()
    assert feature_level_1.linkers.common_linker.flags.is_empty()
    assert len(feature_level_1.linkers.linker_overrides) == 0
    
    # feature level 2
    feature_level_2 = CompilerFeatureNode("level_2")
    feature_level_2.description = "feature level 2"
    feature_level_2.flags = create_str_list(False, ["L2_1", "L2_2"], ["L2_1", "L2_3"] )
    feature_level_2.features = create_feature_str_list(False, ["L2_F1", "L2_F2", "L2_F3"], ["L2_F1"] )
    feature_level_2.linkers = create_linker_override_node(None, None, None)

    feature_level_2 = feature_level_2.resolve_extends(feature_level_1, {},feature_rule_list).unwrap()

    assert feature_level_2.name == "level_2"
    assert feature_level_2.description == "feature level 2"
    assert feature_level_2.flags.override == False
    assert feature_level_2.flags.values == set(["L0_2", "L1_2", "L2_2"])
    assert feature_level_2.flags.remove_modifiers.values == set(["L2_1", "L2_3"] )
    assert feature_level_2.features.override == False
    assert feature_level_2.features.values == set(["L0_F2", "L1_F2", "L2_F2", "L2_F3"])
    assert feature_level_2.features.remove_modifiers.values == set(["L2_F1"])
    assert feature_level_2.linkers.common_linker.features.is_empty()
    assert feature_level_2.linkers.common_linker.flags.is_empty()
    assert len(feature_level_2.linkers.linker_overrides) == 0

def test_extends_3():
    onlyone_rule = create_only_one_rule("one rule F3", "OnlyOne F3", ["L0_F3", "L1_F3", "L2_F3"])
    feature_rule_list = create_feature_rule_node_list([onlyone_rule])
       
    # feature level 0
    feature_level_0 = CompilerFeatureNode("level 0")
    feature_level_0.description = "feature level 0"
    feature_level_0.flags = create_str_list(False, ["L0_1", "L0_2"], ["L0_1", "L0_3"] )
    feature_level_0.features = create_feature_str_list(False, ["L0_F1", "L0_F2", "L0_F3"], ["L0_F1"] )
    feature_level_0.linkers = create_linker_override_node(None, None, None)

    feature_level_0 = feature_level_0.resolve_extends(CompilerFeatureNode("root"),{}, feature_rule_list).unwrap()

    # feature level 1
    feature_level_1 = CompilerFeatureNode("level_1")
    feature_level_1.description = "feature level 1"
    feature_level_1.flags = create_str_list(True, ["L1_1", "L1_2"], ["L1_1", "L1_3"] )
    feature_level_1.features = create_feature_str_list(True, ["L1_F1", "L1_F2", "L1_F3"], ["L1_F1"] )
    feature_level_1.linkers = create_linker_override_node(None, None, None)

    feature_level_1 = feature_level_1.resolve_extends(feature_level_0, {},feature_rule_list).unwrap()

    assert feature_level_1.name == "level_1"
    assert feature_level_1.description == "feature level 1"
    assert feature_level_1.flags.override == True
    assert feature_level_1.flags.values == set(["L1_2"])
    assert feature_level_1.flags.remove_modifiers.values == set(["L1_1", "L1_3"])
    assert feature_level_1.features.override == True
    assert feature_level_1.features.values == set(["L1_F2", "L1_F3"])
    assert feature_level_1.features.remove_modifiers.values == set(["L1_F1"])
    assert feature_level_1.linkers.common_linker.features.is_empty()
    assert feature_level_1.linkers.common_linker.flags.is_empty()
    assert len(feature_level_1.linkers.linker_overrides) == 0

    # feature level 2
    feature_level_2 = CompilerFeatureNode("level_2")
    feature_level_2.description = "feature level 2"
    feature_level_2.flags = create_str_list(False, ["L2_1", "L2_2"], ["L2_1", "L2_3"] )
    feature_level_2.features = create_feature_str_list(False, ["L2_F1", "L2_F2", "L2_F3"], ["L2_F1"] )
    feature_level_2.linkers = create_linker_override_node(None, None, None)

    feature_level_2 = feature_level_2.resolve_extends(feature_level_1, {},feature_rule_list).unwrap()

    assert feature_level_2.name == "level_2"
    assert feature_level_2.description == "feature level 2"
    assert feature_level_2.flags.override == False
    assert feature_level_2.flags.values == set(["L1_2", "L2_2"])
    assert feature_level_2.flags.remove_modifiers.values == set(["L2_1", "L2_3"])
    assert feature_level_2.features.override == False
    assert feature_level_2.features.values == set(["L1_F2", "L2_F2", "L2_F3"])
    assert feature_level_2.features.remove_modifiers.values == set(["L2_F1"])
    assert feature_level_2.linkers.common_linker.features.is_empty()
    assert feature_level_2.linkers.common_linker.flags.is_empty()
    assert len(feature_level_2.linkers.linker_overrides) == 0

def test_extends_4():
    onlyone_rule = create_only_one_rule("one rule F3", "OnlyOne F3", ["L0_F3", "L1_F3", "L2_F3"])
    feature_rule_list = create_feature_rule_node_list([onlyone_rule])
       
    # feature level 0
    feature_level_0 = CompilerFeatureNode("level 0")
    feature_level_0.description = "feature level 0"
    feature_level_0.flags = create_str_list(False, ["L0_1", "L0_2"], ["L0_1", "L0_3"] )
    feature_level_0.features = create_feature_str_list(False, ["L0_F1", "L0_F2", "L0_F3"], ["L0_F1"] )
    feature_level_0.linkers = create_linker_override_node(None, None, None)

    feature_level_0 = feature_level_0.resolve_extends(CompilerFeatureNode("root"), {},feature_rule_list).unwrap()

    # feature level 1
    feature_level_1 = CompilerFeatureNode("level_1")
    feature_level_1.description = "feature level 1"
    feature_level_1.flags = create_str_list(False, ["L1_1", "L1_2"], ["L1_1", "L1_3"] )
    feature_level_1.features = create_feature_str_list(False, ["L1_F1", "L1_F2", "L1_F3"], ["L1_F1"] )
    feature_level_1.linkers = create_linker_override_node(None, None, None)

    feature_level_1 = feature_level_1.resolve_extends(feature_level_0, {},feature_rule_list).unwrap()

    assert feature_level_1.name == "level_1"
    assert feature_level_1.description == "feature level 1"
    assert feature_level_1.flags.override == False
    assert feature_level_1.flags.values == set(["L0_2", "L1_2"])
    assert feature_level_1.flags.remove_modifiers.values == set(["L1_1", "L1_3"])
    assert feature_level_1.features.override == False
    assert feature_level_1.features.values == set(["L0_F2", "L1_F2", "L1_F3"])
    assert feature_level_1.features.remove_modifiers.values == set(["L1_F1"])
    assert feature_level_1.linkers.common_linker.features.is_empty()
    assert feature_level_1.linkers.common_linker.flags.is_empty()
    assert len(feature_level_1.linkers.linker_overrides) == 0

    # feature level 2
    feature_level_2 = CompilerFeatureNode("level_2")
    feature_level_2.description = "feature level 2"
    feature_level_2.flags = create_str_list(True, ["L2_1", "L2_2"], ["L2_1", "L2_3"] )
    feature_level_2.features = create_feature_str_list(True, ["L2_F1", "L2_F2", "L2_F3"], ["L2_F1"] )
    feature_level_2.linkers = create_linker_override_node(None, None, None)

    feature_level_2 = feature_level_2.resolve_extends(feature_level_1, {},feature_rule_list).unwrap()

    assert feature_level_2.name == "level_2"
    assert feature_level_2.description == "feature level 2"
    assert feature_level_2.flags.override == True
    assert feature_level_2.flags.values == set(["L2_2"])
    assert feature_level_2.flags.remove_modifiers.values == set(["L2_1", "L2_3"])
    assert feature_level_2.features.override == True
    assert feature_level_2.features.values == set(["L2_F2", "L2_F3"])
    assert feature_level_2.features.remove_modifiers.values == set(["L2_F1"])
    assert feature_level_2.linkers.common_linker.features.is_empty()
    assert feature_level_2.linkers.common_linker.flags.is_empty()
    assert len(feature_level_2.linkers.linker_overrides) == 0

def test_extends_5():
    onlyone_rule = create_only_one_rule("one rule F3", "OnlyOne F3", ["L0_F3", "L1_F3", "L2_F3"])
    feature_rule_list = create_feature_rule_node_list([onlyone_rule])
       
    # feature level 0
    feature_level_0 = CompilerFeatureNode("level 0")
    feature_level_0.description = "feature level 0"
    feature_level_0.flags = create_str_list(True, ["L0_1", "L0_2"], ["L0_1", "L0_3"] )
    feature_level_0.features = create_feature_str_list(True, ["L0_F1", "L0_F2", "L0_F3"], ["L0_F1"] )
    feature_level_0.linkers = create_linker_override_node(None, None, None)

    feature_level_0 = feature_level_0.resolve_extends(CompilerFeatureNode("root"), {},feature_rule_list).unwrap()

    # feature level 1
    feature_level_1 = CompilerFeatureNode("level_1")
    feature_level_1.description = "feature level 1"
    feature_level_1.flags = create_str_list(True, ["L1_1", "L1_2"], ["L1_1", "L1_3"] )
    feature_level_1.features = create_feature_str_list(True, ["L1_F1", "L1_F2", "L1_F3"], ["L1_F1"] )
    feature_level_1.linkers = create_linker_override_node(None, None, None)
    feature_level_1 = feature_level_1.resolve_extends(feature_level_0, {},feature_rule_list).unwrap()

    assert feature_level_1.name == "level_1"
    assert feature_level_1.description == "feature level 1"
    assert feature_level_1.flags.override == True
    assert feature_level_1.flags.values == set(["L1_2"])
    assert feature_level_1.flags.remove_modifiers.values == set(["L1_1", "L1_3"])
    assert feature_level_1.features.override == True
    assert feature_level_1.features.values == set(["L1_F2", "L1_F3"])
    assert feature_level_1.features.remove_modifiers.values == set(["L1_F1"])
    assert feature_level_1.linkers.common_linker.features.is_empty()
    assert feature_level_1.linkers.common_linker.flags.is_empty()
    assert len(feature_level_1.linkers.linker_overrides) == 0

    # feature level 2
    feature_level_2 = CompilerFeatureNode("level_2")
    feature_level_2.description = "feature level 2"
    feature_level_2.flags = create_str_list(False, ["L2_1", "L2_2"], ["L2_1", "L2_3"] )
    feature_level_2.features = create_feature_str_list(False, ["L2_F1", "L2_F2", "L2_F3"], ["L2_F1"] )
    feature_level_2.linkers = create_linker_override_node(None, None, None)
    feature_level_2 = feature_level_2.resolve_extends(feature_level_1, {},feature_rule_list).unwrap()

    assert feature_level_2.name == "level_2"
    assert feature_level_2.description == "feature level 2"
    assert feature_level_2.flags.override == False
    assert feature_level_2.flags.values == set(["L1_2", "L2_2"])
    assert feature_level_2.flags.remove_modifiers.values == set(["L2_1", "L2_3"])
    assert feature_level_2.features.override == False
    assert feature_level_2.features.values == set(["L1_F2", "L2_F2", "L2_F3"])
    assert feature_level_2.features.remove_modifiers.values == set( ["L2_F1"] )
    assert feature_level_2.linkers.common_linker.features.is_empty()
    assert feature_level_2.linkers.common_linker.flags.is_empty()
    assert len(feature_level_2.linkers.linker_overrides) == 0

def test_extends_6():
    onlyone_rule = create_only_one_rule("one rule F3", "OnlyOne F3", ["L0_F3", "L1_F3", "L2_F3"])
    feature_rule_list = create_feature_rule_node_list([onlyone_rule])
       
    # feature level 0
    feature_level_0 = CompilerFeatureNode("level 0")
    feature_level_0.description = "feature level 0"
    feature_level_0.flags = create_str_list(True, ["L0_1", "L0_2"], ["L0_1", "L0_3"] )
    feature_level_0.features = create_feature_str_list(True, ["L0_F1", "L0_F2", "L0_F3"], ["L0_F1"] )
    feature_level_0.linkers = create_linker_override_node(None, None, None)

    feature_level_0 = feature_level_0.resolve_extends(CompilerFeatureNode("root"), {},feature_rule_list).unwrap()

    # feature level 1
    feature_level_1 = CompilerFeatureNode("level_1")
    feature_level_1.description = "feature level 1"
    feature_level_1.flags = create_str_list(False, ["L1_1", "L1_2"], ["L1_1", "L1_3"] )
    feature_level_1.features = create_feature_str_list(False, ["L1_F1", "L1_F2", "L1_F3"], ["L1_F1"] )
    feature_level_1.linkers = create_linker_override_node(None, None, None)

    feature_level_1 = feature_level_1.resolve_extends(feature_level_0, {},feature_rule_list).unwrap()

    assert feature_level_1.name == "level_1"
    assert feature_level_1.description == "feature level 1"
    assert feature_level_1.flags.override == False
    assert feature_level_1.flags.values == set(["L0_2", "L1_2"])
    assert feature_level_1.flags.remove_modifiers.values == set(["L1_1", "L1_3"])
    assert feature_level_1.features.override == False
    assert feature_level_1.features.values == set(["L0_F2", "L1_F2", "L1_F3"])
    assert feature_level_1.features.remove_modifiers.values == set(["L1_F1"])
    assert feature_level_1.linkers.common_linker.features.is_empty()
    assert feature_level_1.linkers.common_linker.flags.is_empty()
    assert len(feature_level_1.linkers.linker_overrides) == 0

    # feature level 2
    feature_level_2 = CompilerFeatureNode("level_2")
    feature_level_2.description = "feature level 2"
    feature_level_2.flags = create_str_list(True, ["L2_1", "L2_2"], ["L2_1", "L2_3"] )
    feature_level_2.features = create_feature_str_list(True, ["L2_F1", "L2_F2", "L2_F3"], ["L2_F1"] )
    feature_level_2.linkers = create_linker_override_node(None, None, None)

    feature_level_2 = feature_level_2.resolve_extends(feature_level_1, {},feature_rule_list).unwrap()

    assert feature_level_2.name == "level_2"
    assert feature_level_2.description == "feature level 2"
    assert feature_level_2.flags.override == True
    assert feature_level_2.flags.values == set(["L2_2"])
    assert feature_level_2.flags.remove_modifiers.values == set(["L2_1", "L2_3"])
    assert feature_level_2.features.override == True
    assert feature_level_2.features.values == set(["L2_F2", "L2_F3"])
    assert feature_level_2.features.remove_modifiers.values == set(["L2_F1"])
    assert feature_level_2.linkers.common_linker.features.is_empty()
    assert feature_level_2.linkers.common_linker.flags.is_empty()
    assert len(feature_level_2.linkers.linker_overrides) == 0


def test_extends_7():
    onlyone_rule = create_only_one_rule("one rule F3", "OnlyOne F3", ["L0_F3", "L1_F3", "L2_F3"])
    feature_rule_list = create_feature_rule_node_list([onlyone_rule])
       
    # feature level 0
    feature_level_0 = CompilerFeatureNode("level 0")
    feature_level_0.description = "feature level 0"
    feature_level_0.flags = create_str_list(False, ["L0_1", "L0_2"], ["L0_1", "L0_3"] )
    feature_level_0.features = create_feature_str_list(False, ["L0_F1", "L0_F2", "L0_F3"], ["L0_F1"] )
    feature_level_0.linkers = create_linker_override_node(None, None, None)

    feature_level_0 = feature_level_0.resolve_extends(CompilerFeatureNode("root"), {},feature_rule_list).unwrap()

    # feature level 1
    feature_level_1 = CompilerFeatureNode("level_1")
    feature_level_1.description = "feature level 1"
    feature_level_1.flags = create_str_list(True, ["L1_1", "L1_2"], ["L1_1", "L1_3"] )
    feature_level_1.features = create_feature_str_list(True, ["L1_F1", "L1_F2", "L1_F3"], ["L1_F1"] )
    feature_level_1.linkers = create_linker_override_node(None, None, None)

    feature_level_1 = feature_level_1.resolve_extends(feature_level_0, {},feature_rule_list).unwrap()

    assert feature_level_1.name == "level_1"
    assert feature_level_1.description == "feature level 1"
    assert feature_level_1.flags.override == True
    assert feature_level_1.flags.values == set(["L1_2"])
    assert feature_level_1.flags.remove_modifiers.values == set(["L1_1", "L1_3"])
    assert feature_level_1.features.override == True
    assert feature_level_1.features.values == set(["L1_F2", "L1_F3"])
    assert feature_level_1.features.remove_modifiers.values == set(["L1_F1"])
    assert feature_level_1.linkers.common_linker.features.is_empty()
    assert feature_level_1.linkers.common_linker.flags.is_empty()
    assert len(feature_level_1.linkers.linker_overrides) == 0

    # feature level 2
    feature_level_2 = CompilerFeatureNode("level_2")
    feature_level_2.description = "feature level 2"
    feature_level_2.flags = create_str_list(True, ["L2_1", "L2_2"], ["L2_1", "L2_3"] )
    feature_level_2.features = create_feature_str_list(True, ["L2_F1", "L2_F2", "L2_F3"], ["L2_F1"] )
    feature_level_2.linkers = create_linker_override_node(None, None, None)

    feature_level_2 = feature_level_2.resolve_extends(feature_level_1, {},feature_rule_list).unwrap()

    assert feature_level_2.name == "level_2"
    assert feature_level_2.description == "feature level 2"
    assert feature_level_2.flags.override == True
    assert feature_level_2.flags.values == set(["L2_2"])
    assert feature_level_2.flags.remove_modifiers.values == set(["L2_1", "L2_3"] )
    assert feature_level_2.features.override == True
    assert feature_level_2.features.values == set(["L2_F2", "L2_F3"])
    assert feature_level_2.features.remove_modifiers.values == set(["L2_F1"])
    assert feature_level_2.linkers.common_linker.features.is_empty()
    assert feature_level_2.linkers.common_linker.flags.is_empty()
    assert len(feature_level_2.linkers.linker_overrides) == 0

def test_extends_8():
    onlyone_rule = create_only_one_rule("one rule F3", "OnlyOne F3", ["L0_F3", "L1_F3", "L2_F3"])
    feature_rule_list = create_feature_rule_node_list([onlyone_rule])
       
    # feature level 0
    feature_level_0 = CompilerFeatureNode("level 0")
    feature_level_0.description = "feature level 0"
    feature_level_0.flags = create_str_list(True, ["L0_1", "L0_2"], ["L0_1", "L0_3"] )
    feature_level_0.features = create_feature_str_list(True, ["L0_F1", "L0_F2", "L0_F3"], ["L0_F1"] )
    feature_level_0.linkers = create_linker_override_node(None, None, None)

    feature_level_0 = feature_level_0.resolve_extends(CompilerFeatureNode("root"),{}, feature_rule_list).unwrap()

    # feature level 1
    feature_level_1 = CompilerFeatureNode("level_1")
    feature_level_1.description = "feature level 1"
    feature_level_1.flags = create_str_list(True, ["L1_1", "L1_2"], ["L1_1", "L1_3"] )
    feature_level_1.features = create_feature_str_list(True, ["L1_F1", "L1_F2", "L1_F3"], ["L1_F1"] )
    feature_level_1.linkers = create_linker_override_node(None, None, None)

    feature_level_1 = feature_level_1.resolve_extends(feature_level_0,{}, feature_rule_list).unwrap()

    assert feature_level_1.name == "level_1"
    assert feature_level_1.description == "feature level 1"
    assert feature_level_1.flags.override == True
    assert feature_level_1.flags.values == set(["L1_2"])
    assert feature_level_1.flags.remove_modifiers.values == set(["L1_1", "L1_3"])
    assert feature_level_1.features.override == True
    assert feature_level_1.features.values == set(["L1_F2", "L1_F3"])
    assert feature_level_1.features.remove_modifiers.values == set(["L1_F1"])
    assert feature_level_1.linkers.common_linker.features.is_empty()
    assert feature_level_1.linkers.common_linker.flags.is_empty()
    assert len(feature_level_1.linkers.linker_overrides) == 0
    
    # feature level 2
    feature_level_2 = CompilerFeatureNode("level_2")
    feature_level_2.description = "feature level 2"
    feature_level_2.flags = create_str_list(True, ["L2_1", "L2_2"], ["L2_1", "L2_3"] )
    feature_level_2.features = create_feature_str_list(True, ["L2_F1", "L2_F2", "L2_F3"], ["L2_F1"] )
    feature_level_2.linkers = create_linker_override_node(None, None, None)

    feature_level_2 = feature_level_2.resolve_extends(feature_level_1, {},feature_rule_list).unwrap()

    assert feature_level_2.name == "level_2"
    assert feature_level_2.description == "feature level 2"
    assert feature_level_2.flags.override == True
    assert feature_level_2.flags.values == set(["L2_2"])
    assert feature_level_2.flags.remove_modifiers.values == set(["L2_1", "L2_3"])
    assert feature_level_2.features.override == True
    assert feature_level_2.features.values == set(["L2_F2", "L2_F3"])
    assert feature_level_2.features.remove_modifiers.values == set(["L2_F1"])
    assert feature_level_2.linkers.common_linker.features.is_empty()
    assert feature_level_2.linkers.common_linker.flags.is_empty()
    assert len(feature_level_2.linkers.linker_overrides) == 0

def test_extends_linker_override_1():
    onlyone_rule = create_only_one_rule("one rule F3", "OnlyOne F3", ["L0_F3", "L1_F3", "L2_F3"])
    feature_rule_list = create_feature_rule_node_list([onlyone_rule])
       
    # feature level 0
    feature_level_0 = CompilerFeatureNode("level 0")
    feature_level_0.description = "feature level 0"
    feature_level_0.linkers = create_linker_override_node_1()

    feature_level_0 = feature_level_0.resolve_extends(CompilerFeatureNode("root"), {},feature_rule_list).unwrap()

    # feature level 1
    feature_level_1 = CompilerFeatureNode("level_1")
    feature_level_1.description = "feature level 1"
    feature_level_1.linkers = create_linker_override_node_1()
    feature_level_1 = feature_level_1.resolve_extends(feature_level_0,{}, feature_rule_list).unwrap()

    assert feature_level_1.name == "level_1"
    assert feature_level_1.description == "feature level 1"
    assert feature_level_1.flags.override == False
    assert feature_level_1.flags.values == set()
    assert feature_level_1.flags.remove_modifiers.values == set()
    assert feature_level_1.features.override == False
    assert feature_level_1.features.values == set()
    assert feature_level_1.features.remove_modifiers.values == set()
    assert feature_level_1.linkers.common_linker.flags.override == False
    assert feature_level_1.linkers.common_linker.flags.values == set(["C2"])
    assert feature_level_1.linkers.common_linker.flags.remove_modifiers.values == set(["C1", "C3"])
    assert feature_level_1.linkers.common_linker.features.override == False
    assert feature_level_1.linkers.common_linker.features.values == set(["CF2"])
    assert feature_level_1.linkers.common_linker.features.remove_modifiers.values == set(["CF1", "CF3"])
    ld = feature_level_1.linkers.linker_overrides.get("ld")
    assert ld
    assert ld.flags.override == False
    assert ld.flags.values == set(["C2", "C3", "LD1"])
    assert ld.flags.remove_modifiers.values == set(["LD2"]) 
    assert ld.features.override == False
    assert ld.features.values == set(["CF2", "CF3", "LDF1"])
    assert ld.features.remove_modifiers.values == set(["LDF2"]) 

    # feature level 2
    feature_level_2 = CompilerFeatureNode("level_2")
    feature_level_2.description = "feature level 2"
    feature_level_2.linkers = create_linker_override_node_1()
    feature_level_2 = feature_level_2.resolve_extends(feature_level_1, {},feature_rule_list).unwrap()

    assert feature_level_2.name == "level_2"
    assert feature_level_2.description == "feature level 2"
    assert feature_level_2.flags.override == False
    assert feature_level_2.flags.values == set()
    assert feature_level_2.flags.remove_modifiers.values == set()
    assert feature_level_2.features.override == False
    assert feature_level_2.features.values == set()
    assert feature_level_2.features.remove_modifiers.values == set()
    assert feature_level_2.linkers.common_linker.flags.override == False
    assert feature_level_2.linkers.common_linker.flags.values == set(["C2"])
    assert feature_level_2.linkers.common_linker.flags.remove_modifiers.values == set(["C1", "C3"])
    assert feature_level_2.linkers.common_linker.features.override == False
    assert feature_level_2.linkers.common_linker.features.values == set(["CF2"])
    assert feature_level_2.linkers.common_linker.features.remove_modifiers.values == set(["CF1", "CF3"])
    ld = feature_level_2.linkers.linker_overrides.get("ld")
    assert ld
    assert ld.flags.override == False
    assert ld.flags.values == set(["C2", "C3", "LD1"])
    assert ld.flags.remove_modifiers.values == set(["LD2"]) 
    assert ld.features.override == False
    assert ld.features.values == set(["CF2", "CF3", "LDF1"])
    assert ld.features.remove_modifiers.values == set(["LDF2"]) 

def test_extends_compiler_feature_node() :
    
    test_extends_parent_empty_1()
    test_extends_parent_empty_2()

    test_extends_parent_empty_linker_override_1()
    test_extends_parent_empty_linker_override_2()

    test_extends_no_rules_1()
    test_extends_no_rules_2()
    test_extends_no_rules_3()
    test_extends_no_rules_4()

    test_extends_1()
    test_extends_2()
    test_extends_3()
    test_extends_4()
    test_extends_5()
    test_extends_6()
    test_extends_7()
    test_extends_8()

    test_extends_linker_override_1()