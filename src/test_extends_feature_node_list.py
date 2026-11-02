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

from test_common import create_str_list
from toolchain.nodes.feature_node import FeatureNodeList, FeatureRuleNodeIncompatible, FeatureRuleNodeList, FeatureRuleNodeOnlyOne


def test_extends_empty():
    # No feeature rule
    result = FeatureNodeList().resolve_extends(FeatureNodeList(), FeatureRuleNodeList())
    assert result.is_empty()

    # only one feature rule
    onlyone_features = create_str_list(False, ["A1", "A2"], ["A1", "A3"] )
    onlyone_rule = FeatureRuleNodeOnlyOne("A", "desc a", onlyone_features)
    feature_rule_list = FeatureRuleNodeList()
    feature_rule_list.add_feature_rule(onlyone_rule)
    result = FeatureNodeList().resolve_extends(FeatureNodeList(), feature_rule_list)
    assert result.is_empty()

    # incompatible feature rule
    feature_rule_list = FeatureRuleNodeList()
    incompatible_features = create_str_list(False,["A1", "A2"], ["A1", "A3"] )
    incompatible_rule = FeatureRuleNodeIncompatible("A", "desc a", "A0", incompatible_features)    
    feature_rule_list.add_feature_rule(incompatible_rule)
    result = FeatureNodeList().resolve_extends(FeatureNodeList(), feature_rule_list)
    assert result.is_empty()

    # only one  and incompatible feature rule
    feature_rule_list = FeatureRuleNodeList()
    feature_rule_list.add_feature_rule(onlyone_rule)
    feature_rule_list.add_feature_rule(incompatible_rule)
    result = FeatureNodeList().resolve_extends(FeatureNodeList(), feature_rule_list)
    assert result.is_empty()


def test_extends_feature_node_list() :
    test_extends_empty()