
from test_common import create_feature_rule_node_list, create_feature_str_list, create_incompatible_rule, create_only_one_rule, create_str_list
from toolchain.nodes.feature_node import FeatureStrList, resolve_extends_feature_list

def test_extends_empty_1():
    feature_str_list_child = create_feature_str_list(False, [], [])
    feature_str_list_parent = create_feature_str_list(False, [], [])

    feature_str_list_parent = resolve_extends_feature_list(feature_str_list_parent, FeatureStrList(),  create_feature_rule_node_list([])).unwrap()
    result = resolve_extends_feature_list(feature_str_list_child, feature_str_list_parent, create_feature_rule_node_list([])).unwrap()
    
    # Validate result
    assert result.override == False
    assert result.values == set([])
    assert result.remove_modifiers.values == set()

def test_extends_empty_2():
    feature_str_list_child = create_feature_str_list(True, [], [])
    feature_str_list_parent = create_feature_str_list(False, [], [])

    feature_str_list_parent = resolve_extends_feature_list(feature_str_list_parent, FeatureStrList(),  create_feature_rule_node_list([])).unwrap()
    result = resolve_extends_feature_list(feature_str_list_child, feature_str_list_parent, create_feature_rule_node_list([])).unwrap()
    
    # Validate result
    assert result.override == True
    assert result.values == set([])
    assert result.remove_modifiers.values == set()

def test_extends_empty_3():
    feature_str_list_child = create_feature_str_list(False, [], [])
    feature_str_list_parent = create_feature_str_list(True, [], [])

    feature_str_list_parent = resolve_extends_feature_list(feature_str_list_parent, FeatureStrList(),  create_feature_rule_node_list([])).unwrap()
    result = resolve_extends_feature_list(feature_str_list_child, feature_str_list_parent, create_feature_rule_node_list([])).unwrap()
    
    # Validate result
    assert result.override == False
    assert result.values == set([])
    assert result.remove_modifiers.values == set()

def test_extends_empty_4():
    feature_str_list_child = create_feature_str_list(True, [], [])
    feature_str_list_parent = create_feature_str_list(True, [], [])

    feature_str_list_parent = resolve_extends_feature_list(feature_str_list_parent, FeatureStrList(),  create_feature_rule_node_list([])).unwrap()
    result = resolve_extends_feature_list(feature_str_list_child, feature_str_list_parent, create_feature_rule_node_list([])).unwrap()
    
    # Validate result
    assert result.override == True
    assert result.values == set([])
    assert result.remove_modifiers.values == set()

def test_extends_empty_parent_no_rule_1():
    feature_str_list_child = create_feature_str_list(False, ["A1", "A2"], ["A2", "A3"])
    feature_str_list_parent = create_feature_str_list(False, [], [])

    feature_str_list_parent = resolve_extends_feature_list(feature_str_list_parent, FeatureStrList(),  create_feature_rule_node_list([])).unwrap()
    result = resolve_extends_feature_list(feature_str_list_child, feature_str_list_parent, create_feature_rule_node_list([])).unwrap()

     # Validate result
    assert result.override == False
    assert result.values == set(["A1"])
    assert result.remove_modifiers.values == set()

def test_extends_empty_parent_no_rule_2():
    feature_str_list_child = create_feature_str_list(True, ["A1", "A2"], ["A2", "A3"])
    feature_str_list_parent = create_feature_str_list(False, [], [])

    feature_str_list_parent = resolve_extends_feature_list(feature_str_list_parent, FeatureStrList(),  create_feature_rule_node_list([])).unwrap()
    result = resolve_extends_feature_list(feature_str_list_child, feature_str_list_parent, create_feature_rule_node_list([])).unwrap()

     # Validate result
    assert result.override == True
    assert result.values == set(["A1"])
    assert result.remove_modifiers.values == set()

def test_extends_empty_parent_no_rule_3():
    feature_str_list_child = create_feature_str_list(False, ["A1", "A2"], ["A2", "A3"])
    feature_str_list_parent = create_feature_str_list(True, [], [])

    feature_str_list_parent = resolve_extends_feature_list(feature_str_list_parent, FeatureStrList(),  create_feature_rule_node_list([])).unwrap()
    result = resolve_extends_feature_list(feature_str_list_child, feature_str_list_parent, create_feature_rule_node_list([])).unwrap()

     # Validate result
    assert result.override == False
    assert result.values == set(["A1"])
    assert result.remove_modifiers.values == set()

def test_extends_empty_parent_no_rule_4():
    feature_str_list_child = create_feature_str_list(True, ["A1", "A2"], ["A2", "A3"])
    feature_str_list_parent = create_feature_str_list(True, [], [])

    feature_str_list_parent = resolve_extends_feature_list(feature_str_list_parent, FeatureStrList(),  create_feature_rule_node_list([])).unwrap()
    result = resolve_extends_feature_list(feature_str_list_child, feature_str_list_parent, create_feature_rule_node_list([])).unwrap()

     # Validate result
    assert result.override == True
    assert result.values == set(["A1"])
    assert result.remove_modifiers.values == set()

def test_extends_empty_parent_only_one_rule_1():
    feature_str_list_child = create_feature_str_list(False, ["A1", "A2", "A4", "A5"], ["A2", "A3"])
    feature_str_list_parent = create_feature_str_list(False, [], [])

    onlyone_rule = create_only_one_rule("OA", "OnlyOne A", ["A1", "A3"])
    feature_rule_list = create_feature_rule_node_list([onlyone_rule])

    feature_str_list_parent = resolve_extends_feature_list(feature_str_list_parent, FeatureStrList(),feature_rule_list).unwrap()
    result = resolve_extends_feature_list(feature_str_list_child, feature_str_list_parent, feature_rule_list).unwrap()

     # Validate result
    assert result.override == False
    assert result.values == set(["A1", "A4", "A5"])
    assert result.remove_modifiers.values == set()

def test_extends_empty_parent_only_one_rule_2():
    feature_str_list_child = create_feature_str_list(True, ["A1", "A2", "A4", "A5"], ["A2", "A3"])
    feature_str_list_parent = create_feature_str_list(False, [], [])

    onlyone_rule = create_only_one_rule("OA", "OnlyOne A", ["A1", "A3"])
    feature_rule_list = create_feature_rule_node_list([onlyone_rule])

    feature_str_list_parent = resolve_extends_feature_list(feature_str_list_parent, FeatureStrList(),feature_rule_list).unwrap()
    result = resolve_extends_feature_list(feature_str_list_child, feature_str_list_parent, feature_rule_list).unwrap()

     # Validate result
    assert result.override == True
    assert result.values == set(["A1", "A4", "A5"])
    assert result.remove_modifiers.values == set()

def test_extends_empty_parent_only_one_rule_3():
    feature_str_list_child = create_feature_str_list(False, ["A1", "A2", "A4", "A5"], ["A2", "A3"])
    feature_str_list_parent = create_feature_str_list(True, [], [])

    onlyone_rule = create_only_one_rule("OA", "OnlyOne A", ["A1", "A3"])
    feature_rule_list = create_feature_rule_node_list([onlyone_rule])

    feature_str_list_parent = resolve_extends_feature_list(feature_str_list_parent, FeatureStrList(),feature_rule_list).unwrap()
    result = resolve_extends_feature_list(feature_str_list_child, feature_str_list_parent, feature_rule_list).unwrap()

     # Validate result
    assert result.override == False
    assert result.values == set(["A1", "A4", "A5"])
    assert result.remove_modifiers.values == set()

def test_extends_empty_parent_only_one_rule_4():
    feature_str_list_child = create_feature_str_list(True, ["A1", "A2", "A4", "A5"], ["A2", "A3"])
    feature_str_list_parent = create_feature_str_list(True, [], [])

    onlyone_rule = create_only_one_rule("OA", "OnlyOne A", ["A1", "A3"])
    feature_rule_list = create_feature_rule_node_list([onlyone_rule])

    feature_str_list_parent = resolve_extends_feature_list(feature_str_list_parent, FeatureStrList(),feature_rule_list).unwrap()
    result = resolve_extends_feature_list(feature_str_list_child, feature_str_list_parent, feature_rule_list).unwrap()

     # Validate result
    assert result.override == True
    assert result.values == set(["A1", "A4", "A5"])
    assert result.remove_modifiers.values == set()

def test_extends_empty_parent_only_one_rule_failed_1():
    feature_str_list_child = create_feature_str_list(False, ["A1", "A2", "A4", "A5"], ["A2", "A3"])
    feature_str_list_parent = create_feature_str_list(False, [], [])

    onlyone_rule = create_only_one_rule("OA", "OnlyOne A", ["A1", "A4"])
    feature_rule_list = create_feature_rule_node_list([onlyone_rule])

    feature_str_list_parent = resolve_extends_feature_list(feature_str_list_parent, FeatureStrList(),feature_rule_list).unwrap()
    assert resolve_extends_feature_list(feature_str_list_child, feature_str_list_parent, feature_rule_list).is_err()


def test_extends_empty_parent_only_one_rule_failed_2():
    feature_str_list_child = create_feature_str_list(True, ["A1", "A2", "A4", "A5"], ["A2", "A3"])
    feature_str_list_parent = create_feature_str_list(False, [], [])

    onlyone_rule = create_only_one_rule("OA", "OnlyOne A", ["A1", "A4"])
    feature_rule_list = create_feature_rule_node_list([onlyone_rule])

    feature_str_list_parent = resolve_extends_feature_list(feature_str_list_parent, FeatureStrList(),feature_rule_list).unwrap()
    assert resolve_extends_feature_list(feature_str_list_child, feature_str_list_parent, feature_rule_list).is_err()

def test_extends_empty_parent_only_one_rule_failed_3():
    feature_str_list_child = create_feature_str_list(False, ["A1", "A2", "A4", "A5"], ["A2", "A3"])
    feature_str_list_parent = create_feature_str_list(True, [], [])

    onlyone_rule = create_only_one_rule("OA", "OnlyOne A", ["A1", "A4"])
    feature_rule_list = create_feature_rule_node_list([onlyone_rule])

    feature_str_list_parent = resolve_extends_feature_list(feature_str_list_parent, FeatureStrList(),feature_rule_list).unwrap()
    assert resolve_extends_feature_list(feature_str_list_child, feature_str_list_parent, feature_rule_list).is_err()

def test_extends_empty_parent_only_one_rule_failed_4():
    feature_str_list_child = create_feature_str_list(True, ["A1", "A2", "A4", "A5"], ["A2", "A3"])
    feature_str_list_parent = create_feature_str_list(True, [], [])

    onlyone_rule = create_only_one_rule("OA", "OnlyOne A", ["A1", "A4"])
    feature_rule_list = create_feature_rule_node_list([onlyone_rule])

    feature_str_list_parent = resolve_extends_feature_list(feature_str_list_parent, FeatureStrList(),feature_rule_list).unwrap()
    assert resolve_extends_feature_list(feature_str_list_child, feature_str_list_parent, feature_rule_list).is_err()


def test_extends_empty_parent_incompatible_rule_1():
    feature_str_list_child = create_feature_str_list(False, ["A1", "A2", "A4", "A5"], ["A2", "A3"])
    feature_str_list_parent = create_feature_str_list(False, [], [])

    incompatible_rule = create_incompatible_rule("IA", "Incompatible A", "A0", ["A1", "A3"])
    feature_rule_list = create_feature_rule_node_list([incompatible_rule])

    feature_str_list_parent = resolve_extends_feature_list(feature_str_list_parent, FeatureStrList(),feature_rule_list).unwrap()
    result = resolve_extends_feature_list(feature_str_list_child, feature_str_list_parent, feature_rule_list).unwrap()

    # Validate result
    assert result.override == False
    assert result.values == set(["A1", "A4", "A5"])
    assert result.remove_modifiers.values == set()

def test_extends_empty_parent_incompatible_rule_2():
    feature_str_list_child = create_feature_str_list(True, ["A1", "A2", "A4", "A5"], ["A2", "A3"])
    feature_str_list_parent = create_feature_str_list(False, [], [])

    incompatible_rule = create_incompatible_rule("IA", "Incompatible A", "A0", ["A1", "A3"])
    feature_rule_list = create_feature_rule_node_list([incompatible_rule])

    feature_str_list_parent = resolve_extends_feature_list(feature_str_list_parent, FeatureStrList(),feature_rule_list).unwrap()
    result = resolve_extends_feature_list(feature_str_list_child, feature_str_list_parent, feature_rule_list).unwrap()

    # Validate result
    assert result.override == True
    assert result.values == set(["A1", "A4", "A5"])
    assert result.remove_modifiers.values == set()

def test_extends_empty_parent_incompatible_rule_3():
    feature_str_list_child = create_feature_str_list(False, ["A1", "A2", "A4", "A5"], ["A2", "A3"])
    feature_str_list_parent = create_feature_str_list(True, [], [])

    incompatible_rule = create_incompatible_rule("IA", "Incompatible A", "A0", ["A1", "A3"])
    feature_rule_list = create_feature_rule_node_list([incompatible_rule])

    feature_str_list_parent = resolve_extends_feature_list(feature_str_list_parent, FeatureStrList(),feature_rule_list).unwrap()
    result = resolve_extends_feature_list(feature_str_list_child, feature_str_list_parent, feature_rule_list).unwrap()

    # Validate result
    assert result.override == False
    assert result.values == set(["A1", "A4", "A5"])
    assert result.remove_modifiers.values == set()

def test_extends_empty_parent_incompatible_rule_4():
    feature_str_list_child = create_feature_str_list(True, ["A1", "A2", "A4", "A5"], ["A2", "A3"])
    feature_str_list_parent = create_feature_str_list(True, [], [])

    incompatible_rule = create_incompatible_rule("IA", "Incompatible A", "A0", ["A1", "A3"])
    feature_rule_list = create_feature_rule_node_list([incompatible_rule])

    feature_str_list_parent = resolve_extends_feature_list(feature_str_list_parent, FeatureStrList(),feature_rule_list).unwrap()
    result = resolve_extends_feature_list(feature_str_list_child, feature_str_list_parent, feature_rule_list).unwrap()

    # Validate result
    assert result.override == True
    assert result.values == set(["A1", "A4", "A5"])
    assert result.remove_modifiers.values == set()

def test_extends_empty_parent_incompatible_rule_failed_1():
    feature_str_list_child = create_feature_str_list(False, ["A1", "A2", "A4", "A5"], ["A2", "A3"])
    feature_str_list_parent = create_feature_str_list(False, [], [])

    incompatible_rule = create_incompatible_rule("IA", "Incompatible A", "A1", ["A2", "A4"])
    feature_rule_list = create_feature_rule_node_list([incompatible_rule])

    feature_str_list_parent = resolve_extends_feature_list(feature_str_list_parent, FeatureStrList(),feature_rule_list).unwrap()
    assert resolve_extends_feature_list(feature_str_list_child, feature_str_list_parent, feature_rule_list).is_err()

def test_extends_empty_parent_incompatible_rule_failed_2():
    feature_str_list_child = create_feature_str_list(True, ["A1", "A2", "A4", "A5"], ["A2", "A3"])
    feature_str_list_parent = create_feature_str_list(False, [], [])

    incompatible_rule = create_incompatible_rule("IA", "Incompatible A", "A1", ["A2", "A4"])
    feature_rule_list = create_feature_rule_node_list([incompatible_rule])

    feature_str_list_parent = resolve_extends_feature_list(feature_str_list_parent, FeatureStrList(),feature_rule_list).unwrap()
    assert resolve_extends_feature_list(feature_str_list_child, feature_str_list_parent, feature_rule_list).is_err()

def test_extends_empty_parent_incompatible_rule_failed_3():
    feature_str_list_child = create_feature_str_list(False, ["A1", "A2", "A4", "A5"], ["A2", "A3"])
    feature_str_list_parent = create_feature_str_list(True, [], [])

    incompatible_rule = create_incompatible_rule("IA", "Incompatible A", "A1", ["A2", "A4"])
    feature_rule_list = create_feature_rule_node_list([incompatible_rule])

    feature_str_list_parent = resolve_extends_feature_list(feature_str_list_parent, FeatureStrList(),feature_rule_list).unwrap()
    assert resolve_extends_feature_list(feature_str_list_child, feature_str_list_parent, feature_rule_list).is_err()

def test_extends_empty_parent_incompatible_rule_failed_4():
    feature_str_list_child = create_feature_str_list(True, ["A1", "A2", "A4", "A5"], ["A2", "A3"])
    feature_str_list_parent = create_feature_str_list(True, [], [])

    incompatible_rule = create_incompatible_rule("IA", "Incompatible A", "A1", ["A2", "A4"])
    feature_rule_list = create_feature_rule_node_list([incompatible_rule])

    feature_str_list_parent = resolve_extends_feature_list(feature_str_list_parent, FeatureStrList(),feature_rule_list).unwrap()
    assert resolve_extends_feature_list(feature_str_list_child, feature_str_list_parent, feature_rule_list).is_err()

def test_extends_empty_parent_multiple_rules_1():
    feature_str_list_child = create_feature_str_list(False, ["A1", "A2", "A4", "A5"], ["A2", "A3"])
    feature_str_list_parent = create_feature_str_list(False, [], [])

    onlyone_rule_a = create_only_one_rule("OA", "OnlyOne A", ["A1", "A3"])
    onlyone_rule_b = create_only_one_rule("OB", "OnlyOne B", ["A0", "A4"])
    incompatible_rule_a = create_incompatible_rule("IA", "Incompatible A", "A2", ["A1", "A3"])
    incompatible_rule_b = create_incompatible_rule("IB", "Incompatible B", "A4", ["A0", "A3"])
    feature_rule_list = create_feature_rule_node_list([onlyone_rule_a, onlyone_rule_b, incompatible_rule_a, incompatible_rule_b])

    feature_str_list_parent = resolve_extends_feature_list(feature_str_list_parent, FeatureStrList(),feature_rule_list).unwrap()
    result = resolve_extends_feature_list(feature_str_list_child, feature_str_list_parent, feature_rule_list).unwrap()

    # Validate result
    assert result.override == False
    assert result.values == set(["A1", "A4", "A5"])
    assert result.remove_modifiers.values == set()

def test_extends_empty_parent_multiple_rules_2():
    feature_str_list_child = create_feature_str_list(True, ["A1", "A2", "A4", "A5"], ["A2", "A3"])
    feature_str_list_parent = create_feature_str_list(False, [], [])

    onlyone_rule_a = create_only_one_rule("OA", "OnlyOne A", ["A1", "A3"])
    onlyone_rule_b = create_only_one_rule("OB", "OnlyOne B", ["A0", "A4"])
    incompatible_rule_a = create_incompatible_rule("IA", "Incompatible A", "A2", ["A1", "A3"])
    incompatible_rule_b = create_incompatible_rule("IB", "Incompatible B", "A4", ["A0", "A3"])
    feature_rule_list = create_feature_rule_node_list([onlyone_rule_a, onlyone_rule_b, incompatible_rule_a, incompatible_rule_b])

    feature_str_list_parent = resolve_extends_feature_list(feature_str_list_parent, FeatureStrList(),feature_rule_list).unwrap()
    result = resolve_extends_feature_list(feature_str_list_child, feature_str_list_parent, feature_rule_list).unwrap()

    # Validate result
    assert result.override == True
    assert result.values == set(["A1", "A4", "A5"])
    assert result.remove_modifiers.values == set()

def test_extends_empty_parent_multiple_rules_3():
    feature_str_list_child = create_feature_str_list(False, ["A1", "A2", "A4", "A5"], ["A2", "A3"])
    feature_str_list_parent = create_feature_str_list(True, [], [])

    onlyone_rule_a = create_only_one_rule("OA", "OnlyOne A", ["A1", "A3"])
    onlyone_rule_b = create_only_one_rule("OB", "OnlyOne B", ["A0", "A4"])
    incompatible_rule_a = create_incompatible_rule("IA", "Incompatible A", "A2", ["A1", "A3"])
    incompatible_rule_b = create_incompatible_rule("IB", "Incompatible B", "A4", ["A0", "A3"])
    feature_rule_list = create_feature_rule_node_list([onlyone_rule_a, onlyone_rule_b, incompatible_rule_a, incompatible_rule_b])

    feature_str_list_parent = resolve_extends_feature_list(feature_str_list_parent, FeatureStrList(),feature_rule_list).unwrap()
    result = resolve_extends_feature_list(feature_str_list_child, feature_str_list_parent, feature_rule_list).unwrap()

    # Validate result
    assert result.override == False
    assert result.values == set(["A1", "A4", "A5"])
    assert result.remove_modifiers.values == set()

def test_extends_empty_parent_multiple_rules_4():
    feature_str_list_child = create_feature_str_list(True, ["A1", "A2", "A4", "A5"], ["A2", "A3"])
    feature_str_list_parent = create_feature_str_list(True, [], [])

    onlyone_rule_a = create_only_one_rule("OA", "OnlyOne A", ["A1", "A3"])
    onlyone_rule_b = create_only_one_rule("OB", "OnlyOne B", ["A0", "A4"])
    incompatible_rule_a = create_incompatible_rule("IA", "Incompatible A", "A2", ["A1", "A3"])
    incompatible_rule_b = create_incompatible_rule("IB", "Incompatible B", "A4", ["A0", "A3"])
    feature_rule_list = create_feature_rule_node_list([onlyone_rule_a, onlyone_rule_b, incompatible_rule_a, incompatible_rule_b])

    feature_str_list_parent = resolve_extends_feature_list(feature_str_list_parent, FeatureStrList(),feature_rule_list).unwrap()
    result = resolve_extends_feature_list(feature_str_list_child, feature_str_list_parent, feature_rule_list).unwrap()

    # Validate result
    assert result.override == True
    assert result.values == set(["A1", "A4", "A5"])
    assert result.remove_modifiers.values == set()


def test_extends_empty_parent_multiple_rules_failed_1_1():
    feature_str_list_child = create_feature_str_list(False, ["A1", "A2", "A4", "A5"], ["A2", "A3"])
    feature_str_list_parent = create_feature_str_list(False, [], [])

    onlyone_rule_a = create_only_one_rule("OA", "OnlyOne A", ["A1", "A5"])
    onlyone_rule_b = create_only_one_rule("OB", "OnlyOne B", ["A0", "A4"])
    incompatible_rule_a = create_incompatible_rule("IA", "Incompatible A", "A2", ["A1", "A3"])
    incompatible_rule_b = create_incompatible_rule("IB", "Incompatible B", "A4", ["A0", "A3"])
    feature_rule_list = create_feature_rule_node_list([onlyone_rule_a, onlyone_rule_b, incompatible_rule_a, incompatible_rule_b])

    feature_str_list_parent = resolve_extends_feature_list(feature_str_list_parent, FeatureStrList(),feature_rule_list).unwrap()
    assert resolve_extends_feature_list(feature_str_list_child, feature_str_list_parent, feature_rule_list).is_err()

def test_extends_empty_parent_multiple_rules_failed_2_1():
    feature_str_list_child = create_feature_str_list(False, ["A1", "A2", "A4", "A5"], ["A2", "A3"])
    feature_str_list_parent = create_feature_str_list(False, [], [])

    onlyone_rule_a = create_only_one_rule("OA", "OnlyOne A", ["A1", "A3"])
    onlyone_rule_b = create_only_one_rule("OB", "OnlyOne B", ["A5", "A4"])
    incompatible_rule_a = create_incompatible_rule("IA", "Incompatible A", "A2", ["A1", "A3"])
    incompatible_rule_b = create_incompatible_rule("IB", "Incompatible B", "A4", ["A0", "A3"])
    feature_rule_list = create_feature_rule_node_list([onlyone_rule_a, onlyone_rule_b, incompatible_rule_a, incompatible_rule_b])

    feature_str_list_parent = resolve_extends_feature_list(feature_str_list_parent, FeatureStrList(),feature_rule_list).unwrap()
    assert resolve_extends_feature_list(feature_str_list_child, feature_str_list_parent, feature_rule_list).is_err()

def test_extends_empty_parent_multiple_rules_failed_3_1():
    feature_str_list_child = create_feature_str_list(False, ["A1", "A2", "A4", "A5"], ["A2", "A3"])
    feature_str_list_parent = create_feature_str_list(False, [], [])

    onlyone_rule_a = create_only_one_rule("OA", "OnlyOne A", ["A1", "A3"])
    onlyone_rule_b = create_only_one_rule("OB", "OnlyOne B", ["A0", "A4"])
    incompatible_rule_a = create_incompatible_rule("IA", "Incompatible A", "A5", ["A1", "A4"])
    incompatible_rule_b = create_incompatible_rule("IB", "Incompatible B", "A4", ["A0", "A3"])
    feature_rule_list = create_feature_rule_node_list([onlyone_rule_a, onlyone_rule_b, incompatible_rule_a, incompatible_rule_b])

    feature_str_list_parent = resolve_extends_feature_list(feature_str_list_parent, FeatureStrList(),feature_rule_list).unwrap()
    assert resolve_extends_feature_list(feature_str_list_child, feature_str_list_parent, feature_rule_list).is_err()

def test_extends_empty_parent_multiple_rules_failed_4_1():
    feature_str_list_child = create_feature_str_list(False, ["A1", "A2", "A4", "A5"], ["A2", "A3"])
    feature_str_list_parent = create_feature_str_list(False, [], [])

    onlyone_rule_a = create_only_one_rule("OA", "OnlyOne A", ["A1", "A3"])
    onlyone_rule_b = create_only_one_rule("OB", "OnlyOne B", ["A0", "A4"])
    incompatible_rule_a = create_incompatible_rule("IA", "Incompatible A", "A2", ["A1", "A3"])
    incompatible_rule_b = create_incompatible_rule("IB", "Incompatible B", "A4", ["A0", "A5"])
    feature_rule_list = create_feature_rule_node_list([onlyone_rule_a, onlyone_rule_b, incompatible_rule_a, incompatible_rule_b])

    feature_str_list_parent = resolve_extends_feature_list(feature_str_list_parent, FeatureStrList(),feature_rule_list).unwrap()
    assert resolve_extends_feature_list(feature_str_list_child, feature_str_list_parent, feature_rule_list).is_err()


def test_extends_empty_parent_multiple_rules_failed_1_2():
    feature_str_list_child = create_feature_str_list(True, ["A1", "A2", "A4", "A5"], ["A2", "A3"])
    feature_str_list_parent = create_feature_str_list(False, [], [])

    onlyone_rule_a = create_only_one_rule("OA", "OnlyOne A", ["A1", "A5"])
    onlyone_rule_b = create_only_one_rule("OB", "OnlyOne B", ["A0", "A4"])
    incompatible_rule_a = create_incompatible_rule("IA", "Incompatible A", "A2", ["A1", "A3"])
    incompatible_rule_b = create_incompatible_rule("IB", "Incompatible B", "A4", ["A0", "A3"])
    feature_rule_list = create_feature_rule_node_list([onlyone_rule_a, onlyone_rule_b, incompatible_rule_a, incompatible_rule_b])

    feature_str_list_parent = resolve_extends_feature_list(feature_str_list_parent, FeatureStrList(),feature_rule_list).unwrap()
    assert resolve_extends_feature_list(feature_str_list_child, feature_str_list_parent, feature_rule_list).is_err()

def test_extends_empty_parent_multiple_rules_failed_2_2():
    feature_str_list_child = create_feature_str_list(True, ["A1", "A2", "A4", "A5"], ["A2", "A3"])
    feature_str_list_parent = create_feature_str_list(False, [], [])

    onlyone_rule_a = create_only_one_rule("OA", "OnlyOne A", ["A1", "A3"])
    onlyone_rule_b = create_only_one_rule("OB", "OnlyOne B", ["A5", "A4"])
    incompatible_rule_a = create_incompatible_rule("IA", "Incompatible A", "A2", ["A1", "A3"])
    incompatible_rule_b = create_incompatible_rule("IB", "Incompatible B", "A4", ["A0", "A3"])
    feature_rule_list = create_feature_rule_node_list([onlyone_rule_a, onlyone_rule_b, incompatible_rule_a, incompatible_rule_b])

    feature_str_list_parent = resolve_extends_feature_list(feature_str_list_parent, FeatureStrList(),feature_rule_list).unwrap()
    assert resolve_extends_feature_list(feature_str_list_child, feature_str_list_parent, feature_rule_list).is_err()

def test_extends_empty_parent_multiple_rules_failed_3_2():
    feature_str_list_child = create_feature_str_list(True, ["A1", "A2", "A4", "A5"], ["A2", "A3"])
    feature_str_list_parent = create_feature_str_list(False, [], [])

    onlyone_rule_a = create_only_one_rule("OA", "OnlyOne A", ["A1", "A3"])
    onlyone_rule_b = create_only_one_rule("OB", "OnlyOne B", ["A0", "A4"])
    incompatible_rule_a = create_incompatible_rule("IA", "Incompatible A", "A5", ["A1", "A4"])
    incompatible_rule_b = create_incompatible_rule("IB", "Incompatible B", "A4", ["A0", "A3"])
    feature_rule_list = create_feature_rule_node_list([onlyone_rule_a, onlyone_rule_b, incompatible_rule_a, incompatible_rule_b])

    feature_str_list_parent = resolve_extends_feature_list(feature_str_list_parent, FeatureStrList(),feature_rule_list).unwrap()
    assert resolve_extends_feature_list(feature_str_list_child, feature_str_list_parent, feature_rule_list).is_err()

def test_extends_empty_parent_multiple_rules_failed_4_2():
    feature_str_list_child = create_feature_str_list(True, ["A1", "A2", "A4", "A5"], ["A2", "A3"])
    feature_str_list_parent = create_feature_str_list(False, [], [])

    onlyone_rule_a = create_only_one_rule("OA", "OnlyOne A", ["A1", "A3"])
    onlyone_rule_b = create_only_one_rule("OB", "OnlyOne B", ["A0", "A4"])
    incompatible_rule_a = create_incompatible_rule("IA", "Incompatible A", "A2", ["A1", "A3"])
    incompatible_rule_b = create_incompatible_rule("IB", "Incompatible B", "A4", ["A0", "A5"])
    feature_rule_list = create_feature_rule_node_list([onlyone_rule_a, onlyone_rule_b, incompatible_rule_a, incompatible_rule_b])

    feature_str_list_parent = resolve_extends_feature_list(feature_str_list_parent, FeatureStrList(),feature_rule_list).unwrap()
    assert resolve_extends_feature_list(feature_str_list_child, feature_str_list_parent, feature_rule_list).is_err()

def test_extends_empty_parent_multiple_rules_failed_1_3():
    feature_str_list_child = create_feature_str_list(False, ["A1", "A2", "A4", "A5"], ["A2", "A3"])
    feature_str_list_parent = create_feature_str_list(True, [], [])

    onlyone_rule_a = create_only_one_rule("OA", "OnlyOne A", ["A1", "A5"])
    onlyone_rule_b = create_only_one_rule("OB", "OnlyOne B", ["A0", "A4"])
    incompatible_rule_a = create_incompatible_rule("IA", "Incompatible A", "A2", ["A1", "A3"])
    incompatible_rule_b = create_incompatible_rule("IB", "Incompatible B", "A4", ["A0", "A3"])
    feature_rule_list = create_feature_rule_node_list([onlyone_rule_a, onlyone_rule_b, incompatible_rule_a, incompatible_rule_b])

    feature_str_list_parent = resolve_extends_feature_list(feature_str_list_parent, FeatureStrList(),feature_rule_list).unwrap()
    assert resolve_extends_feature_list(feature_str_list_child, feature_str_list_parent, feature_rule_list).is_err()

def test_extends_empty_parent_multiple_rules_failed_2_3():
    feature_str_list_child = create_feature_str_list(False, ["A1", "A2", "A4", "A5"], ["A2", "A3"])
    feature_str_list_parent = create_feature_str_list(True, [], [])

    onlyone_rule_a = create_only_one_rule("OA", "OnlyOne A", ["A1", "A3"])
    onlyone_rule_b = create_only_one_rule("OB", "OnlyOne B", ["A5", "A4"])
    incompatible_rule_a = create_incompatible_rule("IA", "Incompatible A", "A2", ["A1", "A3"])
    incompatible_rule_b = create_incompatible_rule("IB", "Incompatible B", "A4", ["A0", "A3"])
    feature_rule_list = create_feature_rule_node_list([onlyone_rule_a, onlyone_rule_b, incompatible_rule_a, incompatible_rule_b])

    feature_str_list_parent = resolve_extends_feature_list(feature_str_list_parent, FeatureStrList(),feature_rule_list).unwrap()
    assert resolve_extends_feature_list(feature_str_list_child, feature_str_list_parent, feature_rule_list).is_err()

def test_extends_empty_parent_multiple_rules_failed_3_3():
    feature_str_list_child = create_feature_str_list(False, ["A1", "A2", "A4", "A5"], ["A2", "A3"])
    feature_str_list_parent = create_feature_str_list(True, [], [])

    onlyone_rule_a = create_only_one_rule("OA", "OnlyOne A", ["A1", "A3"])
    onlyone_rule_b = create_only_one_rule("OB", "OnlyOne B", ["A0", "A4"])
    incompatible_rule_a = create_incompatible_rule("IA", "Incompatible A", "A5", ["A1", "A4"])
    incompatible_rule_b = create_incompatible_rule("IB", "Incompatible B", "A4", ["A0", "A3"])
    feature_rule_list = create_feature_rule_node_list([onlyone_rule_a, onlyone_rule_b, incompatible_rule_a, incompatible_rule_b])

    feature_str_list_parent = resolve_extends_feature_list(feature_str_list_parent, FeatureStrList(),feature_rule_list).unwrap()
    assert resolve_extends_feature_list(feature_str_list_child, feature_str_list_parent, feature_rule_list).is_err()

def test_extends_empty_parent_multiple_rules_failed_4_3():
    feature_str_list_child = create_feature_str_list(False, ["A1", "A2", "A4", "A5"], ["A2", "A3"])
    feature_str_list_parent = create_feature_str_list(True, [], [])

    onlyone_rule_a = create_only_one_rule("OA", "OnlyOne A", ["A1", "A3"])
    onlyone_rule_b = create_only_one_rule("OB", "OnlyOne B", ["A0", "A4"])
    incompatible_rule_a = create_incompatible_rule("IA", "Incompatible A", "A2", ["A1", "A3"])
    incompatible_rule_b = create_incompatible_rule("IB", "Incompatible B", "A4", ["A0", "A5"])
    feature_rule_list = create_feature_rule_node_list([onlyone_rule_a, onlyone_rule_b, incompatible_rule_a, incompatible_rule_b])

    feature_str_list_parent = resolve_extends_feature_list(feature_str_list_parent, FeatureStrList(),feature_rule_list).unwrap()
    assert resolve_extends_feature_list(feature_str_list_child, feature_str_list_parent, feature_rule_list).is_err()

def test_extends_empty_parent_multiple_rules_failed_1_4():
    feature_str_list_child = create_feature_str_list(True, ["A1", "A2", "A4", "A5"], ["A2", "A3"])
    feature_str_list_parent = create_feature_str_list(True, [], [])

    onlyone_rule_a = create_only_one_rule("OA", "OnlyOne A", ["A1", "A5"])
    onlyone_rule_b = create_only_one_rule("OB", "OnlyOne B", ["A0", "A4"])
    incompatible_rule_a = create_incompatible_rule("IA", "Incompatible A", "A2", ["A1", "A3"])
    incompatible_rule_b = create_incompatible_rule("IB", "Incompatible B", "A4", ["A0", "A3"])
    feature_rule_list = create_feature_rule_node_list([onlyone_rule_a, onlyone_rule_b, incompatible_rule_a, incompatible_rule_b])

    feature_str_list_parent = resolve_extends_feature_list(feature_str_list_parent, FeatureStrList(),feature_rule_list).unwrap()
    assert resolve_extends_feature_list(feature_str_list_child, feature_str_list_parent, feature_rule_list).is_err()

def test_extends_empty_parent_multiple_rules_failed_2_4():
    feature_str_list_child = create_feature_str_list(True, ["A1", "A2", "A4", "A5"], ["A2", "A3"])
    feature_str_list_parent = create_feature_str_list(True, [], [])

    onlyone_rule_a = create_only_one_rule("OA", "OnlyOne A", ["A1", "A3"])
    onlyone_rule_b = create_only_one_rule("OB", "OnlyOne B", ["A5", "A4"])
    incompatible_rule_a = create_incompatible_rule("IA", "Incompatible A", "A2", ["A1", "A3"])
    incompatible_rule_b = create_incompatible_rule("IB", "Incompatible B", "A4", ["A0", "A3"])
    feature_rule_list = create_feature_rule_node_list([onlyone_rule_a, onlyone_rule_b, incompatible_rule_a, incompatible_rule_b])

    feature_str_list_parent = resolve_extends_feature_list(feature_str_list_parent, FeatureStrList(),feature_rule_list).unwrap()
    assert resolve_extends_feature_list(feature_str_list_child, feature_str_list_parent, feature_rule_list).is_err()

def test_extends_empty_parent_multiple_rules_failed_3_4():
    feature_str_list_child = create_feature_str_list(True, ["A1", "A2", "A4", "A5"], ["A2", "A3"])
    feature_str_list_parent = create_feature_str_list(True, [], [])

    onlyone_rule_a = create_only_one_rule("OA", "OnlyOne A", ["A1", "A3"])
    onlyone_rule_b = create_only_one_rule("OB", "OnlyOne B", ["A0", "A4"])
    incompatible_rule_a = create_incompatible_rule("IA", "Incompatible A", "A5", ["A1", "A4"])
    incompatible_rule_b = create_incompatible_rule("IB", "Incompatible B", "A4", ["A0", "A3"])
    feature_rule_list = create_feature_rule_node_list([onlyone_rule_a, onlyone_rule_b, incompatible_rule_a, incompatible_rule_b])

    feature_str_list_parent = resolve_extends_feature_list(feature_str_list_parent, FeatureStrList(),feature_rule_list).unwrap()
    assert resolve_extends_feature_list(feature_str_list_child, feature_str_list_parent, feature_rule_list).is_err()

def test_extends_empty_parent_multiple_rules_failed_4_4():
    feature_str_list_child = create_feature_str_list(True, ["A1", "A2", "A4", "A5"], ["A2", "A3"])
    feature_str_list_parent = create_feature_str_list(True, [], [])

    onlyone_rule_a = create_only_one_rule("OA", "OnlyOne A", ["A1", "A3"])
    onlyone_rule_b = create_only_one_rule("OB", "OnlyOne B", ["A0", "A4"])
    incompatible_rule_a = create_incompatible_rule("IA", "Incompatible A", "A2", ["A1", "A3"])
    incompatible_rule_b = create_incompatible_rule("IB", "Incompatible B", "A4", ["A0", "A5"])
    feature_rule_list = create_feature_rule_node_list([onlyone_rule_a, onlyone_rule_b, incompatible_rule_a, incompatible_rule_b])

    feature_str_list_parent = resolve_extends_feature_list(feature_str_list_parent, FeatureStrList(),feature_rule_list).unwrap()
    assert resolve_extends_feature_list(feature_str_list_child, feature_str_list_parent, feature_rule_list).is_err()

def test_extends_empty_child_no_rule_1():
    feature_str_list_child = create_feature_str_list(False, [], [])
    feature_str_list_parent = create_feature_str_list(False, ["B1", "B2"], ["B2", "B3"])
    
    feature_str_list_parent = resolve_extends_feature_list(feature_str_list_parent, FeatureStrList(),  create_feature_rule_node_list([])).unwrap()
    result = resolve_extends_feature_list(feature_str_list_child, feature_str_list_parent, create_feature_rule_node_list([])).unwrap()

     # Validate result
    assert result.override == False
    assert result.values == set(["B1"])
    assert result.remove_modifiers.values == set()

def test_extends_empty_child_no_rule_2():
    feature_str_list_child = create_feature_str_list(True, [], [])
    feature_str_list_parent = create_feature_str_list(False, ["B1", "B2"], ["B2", "B3"])
    
    feature_str_list_parent = resolve_extends_feature_list(feature_str_list_parent, FeatureStrList(),  create_feature_rule_node_list([])).unwrap()
    result = resolve_extends_feature_list(feature_str_list_child, feature_str_list_parent, create_feature_rule_node_list([])).unwrap()

     # Validate result
    assert result.override == True
    assert result.values == set([])
    assert result.remove_modifiers.values == set()


def test_extends_empty_child_no_rule_3():
    feature_str_list_child = create_feature_str_list(False, [], [])
    feature_str_list_parent = create_feature_str_list(True, ["B1", "B2"], ["B2", "B3"])
    
    feature_str_list_parent = resolve_extends_feature_list(feature_str_list_parent, FeatureStrList(),  create_feature_rule_node_list([])).unwrap()
    result = resolve_extends_feature_list(feature_str_list_child, feature_str_list_parent, create_feature_rule_node_list([])).unwrap()

     # Validate result
    assert result.override == False
    assert result.values == set(["B1"])
    assert result.remove_modifiers.values == set()

def test_extends_empty_child_no_rule_4():
    feature_str_list_child = create_feature_str_list(True, [], [])
    feature_str_list_parent = create_feature_str_list(False, ["B1", "B2"], ["B2", "B3"])
    
    feature_str_list_parent = resolve_extends_feature_list(feature_str_list_parent, FeatureStrList(),  create_feature_rule_node_list([])).unwrap()
    result = resolve_extends_feature_list(feature_str_list_child, feature_str_list_parent, create_feature_rule_node_list([])).unwrap()

     # Validate result
    assert result.override == True
    assert result.values == set([])
    assert result.remove_modifiers.values == set()

def test_extends_empty_child_only_one_rule_1():
    feature_str_list_child = create_feature_str_list(False, [], [])
    feature_str_list_parent = create_feature_str_list(False, ["A1", "A2", "A4", "A5"], ["A2", "A3"])

    onlyone_rule = create_only_one_rule("OA", "OnlyOne A", ["A1", "A3"])
    feature_rule_list = create_feature_rule_node_list([onlyone_rule])

    feature_str_list_parent = resolve_extends_feature_list(feature_str_list_parent, FeatureStrList(),feature_rule_list).unwrap()
    result = resolve_extends_feature_list(feature_str_list_child, feature_str_list_parent, feature_rule_list).unwrap()

     # Validate result
    assert result.override == False
    assert result.values == set(["A1", "A4", "A5"])
    assert result.remove_modifiers.values == set()

def test_extends_empty_child_only_one_rule_2():
    feature_str_list_child = create_feature_str_list(True, [], [])
    feature_str_list_parent = create_feature_str_list(False, ["A1", "A2", "A4", "A5"], ["A2", "A3"])

    onlyone_rule = create_only_one_rule("OA", "OnlyOne A", ["A1", "A3"])
    feature_rule_list = create_feature_rule_node_list([onlyone_rule])

    feature_str_list_parent = resolve_extends_feature_list(feature_str_list_parent, FeatureStrList(),feature_rule_list).unwrap()
    result = resolve_extends_feature_list(feature_str_list_child, feature_str_list_parent, feature_rule_list).unwrap()

     # Validate result
    assert result.override == True
    assert result.values == set([])
    assert result.remove_modifiers.values == set()


def test_extends_empty_child_only_one_rule_3():
    feature_str_list_child = create_feature_str_list(False, [], [])
    feature_str_list_parent = create_feature_str_list(True, ["A1", "A2", "A4", "A5"], ["A2", "A3"])

    onlyone_rule = create_only_one_rule("OA", "OnlyOne A", ["A1", "A3"])
    feature_rule_list = create_feature_rule_node_list([onlyone_rule])

    feature_str_list_parent = resolve_extends_feature_list(feature_str_list_parent, FeatureStrList(),feature_rule_list).unwrap()
    result = resolve_extends_feature_list(feature_str_list_child, feature_str_list_parent, feature_rule_list).unwrap()

     # Validate result
    assert result.override == False
    assert result.values == set(["A1", "A4", "A5"])
    assert result.remove_modifiers.values == set()


def test_extends_empty_child_only_one_rule_4():
    feature_str_list_child = create_feature_str_list(True, [], [])
    feature_str_list_parent = create_feature_str_list(True, ["A1", "A2", "A4", "A5"], ["A2", "A3"])

    onlyone_rule = create_only_one_rule("OA", "OnlyOne A", ["A1", "A3"])
    feature_rule_list = create_feature_rule_node_list([onlyone_rule])

    feature_str_list_parent = resolve_extends_feature_list(feature_str_list_parent, FeatureStrList(),feature_rule_list).unwrap()
    result = resolve_extends_feature_list(feature_str_list_child, feature_str_list_parent, feature_rule_list).unwrap()

     # Validate result
    assert result.override == True
    assert result.values == set([])
    assert result.remove_modifiers.values == set()

def test_extends_empty_child_only_one_rule_failed_1():
    # Child will never be merged because parent will fail
    #feature_str_list_child = create_feature_str_list(False, [], [])
    feature_str_list_parent = create_feature_str_list(False, ["A1", "A2", "A4", "A5"], ["A2", "A3"])

    onlyone_rule = create_only_one_rule("OA", "OnlyOne A", ["A1", "A4"])
    feature_rule_list = create_feature_rule_node_list([onlyone_rule])

    assert resolve_extends_feature_list(feature_str_list_parent, FeatureStrList(),feature_rule_list).is_err()

def test_extends_empty_child_only_one_rule_failed_2():
    # Child will never be merged because parent will fail
    #feature_str_list_child = create_feature_str_list(True, [], [])
    feature_str_list_parent = create_feature_str_list(True, ["A1", "A2", "A4", "A5"], ["A2", "A3"])

    onlyone_rule = create_only_one_rule("OA", "OnlyOne A", ["A1", "A4"])
    feature_rule_list = create_feature_rule_node_list([onlyone_rule])

    assert resolve_extends_feature_list(feature_str_list_parent, FeatureStrList(),feature_rule_list).is_err()

def test_extends_empty_child_incompatible_rule_1():
    feature_str_list_child = create_feature_str_list(False, [], [])
    feature_str_list_parent = create_feature_str_list(False, ["A1", "A2", "A4", "A5"], ["A2", "A3"])

    incompatible_rule = create_incompatible_rule("IA", "Incompatible A", "A0", ["A1", "A3"])
    feature_rule_list = create_feature_rule_node_list([incompatible_rule])

    feature_str_list_parent = resolve_extends_feature_list(feature_str_list_parent, FeatureStrList(),feature_rule_list).unwrap()
    result = resolve_extends_feature_list(feature_str_list_child, feature_str_list_parent, feature_rule_list).unwrap()

    # Validate result
    assert result.override == False
    assert result.values == set(["A1", "A4", "A5"])
    assert result.remove_modifiers.values == set()

def test_extends_empty_child_incompatible_rule_2():
    feature_str_list_child = create_feature_str_list(True, [], [])
    feature_str_list_parent = create_feature_str_list(False, ["A1", "A2", "A4", "A5"], ["A2", "A3"])

    incompatible_rule = create_incompatible_rule("IA", "Incompatible A", "A0", ["A1", "A3"])
    feature_rule_list = create_feature_rule_node_list([incompatible_rule])

    feature_str_list_parent = resolve_extends_feature_list(feature_str_list_parent, FeatureStrList(),feature_rule_list).unwrap()
    result = resolve_extends_feature_list(feature_str_list_child, feature_str_list_parent, feature_rule_list).unwrap()

    # Validate result
    assert result.override == True
    assert result.values == set([])
    assert result.remove_modifiers.values == set()

def test_extends_empty_child_incompatible_rule_3():
    feature_str_list_child = create_feature_str_list(False, [], [])
    feature_str_list_parent = create_feature_str_list(True, ["A1", "A2", "A4", "A5"], ["A2", "A3"])

    incompatible_rule = create_incompatible_rule("IA", "Incompatible A", "A0", ["A1", "A3"])
    feature_rule_list = create_feature_rule_node_list([incompatible_rule])

    feature_str_list_parent = resolve_extends_feature_list(feature_str_list_parent, FeatureStrList(),feature_rule_list).unwrap()
    result = resolve_extends_feature_list(feature_str_list_child, feature_str_list_parent, feature_rule_list).unwrap()

    # Validate result
    assert result.override == False
    assert result.values == set(["A1", "A4", "A5"])
    assert result.remove_modifiers.values == set()

def test_extends_empty_child_incompatible_rule_4():
    feature_str_list_child = create_feature_str_list(True, [], [])
    feature_str_list_parent = create_feature_str_list(True, ["A1", "A2", "A4", "A5"], ["A2", "A3"])

    incompatible_rule = create_incompatible_rule("IA", "Incompatible A", "A0", ["A1", "A3"])
    feature_rule_list = create_feature_rule_node_list([incompatible_rule])

    feature_str_list_parent = resolve_extends_feature_list(feature_str_list_parent, FeatureStrList(),feature_rule_list).unwrap()
    result = resolve_extends_feature_list(feature_str_list_child, feature_str_list_parent, feature_rule_list).unwrap()

    # Validate result
    assert result.override == True
    assert result.values == set([])
    assert result.remove_modifiers.values == set()

def test_extends_empty_child_incompatible_rule_failed_1():
     # Child will never be merged because parent will fail
    #feature_str_list_child = create_feature_str_list(False, [], [])
    feature_str_list_parent = create_feature_str_list(False, ["A1", "A2", "A4", "A5"], ["A2", "A3"])

    incompatible_rule = create_incompatible_rule("IA", "Incompatible A", "A1", ["A2", "A4"])
    feature_rule_list = create_feature_rule_node_list([incompatible_rule])

    assert resolve_extends_feature_list(feature_str_list_parent, FeatureStrList(),feature_rule_list).is_err()

def test_extends_empty_child_incompatible_rule_failed_2():
    # Child will never be merged because parent will fail
    #feature_str_list_child = create_feature_str_list(True, [], [])
    feature_str_list_parent = create_feature_str_list(True, ["A1", "A2", "A4", "A5"], ["A2", "A3"])

    incompatible_rule = create_incompatible_rule("IA", "Incompatible A", "A1", ["A2", "A4"])
    feature_rule_list = create_feature_rule_node_list([incompatible_rule])

    assert resolve_extends_feature_list(feature_str_list_parent, FeatureStrList(),feature_rule_list).is_err()

def test_extends_empty_child_multiple_rules_1():
    feature_str_list_child = create_feature_str_list(False, [], [])
    feature_str_list_parent = create_feature_str_list(False, ["A1", "A2", "A4", "A5"], ["A2", "A3"])

    onlyone_rule_a = create_only_one_rule("OA", "OnlyOne A", ["A1", "A3"])
    onlyone_rule_b = create_only_one_rule("OB", "OnlyOne B", ["A0", "A4"])
    incompatible_rule_a = create_incompatible_rule("IA", "Incompatible A", "A2", ["A1", "A3"])
    incompatible_rule_b = create_incompatible_rule("IB", "Incompatible B", "A4", ["A0", "A3"])
    feature_rule_list = create_feature_rule_node_list([onlyone_rule_a, onlyone_rule_b, incompatible_rule_a, incompatible_rule_b])

    feature_str_list_parent = resolve_extends_feature_list(feature_str_list_parent, FeatureStrList(),feature_rule_list).unwrap()
    result = resolve_extends_feature_list(feature_str_list_child, feature_str_list_parent, feature_rule_list).unwrap()

    # Validate result
    assert result.override == False
    assert result.values == set(["A1", "A4", "A5"])
    assert result.remove_modifiers.values == set()

def test_extends_empty_child_multiple_rules_2():
    feature_str_list_child = create_feature_str_list(True, [], [])
    feature_str_list_parent = create_feature_str_list(False, ["A1", "A2", "A4", "A5"], ["A2", "A3"])

    onlyone_rule_a = create_only_one_rule("OA", "OnlyOne A", ["A1", "A3"])
    onlyone_rule_b = create_only_one_rule("OB", "OnlyOne B", ["A0", "A4"])
    incompatible_rule_a = create_incompatible_rule("IA", "Incompatible A", "A2", ["A1", "A3"])
    incompatible_rule_b = create_incompatible_rule("IB", "Incompatible B", "A4", ["A0", "A3"])
    feature_rule_list = create_feature_rule_node_list([onlyone_rule_a, onlyone_rule_b, incompatible_rule_a, incompatible_rule_b])

    feature_str_list_parent = resolve_extends_feature_list(feature_str_list_parent, FeatureStrList(),feature_rule_list).unwrap()
    result = resolve_extends_feature_list(feature_str_list_child, feature_str_list_parent, feature_rule_list).unwrap()

    # Validate result
    assert result.override == True
    assert result.values == set([])
    assert result.remove_modifiers.values == set()

def test_extends_empty_child_multiple_rules_3():
    feature_str_list_child = create_feature_str_list(False, [], [])
    feature_str_list_parent = create_feature_str_list(True, ["A1", "A2", "A4", "A5"], ["A2", "A3"])

    onlyone_rule_a = create_only_one_rule("OA", "OnlyOne A", ["A1", "A3"])
    onlyone_rule_b = create_only_one_rule("OB", "OnlyOne B", ["A0", "A4"])
    incompatible_rule_a = create_incompatible_rule("IA", "Incompatible A", "A2", ["A1", "A3"])
    incompatible_rule_b = create_incompatible_rule("IB", "Incompatible B", "A4", ["A0", "A3"])
    feature_rule_list = create_feature_rule_node_list([onlyone_rule_a, onlyone_rule_b, incompatible_rule_a, incompatible_rule_b])

    feature_str_list_parent = resolve_extends_feature_list(feature_str_list_parent, FeatureStrList(),feature_rule_list).unwrap()
    result = resolve_extends_feature_list(feature_str_list_child, feature_str_list_parent, feature_rule_list).unwrap()

    # Validate result
    assert result.override == False
    assert result.values == set(["A1", "A4", "A5"])
    assert result.remove_modifiers.values == set()

def test_extends_empty_child_multiple_rules_4():
    feature_str_list_child = create_feature_str_list(True, [], [])
    feature_str_list_parent = create_feature_str_list(True, ["A1", "A2", "A4", "A5"], ["A2", "A3"])

    onlyone_rule_a = create_only_one_rule("OA", "OnlyOne A", ["A1", "A3"])
    onlyone_rule_b = create_only_one_rule("OB", "OnlyOne B", ["A0", "A4"])
    incompatible_rule_a = create_incompatible_rule("IA", "Incompatible A", "A2", ["A1", "A3"])
    incompatible_rule_b = create_incompatible_rule("IB", "Incompatible B", "A4", ["A0", "A3"])
    feature_rule_list = create_feature_rule_node_list([onlyone_rule_a, onlyone_rule_b, incompatible_rule_a, incompatible_rule_b])

    feature_str_list_parent = resolve_extends_feature_list(feature_str_list_parent, FeatureStrList(),feature_rule_list).unwrap()
    result = resolve_extends_feature_list(feature_str_list_child, feature_str_list_parent, feature_rule_list).unwrap()

    # Validate result
    assert result.override == True
    assert result.values == set([])
    assert result.remove_modifiers.values == set()

def test_extends_empty_child_multiple_rules_failed_1_1():
    # Child will never be merged because parent will fail
    # feature_str_list_child = create_feature_str_list(False, [], [])
    feature_str_list_parent = create_feature_str_list(False, ["A1", "A2", "A4", "A5"], ["A2", "A3"])

    onlyone_rule_a = create_only_one_rule("OA", "OnlyOne A", ["A1", "A5"])
    onlyone_rule_b = create_only_one_rule("OB", "OnlyOne B", ["A0", "A4"])
    incompatible_rule_a = create_incompatible_rule("IA", "Incompatible A", "A2", ["A1", "A3"])
    incompatible_rule_b = create_incompatible_rule("IB", "Incompatible B", "A4", ["A0", "A3"])
    feature_rule_list = create_feature_rule_node_list([onlyone_rule_a, onlyone_rule_b, incompatible_rule_a, incompatible_rule_b])

    assert resolve_extends_feature_list(feature_str_list_parent, FeatureStrList(),feature_rule_list).is_err()


def test_extends_empty_child_multiple_rules_failed_2_1():
    # Child will never be merged because parent will fail
    #feature_str_list_child = create_feature_str_list(False, [], [])
    feature_str_list_parent = create_feature_str_list(False, ["A1", "A2", "A4", "A5"], ["A2", "A3"])

    onlyone_rule_a = create_only_one_rule("OA", "OnlyOne A", ["A1", "A3"])
    onlyone_rule_b = create_only_one_rule("OB", "OnlyOne B", ["A5", "A4"])
    incompatible_rule_a = create_incompatible_rule("IA", "Incompatible A", "A2", ["A1", "A3"])
    incompatible_rule_b = create_incompatible_rule("IB", "Incompatible B", "A4", ["A0", "A3"])
    feature_rule_list = create_feature_rule_node_list([onlyone_rule_a, onlyone_rule_b, incompatible_rule_a, incompatible_rule_b])

    assert resolve_extends_feature_list(feature_str_list_parent, FeatureStrList(),feature_rule_list).is_err()

def test_extends_empty_child_multiple_rules_failed_3_1():
    # Child will never be merged because parent will fail
    #feature_str_list_child = create_feature_str_list(False, [], [])
    feature_str_list_parent = create_feature_str_list(False, ["A1", "A2", "A4", "A5"], ["A2", "A3"])

    onlyone_rule_a = create_only_one_rule("OA", "OnlyOne A", ["A1", "A3"])
    onlyone_rule_b = create_only_one_rule("OB", "OnlyOne B", ["A0", "A4"])
    incompatible_rule_a = create_incompatible_rule("IA", "Incompatible A", "A5", ["A1", "A4"])
    incompatible_rule_b = create_incompatible_rule("IB", "Incompatible B", "A4", ["A0", "A3"])
    feature_rule_list = create_feature_rule_node_list([onlyone_rule_a, onlyone_rule_b, incompatible_rule_a, incompatible_rule_b])

    assert resolve_extends_feature_list(feature_str_list_parent, FeatureStrList(),feature_rule_list).is_err()

def test_extends_empty_child_multiple_rules_failed_4_1():
    # Child will never be merged because parent will fail
    #feature_str_list_child = create_feature_str_list(False, [], [])
    feature_str_list_parent = create_feature_str_list(False, ["A1", "A2", "A4", "A5"], ["A2", "A3"])

    onlyone_rule_a = create_only_one_rule("OA", "OnlyOne A", ["A1", "A3"])
    onlyone_rule_b = create_only_one_rule("OB", "OnlyOne B", ["A0", "A4"])
    incompatible_rule_a = create_incompatible_rule("IA", "Incompatible A", "A2", ["A1", "A3"])
    incompatible_rule_b = create_incompatible_rule("IB", "Incompatible B", "A4", ["A0", "A5"])
    feature_rule_list = create_feature_rule_node_list([onlyone_rule_a, onlyone_rule_b, incompatible_rule_a, incompatible_rule_b])

    assert resolve_extends_feature_list(feature_str_list_parent, FeatureStrList(),feature_rule_list).is_err()

def test_extends_empty_child_multiple_rules_failed_1_2():
    # Child will never be merged because parent will fail
    # feature_str_list_child = create_feature_str_list(False, [], [])
    feature_str_list_parent = create_feature_str_list(True, ["A1", "A2", "A4", "A5"], ["A2", "A3"])

    onlyone_rule_a = create_only_one_rule("OA", "OnlyOne A", ["A1", "A5"])
    onlyone_rule_b = create_only_one_rule("OB", "OnlyOne B", ["A0", "A4"])
    incompatible_rule_a = create_incompatible_rule("IA", "Incompatible A", "A2", ["A1", "A3"])
    incompatible_rule_b = create_incompatible_rule("IB", "Incompatible B", "A4", ["A0", "A3"])
    feature_rule_list = create_feature_rule_node_list([onlyone_rule_a, onlyone_rule_b, incompatible_rule_a, incompatible_rule_b])

    assert resolve_extends_feature_list(feature_str_list_parent, FeatureStrList(),feature_rule_list).is_err()


def test_extends_empty_child_multiple_rules_failed_2_2():
    # Child will never be merged because parent will fail
    #feature_str_list_child = create_feature_str_list(False, [], [])
    feature_str_list_parent = create_feature_str_list(True, ["A1", "A2", "A4", "A5"], ["A2", "A3"])

    onlyone_rule_a = create_only_one_rule("OA", "OnlyOne A", ["A1", "A3"])
    onlyone_rule_b = create_only_one_rule("OB", "OnlyOne B", ["A5", "A4"])
    incompatible_rule_a = create_incompatible_rule("IA", "Incompatible A", "A2", ["A1", "A3"])
    incompatible_rule_b = create_incompatible_rule("IB", "Incompatible B", "A4", ["A0", "A3"])
    feature_rule_list = create_feature_rule_node_list([onlyone_rule_a, onlyone_rule_b, incompatible_rule_a, incompatible_rule_b])

    assert resolve_extends_feature_list(feature_str_list_parent, FeatureStrList(),feature_rule_list).is_err()

def test_extends_empty_child_multiple_rules_failed_3_2():
    # Child will never be merged because parent will fail
    #feature_str_list_child = create_feature_str_list(False, [], [])
    feature_str_list_parent = create_feature_str_list(True, ["A1", "A2", "A4", "A5"], ["A2", "A3"])

    onlyone_rule_a = create_only_one_rule("OA", "OnlyOne A", ["A1", "A3"])
    onlyone_rule_b = create_only_one_rule("OB", "OnlyOne B", ["A0", "A4"])
    incompatible_rule_a = create_incompatible_rule("IA", "Incompatible A", "A5", ["A1", "A4"])
    incompatible_rule_b = create_incompatible_rule("IB", "Incompatible B", "A4", ["A0", "A3"])
    feature_rule_list = create_feature_rule_node_list([onlyone_rule_a, onlyone_rule_b, incompatible_rule_a, incompatible_rule_b])

    assert resolve_extends_feature_list(feature_str_list_parent, FeatureStrList(),feature_rule_list).is_err()

def test_extends_empty_child_multiple_rules_failed_4_2():
    # Child will never be merged because parent will fail
    #feature_str_list_child = create_feature_str_list(False, [], [])
    feature_str_list_parent = create_feature_str_list(True, ["A1", "A2", "A4", "A5"], ["A2", "A3"])

    onlyone_rule_a = create_only_one_rule("OA", "OnlyOne A", ["A1", "A3"])
    onlyone_rule_b = create_only_one_rule("OB", "OnlyOne B", ["A0", "A4"])
    incompatible_rule_a = create_incompatible_rule("IA", "Incompatible A", "A2", ["A1", "A3"])
    incompatible_rule_b = create_incompatible_rule("IB", "Incompatible B", "A4", ["A0", "A5"])
    feature_rule_list = create_feature_rule_node_list([onlyone_rule_a, onlyone_rule_b, incompatible_rule_a, incompatible_rule_b])

    assert resolve_extends_feature_list(feature_str_list_parent, FeatureStrList(),feature_rule_list).is_err()

def test_extends_no_rule_1():
    
    feature_str_list_child = create_feature_str_list(False, ["A1", "A2"], ["A2", "A3"])
    feature_str_list_parent = create_feature_str_list(False, ["B1", "B2"], ["B2", "B3"])

    feature_str_list_parent = resolve_extends_feature_list(feature_str_list_parent, FeatureStrList(),  create_feature_rule_node_list([])).unwrap()
    result = resolve_extends_feature_list(feature_str_list_child, feature_str_list_parent, create_feature_rule_node_list([])).unwrap()

    # Validate result
    assert result.override == False
    assert result.values == set(["B1", "A1"])
    assert result.remove_modifiers.values == set()

def test_extends_no_rule_2():
    feature_str_list_child = create_feature_str_list(True, ["A1", "A2"], ["A2", "A3"])
    feature_str_list_parent = create_feature_str_list(False, ["B1", "B2"], ["B2", "B3"])

    feature_str_list_parent = resolve_extends_feature_list(feature_str_list_parent, FeatureStrList(),  create_feature_rule_node_list([])).unwrap()
    result = resolve_extends_feature_list(feature_str_list_child, feature_str_list_parent, create_feature_rule_node_list([])).unwrap()

    # Validate result
    assert result.override == True
    assert result.values == set(["A1"])
    assert result.remove_modifiers.values == set()

def test_extends_no_rule_3():
    feature_str_list_child = create_feature_str_list(False, ["A1", "A2"], ["A2", "A3"])
    feature_str_list_parent = create_feature_str_list(True, ["B1", "B2"], ["B2", "B3"])

    feature_str_list_parent = resolve_extends_feature_list(feature_str_list_parent, FeatureStrList(),  create_feature_rule_node_list([])).unwrap()
    result = resolve_extends_feature_list(feature_str_list_child, feature_str_list_parent, create_feature_rule_node_list([])).unwrap()

    # Validate result
    assert result.override == False
    assert result.values == set(["B1", "A1"])
    assert result.remove_modifiers.values == set()


def test_extends_no_rule_4():
    feature_str_list_child = create_feature_str_list(True, ["A1", "A2"], ["A2", "A3"])
    feature_str_list_parent = create_feature_str_list(True, ["B1", "B2"], ["B2", "B3"])

    feature_str_list_parent = resolve_extends_feature_list(feature_str_list_parent, FeatureStrList(),  create_feature_rule_node_list([])).unwrap()
    result = resolve_extends_feature_list(feature_str_list_child, feature_str_list_parent, create_feature_rule_node_list([])).unwrap()

    # Validate result
    assert result.override == True
    assert result.values == set(["A1"])
    assert result.remove_modifiers.values == set()

def test_extends_only_one_rule_1():
    feature_str_list_child = create_feature_str_list(False, ["A1", "A2"], ["A2", "A3"])
    feature_str_list_parent = create_feature_str_list(False, ["B1", "B2"], ["B2", "B3"])

    onlyone_rule = create_only_one_rule("OA", "OnlyOne A", ["A1", "A3"])
    feature_rule_list = create_feature_rule_node_list([onlyone_rule])

    feature_str_list_parent = resolve_extends_feature_list(feature_str_list_parent, FeatureStrList(),  feature_rule_list).unwrap()
    result = resolve_extends_feature_list(feature_str_list_child, feature_str_list_parent, feature_rule_list).unwrap()

    # Validate result
    assert result.override == False
    assert result.values == set(["B1", "A1"])
    assert result.remove_modifiers.values == set()

def test_extends_only_one_rule_2():
    feature_str_list_child = create_feature_str_list(True, ["A1", "A2"], ["A2", "A3"])
    feature_str_list_parent = create_feature_str_list(False, ["B1", "B2"], ["B2", "B3"])

    onlyone_rule = create_only_one_rule("OA", "OnlyOne A", ["A1", "A3"])
    feature_rule_list = create_feature_rule_node_list([onlyone_rule])

    feature_str_list_parent = resolve_extends_feature_list(feature_str_list_parent, FeatureStrList(),  feature_rule_list).unwrap()
    result = resolve_extends_feature_list(feature_str_list_child, feature_str_list_parent, feature_rule_list).unwrap()

    # Validate result
    assert result.override == True
    assert result.values == set(["A1"])
    assert result.remove_modifiers.values == set()

def test_extends_only_one_rule_3():
    feature_str_list_child = create_feature_str_list(False, ["A1", "A2"], ["A2", "A3"])
    feature_str_list_parent = create_feature_str_list(True, ["B1", "B2"], ["B2", "B3"])

    onlyone_rule = create_only_one_rule("OA", "OnlyOne A", ["A1", "A3"])
    feature_rule_list = create_feature_rule_node_list([onlyone_rule])

    feature_str_list_parent = resolve_extends_feature_list(feature_str_list_parent, FeatureStrList(),  feature_rule_list).unwrap()
    result = resolve_extends_feature_list(feature_str_list_child, feature_str_list_parent, feature_rule_list).unwrap()

    # Validate result
    assert result.override == False
    assert result.values == set(["B1", "A1"])
    assert result.remove_modifiers.values == set()

def test_extends_only_one_rule_4():
    feature_str_list_child = create_feature_str_list(True, ["A1", "A2"], ["A2", "A3"])
    feature_str_list_parent = create_feature_str_list(True, ["B1", "B2"], ["B2", "B3"])

    onlyone_rule = create_only_one_rule("OA", "OnlyOne A", ["A1", "A3"])
    feature_rule_list = create_feature_rule_node_list([onlyone_rule])

    feature_str_list_parent = resolve_extends_feature_list(feature_str_list_parent, FeatureStrList(),  feature_rule_list).unwrap()
    result = resolve_extends_feature_list(feature_str_list_child, feature_str_list_parent, feature_rule_list).unwrap()

    # Validate result
    assert result.override == True
    assert result.values == set(["A1"])
    assert result.remove_modifiers.values == set()

def test_extends_only_one_rule_failed_1():
    feature_str_list_child = create_feature_str_list(False, ["A1", "A2", "A4"], ["A2", "A3"])
    feature_str_list_parent = create_feature_str_list(False, ["B1", "B2", "B5"], ["B2", "B3"])

    onlyone_rule = create_only_one_rule("OA", "OnlyOne A", ["A1", "A4"])
    feature_rule_list = create_feature_rule_node_list([onlyone_rule])

    feature_str_list_parent = resolve_extends_feature_list(feature_str_list_parent, FeatureStrList(),  feature_rule_list).unwrap()
    assert resolve_extends_feature_list(feature_str_list_child, feature_str_list_parent, feature_rule_list).is_err()

def test_extends_only_one_rule_failed_2():
    feature_str_list_child = create_feature_str_list(True, ["A1", "A2", "A4"], ["A2", "A3"])
    feature_str_list_parent = create_feature_str_list(False, ["B1", "B2", "B5"], ["B2", "B3"])

    onlyone_rule = create_only_one_rule("OA", "OnlyOne A", ["A1", "A4"])
    feature_rule_list = create_feature_rule_node_list([onlyone_rule])

    feature_str_list_parent = resolve_extends_feature_list(feature_str_list_parent, FeatureStrList(),  feature_rule_list).unwrap()
    assert resolve_extends_feature_list(feature_str_list_child, feature_str_list_parent, feature_rule_list).is_err()

def test_extends_only_one_rule_failed_3():
    feature_str_list_child = create_feature_str_list(False, ["A1", "A2", "A4"], ["A2", "A3"])
    feature_str_list_parent = create_feature_str_list(True, ["B1", "B2", "B5"], ["B2", "B3"])

    onlyone_rule = create_only_one_rule("OA", "OnlyOne A", ["A1", "A4"])
    feature_rule_list = create_feature_rule_node_list([onlyone_rule])

    feature_str_list_parent = resolve_extends_feature_list(feature_str_list_parent, FeatureStrList(),  feature_rule_list).unwrap()
    assert resolve_extends_feature_list(feature_str_list_child, feature_str_list_parent, feature_rule_list).is_err()

def test_extends_only_one_rule_failed_4():
    feature_str_list_child = create_feature_str_list(True, ["A1", "A2", "A4"], ["A2", "A3"])
    feature_str_list_parent = create_feature_str_list(True, ["B1", "B2", "B5"], ["B2", "B3"])

    onlyone_rule = create_only_one_rule("OA", "OnlyOne A", ["A1", "A4"])
    feature_rule_list = create_feature_rule_node_list([onlyone_rule])

    feature_str_list_parent = resolve_extends_feature_list(feature_str_list_parent, FeatureStrList(),  feature_rule_list).unwrap()
    assert resolve_extends_feature_list(feature_str_list_child, feature_str_list_parent, feature_rule_list).is_err()

def test_extends_only_one_rule_failed_5():
    # Child will never be merged because parent will fail
    #feature_str_list_child = create_feature_str_list(False, ["A1", "A2", "A4"], ["A2", "A3"])
    feature_str_list_parent = create_feature_str_list(False, ["B1", "B2", "B5"], ["B2", "B3"])

    onlyone_rule = create_only_one_rule("OA", "OnlyOne A", ["B1", "B5"])
    feature_rule_list = create_feature_rule_node_list([onlyone_rule])

    assert resolve_extends_feature_list(feature_str_list_parent, FeatureStrList(),  feature_rule_list).is_err()

def test_extends_only_one_rule_failed_6():
    # Child will never be merged because parent will fail
    #feature_str_list_child = create_feature_str_list(False, ["A1", "A2", "A4"], ["A2", "A3"])
    feature_str_list_parent = create_feature_str_list(True, ["B1", "B2", "B5"], ["B2", "B3"])

    onlyone_rule = create_only_one_rule("OA", "OnlyOne A", ["B1", "B5"])
    feature_rule_list = create_feature_rule_node_list([onlyone_rule])

    assert resolve_extends_feature_list(feature_str_list_parent, FeatureStrList(),  feature_rule_list).is_err()
def test_extends_incompatible_rule_1():
    feature_str_list_child = create_feature_str_list(False, ["A1", "A2"], ["A2", "A3"])
    feature_str_list_parent = create_feature_str_list(False, ["B1", "B2"], ["B2", "B3"])

    incompatible_rule = create_incompatible_rule("IA", "Incompatible A"," A0", ["A1", "A3"])
    feature_rule_list = create_feature_rule_node_list([incompatible_rule])

    feature_str_list_parent = resolve_extends_feature_list(feature_str_list_parent, FeatureStrList(),  feature_rule_list).unwrap()
    result = resolve_extends_feature_list(feature_str_list_child, feature_str_list_parent, feature_rule_list).unwrap()

    # Validate result
    assert result.override == False
    assert result.values == set(["B1", "A1"])
    assert result.remove_modifiers.values == set()

def test_extends_incompatible_rule_2():
    feature_str_list_child = create_feature_str_list(True, ["A1", "A2"], ["A2", "A3"])
    feature_str_list_parent = create_feature_str_list(False, ["B1", "B2"], ["B2", "B3"])

    incompatible_rule = create_incompatible_rule("IA", "Incompatible A"," A0", ["A1", "A3"])
    feature_rule_list = create_feature_rule_node_list([incompatible_rule])

    feature_str_list_parent = resolve_extends_feature_list(feature_str_list_parent, FeatureStrList(),  feature_rule_list).unwrap()
    result = resolve_extends_feature_list(feature_str_list_child, feature_str_list_parent, feature_rule_list).unwrap()

    # Validate result
    assert result.override == True
    assert result.values == set(["A1"])
    assert result.remove_modifiers.values == set()

def test_extends_incompatible_rule_3():
    feature_str_list_child = create_feature_str_list(False, ["A1", "A2"], ["A2", "A3"])
    feature_str_list_parent = create_feature_str_list(True, ["B1", "B2"], ["B2", "B3"])

    incompatible_rule = create_incompatible_rule("IA", "Incompatible A"," A0", ["A1", "A3"])
    feature_rule_list = create_feature_rule_node_list([incompatible_rule])

    feature_str_list_parent = resolve_extends_feature_list(feature_str_list_parent, FeatureStrList(),  feature_rule_list).unwrap()
    result = resolve_extends_feature_list(feature_str_list_child, feature_str_list_parent, feature_rule_list).unwrap()

    # Validate result
    assert result.override == False
    assert result.values == set(["B1", "A1"])
    assert result.remove_modifiers.values == set()

def test_extends_incompatible_rule_4():
    feature_str_list_child = create_feature_str_list(True, ["A1", "A2"], ["A2", "A3"])
    feature_str_list_parent = create_feature_str_list(True, ["B1", "B2"], ["B2", "B3"])

    incompatible_rule = create_incompatible_rule("IA", "Incompatible A"," A0", ["A1", "A3"])
    feature_rule_list = create_feature_rule_node_list([incompatible_rule])

    feature_str_list_parent = resolve_extends_feature_list(feature_str_list_parent, FeatureStrList(),  feature_rule_list).unwrap()
    result = resolve_extends_feature_list(feature_str_list_child, feature_str_list_parent, feature_rule_list).unwrap()

    # Validate result
    assert result.override == True
    assert result.values == set(["A1"])
    assert result.remove_modifiers.values == set()


def test_extends_incompatible_rule_failed_1():
    feature_str_list_child = create_feature_str_list(False, ["A1", "A2", "A5"], ["A2", "A3"])
    feature_str_list_parent = create_feature_str_list(False, ["B1", "B2"], ["B2", "B3"])

    incompatible_rule = create_incompatible_rule("IA", "Incompatible A","A1", ["A2", "A5"])
    feature_rule_list = create_feature_rule_node_list([incompatible_rule])

    feature_str_list_parent = resolve_extends_feature_list(feature_str_list_parent, FeatureStrList(),  feature_rule_list).unwrap()
    assert resolve_extends_feature_list(feature_str_list_child, feature_str_list_parent, feature_rule_list).is_err()


def test_extends_incompatible_rule_failed_2():
    feature_str_list_child = create_feature_str_list(True, ["A1", "A2", "A5"], ["A2", "A3"])
    feature_str_list_parent = create_feature_str_list(False, ["B1", "B2"], ["B2", "B3"])

    incompatible_rule = create_incompatible_rule("IA", "Incompatible A","A1", ["A2", "A5"])
    feature_rule_list = create_feature_rule_node_list([incompatible_rule])

    feature_str_list_parent = resolve_extends_feature_list(feature_str_list_parent, FeatureStrList(),  feature_rule_list).unwrap()
    assert resolve_extends_feature_list(feature_str_list_child, feature_str_list_parent, feature_rule_list).is_err()

def test_extends_incompatible_rule_failed_3():
    feature_str_list_child = create_feature_str_list(False, ["A1", "A2", "A5"], ["A2", "A3"])
    feature_str_list_parent = create_feature_str_list(True, ["B1", "B2"], ["B2", "B3"])

    incompatible_rule = create_incompatible_rule("IA", "Incompatible A","A1", ["A2", "A5"])
    feature_rule_list = create_feature_rule_node_list([incompatible_rule])

    feature_str_list_parent = resolve_extends_feature_list(feature_str_list_parent, FeatureStrList(),  feature_rule_list).unwrap()
    assert resolve_extends_feature_list(feature_str_list_child, feature_str_list_parent, feature_rule_list).is_err()

def test_extends_incompatible_rule_failed_4():
    feature_str_list_child = create_feature_str_list(True, ["A1", "A2", "A5"], ["A2", "A3"])
    feature_str_list_parent = create_feature_str_list(True, ["B1", "B2"], ["B2", "B3"])

    incompatible_rule = create_incompatible_rule("IA", "Incompatible A","A1", ["A2", "A5"])
    feature_rule_list = create_feature_rule_node_list([incompatible_rule])

    feature_str_list_parent = resolve_extends_feature_list(feature_str_list_parent, FeatureStrList(),  feature_rule_list).unwrap()
    assert resolve_extends_feature_list(feature_str_list_child, feature_str_list_parent, feature_rule_list).is_err()

def test_extends_incompatible_rule_failed_5():
    # Child will never be merged because parent will fail
    # feature_str_list_child = create_feature_str_list(False, ["A1", "A2", "A3"], ["A2", "A3"])
    feature_str_list_parent = create_feature_str_list(False, ["B1", "B2", "B5"], ["B2", "B3"])

    incompatible_rule = create_incompatible_rule("IA", "Incompatible A","B1", ["A2", "B5"])
    feature_rule_list = create_feature_rule_node_list([incompatible_rule])

    assert resolve_extends_feature_list(feature_str_list_parent, FeatureStrList(),  feature_rule_list).is_err()

def test_extends_incompatible_rule_failed_6():
    # Child will never be merged because parent will fail
    # feature_str_list_child = create_feature_str_list(False, ["A1", "A2", "A3"], ["A2", "A3"])
    feature_str_list_parent = create_feature_str_list(True, ["B1", "B2", "B5"], ["B2", "B3"])

    incompatible_rule = create_incompatible_rule("IA", "Incompatible A","B1", ["A2", "B5"])
    feature_rule_list = create_feature_rule_node_list([incompatible_rule])

    assert resolve_extends_feature_list(feature_str_list_parent, FeatureStrList(),  feature_rule_list).is_err()

def test_extends_multiple_rules_1():
    # This test validates that rules are applied
    # A1 in the child must replace B1 in the parent because of the only one rule
    # Also ensure the incompatible rule is valid:
    #  - IA test that the replacement of only one rule is applied before checking incompatible rules
    #  - IB test that after the replacement of only one rule, the incompatible rule is applied to the resulting list after only one rules are applied

    feature_str_list_child = create_feature_str_list(False, ["A1", "A2", "A4", "A5"], ["A2", "A3"])
    feature_str_list_parent = create_feature_str_list(False, ["B1", "B2", "B4", "B5"], ["B2", "B3"])

    onlyone_rule_a = create_only_one_rule("OA", "OnlyOne A", ["A1", "B1"])
    onlyone_rule_b = create_only_one_rule("OB", "OnlyOne B", ["B5", "A4"])
    incompatible_rule_a = create_incompatible_rule("IA", "Incompatible A", "A1", ["B1"])
    incompatible_rule_b = create_incompatible_rule("IB", "Incompatible B", "B1", ["A4"])
    feature_rule_list = create_feature_rule_node_list([onlyone_rule_a, onlyone_rule_b, incompatible_rule_a, incompatible_rule_b])

    feature_str_list_parent = resolve_extends_feature_list(feature_str_list_parent, FeatureStrList(),feature_rule_list).unwrap()
    result = resolve_extends_feature_list(feature_str_list_child, feature_str_list_parent, feature_rule_list).unwrap()

    # Validate result
    assert result.override == False
    assert result.values == set(["A1", "A4", "A5", "B4"])
    assert result.remove_modifiers.values == set()

def test_extends_multiple_rules_2():
    # This test validates that rules are applied
    # Parent is ignored because the child has override set to True
    feature_str_list_child = create_feature_str_list(True, ["A1", "A2", "A4", "A5"], ["A2", "A3"])
    feature_str_list_parent = create_feature_str_list(False, ["B1", "B2", "B4", "B5"], ["B2", "B3"])

    onlyone_rule_a = create_only_one_rule("OA", "OnlyOne A", ["A1", "B1"])
    onlyone_rule_b = create_only_one_rule("OB", "OnlyOne B", ["B5", "A4"])
    incompatible_rule_a = create_incompatible_rule("IA", "Incompatible A", "A1", ["B1"])
    incompatible_rule_b = create_incompatible_rule("IB", "Incompatible B", "B1", ["A4"])
    feature_rule_list = create_feature_rule_node_list([onlyone_rule_a, onlyone_rule_b, incompatible_rule_a, incompatible_rule_b])

    feature_str_list_parent = resolve_extends_feature_list(feature_str_list_parent, FeatureStrList(),feature_rule_list).unwrap()
    result = resolve_extends_feature_list(feature_str_list_child, feature_str_list_parent, feature_rule_list).unwrap()

    # Validate result
    assert result.override == True
    assert result.values == set(["A1", "A4", "A5"])
    assert result.remove_modifiers.values == set()

def test_extends_multiple_rules_3():
    # This test validates that rules are applied
    # A1 in the child must replace B1 in the parent because of the only one rule
    # Also ensure the incompatible rule is valid:
    #  - IA test that the replacement of only one rule is applied before checking incompatible rules
    #  - IB test that after the replacement of only one rule, the incompatible rule is applied to the resulting list after only one rules are applied
    feature_str_list_child = create_feature_str_list(False, ["A1", "A2", "A4", "A5"], ["A2", "A3"])
    feature_str_list_parent = create_feature_str_list(True, ["B1", "B2", "B4", "B5"], ["B2", "B3"])

    onlyone_rule_a = create_only_one_rule("OA", "OnlyOne A", ["A1", "B1"])
    onlyone_rule_b = create_only_one_rule("OB", "OnlyOne B", ["B5", "A4"])
    incompatible_rule_a = create_incompatible_rule("IA", "Incompatible A", "A1", ["B1"])
    incompatible_rule_b = create_incompatible_rule("IB", "Incompatible B", "B1", ["A4"])
    feature_rule_list = create_feature_rule_node_list([onlyone_rule_a, onlyone_rule_b, incompatible_rule_a, incompatible_rule_b])

    feature_str_list_parent = resolve_extends_feature_list(feature_str_list_parent, FeatureStrList(),feature_rule_list).unwrap()
    result = resolve_extends_feature_list(feature_str_list_child, feature_str_list_parent, feature_rule_list).unwrap()

    # Validate result
    assert result.override == False
    assert result.values == set(["A1", "A4", "A5", "B4"])
    assert result.remove_modifiers.values == set()

def test_extends_multiple_rules_4():
    # This test validates that rules are applied
    # Parent is ignored because the child has override set to True
    feature_str_list_child = create_feature_str_list(True, ["A1", "A2", "A4", "A5"], ["A2", "A3"])
    feature_str_list_parent = create_feature_str_list(True, ["B1", "B2", "B4", "B5"], ["B2", "B3"])

    onlyone_rule_a = create_only_one_rule("OA", "OnlyOne A", ["A1", "B1"])
    onlyone_rule_b = create_only_one_rule("OB", "OnlyOne B", ["B5", "A4"])
    incompatible_rule_a = create_incompatible_rule("IA", "Incompatible A", "A1", ["B1"])
    incompatible_rule_b = create_incompatible_rule("IB", "Incompatible B", "B1", ["A4"])
    feature_rule_list = create_feature_rule_node_list([onlyone_rule_a, onlyone_rule_b, incompatible_rule_a, incompatible_rule_b])

    feature_str_list_parent = resolve_extends_feature_list(feature_str_list_parent, FeatureStrList(),feature_rule_list).unwrap()
    result = resolve_extends_feature_list(feature_str_list_child, feature_str_list_parent, feature_rule_list).unwrap()

    # Validate result
    assert result.override == True
    assert result.values == set(["A1", "A4", "A5"])
    assert result.remove_modifiers.values == set()

def test_extends_multiple_rules_failed_1():
    # This test validates that rules are applied
    # A1 in the child must replace B1 in the parent because of the only one rule
    # Also ensure the incompatible rule trigger the invalid result:
    #  - B4 and A1 are incompatible, so the result should be an error
    feature_str_list_child = create_feature_str_list(False, ["A1", "A2", "A4", "A5"], ["A2", "A3"])
    feature_str_list_parent = create_feature_str_list(False, ["B1", "B2", "B4", "B5"], ["B2", "B3"])

    onlyone_rule_a = create_only_one_rule("OA", "OnlyOne A", ["A1", "B1"])
    onlyone_rule_b = create_only_one_rule("OB", "OnlyOne B", ["B5", "A4"])
    incompatible_rule_a = create_incompatible_rule("IA", "Incompatible A", "B4", ["A1"])
    incompatible_rule_b = create_incompatible_rule("IB", "Incompatible B", "B1", ["A4"])
    feature_rule_list = create_feature_rule_node_list([onlyone_rule_a, onlyone_rule_b, incompatible_rule_a, incompatible_rule_b])

    feature_str_list_parent = resolve_extends_feature_list(feature_str_list_parent, FeatureStrList(),feature_rule_list).unwrap()
    assert resolve_extends_feature_list(feature_str_list_child, feature_str_list_parent, feature_rule_list).is_err()

def test_extends_multiple_rules_failed_2():
    # This test validates that rules are applied
    # A1 in the child must replace B1 in the parent because of the only one rule
    # Also ensure the incompatible rule trigger the invalid result:
    #  - B4 and A1 are incompatible, so the result should be an error
    feature_str_list_child = create_feature_str_list(False, ["A1", "A2", "A4", "A5"], ["A2", "A3"])
    feature_str_list_parent = create_feature_str_list(True, ["B1", "B2", "B4", "B5"], ["B2", "B3"])

    onlyone_rule_a = create_only_one_rule("OA", "OnlyOne A", ["A1", "B1"])
    onlyone_rule_b = create_only_one_rule("OB", "OnlyOne B", ["B5", "A4"])
    incompatible_rule_a = create_incompatible_rule("IA", "Incompatible A", "B4", ["A1"])
    incompatible_rule_b = create_incompatible_rule("IB", "Incompatible B", "B1", ["A4"])
    feature_rule_list = create_feature_rule_node_list([onlyone_rule_a, onlyone_rule_b, incompatible_rule_a, incompatible_rule_b])

    feature_str_list_parent = resolve_extends_feature_list(feature_str_list_parent, FeatureStrList(),feature_rule_list).unwrap()
    assert resolve_extends_feature_list(feature_str_list_child, feature_str_list_parent, feature_rule_list).is_err()


def test_extends_multiple_levels_1():
    # level 0
    # features: A1, A2, A3, A4, A5
    # level 1:
    # features: B1, B2, B3, B4, B5
    # level 2:
    # features: C1, C2, C3, C4, C5
    feature_str_list_level_0 = create_feature_str_list(False, ["A1", "A2", "A3", "A4", "A5"], ["A2", "A3"])
    feature_str_list_level_1 = create_feature_str_list(False, ["B1", "B2", "B3", "B4", "B5"], ["B2", "B3", "A5"])
    feature_str_list_level_2 = create_feature_str_list(False, ["C1", "C2", "C3", "C4", "C5"], ["C2", "C3", "B5"])

    onlyone_rule_level_0 = create_only_one_rule("O0", "OnlyOne level 0", ["A1", "C1"])
    onlyone_rule_level_1 = create_only_one_rule("O1", "OnlyOne level 1", ["B5", "A4"])
    onlyone_rule_level_2 = create_only_one_rule("O2", "OnlyOne level 2", ["C5", "B4"])

    feature_rule_list_level_0 = create_feature_rule_node_list([onlyone_rule_level_0])
    feature_rule_list_level_1 = create_feature_rule_node_list([onlyone_rule_level_0, onlyone_rule_level_1])
    feature_rule_list_level_2 = create_feature_rule_node_list([onlyone_rule_level_0, onlyone_rule_level_1,onlyone_rule_level_2])

    # Level 0 is like a root and extends to nothing
    # Only remove modifiers are applied to the level 0 feature list
    feature_str_list_level_0 = resolve_extends_feature_list(feature_str_list_level_0, FeatureStrList(),feature_rule_list_level_0).unwrap()
    assert feature_str_list_level_0.override == False
    assert feature_str_list_level_0.values == set(["A1", "A4", "A5"])
    assert feature_str_list_level_0.remove_modifiers.values == set()

    # Level 1 extends level 0, so the only one rule is applied to the level 1 feature list
    # The only one rule will remove A4 from the level 0 feature list and add B5 to the level 1 feature list
    feature_str_list_level_1 = resolve_extends_feature_list(feature_str_list_level_1, feature_str_list_level_0, feature_rule_list_level_1).unwrap()
    assert feature_str_list_level_1.override == False
    assert feature_str_list_level_1.values == set(["A1", "B1", "B4", "B5"])
    assert feature_str_list_level_1.remove_modifiers.values == set()

    # Level 2 extends level 1, so the only one rule is applied to the level 2 feature list
    # Level 2 is 'C5', 'C3', 'C1', 'C2', 'C4'
    # Level 1 is 'B5', 'A1', 'B1', 'B4'
    # The only one rule at level 0 replace A1 with C1.
    # The only one rule at level 2 replace B4 with C5.
    # Result is 'C1', 'C4', 'B1', 'C5'
    feature_str_list_level_2 = resolve_extends_feature_list(feature_str_list_level_2, feature_str_list_level_1, feature_rule_list_level_2).unwrap()
    assert feature_str_list_level_2.override == False
    assert feature_str_list_level_2.values == set(["C1", "C4", "B1", "C5"])
    assert feature_str_list_level_2.remove_modifiers.values == set()

def test_extends_multiple_levels_2():
    # level 0
    # features: A1, A2, A3, A4, A5
    # level 1:
    # features: B1, B2, B3, B4, B5
    # level 2:
    # features: C1, C2, C3, C4, C5
    feature_str_list_level_0 = create_feature_str_list(True, ["A1", "A2", "A3", "A4", "A5"], ["A2", "A3"])
    feature_str_list_level_1 = create_feature_str_list(False, ["B1", "B2", "B3", "B4", "B5"], ["B2", "B3", "A5"])
    feature_str_list_level_2 = create_feature_str_list(False, ["C1", "C2", "C3", "C4", "C5"], ["C2", "C3", "B5"])

    onlyone_rule_level_0 = create_only_one_rule("O0", "OnlyOne level 0", ["A1", "C1"])
    onlyone_rule_level_1 = create_only_one_rule("O1", "OnlyOne level 1", ["B5", "A4"])
    onlyone_rule_level_2 = create_only_one_rule("O2", "OnlyOne level 2", ["C5", "B4"])

    feature_rule_list_level_0 = create_feature_rule_node_list([onlyone_rule_level_0])
    feature_rule_list_level_1 = create_feature_rule_node_list([onlyone_rule_level_0, onlyone_rule_level_1])
    feature_rule_list_level_2 = create_feature_rule_node_list([onlyone_rule_level_0, onlyone_rule_level_1,onlyone_rule_level_2])

    # Level 0 is like a root and extends to nothing
    # Only remove modifiers are applied to the level 0 feature list
    feature_str_list_level_0 = resolve_extends_feature_list(feature_str_list_level_0, FeatureStrList(),feature_rule_list_level_0).unwrap()
    assert feature_str_list_level_0.override == True
    assert feature_str_list_level_0.values == set(["A1", "A4", "A5"])
    assert feature_str_list_level_0.remove_modifiers.values == set()

    # Level 1 extends level 0, so the only one rule is applied to the level 1 feature list
    # The only one rule will remove A4 from the level 0 feature list and add B5 to the level 1 feature list
    feature_str_list_level_1 = resolve_extends_feature_list(feature_str_list_level_1, feature_str_list_level_0, feature_rule_list_level_1).unwrap()
    assert feature_str_list_level_1.override == False
    assert feature_str_list_level_1.values == set(["A1", "B1", "B4", "B5"])
    assert feature_str_list_level_1.remove_modifiers.values == set()

    # Level 2 extends level 1, so the only one rule is applied to the level 2 feature list
    # Level 2 is 'C5', 'C3', 'C1', 'C2', 'C4'
    # Level 1 is 'B5', 'A1', 'B1', 'B4'
    # The only one rule at level 0 replace A1 with C1.
    # The only one rule at level 2 replace B4 with C5.
    # Result is 'C1', 'C4', 'B1', 'C5'
    feature_str_list_level_2 = resolve_extends_feature_list(feature_str_list_level_2, feature_str_list_level_1, feature_rule_list_level_2).unwrap()
    assert feature_str_list_level_2.override == False
    assert feature_str_list_level_2.values == set(["C1", "C4", "B1", "C5"])
    assert feature_str_list_level_2.remove_modifiers.values == set()


def test_extends_multiple_levels_3():
    # level 0
    # features: A1, A2, A3, A4, A5
    # level 1:
    # features: B1, B2, B3, B4, B5
    # level 2:
    # features: C1, C2, C3, C4, C5
    feature_str_list_level_0 = create_feature_str_list(False, ["A1", "A2", "A3", "A4", "A5"], ["A2", "A3"])
    feature_str_list_level_1 = create_feature_str_list(True, ["B1", "B2", "B3", "B4", "B5"], ["B2", "B3", "A5"])
    feature_str_list_level_2 = create_feature_str_list(False, ["C1", "C2", "C3", "C4", "C5"], ["C2", "C3", "B5"])

    onlyone_rule_level_0 = create_only_one_rule("O0", "OnlyOne level 0", ["A1", "C1"])
    onlyone_rule_level_1 = create_only_one_rule("O1", "OnlyOne level 1", ["B5", "A4"])
    onlyone_rule_level_2 = create_only_one_rule("O2", "OnlyOne level 2", ["C5", "B4"])

    feature_rule_list_level_0 = create_feature_rule_node_list([onlyone_rule_level_0])
    feature_rule_list_level_1 = create_feature_rule_node_list([onlyone_rule_level_0, onlyone_rule_level_1])
    feature_rule_list_level_2 = create_feature_rule_node_list([onlyone_rule_level_0, onlyone_rule_level_1,onlyone_rule_level_2])

    # Level 0 is like a root and extends to nothing
    # Only remove modifiers are applied to the level 0 feature list
    feature_str_list_level_0 = resolve_extends_feature_list(feature_str_list_level_0, FeatureStrList(),feature_rule_list_level_0).unwrap()
    assert feature_str_list_level_0.override == False
    assert feature_str_list_level_0.values == set(["A1", "A4", "A5"])
    assert feature_str_list_level_0.remove_modifiers.values == set()

    # Level 1 extends level 0, so the only one rule is applied to the level 1 feature list
    # Level 0 is ignored, only one rule is applied on level 1 only
    feature_str_list_level_1 = resolve_extends_feature_list(feature_str_list_level_1, feature_str_list_level_0, feature_rule_list_level_1).unwrap()
    assert feature_str_list_level_1.override == True
    assert feature_str_list_level_1.values == set(["B1", "B4", "B5"])
    assert feature_str_list_level_1.remove_modifiers.values == set()

    # Level 2 extends level 1, so the only one rule is applied to the level 2 feature list
    # Level 2 is 'C5', 'C3', 'C1', 'C2', 'C4'
    # Level 1 is 'B5', 'B1', 'B4'
    # The only one rule at level 0 replace A1 with C1.
    # The only one rule at level 2 replace B4 with C5.
    # Result is 'C1', 'C4', 'B1', 'C5'
    feature_str_list_level_2 = resolve_extends_feature_list(feature_str_list_level_2, feature_str_list_level_1, feature_rule_list_level_2).unwrap()
    assert feature_str_list_level_2.override == False
    assert feature_str_list_level_2.values == set(["C1", "C4", "B1", "C5"])
    assert feature_str_list_level_2.remove_modifiers.values == set()


def test_extends_multiple_levels_4():
    # level 0
    # features: A1, A2, A3, A4, A5
    # level 1:
    # features: B1, B2, B3, B4, B5
    # level 2:
    # features: C1, C2, C3, C4, C5
    feature_str_list_level_0 = create_feature_str_list(False, ["A1", "A2", "A3", "A4", "A5"], ["A2", "A3"])
    feature_str_list_level_1 = create_feature_str_list(False, ["B1", "B2", "B3", "B4", "B5"], ["B2", "B3", "A5"])
    feature_str_list_level_2 = create_feature_str_list(True, ["C1", "C2", "C3", "C4", "C5"], ["C2", "C3", "B5"])

    onlyone_rule_level_0 = create_only_one_rule("O0", "OnlyOne level 0", ["A1", "C1"])
    onlyone_rule_level_1 = create_only_one_rule("O1", "OnlyOne level 1", ["B5", "A4"])
    onlyone_rule_level_2 = create_only_one_rule("O2", "OnlyOne level 2", ["C5", "B4"])

    feature_rule_list_level_0 = create_feature_rule_node_list([onlyone_rule_level_0])
    feature_rule_list_level_1 = create_feature_rule_node_list([onlyone_rule_level_0, onlyone_rule_level_1])
    feature_rule_list_level_2 = create_feature_rule_node_list([onlyone_rule_level_0, onlyone_rule_level_1,onlyone_rule_level_2])

    # Level 0 is like a root and extends to nothing
    # Only remove modifiers are applied to the level 0 feature list
    feature_str_list_level_0 = resolve_extends_feature_list(feature_str_list_level_0, FeatureStrList(),feature_rule_list_level_0).unwrap()
    assert feature_str_list_level_0.override == False
    assert feature_str_list_level_0.values == set(["A1", "A4", "A5"])
    assert feature_str_list_level_0.remove_modifiers.values == set()

    # Level 1 extends level 0, so the only one rule is applied to the level 1 feature list
    # The only one rule will remove A4 from the level 0 feature list and add B5 to the level 1 feature list
    feature_str_list_level_1 = resolve_extends_feature_list(feature_str_list_level_1, feature_str_list_level_0, feature_rule_list_level_1).unwrap()
    assert feature_str_list_level_1.override == False
    assert feature_str_list_level_1.values == set(["A1", "B1", "B4", "B5"])
    assert feature_str_list_level_1.remove_modifiers.values == set()

    # Level 2 extends level 1, so the only one rule is applied to the level 2 feature list
    # Level 2 is 'C5', 'C3', 'C1', 'C2', 'C4'
    # Level 1 is 'B5', 'A1', 'B1', 'B4'
    # Level 1 is ignored
    # Result is 'C1', 'C4', 'C5'
    feature_str_list_level_2 = resolve_extends_feature_list(feature_str_list_level_2, feature_str_list_level_1, feature_rule_list_level_2).unwrap()
    assert feature_str_list_level_2.override == True
    assert feature_str_list_level_2.values == set(["C1", "C4", "C5"])
    assert feature_str_list_level_2.remove_modifiers.values == set()

def test_extends_multiple_levels_5():
    # level 0
    # features: A1, A2, A3, A4, A5
    # level 1:
    # features: B1, B2, B3, B4, B5
    # level 2:
    # features: C1, C2, C3, C4, C5
    feature_str_list_level_0 = create_feature_str_list(True, ["A1", "A2", "A3", "A4", "A5"], ["A2", "A3"])
    feature_str_list_level_1 = create_feature_str_list(True, ["B1", "B2", "B3", "B4", "B5"], ["B2", "B3", "A5"])
    feature_str_list_level_2 = create_feature_str_list(True, ["C1", "C2", "C3", "C4", "C5"], ["C2", "C3", "B5"])

    onlyone_rule_level_0 = create_only_one_rule("O0", "OnlyOne level 0", ["A1", "C1"])
    onlyone_rule_level_1 = create_only_one_rule("O1", "OnlyOne level 1", ["B5", "A4"])
    onlyone_rule_level_2 = create_only_one_rule("O2", "OnlyOne level 2", ["C5", "B4"])

    feature_rule_list_level_0 = create_feature_rule_node_list([onlyone_rule_level_0])
    feature_rule_list_level_1 = create_feature_rule_node_list([onlyone_rule_level_0, onlyone_rule_level_1])
    feature_rule_list_level_2 = create_feature_rule_node_list([onlyone_rule_level_0, onlyone_rule_level_1,onlyone_rule_level_2])

    # Level 0 is like a root and extends to nothing
    # Only remove modifiers are applied to the level 0 feature list
    feature_str_list_level_0 = resolve_extends_feature_list(feature_str_list_level_0, FeatureStrList(),feature_rule_list_level_0).unwrap()
    assert feature_str_list_level_0.override == True
    assert feature_str_list_level_0.values == set(["A1", "A4", "A5"])
    assert feature_str_list_level_0.remove_modifiers.values == set()

    # Level 1 extends level 0, so the only one rule is applied to the level 1 feature list
    # Level 0 is ignored, only one rule is applied on level 1 only
    feature_str_list_level_1 = resolve_extends_feature_list(feature_str_list_level_1, feature_str_list_level_0, feature_rule_list_level_1).unwrap()
    assert feature_str_list_level_1.override == True
    assert feature_str_list_level_1.values == set(["B1", "B4", "B5"])
    assert feature_str_list_level_1.remove_modifiers.values == set()

    # Level 2 extends level 1, so the only one rule is applied to the level 2 feature list
    # Level 2 is 'C5', 'C3', 'C1', 'C2', 'C4'
    # Level 1 is ignored
    # Result is 'C1', 'C4', 'C5'
    feature_str_list_level_2 = resolve_extends_feature_list(feature_str_list_level_2, feature_str_list_level_1, feature_rule_list_level_2).unwrap()
    assert feature_str_list_level_2.override == True
    assert feature_str_list_level_2.values == set(["C1", "C4", "C5"])
    assert feature_str_list_level_2.remove_modifiers.values == set()

def test_extends_feature_str_list():

    # Empty child and parent
    test_extends_empty_1()
    test_extends_empty_2()
    test_extends_empty_3()
    test_extends_empty_4()

    # Empty parent
    test_extends_empty_parent_no_rule_1()
    test_extends_empty_parent_no_rule_2()
    test_extends_empty_parent_no_rule_3()
    test_extends_empty_parent_no_rule_4()

    test_extends_empty_parent_only_one_rule_1()
    test_extends_empty_parent_only_one_rule_2()
    test_extends_empty_parent_only_one_rule_3()
    test_extends_empty_parent_only_one_rule_4()
    
    test_extends_empty_parent_only_one_rule_failed_1()
    test_extends_empty_parent_only_one_rule_failed_2()
    test_extends_empty_parent_only_one_rule_failed_3()
    test_extends_empty_parent_only_one_rule_failed_4()

    test_extends_empty_parent_incompatible_rule_1()
    test_extends_empty_parent_incompatible_rule_2()
    test_extends_empty_parent_incompatible_rule_3()
    test_extends_empty_parent_incompatible_rule_4()

    test_extends_empty_parent_incompatible_rule_failed_1()
    test_extends_empty_parent_incompatible_rule_failed_2()
    test_extends_empty_parent_incompatible_rule_failed_3()
    test_extends_empty_parent_incompatible_rule_failed_4()

    test_extends_empty_parent_multiple_rules_1()
    test_extends_empty_parent_multiple_rules_2()
    test_extends_empty_parent_multiple_rules_3()
    test_extends_empty_parent_multiple_rules_4()

    test_extends_empty_parent_multiple_rules_failed_1_1()
    test_extends_empty_parent_multiple_rules_failed_2_1()
    test_extends_empty_parent_multiple_rules_failed_3_1()
    test_extends_empty_parent_multiple_rules_failed_4_1()
    test_extends_empty_parent_multiple_rules_failed_1_2()
    test_extends_empty_parent_multiple_rules_failed_2_2()
    test_extends_empty_parent_multiple_rules_failed_3_2()
    test_extends_empty_parent_multiple_rules_failed_4_2()
    test_extends_empty_parent_multiple_rules_failed_1_3()
    test_extends_empty_parent_multiple_rules_failed_2_3()
    test_extends_empty_parent_multiple_rules_failed_3_3()
    test_extends_empty_parent_multiple_rules_failed_4_3()
    test_extends_empty_parent_multiple_rules_failed_1_4()
    test_extends_empty_parent_multiple_rules_failed_2_4()
    test_extends_empty_parent_multiple_rules_failed_3_4()
    test_extends_empty_parent_multiple_rules_failed_4_4()

    # Empty child
    test_extends_empty_child_no_rule_1()
    test_extends_empty_child_no_rule_2()
    test_extends_empty_child_no_rule_3()
    test_extends_empty_child_no_rule_4()

    test_extends_empty_child_only_one_rule_1()
    test_extends_empty_child_only_one_rule_2()
    test_extends_empty_child_only_one_rule_3()
    test_extends_empty_child_only_one_rule_4()

    test_extends_empty_child_only_one_rule_failed_1()
    test_extends_empty_child_only_one_rule_failed_2()

    test_extends_empty_child_incompatible_rule_1()
    test_extends_empty_child_incompatible_rule_2()
    test_extends_empty_child_incompatible_rule_3()
    test_extends_empty_child_incompatible_rule_4()

    test_extends_empty_child_incompatible_rule_failed_1()
    test_extends_empty_child_incompatible_rule_failed_2()

    test_extends_empty_child_multiple_rules_1()
    test_extends_empty_child_multiple_rules_2()
    test_extends_empty_child_multiple_rules_3()
    test_extends_empty_child_multiple_rules_4()

    test_extends_empty_child_multiple_rules_failed_1_1()
    test_extends_empty_child_multiple_rules_failed_2_1()
    test_extends_empty_child_multiple_rules_failed_3_1()
    test_extends_empty_child_multiple_rules_failed_4_1()
    test_extends_empty_child_multiple_rules_failed_1_2()
    test_extends_empty_child_multiple_rules_failed_2_2()
    test_extends_empty_child_multiple_rules_failed_3_2()
    test_extends_empty_child_multiple_rules_failed_4_2()

    # Child and parent
    test_extends_no_rule_1()
    test_extends_no_rule_2()
    test_extends_no_rule_3()
    test_extends_no_rule_4()

    test_extends_only_one_rule_1()
    test_extends_only_one_rule_2()
    test_extends_only_one_rule_3()
    test_extends_only_one_rule_4()

    test_extends_only_one_rule_failed_1()
    test_extends_only_one_rule_failed_2()
    test_extends_only_one_rule_failed_3()
    test_extends_only_one_rule_failed_4()
    test_extends_only_one_rule_failed_5()
    test_extends_only_one_rule_failed_6()

    test_extends_incompatible_rule_1()
    test_extends_incompatible_rule_2()
    test_extends_incompatible_rule_3()
    test_extends_incompatible_rule_4()

    test_extends_incompatible_rule_failed_1()
    test_extends_incompatible_rule_failed_2()
    test_extends_incompatible_rule_failed_3()
    test_extends_incompatible_rule_failed_4()
    test_extends_incompatible_rule_failed_5()
    test_extends_incompatible_rule_failed_6()

    test_extends_multiple_rules_1()
    test_extends_multiple_rules_2()
    test_extends_multiple_rules_3()
    test_extends_multiple_rules_4()

    test_extends_multiple_rules_failed_1()
    test_extends_multiple_rules_failed_2()

    test_extends_multiple_levels_1()
    test_extends_multiple_levels_2()
    test_extends_multiple_levels_3()
    test_extends_multiple_levels_4()
    test_extends_multiple_levels_5()