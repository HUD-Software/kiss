
from test_common import create_feature_rule_list, create_inccompatible_rule, create_only_one_rule, create_str_list
from toolchain.nodes.feature_node import FeatureRuleNodeOnlyOne, FeatureStrList, resolve_extends_feature_list
from toolchain.nodes.property import StrListModifierRemove


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

def test_extends_empty_1():
    feature_str_list_child = create_feature_str_list(False, [], [])
    feature_str_list_parent = create_feature_str_list(False, [], [])

    feature_str_list_parent = resolve_extends_feature_list(feature_str_list_parent, FeatureStrList(),  create_feature_rule_list([])).unwrap()
    result = resolve_extends_feature_list(feature_str_list_child, feature_str_list_parent, create_feature_rule_list([])).unwrap()
    
    # Validate result
    assert result.override == False
    assert result.values == set([])
    assert result.remove_modifiers.values == set()

def test_extends_empty_2():
    feature_str_list_child = create_feature_str_list(True, [], [])
    feature_str_list_parent = create_feature_str_list(False, [], [])

    feature_str_list_parent = resolve_extends_feature_list(feature_str_list_parent, FeatureStrList(),  create_feature_rule_list([])).unwrap()
    result = resolve_extends_feature_list(feature_str_list_child, feature_str_list_parent, create_feature_rule_list([])).unwrap()
    
    # Validate result
    assert result.override == True
    assert result.values == set([])
    assert result.remove_modifiers.values == set()

def test_extends_empty_3():
    feature_str_list_child = create_feature_str_list(False, [], [])
    feature_str_list_parent = create_feature_str_list(True, [], [])

    feature_str_list_parent = resolve_extends_feature_list(feature_str_list_parent, FeatureStrList(),  create_feature_rule_list([])).unwrap()
    result = resolve_extends_feature_list(feature_str_list_child, feature_str_list_parent, create_feature_rule_list([])).unwrap()
    
    # Validate result
    assert result.override == False
    assert result.values == set([])
    assert result.remove_modifiers.values == set()

def test_extends_empty_4():
    feature_str_list_child = create_feature_str_list(True, [], [])
    feature_str_list_parent = create_feature_str_list(True, [], [])

    feature_str_list_parent = resolve_extends_feature_list(feature_str_list_parent, FeatureStrList(),  create_feature_rule_list([])).unwrap()
    result = resolve_extends_feature_list(feature_str_list_child, feature_str_list_parent, create_feature_rule_list([])).unwrap()
    
    # Validate result
    assert result.override == True
    assert result.values == set([])
    assert result.remove_modifiers.values == set()

def test_extends_empty_parent_no_rule_1():
    feature_str_list_child = create_feature_str_list(False, ["A1", "A2"], ["A2", "A3"])
    feature_str_list_parent = create_feature_str_list(False, [], [])

    feature_str_list_parent = resolve_extends_feature_list(feature_str_list_parent, FeatureStrList(),  create_feature_rule_list([])).unwrap()
    result = resolve_extends_feature_list(feature_str_list_child, feature_str_list_parent, create_feature_rule_list([])).unwrap()

     # Validate result
    assert result.override == False
    assert result.values == set(["A1"])
    assert result.remove_modifiers.values == set()

def test_extends_empty_parent_no_rule_2():
    feature_str_list_child = create_feature_str_list(True, ["A1", "A2"], ["A2", "A3"])
    feature_str_list_parent = create_feature_str_list(False, [], [])

    feature_str_list_parent = resolve_extends_feature_list(feature_str_list_parent, FeatureStrList(),  create_feature_rule_list([])).unwrap()
    result = resolve_extends_feature_list(feature_str_list_child, feature_str_list_parent, create_feature_rule_list([])).unwrap()

     # Validate result
    assert result.override == True
    assert result.values == set(["A1"])
    assert result.remove_modifiers.values == set()

def test_extends_empty_parent_no_rule_3():
    feature_str_list_child = create_feature_str_list(False, ["A1", "A2"], ["A2", "A3"])
    feature_str_list_parent = create_feature_str_list(True, [], [])

    feature_str_list_parent = resolve_extends_feature_list(feature_str_list_parent, FeatureStrList(),  create_feature_rule_list([])).unwrap()
    result = resolve_extends_feature_list(feature_str_list_child, feature_str_list_parent, create_feature_rule_list([])).unwrap()

     # Validate result
    assert result.override == False
    assert result.values == set(["A1"])
    assert result.remove_modifiers.values == set()

def test_extends_empty_parent_no_rule_4():
    feature_str_list_child = create_feature_str_list(True, ["A1", "A2"], ["A2", "A3"])
    feature_str_list_parent = create_feature_str_list(True, [], [])

    feature_str_list_parent = resolve_extends_feature_list(feature_str_list_parent, FeatureStrList(),  create_feature_rule_list([])).unwrap()
    result = resolve_extends_feature_list(feature_str_list_child, feature_str_list_parent, create_feature_rule_list([])).unwrap()

     # Validate result
    assert result.override == True
    assert result.values == set(["A1"])
    assert result.remove_modifiers.values == set()

def test_extends_empty_parent_only_one_rule_1():
    feature_str_list_child = create_feature_str_list(False, ["A1", "A2", "A4", "A5"], ["A2", "A3"])
    feature_str_list_parent = create_feature_str_list(False, [], [])

    onlyone_rule = create_only_one_rule("OA", "OnlyOne A", ["A1", "A3"])
    feature_rule_list = create_feature_rule_list([onlyone_rule])

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
    feature_rule_list = create_feature_rule_list([onlyone_rule])

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
    feature_rule_list = create_feature_rule_list([onlyone_rule])

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
    feature_rule_list = create_feature_rule_list([onlyone_rule])

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
    feature_rule_list = create_feature_rule_list([onlyone_rule])

    feature_str_list_parent = resolve_extends_feature_list(feature_str_list_parent, FeatureStrList(),feature_rule_list).unwrap()
    assert resolve_extends_feature_list(feature_str_list_child, feature_str_list_parent, feature_rule_list).is_err()


def test_extends_empty_parent_only_one_rule_failed_2():
    feature_str_list_child = create_feature_str_list(True, ["A1", "A2", "A4", "A5"], ["A2", "A3"])
    feature_str_list_parent = create_feature_str_list(False, [], [])

    onlyone_rule = create_only_one_rule("OA", "OnlyOne A", ["A1", "A4"])
    feature_rule_list = create_feature_rule_list([onlyone_rule])

    feature_str_list_parent = resolve_extends_feature_list(feature_str_list_parent, FeatureStrList(),feature_rule_list).unwrap()
    assert resolve_extends_feature_list(feature_str_list_child, feature_str_list_parent, feature_rule_list).is_err()

def test_extends_empty_parent_only_one_rule_failed_3():
    feature_str_list_child = create_feature_str_list(False, ["A1", "A2", "A4", "A5"], ["A2", "A3"])
    feature_str_list_parent = create_feature_str_list(True, [], [])

    onlyone_rule = create_only_one_rule("OA", "OnlyOne A", ["A1", "A4"])
    feature_rule_list = create_feature_rule_list([onlyone_rule])

    feature_str_list_parent = resolve_extends_feature_list(feature_str_list_parent, FeatureStrList(),feature_rule_list).unwrap()
    assert resolve_extends_feature_list(feature_str_list_child, feature_str_list_parent, feature_rule_list).is_err()

def test_extends_empty_parent_only_one_rule_failed_4():
    feature_str_list_child = create_feature_str_list(True, ["A1", "A2", "A4", "A5"], ["A2", "A3"])
    feature_str_list_parent = create_feature_str_list(True, [], [])

    onlyone_rule = create_only_one_rule("OA", "OnlyOne A", ["A1", "A4"])
    feature_rule_list = create_feature_rule_list([onlyone_rule])

    feature_str_list_parent = resolve_extends_feature_list(feature_str_list_parent, FeatureStrList(),feature_rule_list).unwrap()
    assert resolve_extends_feature_list(feature_str_list_child, feature_str_list_parent, feature_rule_list).is_err()


def test_extends_empty_parent_incompatible_rule_1():
    feature_str_list_child = create_feature_str_list(False, ["A1", "A2", "A4", "A5"], ["A2", "A3"])
    feature_str_list_parent = create_feature_str_list(False, [], [])

    incompatible_rule = create_inccompatible_rule("IA", "Incompatible A", "A0", ["A1", "A3"])
    feature_rule_list = create_feature_rule_list([incompatible_rule])

    feature_str_list_parent = resolve_extends_feature_list(feature_str_list_parent, FeatureStrList(),feature_rule_list).unwrap()
    result = resolve_extends_feature_list(feature_str_list_child, feature_str_list_parent, feature_rule_list).unwrap()

    # Validate result
    assert result.override == False
    assert result.values == set(["A1", "A4", "A5"])
    assert result.remove_modifiers.values == set()

def test_extends_empty_parent_incompatible_rule_2():
    feature_str_list_child = create_feature_str_list(True, ["A1", "A2", "A4", "A5"], ["A2", "A3"])
    feature_str_list_parent = create_feature_str_list(False, [], [])

    incompatible_rule = create_inccompatible_rule("IA", "Incompatible A", "A0", ["A1", "A3"])
    feature_rule_list = create_feature_rule_list([incompatible_rule])

    feature_str_list_parent = resolve_extends_feature_list(feature_str_list_parent, FeatureStrList(),feature_rule_list).unwrap()
    result = resolve_extends_feature_list(feature_str_list_child, feature_str_list_parent, feature_rule_list).unwrap()

    # Validate result
    assert result.override == True
    assert result.values == set(["A1", "A4", "A5"])
    assert result.remove_modifiers.values == set()

def test_extends_empty_parent_incompatible_rule_3():
    feature_str_list_child = create_feature_str_list(False, ["A1", "A2", "A4", "A5"], ["A2", "A3"])
    feature_str_list_parent = create_feature_str_list(True, [], [])

    incompatible_rule = create_inccompatible_rule("IA", "Incompatible A", "A0", ["A1", "A3"])
    feature_rule_list = create_feature_rule_list([incompatible_rule])

    feature_str_list_parent = resolve_extends_feature_list(feature_str_list_parent, FeatureStrList(),feature_rule_list).unwrap()
    result = resolve_extends_feature_list(feature_str_list_child, feature_str_list_parent, feature_rule_list).unwrap()

    # Validate result
    assert result.override == False
    assert result.values == set(["A1", "A4", "A5"])
    assert result.remove_modifiers.values == set()

def test_extends_empty_parent_incompatible_rule_4():
    feature_str_list_child = create_feature_str_list(True, ["A1", "A2", "A4", "A5"], ["A2", "A3"])
    feature_str_list_parent = create_feature_str_list(True, [], [])

    incompatible_rule = create_inccompatible_rule("IA", "Incompatible A", "A0", ["A1", "A3"])
    feature_rule_list = create_feature_rule_list([incompatible_rule])

    feature_str_list_parent = resolve_extends_feature_list(feature_str_list_parent, FeatureStrList(),feature_rule_list).unwrap()
    result = resolve_extends_feature_list(feature_str_list_child, feature_str_list_parent, feature_rule_list).unwrap()

    # Validate result
    assert result.override == True
    assert result.values == set(["A1", "A4", "A5"])
    assert result.remove_modifiers.values == set()

def test_extends_empty_parent_incompatible_rule_failed_1():
    feature_str_list_child = create_feature_str_list(False, ["A1", "A2", "A4", "A5"], ["A2", "A3"])
    feature_str_list_parent = create_feature_str_list(False, [], [])

    incompatible_rule = create_inccompatible_rule("IA", "Incompatible A", "A1", ["A2", "A4"])
    feature_rule_list = create_feature_rule_list([incompatible_rule])

    feature_str_list_parent = resolve_extends_feature_list(feature_str_list_parent, FeatureStrList(),feature_rule_list).unwrap()
    assert resolve_extends_feature_list(feature_str_list_child, feature_str_list_parent, feature_rule_list).is_err()

def test_extends_empty_parent_incompatible_rule_failed_2():
    feature_str_list_child = create_feature_str_list(True, ["A1", "A2", "A4", "A5"], ["A2", "A3"])
    feature_str_list_parent = create_feature_str_list(False, [], [])

    incompatible_rule = create_inccompatible_rule("IA", "Incompatible A", "A1", ["A2", "A4"])
    feature_rule_list = create_feature_rule_list([incompatible_rule])

    feature_str_list_parent = resolve_extends_feature_list(feature_str_list_parent, FeatureStrList(),feature_rule_list).unwrap()
    assert resolve_extends_feature_list(feature_str_list_child, feature_str_list_parent, feature_rule_list).is_err()

def test_extends_empty_parent_incompatible_rule_failed_3():
    feature_str_list_child = create_feature_str_list(False, ["A1", "A2", "A4", "A5"], ["A2", "A3"])
    feature_str_list_parent = create_feature_str_list(True, [], [])

    incompatible_rule = create_inccompatible_rule("IA", "Incompatible A", "A1", ["A2", "A4"])
    feature_rule_list = create_feature_rule_list([incompatible_rule])

    feature_str_list_parent = resolve_extends_feature_list(feature_str_list_parent, FeatureStrList(),feature_rule_list).unwrap()
    assert resolve_extends_feature_list(feature_str_list_child, feature_str_list_parent, feature_rule_list).is_err()

def test_extends_empty_parent_incompatible_rule_failed_4():
    feature_str_list_child = create_feature_str_list(True, ["A1", "A2", "A4", "A5"], ["A2", "A3"])
    feature_str_list_parent = create_feature_str_list(True, [], [])

    incompatible_rule = create_inccompatible_rule("IA", "Incompatible A", "A1", ["A2", "A4"])
    feature_rule_list = create_feature_rule_list([incompatible_rule])

    feature_str_list_parent = resolve_extends_feature_list(feature_str_list_parent, FeatureStrList(),feature_rule_list).unwrap()
    assert resolve_extends_feature_list(feature_str_list_child, feature_str_list_parent, feature_rule_list).is_err()


def test_extends_empty_child_no_rule_1():
    feature_str_list_child = create_feature_str_list(False, [], [])
    feature_str_list_parent = create_feature_str_list(False, ["B1", "B2"], ["B2", "B3"])
    
    feature_str_list_parent = resolve_extends_feature_list(feature_str_list_parent, FeatureStrList(),  create_feature_rule_list([])).unwrap()
    result = resolve_extends_feature_list(feature_str_list_child, feature_str_list_parent, create_feature_rule_list([])).unwrap()

     # Validate result
    assert result.override == False
    assert result.values == set(["B1"])
    assert result.remove_modifiers.values == set()

def test_extends_empty_child_no_rule_2():
    feature_str_list_child = create_feature_str_list(True, [], [])
    feature_str_list_parent = create_feature_str_list(False, ["B1", "B2"], ["B2", "B3"])
    
    feature_str_list_parent = resolve_extends_feature_list(feature_str_list_parent, FeatureStrList(),  create_feature_rule_list([])).unwrap()
    result = resolve_extends_feature_list(feature_str_list_child, feature_str_list_parent, create_feature_rule_list([])).unwrap()

     # Validate result
    assert result.override == True
    assert result.values == set([])
    assert result.remove_modifiers.values == set()


def test_extends_empty_child_no_rule_3():
    feature_str_list_child = create_feature_str_list(False, [], [])
    feature_str_list_parent = create_feature_str_list(True, ["B1", "B2"], ["B2", "B3"])
    
    feature_str_list_parent = resolve_extends_feature_list(feature_str_list_parent, FeatureStrList(),  create_feature_rule_list([])).unwrap()
    result = resolve_extends_feature_list(feature_str_list_child, feature_str_list_parent, create_feature_rule_list([])).unwrap()

     # Validate result
    assert result.override == False
    assert result.values == set(["B1"])
    assert result.remove_modifiers.values == set()

def test_extends_empty_child_no_rule_4():
    feature_str_list_child = create_feature_str_list(True, [], [])
    feature_str_list_parent = create_feature_str_list(False, ["B1", "B2"], ["B2", "B3"])
    
    feature_str_list_parent = resolve_extends_feature_list(feature_str_list_parent, FeatureStrList(),  create_feature_rule_list([])).unwrap()
    result = resolve_extends_feature_list(feature_str_list_child, feature_str_list_parent, create_feature_rule_list([])).unwrap()

     # Validate result
    assert result.override == True
    assert result.values == set([])
    assert result.remove_modifiers.values == set()

def test_extends_no_rule_1():
    feature_str_list_child = create_feature_str_list(False, ["A1", "A2"], ["A2", "A3"])
    feature_str_list_parent = create_feature_str_list(False, ["B1", "B2"], ["B2", "B3"])

    feature_str_list_parent = resolve_extends_feature_list(feature_str_list_parent, FeatureStrList(),  create_feature_rule_list([])).unwrap()
    result = resolve_extends_feature_list(feature_str_list_child, feature_str_list_parent, create_feature_rule_list([])).unwrap()

     # Validate result
    assert result.override == False
    assert result.values == set(["B1", "A1"])
    assert result.remove_modifiers.values == set()

def test_extends_no_rule_2():
    feature_str_list_child = create_feature_str_list(True, ["A1", "A2"], ["A2", "A3"])
    feature_str_list_parent = create_feature_str_list(False, ["B1", "B2"], ["B2", "B3"])

    feature_str_list_parent = resolve_extends_feature_list(feature_str_list_parent, FeatureStrList(),  create_feature_rule_list([])).unwrap()
    result = resolve_extends_feature_list(feature_str_list_child, feature_str_list_parent, create_feature_rule_list([])).unwrap()

     # Validate result
    assert result.override == True
    assert result.values == set(["A1"])
    assert result.remove_modifiers.values == set()

def test_extends_no_rule_3():
    feature_str_list_child = create_feature_str_list(False, ["A1", "A2"], ["A2", "A3"])
    feature_str_list_parent = create_feature_str_list(True, ["B1", "B2"], ["B2", "B3"])

    feature_str_list_parent = resolve_extends_feature_list(feature_str_list_parent, FeatureStrList(),  create_feature_rule_list([])).unwrap()
    result = resolve_extends_feature_list(feature_str_list_child, feature_str_list_parent, create_feature_rule_list([])).unwrap()

     # Validate result
    assert result.override == False
    assert result.values == set(["B1", "A1"])
    assert result.remove_modifiers.values == set()


def test_extends_no_rule_4():
    feature_str_list_child = create_feature_str_list(True, ["A1", "A2"], ["A2", "A3"])
    feature_str_list_parent = create_feature_str_list(True, ["B1", "B2"], ["B2", "B3"])

    feature_str_list_parent = resolve_extends_feature_list(feature_str_list_parent, FeatureStrList(),  create_feature_rule_list([])).unwrap()
    result = resolve_extends_feature_list(feature_str_list_child, feature_str_list_parent, create_feature_rule_list([])).unwrap()

     # Validate result
    assert result.override == True
    assert result.values == set(["A1"])
    assert result.remove_modifiers.values == set()


# def test_extends_rule_only_one():
#     feature_str_list_child = create_feature_str_list(False, ["A1", "A2"], ["A2", "A3"])
#     feature_str_list_parent = create_feature_str_list(False, ["B1", "B2"], ["B2", "B3"])
#     onlyone_features = create_str_list(True,["A1", "A2"], ["A1", "A3"] )
#     onlyone_rule = FeatureRuleNodeOnlyOne("A", "desc a", onlyone_features)    
    
#     feature_str_list_parent = resolve_extends_feature_list(feature_str_list_parent, FeatureStrList(),  create_feature_rule_list([onlyone_rule]))
#     result = resolve_extends_feature_list(feature_str_list_child, feature_str_list_parent, create_feature_rule_list([]))

#      # Validate result
#     assert result.override == False
#     assert result.values == set(["B1", "A1"])
#     assert result.remove_modifiers.values == set()


def test_extends_feature_str_list():
    
    test_extends_empty_1()
    test_extends_empty_2()
    test_extends_empty_3()
    test_extends_empty_4()

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



    test_extends_empty_child_no_rule_1()
    test_extends_empty_child_no_rule_2()
    test_extends_empty_child_no_rule_3()
    test_extends_empty_child_no_rule_4()

    test_extends_no_rule_1()
    test_extends_no_rule_2()
    test_extends_no_rule_3()
    test_extends_no_rule_4()

    pass