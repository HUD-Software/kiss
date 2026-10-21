#   feature-rules:
#       # Only one target mode
#       - only-one: target
#         description: Only one target mode is applicable
#         features: [TARGET_X64, TARGET_X86]

#       # ASAN is incompatible with LTO
#       - incompatible: asan
#         description: ASAN is incompatible with LTO
#         feature: ASAN
#         with: [LTO]

from toolchain.nodes.feature_node import FeatureRuleNodeIncompatible, FeatureRuleNodeList, FeatureRuleNodeOnlyOne
from toolchain.nodes.property import StrList

def create_str_list(override : bool, values : list[str], removes: list[str]):
    list = StrList()
    list.override = override
    for value in values:
        list.add_value(value)
    for remove in removes:
        list.add_modifier_remove(remove)
    return list

def test_extends_empty():
    result = FeatureRuleNodeList().resolve_extends(FeatureRuleNodeList())
    assert result.is_empty()

def test_only_one_extends_empty():
    feature_rule_list = FeatureRuleNodeList()
    onlyone_features = create_str_list(False,["A1", "A2"], ["A1", "A3"] )
    onlyone_rule = FeatureRuleNodeOnlyOne("A", "desc a", onlyone_features)    
    feature_rule_list.add_feature_rule(onlyone_rule)
    result = feature_rule_list.resolve_extends(FeatureRuleNodeList())

    # Validate result
    assert not result.is_empty()
    assert len(result.feature_rules_only_one) == 1
    assert len(result.feature_rules_incompatible) == 0
    result_rule = next((o for o in result.feature_rules_only_one if o.name == "A"), None)
    assert result_rule.name == onlyone_rule.name
    assert result_rule.description == onlyone_rule.description
    assert result_rule.feature_names.values == set(["A2"])
    assert result_rule.feature_names.override == False
    assert result_rule.feature_names.remove_modifiers.values == set()
    assert result_rule.feature_names.remove_modifiers.operation == onlyone_rule.feature_names.remove_modifiers.operation

def test_only_one_extends_empty_override():
    feature_rule_list = FeatureRuleNodeList()
    onlyone_features = create_str_list(True,["A1", "A2"], ["A1", "A3"] )
    onlyone_rule = FeatureRuleNodeOnlyOne("A", "desc a", onlyone_features)    
    feature_rule_list.add_feature_rule(onlyone_rule)
    result = feature_rule_list.resolve_extends(FeatureRuleNodeList())

    # Validate result
    assert not result.is_empty()
    assert len(result.feature_rules_only_one) == 1
    assert len(result.feature_rules_incompatible) == 0
    result_rule = next((o for o in result.feature_rules_only_one if o.name == "A"), None)
    assert result_rule.name == onlyone_rule.name
    assert result_rule.description == onlyone_rule.description
    assert result_rule.feature_names.values == set(["A2"])
    assert result_rule.feature_names.override == True
    assert result_rule.feature_names.remove_modifiers.values == set()
    assert result_rule.feature_names.remove_modifiers.operation == onlyone_rule.feature_names.remove_modifiers.operation

def test_incompatible_extends_empty():
    feature_rule_list = FeatureRuleNodeList()
    incompatible_features = create_str_list(False,["A1", "A2"], ["A1", "A3"] )
    incompatible_rule = FeatureRuleNodeIncompatible("A", "desc a", "A0", incompatible_features)    
    feature_rule_list.add_feature_rule(incompatible_rule)
    result = feature_rule_list.resolve_extends(FeatureRuleNodeList())
    
    # Validate result
    assert not result.is_empty()
    assert len(result.feature_rules_only_one) == 0
    assert len(result.feature_rules_incompatible) == 1
    result_rule = next((o for o in result.feature_rules_incompatible if o.name == "A"), None)
    assert result_rule.name == incompatible_rule.name
    assert result_rule.description == incompatible_rule.description
    assert result_rule.feature == "A0"
    assert result_rule.incompatible_with.override == False
    assert result_rule.incompatible_with.values == set(["A2"])
    assert result_rule.incompatible_with.remove_modifiers.values == set()
    assert result_rule.incompatible_with.remove_modifiers.operation == incompatible_rule.incompatible_with.remove_modifiers.operation

def test_incompatible_extends_empty_override():
    feature_rule_list = FeatureRuleNodeList()
    incompatible_features = create_str_list(True,["A1", "A2"], ["A1", "A3"] )
    incompatible_rule = FeatureRuleNodeIncompatible("A", "desc a", "A0", incompatible_features)    
    feature_rule_list.add_feature_rule(incompatible_rule)
    result = feature_rule_list.resolve_extends(FeatureRuleNodeList())
    
    # Validate result
    assert not result.is_empty()
    assert len(result.feature_rules_only_one) == 0
    assert len(result.feature_rules_incompatible) == 1
    result_rule = next((o for o in result.feature_rules_incompatible if o.name == "A"), None)
    assert result_rule.name == incompatible_rule.name
    assert result_rule.description == incompatible_rule.description
    assert result_rule.feature == "A0"
    assert result_rule.incompatible_with.override == True
    assert result_rule.incompatible_with.values == set(["A2"])
    assert result_rule.incompatible_with.remove_modifiers.values == set()
    assert result_rule.incompatible_with.remove_modifiers.operation == incompatible_rule.incompatible_with.remove_modifiers.operation

def test_empty_extends_only_one_extends():
    feature_rule_list = FeatureRuleNodeList()
    onlyone_features = create_str_list(False,["A1", "A2"], ["A1", "A3"] )
    onlyone_rule = FeatureRuleNodeOnlyOne("A", "desc a", onlyone_features)    
    feature_rule_list.add_feature_rule(onlyone_rule)
    feature_rule_list = feature_rule_list.resolve_extends(FeatureRuleNodeList())
    
    result = FeatureRuleNodeList().resolve_extends(feature_rule_list)

    # Validate result
    assert not result.is_empty()
    assert len(result.feature_rules_only_one) == 1
    assert len(result.feature_rules_incompatible) == 0
    result_rule = next((o for o in result.feature_rules_only_one if o.name == "A"), None)
    assert result_rule.name == onlyone_rule.name
    assert result_rule.description == onlyone_rule.description
    assert result_rule.feature_names.values == set(["A2"])
    assert result_rule.feature_names.override == False
    assert result_rule.feature_names.remove_modifiers.values == set()
    assert result_rule.feature_names.remove_modifiers.operation == onlyone_rule.feature_names.remove_modifiers.operation

def test_empty_extends_only_one_extends_override():
    feature_rule_list = FeatureRuleNodeList()
    onlyone_features = create_str_list(True,["A1", "A2"], ["A1", "A3"] )
    onlyone_rule = FeatureRuleNodeOnlyOne("A", "desc a", onlyone_features)    
    feature_rule_list.add_feature_rule(onlyone_rule)
    feature_rule_list = feature_rule_list.resolve_extends(FeatureRuleNodeList())
    
    result = FeatureRuleNodeList().resolve_extends(feature_rule_list)

    # Validate result
    assert not result.is_empty()
    assert len(result.feature_rules_only_one) == 1
    assert len(result.feature_rules_incompatible) == 0
    result_rule = next((o for o in result.feature_rules_only_one if o.name == "A"), None)
    assert result_rule.name == onlyone_rule.name
    assert result_rule.description == onlyone_rule.description
    assert result_rule.feature_names.values == set(["A2"])
    assert result_rule.feature_names.override == True
    assert result_rule.feature_names.remove_modifiers.values == set()
    assert result_rule.feature_names.remove_modifiers.operation == onlyone_rule.feature_names.remove_modifiers.operation

def test_empty_extends_incompatible():
    feature_rule_list = FeatureRuleNodeList()
    incompatible_features = create_str_list(False,["A1", "A2"], ["A1", "A3"] )
    incompatible_rule = FeatureRuleNodeIncompatible("A", "desc a", "A0", incompatible_features)    
    feature_rule_list.add_feature_rule(incompatible_rule)
    feature_rule_list = feature_rule_list.resolve_extends(FeatureRuleNodeList())

    result = FeatureRuleNodeList().resolve_extends(feature_rule_list)

    # Validate result
    assert not result.is_empty()
    assert len(result.feature_rules_only_one) == 0
    assert len(result.feature_rules_incompatible) == 1
    result_rule = next((o for o in result.feature_rules_incompatible if o.name == "A"), None)
    assert result_rule.name == incompatible_rule.name
    assert result_rule.description == incompatible_rule.description
    assert result_rule.feature == "A0"
    assert result_rule.incompatible_with.override == False
    assert result_rule.incompatible_with.values == set(["A2"])
    assert result_rule.incompatible_with.remove_modifiers.values == set()
    assert result_rule.incompatible_with.remove_modifiers.operation == incompatible_rule.incompatible_with.remove_modifiers.operation

def test_empty_extends_incompatible_override():
    feature_rule_list = FeatureRuleNodeList()
    incompatible_features = create_str_list(True,["A1", "A2"], ["A1", "A3"] )
    incompatible_rule = FeatureRuleNodeIncompatible("A", "desc a", "A0", incompatible_features)    
    feature_rule_list.add_feature_rule(incompatible_rule)
    feature_rule_list = feature_rule_list.resolve_extends(FeatureRuleNodeList())
    
    result = FeatureRuleNodeList().resolve_extends(feature_rule_list)

    # Validate result
    assert not result.is_empty()
    assert len(result.feature_rules_only_one) == 0
    assert len(result.feature_rules_incompatible) == 1
    result_rule = next((o for o in result.feature_rules_incompatible if o.name == "A"), None)
    assert result_rule.name == incompatible_rule.name
    assert result_rule.description == incompatible_rule.description
    assert result_rule.feature == "A0"
    assert result_rule.incompatible_with.override == True
    assert result_rule.incompatible_with.values == set(["A2"])
    assert result_rule.incompatible_with.remove_modifiers.values == set()
    assert result_rule.incompatible_with.remove_modifiers.operation == incompatible_rule.incompatible_with.remove_modifiers.operation
    
def test_only_one_extends_diff_only_one_1():
    # base
    base_feature_rule_list = FeatureRuleNodeList()
    base_onlyone_features = create_str_list(False,["A1", "A2"], ["A1", "A3"] )
    base_onlyone_rule = FeatureRuleNodeOnlyOne("A", "desc a", base_onlyone_features)    
    base_feature_rule_list.add_feature_rule(base_onlyone_rule)
    base_feature_rule_list = base_feature_rule_list.resolve_extends(FeatureRuleNodeList())

    # child
    child_feature_rule_list = FeatureRuleNodeList()
    child_onlyone_features = create_str_list(False,["B1", "B2"], ["B1", "B3"] )
    child_onlyone_rule = FeatureRuleNodeOnlyOne("B", "desc b", child_onlyone_features)    
    child_feature_rule_list.add_feature_rule(child_onlyone_rule)
    result = child_feature_rule_list.resolve_extends(base_feature_rule_list)

    # Validate result
    assert not result.is_empty()
    assert len(result.feature_rules_only_one) == 2
    assert len(result.feature_rules_incompatible) == 0
    result_rule = next((o for o in result.feature_rules_only_one if o.name == "A"), None)
    assert result_rule.name == base_onlyone_rule.name
    assert result_rule.description == base_onlyone_rule.description
    assert result_rule.feature_names.values == set(["A2"])
    assert result_rule.feature_names.override == False
    assert result_rule.feature_names.remove_modifiers.values == set()
    assert result_rule.feature_names.remove_modifiers.operation == base_onlyone_rule.feature_names.remove_modifiers.operation

    result_rule = next((o for o in result.feature_rules_only_one if o.name == "B"), None)
    assert result_rule.name == child_onlyone_rule.name
    assert result_rule.description == child_onlyone_rule.description
    assert result_rule.feature_names.values == set(["B2"])
    assert result_rule.feature_names.override == False
    assert result_rule.feature_names.remove_modifiers.values == set()
    assert result_rule.feature_names.remove_modifiers.operation == child_onlyone_rule.feature_names.remove_modifiers.operation

def test_only_one_extends_diff_only_one_2():
    # base
    base_feature_rule_list = FeatureRuleNodeList()
    base_onlyone_features = create_str_list(True,["A1", "A2"], ["A1", "A3"] )
    base_onlyone_rule = FeatureRuleNodeOnlyOne("A", "desc a", base_onlyone_features)    
    base_feature_rule_list.add_feature_rule(base_onlyone_rule)
    base_feature_rule_list = base_feature_rule_list.resolve_extends(FeatureRuleNodeList())

    # child
    child_feature_rule_list = FeatureRuleNodeList()
    child_onlyone_features = create_str_list(False,["B1", "B2"], ["B1", "B3"] )
    child_onlyone_rule = FeatureRuleNodeOnlyOne("B", "desc b", child_onlyone_features)    
    child_feature_rule_list.add_feature_rule(child_onlyone_rule)
    result = child_feature_rule_list.resolve_extends(base_feature_rule_list)

    # Validate result
    assert not result.is_empty()
    assert len(result.feature_rules_only_one) == 2
    assert len(result.feature_rules_incompatible) == 0
    result_rule = next((o for o in result.feature_rules_only_one if o.name == "A"), None)
    assert result_rule.name == base_onlyone_rule.name
    assert result_rule.description == base_onlyone_rule.description
    assert result_rule.feature_names.values == set(["A2"])
    assert result_rule.feature_names.override == True
    assert result_rule.feature_names.remove_modifiers.values == set()
    assert result_rule.feature_names.remove_modifiers.operation == base_onlyone_rule.feature_names.remove_modifiers.operation

    result_rule = next((o for o in result.feature_rules_only_one if o.name == "B"), None)
    assert result_rule.name == child_onlyone_rule.name
    assert result_rule.description == child_onlyone_rule.description
    assert result_rule.feature_names.values == set(["B2"])
    assert result_rule.feature_names.override == False
    assert result_rule.feature_names.remove_modifiers.values == set()
    assert result_rule.feature_names.remove_modifiers.operation == child_onlyone_rule.feature_names.remove_modifiers.operation

def test_only_one_extends_diff_only_one_3():
    # base
    base_feature_rule_list = FeatureRuleNodeList()
    base_onlyone_features = create_str_list(False,["A1", "A2"], ["A1", "A3"] )
    base_onlyone_rule = FeatureRuleNodeOnlyOne("A", "desc a", base_onlyone_features)    
    base_feature_rule_list.add_feature_rule(base_onlyone_rule)
    base_feature_rule_list = base_feature_rule_list.resolve_extends(FeatureRuleNodeList())

    # child
    child_feature_rule_list = FeatureRuleNodeList()
    child_onlyone_features = create_str_list(True,["B1", "B2"], ["B1", "B3"] )
    child_onlyone_rule = FeatureRuleNodeOnlyOne("B", "desc b", child_onlyone_features)    
    child_feature_rule_list.add_feature_rule(child_onlyone_rule)
    result = child_feature_rule_list.resolve_extends(base_feature_rule_list)

    # Validate result
    assert not result.is_empty()
    assert len(result.feature_rules_only_one) == 2
    assert len(result.feature_rules_incompatible) == 0
    result_rule = next((o for o in result.feature_rules_only_one if o.name == "A"), None)
    assert result_rule.name == base_onlyone_rule.name
    assert result_rule.description == base_onlyone_rule.description
    assert result_rule.feature_names.values == set(["A2"])
    assert result_rule.feature_names.override == False
    assert result_rule.feature_names.remove_modifiers.values == set()
    assert result_rule.feature_names.remove_modifiers.operation == base_onlyone_rule.feature_names.remove_modifiers.operation

    result_rule = next((o for o in result.feature_rules_only_one if o.name == "B"), None)
    assert result_rule.name == child_onlyone_rule.name
    assert result_rule.description == child_onlyone_rule.description
    assert result_rule.feature_names.values == set(["B2"])
    assert result_rule.feature_names.override == True
    assert result_rule.feature_names.remove_modifiers.values == set()
    assert result_rule.feature_names.remove_modifiers.operation == child_onlyone_rule.feature_names.remove_modifiers.operation

def test_only_one_extends_diff_only_one_4():
    # base
    base_feature_rule_list = FeatureRuleNodeList()
    base_onlyone_features = create_str_list(True,["A1", "A2"], ["A1", "A3"] )
    base_onlyone_rule = FeatureRuleNodeOnlyOne("A", "desc a", base_onlyone_features)    
    base_feature_rule_list.add_feature_rule(base_onlyone_rule)
    base_feature_rule_list = base_feature_rule_list.resolve_extends(FeatureRuleNodeList())

    # child
    child_feature_rule_list = FeatureRuleNodeList()
    child_onlyone_features = create_str_list(True,["B1", "B2"], ["B1", "B3"] )
    child_onlyone_rule = FeatureRuleNodeOnlyOne("B", "desc b", child_onlyone_features)    
    child_feature_rule_list.add_feature_rule(child_onlyone_rule)
    result = child_feature_rule_list.resolve_extends(base_feature_rule_list)

    # Validate result
    assert not result.is_empty()
    assert len(result.feature_rules_only_one) == 2
    assert len(result.feature_rules_incompatible) == 0
    result_rule = next((o for o in result.feature_rules_only_one if o.name == "A"), None)
    assert result_rule.name == base_onlyone_rule.name
    assert result_rule.description == base_onlyone_rule.description
    assert result_rule.feature_names.values == set(["A2"])
    assert result_rule.feature_names.override == True
    assert result_rule.feature_names.remove_modifiers.values == set()
    assert result_rule.feature_names.remove_modifiers.operation == base_onlyone_rule.feature_names.remove_modifiers.operation

    result_rule = next((o for o in result.feature_rules_only_one if o.name == "B"), None)
    assert result_rule.name == child_onlyone_rule.name
    assert result_rule.description == child_onlyone_rule.description
    assert result_rule.feature_names.values == set(["B2"])
    assert result_rule.feature_names.override == True
    assert result_rule.feature_names.remove_modifiers.values == set()
    assert result_rule.feature_names.remove_modifiers.operation == child_onlyone_rule.feature_names.remove_modifiers.operation

def test_incompatible_extends_diff_incompatible_1():
    # base
    base_feature_rule_list = FeatureRuleNodeList()
    base_incompatible_features = create_str_list(False,["A1", "A2"], ["A1", "A3"] )
    base_incompatible_rule = FeatureRuleNodeIncompatible("A", "desc a", "A0", base_incompatible_features)    
    base_feature_rule_list.add_feature_rule(base_incompatible_rule)
    base_feature_rule_list = base_feature_rule_list.resolve_extends(FeatureRuleNodeList())

    # child
    child_feature_rule_list = FeatureRuleNodeList()
    child_incompatible_features = create_str_list(False,["B1", "B2"], ["B1", "B3"] )
    child_incompatible_rule = FeatureRuleNodeIncompatible("B", "desc b", "B0", child_incompatible_features)    
    child_feature_rule_list.add_feature_rule(child_incompatible_rule)
    result = child_feature_rule_list.resolve_extends(base_feature_rule_list)

    # Validate result
    assert not result.is_empty()
    assert len(result.feature_rules_only_one) == 0
    assert len(result.feature_rules_incompatible) == 2
    result_rule = next((o for o in result.feature_rules_incompatible if o.name == "A"), None)
    assert result_rule.name == base_incompatible_rule.name
    assert result_rule.description == base_incompatible_rule.description
    assert result_rule.feature == "A0"
    assert result_rule.incompatible_with.override == False
    assert result_rule.incompatible_with.values == set(["A2"])
    assert result_rule.incompatible_with.remove_modifiers.values == set()
    assert result_rule.incompatible_with.remove_modifiers.operation == base_incompatible_rule.incompatible_with.remove_modifiers.operation

    result_rule = next((o for o in result.feature_rules_incompatible if o.name == "B"), None)
    assert result_rule.name == child_incompatible_rule.name
    assert result_rule.description == child_incompatible_rule.description
    assert result_rule.feature == "B0"
    assert result_rule.incompatible_with.override == False
    assert result_rule.incompatible_with.values == set(["B2"])
    assert result_rule.incompatible_with.remove_modifiers.values == set()
    assert result_rule.incompatible_with.remove_modifiers.operation == base_incompatible_rule.incompatible_with.remove_modifiers.operation

def test_incompatible_extends_diff_incompatible_2():
    # base
    base_feature_rule_list = FeatureRuleNodeList()
    base_incompatible_features = create_str_list(True,["A1", "A2"], ["A1", "A3"] )
    base_incompatible_rule = FeatureRuleNodeIncompatible("A", "desc a", "A0", base_incompatible_features)    
    base_feature_rule_list.add_feature_rule(base_incompatible_rule)
    base_feature_rule_list = base_feature_rule_list.resolve_extends(FeatureRuleNodeList())

    # child
    child_feature_rule_list = FeatureRuleNodeList()
    child_incompatible_features = create_str_list(False,["B1", "B2"], ["B1", "B3"] )
    child_incompatible_rule = FeatureRuleNodeIncompatible("B", "desc b", "B0", child_incompatible_features)    
    child_feature_rule_list.add_feature_rule(child_incompatible_rule)
    result = child_feature_rule_list.resolve_extends(base_feature_rule_list)

    # Validate result
    assert not result.is_empty()
    assert len(result.feature_rules_only_one) == 0
    assert len(result.feature_rules_incompatible) == 2
    result_rule = next((o for o in result.feature_rules_incompatible if o.name == "A"), None)
    assert result_rule.name == base_incompatible_rule.name
    assert result_rule.description == base_incompatible_rule.description
    assert result_rule.feature == "A0"
    assert result_rule.incompatible_with.override == True
    assert result_rule.incompatible_with.values == set(["A2"])
    assert result_rule.incompatible_with.remove_modifiers.values == set()
    assert result_rule.incompatible_with.remove_modifiers.operation == base_incompatible_rule.incompatible_with.remove_modifiers.operation

    result_rule = next((o for o in result.feature_rules_incompatible if o.name == "B"), None)
    assert result_rule.name == child_incompatible_rule.name
    assert result_rule.description == child_incompatible_rule.description
    assert result_rule.feature == "B0"
    assert result_rule.incompatible_with.override == False
    assert result_rule.incompatible_with.values == set(["B2"])
    assert result_rule.incompatible_with.remove_modifiers.values == set()
    assert result_rule.incompatible_with.remove_modifiers.operation == base_incompatible_rule.incompatible_with.remove_modifiers.operation
    
def test_incompatible_extends_diff_incompatible_3():
    # base
    base_feature_rule_list = FeatureRuleNodeList()
    base_incompatible_features = create_str_list(False,["A1", "A2"], ["A1", "A3"] )
    base_incompatible_rule = FeatureRuleNodeIncompatible("A", "desc a", "A0", base_incompatible_features)    
    base_feature_rule_list.add_feature_rule(base_incompatible_rule)
    base_feature_rule_list = base_feature_rule_list.resolve_extends(FeatureRuleNodeList())

    # child
    child_feature_rule_list = FeatureRuleNodeList()
    child_incompatible_features = create_str_list(True,["B1", "B2"], ["B1", "B3"] )
    child_incompatible_rule = FeatureRuleNodeIncompatible("B", "desc b", "B0", child_incompatible_features)    
    child_feature_rule_list.add_feature_rule(child_incompatible_rule)
    result = child_feature_rule_list.resolve_extends(base_feature_rule_list)

    # Validate result
    assert not result.is_empty()
    assert len(result.feature_rules_only_one) == 0
    assert len(result.feature_rules_incompatible) == 2
    result_rule = next((o for o in result.feature_rules_incompatible if o.name == "A"), None)
    assert result_rule.name == base_incompatible_rule.name
    assert result_rule.description == base_incompatible_rule.description
    assert result_rule.feature == "A0"
    assert result_rule.incompatible_with.override == False
    assert result_rule.incompatible_with.values == set(["A2"])
    assert result_rule.incompatible_with.remove_modifiers.values == set()
    assert result_rule.incompatible_with.remove_modifiers.operation == base_incompatible_rule.incompatible_with.remove_modifiers.operation

    result_rule = next((o for o in result.feature_rules_incompatible if o.name == "B"), None)
    assert result_rule.name == child_incompatible_rule.name
    assert result_rule.description == child_incompatible_rule.description
    assert result_rule.feature == "B0"
    assert result_rule.incompatible_with.override == True
    assert result_rule.incompatible_with.values == set(["B2"])
    assert result_rule.incompatible_with.remove_modifiers.values == set()
    assert result_rule.incompatible_with.remove_modifiers.operation == base_incompatible_rule.incompatible_with.remove_modifiers.operation
    
def test_incompatible_extends_diff_incompatible_4():
    # base
    base_feature_rule_list = FeatureRuleNodeList()
    base_incompatible_features = create_str_list(True,["A1", "A2"], ["A1", "A3"] )
    base_incompatible_rule = FeatureRuleNodeIncompatible("A", "desc a", "A0", base_incompatible_features)    
    base_feature_rule_list.add_feature_rule(base_incompatible_rule)
    base_feature_rule_list = base_feature_rule_list.resolve_extends(FeatureRuleNodeList())

    # child
    child_feature_rule_list = FeatureRuleNodeList()
    child_incompatible_features = create_str_list(True,["B1", "B2"], ["B1", "B3"] )
    child_incompatible_rule = FeatureRuleNodeIncompatible("B", "desc b", "B0", child_incompatible_features)    
    child_feature_rule_list.add_feature_rule(child_incompatible_rule)
    result = child_feature_rule_list.resolve_extends(base_feature_rule_list)

    # Validate result
    assert not result.is_empty()
    assert len(result.feature_rules_only_one) == 0
    assert len(result.feature_rules_incompatible) == 2
    result_rule = next((o for o in result.feature_rules_incompatible if o.name == "A"), None)
    assert result_rule.name == base_incompatible_rule.name
    assert result_rule.description == base_incompatible_rule.description
    assert result_rule.feature == "A0"
    assert result_rule.incompatible_with.override == True
    assert result_rule.incompatible_with.values == set(["A2"])
    assert result_rule.incompatible_with.remove_modifiers.values == set()
    assert result_rule.incompatible_with.remove_modifiers.operation == base_incompatible_rule.incompatible_with.remove_modifiers.operation

    result_rule = next((o for o in result.feature_rules_incompatible if o.name == "B"), None)
    assert result_rule.name == child_incompatible_rule.name
    assert result_rule.description == child_incompatible_rule.description
    assert result_rule.feature == "B0"
    assert result_rule.incompatible_with.override == True
    assert result_rule.incompatible_with.values == set(["B2"])
    assert result_rule.incompatible_with.remove_modifiers.values == set()
    assert result_rule.incompatible_with.remove_modifiers.operation == base_incompatible_rule.incompatible_with.remove_modifiers.operation
    


def test_only_one_extends_same_only_one_1():
    # base
    base_feature_rule_list = FeatureRuleNodeList()
    base_onlyone_features = create_str_list(False,["A1", "A2"], ["A1", "A3"] )
    base_onlyone_rule = FeatureRuleNodeOnlyOne("A", "desc a", base_onlyone_features)    
    base_feature_rule_list.add_feature_rule(base_onlyone_rule)
    base_feature_rule_list = base_feature_rule_list.resolve_extends(FeatureRuleNodeList())

    # child
    child_feature_rule_list = FeatureRuleNodeList()
    child_onlyone_features = create_str_list(False,["A1", "A4", "A3", "A5"], ["A5"] )
    child_onlyone_rule = FeatureRuleNodeOnlyOne("A", "", child_onlyone_features)    
    child_feature_rule_list.add_feature_rule(child_onlyone_rule)
    result = child_feature_rule_list.resolve_extends(base_feature_rule_list)

    # Validate result
    assert not result.is_empty()
    assert len(result.feature_rules_only_one) == 1
    assert len(result.feature_rules_incompatible) == 0
    result_rule = next((o for o in result.feature_rules_only_one if o.name == "A"), None)
    assert result_rule.name == base_onlyone_rule.name
    assert result_rule.description == base_onlyone_rule.description
    assert result_rule.feature_names.values == set(["A1", "A2", "A4", "A3"])
    assert result_rule.feature_names.override == False
    assert result_rule.feature_names.remove_modifiers.values == set()
    assert result_rule.feature_names.remove_modifiers.operation == base_onlyone_rule.feature_names.remove_modifiers.operation

def test_only_one_extends_same_only_one_2():
    # base
    base_feature_rule_list = FeatureRuleNodeList()
    base_onlyone_features = create_str_list(True,["A1", "A2"], ["A1", "A3"] )
    base_onlyone_rule = FeatureRuleNodeOnlyOne("A", "desc a", base_onlyone_features)    
    base_feature_rule_list.add_feature_rule(base_onlyone_rule)
    base_feature_rule_list = base_feature_rule_list.resolve_extends(FeatureRuleNodeList())

    # child
    child_feature_rule_list = FeatureRuleNodeList()
    child_onlyone_features = create_str_list(False,["A1", "A4", "A3", "A5"], ["A5"] )
    child_onlyone_rule = FeatureRuleNodeOnlyOne("A", "", child_onlyone_features)    
    child_feature_rule_list.add_feature_rule(child_onlyone_rule)
    result = child_feature_rule_list.resolve_extends(base_feature_rule_list)

    # Validate result
    assert not result.is_empty()
    assert len(result.feature_rules_only_one) == 1
    assert len(result.feature_rules_incompatible) == 0
    result_rule = next((o for o in result.feature_rules_only_one if o.name == "A"), None)
    assert result_rule.name == base_onlyone_rule.name
    assert result_rule.description == base_onlyone_rule.description
    assert result_rule.feature_names.values == set(["A1", "A2", "A4", "A3"])
    assert result_rule.feature_names.override == False
    assert result_rule.feature_names.remove_modifiers.values == set()
    assert result_rule.feature_names.remove_modifiers.operation == base_onlyone_rule.feature_names.remove_modifiers.operation

def test_only_one_extends_same_only_one_3():
    # base
    base_feature_rule_list = FeatureRuleNodeList()
    base_onlyone_features = create_str_list(False,["A1", "A2"], ["A1", "A3"] )
    base_onlyone_rule = FeatureRuleNodeOnlyOne("A", "desc a", base_onlyone_features)    
    base_feature_rule_list.add_feature_rule(base_onlyone_rule)
    base_feature_rule_list = base_feature_rule_list.resolve_extends(FeatureRuleNodeList())

    # child
    child_feature_rule_list = FeatureRuleNodeList()
    child_onlyone_features = create_str_list(True,["A1", "A4", "A3", "A5"], ["A5"] )
    child_onlyone_rule = FeatureRuleNodeOnlyOne("A", "", child_onlyone_features)    
    child_feature_rule_list.add_feature_rule(child_onlyone_rule)
    result = child_feature_rule_list.resolve_extends(base_feature_rule_list)

    # Validate result
    assert not result.is_empty()
    assert len(result.feature_rules_only_one) == 1
    assert len(result.feature_rules_incompatible) == 0
    result_rule = next((o for o in result.feature_rules_only_one if o.name == "A"), None)
    assert result_rule.name == base_onlyone_rule.name
    assert result_rule.description == base_onlyone_rule.description
    assert result_rule.feature_names.values == set(["A1", "A4", "A3"])
    assert result_rule.feature_names.override == True
    assert result_rule.feature_names.remove_modifiers.values == set()
    assert result_rule.feature_names.remove_modifiers.operation == base_onlyone_rule.feature_names.remove_modifiers.operation

def test_only_one_extends_same_only_one_4():
    # base
    base_feature_rule_list = FeatureRuleNodeList()
    base_onlyone_features = create_str_list(True,["A1", "A2"], ["A1", "A3"] )
    base_onlyone_rule = FeatureRuleNodeOnlyOne("A", "desc a", base_onlyone_features)    
    base_feature_rule_list.add_feature_rule(base_onlyone_rule)
    base_feature_rule_list = base_feature_rule_list.resolve_extends(FeatureRuleNodeList())

    # child
    child_feature_rule_list = FeatureRuleNodeList()
    child_onlyone_features = create_str_list(True,["A1", "A4", "A3", "A5"], ["A5"] )
    child_onlyone_rule = FeatureRuleNodeOnlyOne("A", "", child_onlyone_features)    
    child_feature_rule_list.add_feature_rule(child_onlyone_rule)
    result = child_feature_rule_list.resolve_extends(base_feature_rule_list)

    # Validate result
    assert not result.is_empty()
    assert len(result.feature_rules_only_one) == 1
    assert len(result.feature_rules_incompatible) == 0
    result_rule = next((o for o in result.feature_rules_only_one if o.name == "A"), None)
    assert result_rule.name == base_onlyone_rule.name
    assert result_rule.description == base_onlyone_rule.description
    assert result_rule.feature_names.values == set(["A1", "A4", "A3"])
    assert result_rule.feature_names.override == True
    assert result_rule.feature_names.remove_modifiers.values == set()
    assert result_rule.feature_names.remove_modifiers.operation == base_onlyone_rule.feature_names.remove_modifiers.operation


def test_incompatible_extends_same_incompatible_1():
    # base
    base_feature_rule_list = FeatureRuleNodeList()
    base_incompatible_features = create_str_list(False,["A1", "A2"], ["A1", "A3"] )
    base_incompatible_rule = FeatureRuleNodeIncompatible("A", "desc a", "A0", base_incompatible_features)    
    base_feature_rule_list.add_feature_rule(base_incompatible_rule)
    base_feature_rule_list = base_feature_rule_list.resolve_extends(FeatureRuleNodeList())

    # child
    child_feature_rule_list = FeatureRuleNodeList()
    child_incompatible_features = create_str_list(False,["A1", "A4", "A3", "A5"], ["A5"] )
    child_incompatible_rule = FeatureRuleNodeIncompatible("A", "",  "A0", child_incompatible_features)    
    child_feature_rule_list.add_feature_rule(child_incompatible_rule)
    result = child_feature_rule_list.resolve_extends(base_feature_rule_list)

    # Validate result
    assert not result.is_empty()
    assert len(result.feature_rules_only_one) == 0
    assert len(result.feature_rules_incompatible) == 1
    result_rule = next((o for o in result.feature_rules_incompatible if o.name == "A"), None)
    assert result_rule.name == "A"
    assert result_rule.description == base_incompatible_rule.description
    assert result_rule.feature == "A0"
    assert result_rule.incompatible_with.values == set(["A1", "A2", "A4", "A3"])
    assert result_rule.incompatible_with.override == False
    assert result_rule.incompatible_with.remove_modifiers.values == set()
    assert result_rule.incompatible_with.remove_modifiers.operation == base_incompatible_rule.incompatible_with.remove_modifiers.operation

def test_incompatible_extends_same_incompatible_2():
    # base
    base_feature_rule_list = FeatureRuleNodeList()
    base_incompatible_features = create_str_list(True,["A1", "A2"], ["A1", "A3"] )
    base_incompatible_rule = FeatureRuleNodeIncompatible("A", "desc a", "A0", base_incompatible_features)    
    base_feature_rule_list.add_feature_rule(base_incompatible_rule)
    base_feature_rule_list = base_feature_rule_list.resolve_extends(FeatureRuleNodeList())

    # child
    child_feature_rule_list = FeatureRuleNodeList()
    child_incompatible_features = create_str_list(False,["A1", "A4", "A3", "A5"], ["A5"] )
    child_incompatible_rule = FeatureRuleNodeIncompatible("A", "",  "A0", child_incompatible_features)    
    child_feature_rule_list.add_feature_rule(child_incompatible_rule)
    result = child_feature_rule_list.resolve_extends(base_feature_rule_list)

    # Validate result
    assert not result.is_empty()
    assert len(result.feature_rules_only_one) == 0
    assert len(result.feature_rules_incompatible) == 1
    result_rule = next((o for o in result.feature_rules_incompatible if o.name == "A"), None)
    assert result_rule.name == "A"
    assert result_rule.description == base_incompatible_rule.description
    assert result_rule.feature == "A0"
    assert result_rule.incompatible_with.values == set(["A1", "A2", "A4", "A3"])
    assert result_rule.incompatible_with.override == False
    assert result_rule.incompatible_with.remove_modifiers.values == set()
    assert result_rule.incompatible_with.remove_modifiers.operation == base_incompatible_rule.incompatible_with.remove_modifiers.operation

def test_incompatible_extends_same_incompatible_3():
    # base
    base_feature_rule_list = FeatureRuleNodeList()
    base_incompatible_features = create_str_list(False,["A1", "A2"], ["A1", "A3"] )
    base_incompatible_rule = FeatureRuleNodeIncompatible("A", "desc a", "A0", base_incompatible_features)    
    base_feature_rule_list.add_feature_rule(base_incompatible_rule)
    base_feature_rule_list = base_feature_rule_list.resolve_extends(FeatureRuleNodeList())

    # child
    child_feature_rule_list = FeatureRuleNodeList()
    child_incompatible_features = create_str_list(True,["A1", "A4", "A3", "A5"], ["A5"] )
    child_incompatible_rule = FeatureRuleNodeIncompatible("A", "",  "A0", child_incompatible_features)    
    child_feature_rule_list.add_feature_rule(child_incompatible_rule)
    result = child_feature_rule_list.resolve_extends(base_feature_rule_list)

    # Validate result
    assert not result.is_empty()
    assert len(result.feature_rules_only_one) == 0
    assert len(result.feature_rules_incompatible) == 1
    result_rule = next((o for o in result.feature_rules_incompatible if o.name == "A"), None)
    assert result_rule.name == "A"
    assert result_rule.description == base_incompatible_rule.description
    assert result_rule.feature == "A0"
    assert result_rule.incompatible_with.values == set(["A1", "A4", "A3"])
    assert result_rule.incompatible_with.override == True
    assert result_rule.incompatible_with.remove_modifiers.values == set()
    assert result_rule.incompatible_with.remove_modifiers.operation == base_incompatible_rule.incompatible_with.remove_modifiers.operation

def test_incompatible_extends_same_incompatible_4():
    # base
    base_feature_rule_list = FeatureRuleNodeList()
    base_incompatible_features = create_str_list(True,["A1", "A2"], ["A1", "A3"] )
    base_incompatible_rule = FeatureRuleNodeIncompatible("A", "desc a", "A0", base_incompatible_features)    
    base_feature_rule_list.add_feature_rule(base_incompatible_rule)
    base_feature_rule_list = base_feature_rule_list.resolve_extends(FeatureRuleNodeList())

    # child
    child_feature_rule_list = FeatureRuleNodeList()
    child_incompatible_features = create_str_list(True,["A1", "A4", "A3", "A5"], ["A5"] )
    child_incompatible_rule = FeatureRuleNodeIncompatible("A", "",  "A0", child_incompatible_features)    
    child_feature_rule_list.add_feature_rule(child_incompatible_rule)
    result = child_feature_rule_list.resolve_extends(base_feature_rule_list)

    # Validate result
    assert not result.is_empty()
    assert len(result.feature_rules_only_one) == 0
    assert len(result.feature_rules_incompatible) == 1
    result_rule = next((o for o in result.feature_rules_incompatible if o.name == "A"), None)
    assert result_rule.name == "A"
    assert result_rule.description == base_incompatible_rule.description
    assert result_rule.feature == "A0"
    assert result_rule.incompatible_with.values == set(["A1", "A4", "A3"])
    assert result_rule.incompatible_with.override == True
    assert result_rule.incompatible_with.remove_modifiers.values == set()
    assert result_rule.incompatible_with.remove_modifiers.operation == base_incompatible_rule.incompatible_with.remove_modifiers.operation

def test_extends_feature_rule_node_list():

    test_extends_empty()

    test_only_one_extends_empty()
    test_only_one_extends_empty_override()
    test_incompatible_extends_empty()
    test_incompatible_extends_empty_override()

    test_empty_extends_only_one_extends()
    test_empty_extends_only_one_extends_override()
    test_empty_extends_incompatible()
    test_empty_extends_incompatible_override()

    test_only_one_extends_diff_only_one_1()
    test_only_one_extends_diff_only_one_2()
    test_only_one_extends_diff_only_one_3()
    test_only_one_extends_diff_only_one_4()

    test_incompatible_extends_diff_incompatible_1()
    test_incompatible_extends_diff_incompatible_2()
    test_incompatible_extends_diff_incompatible_3()
    test_incompatible_extends_diff_incompatible_4()

    test_only_one_extends_same_only_one_1()
    test_only_one_extends_same_only_one_2()
    test_only_one_extends_same_only_one_3()
    test_only_one_extends_same_only_one_4()

    test_incompatible_extends_same_incompatible_1()
    test_incompatible_extends_same_incompatible_2()
    test_incompatible_extends_same_incompatible_3()
    test_incompatible_extends_same_incompatible_4()
    