import sys
import os

from test_extends_feature_rule_node_list import test_extends_feature_rule_node_list
from test_extends_str_list import test_extends_str_list
sys.path.insert(0, os.path.dirname(__file__))

from cli.app import app

if __name__ == "__main__":
    test_extends_str_list()
    test_extends_feature_rule_node_list()
    app()
    