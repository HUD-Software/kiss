import sys
import os

from test_extends_feature_rule_node_list import test_extends_feature_rule_node_list
from test_extends_linker_override_node import test_extends_linker_override_node
from test_extends_feature_node_list import test_extends_feature_node_list
from test_extends_feature_node import test_extends_feature_node
from test_extends_feature_str_list import test_extends_feature_str_list
from test_extends_linker_specific_override_node import test_extends_linker_specific_override_node


sys.path.insert(0, os.path.dirname(__file__))

from cli.app import app

if __name__ == "__main__":
    test_extends_feature_str_list()
    test_extends_feature_rule_node_list()
    test_extends_feature_node()
    test_extends_feature_node_list()
    test_extends_linker_specific_override_node()
    test_extends_linker_override_node()


    app()
    