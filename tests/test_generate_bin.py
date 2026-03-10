from pathlib import Path

from tests.runtime_fixture import runtime_dir, RUNTIME_DIR
from tests.common import new_project, generate_project

def find_cmake_files(root):
    return list(Path(root).rglob("CMakeLists.txt"))

def test_generate_bin_default(runtime_dir):
    project_type = "bin"
    project_name = "my_bin"
    new_project([project_type, project_name])

    generate_project(project_name)

    # Find CMakeLists.txt
    files = find_cmake_files(RUNTIME_DIR)
    assert len(files) == 1

