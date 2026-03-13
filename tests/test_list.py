import subprocess
from tests.common import *

def test_new_empty(runtime_dir):
    result = subprocess.run(["python", "src/kiss.py", "-d", str(RUNTIME_DIR), "list", "-r", "-d" ])
    assert result.returncode == 0

def create_project():
    # Create a bin project
    result = subprocess.run(["python", "src/kiss.py", "-d", str(RUNTIME_DIR), "new", "bin", "my_bin" ])
    assert result.returncode == 0

    # Create a dyn project
    result = subprocess.run(["python", "src/kiss.py", "-d", str(RUNTIME_DIR), "new", "dyn", "my_dyn" ])
    assert result.returncode == 0

    # Create a lib project
    result = subprocess.run(["python", "src/kiss.py", "-d", str(RUNTIME_DIR), "new", "lib", "my_lib" ])
    assert result.returncode == 0

    # Create a lib project
    result = subprocess.run(["python", "src/kiss.py", "-d", str(RUNTIME_DIR/"my_bin"), "new", "-e", "lib", "my_inner_lib" ])
    assert result.returncode == 0

def test_new(runtime_dir):
    # Create project to list
    create_project()
    result = subprocess.run(["python", "src/kiss.py", "-d", str(RUNTIME_DIR), "list", "-r", "-d" ])
    assert result.returncode == 0
