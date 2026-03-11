from tests.runtime_fixture import runtime_dir, RUNTIME_DIR
from tests.common import *

def test_generate_dyn_default(runtime_dir):
    dyn_type = "dyn"
    dyn_name = "my_dyn"
    new_project([dyn_type, dyn_name])

    assert generate_project(directory= RUNTIME_DIR/dyn_name) == 0

    # Find CMakeLists.txt
    files = find_cmake_files(RUNTIME_DIR)
    assert len(files) == 1
    validate_cmakelist_path(path=files[0],
                            project_name=dyn_name)

    assert generate_project(directory= RUNTIME_DIR/dyn_name) == 0

    # Find CMakeLists.txt
    files = find_cmake_files(RUNTIME_DIR)
    assert len(files) == 1
    validate_cmakelist_path(path=files[0],
                            project_name=dyn_name)