import sys
import os

from test import test_extends
sys.path.insert(0, os.path.dirname(__file__))

from cli.app import app

if __name__ == "__main__":
    test_extends()
    
    app()
    