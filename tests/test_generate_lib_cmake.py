from tests.runtime_fixture import runtime_dir, RUNTIME_DIR
from tests.common import *

# Test generation of a single lib project
# The single lib project must be generated and found automatically
def test_generate_lib_default(runtime_dir):
    lib_type = "lib"
    lib_name = "my_lib"
    new_project([lib_type, lib_name])

    assert generate_project(directory=RUNTIME_DIR/lib_name) == 0

    # Find CMakeLists.txt
    files = find_cmake_files(RUNTIME_DIR)
    assert len(files) == 1
    validate_cmakelist_path(path=files[0],
                            project_name=lib_name)

    assert generate_project(directory=RUNTIME_DIR/lib_name) == 0

    # Find CMakeLists.txt
    files = find_cmake_files(RUNTIME_DIR)
    assert len(files) == 1
    validate_cmakelist_path(path=files[0],
                            project_name=lib_name)

# Test generation of a two lib project in the same root directory
# But without dependency
# The single lib project in the given directory must be generated and found automatically
def test_generate_lib_default_inner(runtime_dir):
    ## SETUP
    lib_type = "lib"
    lib_name = "my_lib"
    new_project([lib_type, lib_name])
    lib_2_name = "my_inner_lib"
    new_inner_project(lib_name, [lib_type, lib_2_name])

    ## TEST
    assert generate_project(directory=RUNTIME_DIR/lib_name) == 0

    # Find CMakeLists.txt
    files = find_cmake_files(RUNTIME_DIR)
    assert len(files) == 1
    validate_cmakelist_path(path=files[0],
                            project_name=lib_name)
    
    assert generate_project(directory=RUNTIME_DIR/lib_name/lib_2_name) == 0

    # Find CMakeLists.txt
    files = find_cmake_files(RUNTIME_DIR)
    assert len(files) == 2
    lib_file = [f for f in files if lib_name in str(f.parent.parent.name)]
    validate_cmakelist_path(path=lib_file[0],
                            project_name=lib_name)
    lib_2_file = [f for f in files if lib_2_name in str(f.parent.parent.name)]
    validate_cmakelist_path(path=lib_2_file[0],
                            project_name=lib_2_name)

# Test generation of a two lib project in the same root directory
# lib in root directory depends of inner lib, user must provide the name of the projec to generate
# kiss see both project and can't select which one is the default
def test_generate_lib_no_depends(runtime_dir):
    ## SETUP
    lib_type = "lib"
    lib_name = "my_lib"
    new_project([lib_type, lib_name])

    # Create 'my_inner_lib' inner dependency of 'my_lib'
    lib_2_name = "my_inner_lib"
    new_inner_project(lib_name, ["-e", lib_type, lib_2_name])

    # Add 'my_inner_lib' as dependency of 'my_lib'
    add_dependency(lib_name, [lib_2_name])

    ## TEST
    # If no name is given, kiss must fail
    assert generate_project(directory=RUNTIME_DIR/lib_name) == 1
    
    # user must specify a name to generate
    assert generate_project(directory=RUNTIME_DIR/lib_name,
                            args= ["-p", "my_inner_lib"]) == 0

    # Find CMakeLists.txt
    # Only one must be present because my_inner_lib depends on nothing
    files = find_cmake_files(RUNTIME_DIR)
    assert len(files) == 1
    validate_cmakelist_path(path=files[0],
                            project_name=lib_2_name)


# Test generation of a two lib project in the same root directory
# lib in root directory depends of inner lib, user must provide the name of the projec to generate
# kiss see both project and can't select which one is the default
def test_generate_lib_depends(runtime_dir):
    ## SETUP
    lib_type = "lib"
    lib_name = "my_lib"
    new_project([lib_type, lib_name])

    # Create 'my_inner_lib' inner dependency of 'my_lib'
    lib_2_name = "my_inner_lib"
    new_inner_project(lib_name, ["-e", lib_type, lib_2_name])

    # Add 'my_inner_lib' as dependency of 'my_lib'
    add_dependency(lib_name, [lib_2_name])

    ## TEST
    # If no name is given, kiss must fail
    assert generate_project(directory=RUNTIME_DIR/lib_name) == 1
    
    # user must specify a name to generate
    assert generate_project(directory=RUNTIME_DIR/lib_name,
                            args= ["-p", "my_lib"]) == 0

    # Find CMakeLists.txt
    # Only one must be present because my_inner_lib depends on nothing
    files = find_cmake_files(RUNTIME_DIR)
    assert len(files) == 2
    lib_file = [f for f in files if lib_name in str(f.parent.parent.name)]
    validate_cmakelist_path(path=lib_file[0],
                            project_name=lib_name)
    lib_2_file = [f for f in files if lib_2_name in str(f.parent.parent.name)]
    validate_cmakelist_path(path=lib_2_file[0],
                            project_name=lib_2_name)


# Test generation of a two lib project in the same root directory
# lib in root directory depends of inner lib, user must provide the name of the projec to generate
# kiss see both project and can't select which one is the default
def test_generate_lib_profile(runtime_dir):
    ## SETUP
    lib_type = "lib"
    lib_name = "my_lib"
    new_project([lib_type, lib_name])

    # Create 'my_inner_lib' inner dependency of 'my_lib'
    lib_2_name = "my_inner_lib"
    new_inner_project(lib_name, ["-e", lib_type, lib_2_name])

    # Add 'my_inner_lib' as dependency of 'my_lib'
    add_dependency(lib_name, [lib_2_name])

    ## TEST
    profile_name = "release"
    assert profile_name != DEFAULT_PROFILE_NAME

    # user must specify a name to generate
    assert generate_project(directory=RUNTIME_DIR/lib_name,
                            args= ["-p", "my_lib", "--profile", profile_name]) == 0

    # Find CMakeLists.txt
    # Only one must be present because my_inner_lib depends on nothing
    files = find_cmake_files(RUNTIME_DIR)
    assert len(files) == 2
    lib_file = [f for f in files if lib_name in str(f.parent.parent.name)]
    validate_cmakelist_path(path=lib_file[0],
                            project_name=lib_name,
                            profile_name=profile_name)
    lib_2_file = [f for f in files if lib_2_name in str(f.parent.parent.name)]
    validate_cmakelist_path(path=lib_2_file[0],
                            project_name=lib_2_name,
                            profile_name=profile_name)

# Test generation of a two lib project in the same root directory
# lib in root directory depends of inner lib, user must provide the name of the projec to generate
# kiss see both project and can't select which one is the default
def test_generate_lib_target(runtime_dir):
    ## SETUP
    lib_type = "lib"
    lib_name = "my_lib"
    new_project([lib_type, lib_name])

    # Create 'my_inner_lib' inner dependency of 'my_lib'
    lib_2_name = "my_inner_lib"
    new_inner_project(lib_name, ["-e", lib_type, lib_2_name])

    # Add 'my_inner_lib' as dependency of 'my_lib'
    add_dependency(lib_name, [lib_2_name])

    ## TEST
    target_name = "i686-unknown-linux-gnu"
    assert target_name != DEFAULT_TARGET_NAME
    # user must specify a name to generate
    assert generate_project(directory=RUNTIME_DIR/lib_name,
                            args= ["-p", "my_lib", "--target", "i686-unknown-linux-gnu"]) == 0

    # Find CMakeLists.txt
    # Only one must be present because my_inner_lib depends on nothing
    files = find_cmake_files(RUNTIME_DIR)
    assert len(files) == 2
    lib_file = [f for f in files if lib_name in str(f.parent.parent.name)]
    validate_cmakelist_path(path=lib_file[0],
                            project_name=lib_name,
                            target_name=target_name)
    lib_2_file = [f for f in files if lib_2_name in str(f.parent.parent.name)]
    validate_cmakelist_path(path=lib_2_file[0],
                            project_name=lib_2_name,
                            target_name=target_name)


# Test generation of a two lib project in the same root directory
# lib in root directory depends of inner lib, user must provide the name of the projec to generate
# kiss see both project and can't select which one is the default
def test_generate_lib_compiler(runtime_dir):
    ## SETUP
    lib_type = "lib"
    lib_name = "my_lib"
    new_project([lib_type, lib_name])

    # Create 'my_inner_lib' inner dependency of 'my_lib'
    lib_2_name = "my_inner_lib"
    new_inner_project(lib_name, ["-e", lib_type, lib_2_name])

    # Add 'my_inner_lib' as dependency of 'my_lib'
    add_dependency(lib_name, [lib_2_name])

    ## TEST
    compiler_name = "clang"
    assert compiler_name != DEFAULT_COMPILER_NAME
    # user must specify a name to generate
    assert generate_project(directory=RUNTIME_DIR/lib_name,
                            args= ["-p", "my_lib", "--compiler", compiler_name]) == 0

    # Find CMakeLists.txt
    # Only one must be present because my_inner_lib depends on nothing
    files = find_cmake_files(RUNTIME_DIR)
    assert len(files) == 2
    lib_file = [f for f in files if lib_name in str(f.parent.parent.name)]
    validate_cmakelist_path(path=lib_file[0],
                            project_name=lib_name,
                            compiler_name=compiler_name)
    lib_2_file = [f for f in files if lib_2_name in str(f.parent.parent.name)]
    validate_cmakelist_path(path=lib_2_file[0],
                            project_name=lib_2_name,
                            compiler_name=compiler_name)
