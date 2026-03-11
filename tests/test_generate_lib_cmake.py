from tests.runtime_fixture import runtime_dir, RUNTIME_DIR
from tests.common import *

def test_generate_lib_default(runtime_dir):
    lib_type = "lib"
    lib_name = "my_lib"
    new_project([lib_type, lib_name])

    assert generate_project(directory= RUNTIME_DIR/lib_name) == 0

    # Find CMakeLists.txt
    files = find_cmake_files(RUNTIME_DIR)
    assert len(files) == 1
    validate_cmakelist_path(path=files[0],
                            project_name=lib_name)

    assert generate_project(directory= RUNTIME_DIR/lib_name) == 0

    # Find CMakeLists.txt
    files = find_cmake_files(RUNTIME_DIR)
    assert len(files) == 1
    validate_cmakelist_path(path=files[0],
                            project_name=lib_name)
