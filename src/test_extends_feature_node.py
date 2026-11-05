# - name:
#     description:
#     flags: [] # Add/remove flags
#     features: [] # Add/remove features
#     args:
#       min: 1
#       max: ~
#       separator: ","
#       pattern: "*.lib"


from test_common import create_feature_str_list, create_str_list
from toolchain.nodes.feature_node import FeatureNode, FeatureRuleNodeList

def test_extends_empty():
    # feature level 0
    feature_level_0 = FeatureNode("A")
    feature_level_0.description = "feature A"
    feature_level_0.flags = create_str_list(False, ["A1", "A2"], ["A1", "A3"] )
    feature_level_0.features = create_feature_str_list(False, ["F1", "F2"], ["F1", "F3"] )

    result = feature_level_0.resolve_extends(FeatureNode("B"), FeatureRuleNodeList())

    assert result.name == "A"
    assert result.description == "feature A"
    assert result.flags.override == False
    assert result.flags.values == set(["A2"])
    assert result.flags.remove_modifiers.values == set([])
    assert result.features.override == False
    assert result.features.values == set(["F2"])
    assert result.features.remove_modifiers.values == set([])


def test_extends_feature_node() :
    test_extends_empty()
    