import subprocess
from tests.runtime_fixture import runtime_dir

def test_new_empty(runtime_dir):
    result = subprocess.run(
        ["python", "src/kiss.py", "-d", "runtime", "list", "-r", "-d" ],
        capture_output=True,
        text=True,
    )
    print(result.stdout)
    print(result.stderr)
    assert result.returncode == 0

def create_project():
    # Create a bin project
    result = subprocess.run(
        ["python", "src/kiss.py", "-d", "runtime", "new", "bin", "my_bin" ],
        capture_output=True,
        text=True,
    )
    print(result.stdout)
    print(result.stderr)
    assert result.returncode == 0

    # Create a dyn project
    result = subprocess.run(
        ["python", "src/kiss.py", "-d", "runtime", "new", "dyn", "my_dyn" ],
        capture_output=True,
        text=True,
    )
    print(result.stdout)
    print(result.stderr)
    assert result.returncode == 0

    # Create a lib project
    result = subprocess.run(
        ["python", "src/kiss.py", "-d", "runtime", "new", "lib", "my_lib" ],
        capture_output=True,
        text=True,
    )
    print(result.stdout)
    print(result.stderr)
    assert result.returncode == 0


    # Create a lib project
    result = subprocess.run(
        ["python", "src/kiss.py", "-d", "runtime/my_bin", "new", "-e", "lib", "my_inner_lib" ],
        capture_output=True,
        text=True,
    )
    print(result.stdout)
    print(result.stderr)
    assert result.returncode == 0

def test_new(runtime_dir):
    # Create project to list
    create_project()
    result = subprocess.run(
        ["python", "src/kiss.py", "-d", "runtime", "list", "-r", "-d" ],
        capture_output=True,
        text=True,
    )
    print(result.stdout)
    print(result.stderr)
    assert result.returncode == 0
