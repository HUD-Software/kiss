from tests.runtime_fixture import runtime_dir
from tests.common import *

# Test generation of a single bin project
# The single bin project must be generated and found automatically
def test_generate_bin_default(runtime_dir):
    bin_type = "bin"
    bin_name = "my_bin"
    new_project([bin_type, bin_name])

    assert generate_project(directory=RUNTIME_DIR/bin_name) == 0

    # Find CMakeLists.txt
    files = find_cmake_files(RUNTIME_DIR)
    assert len(files) == 1
    validate_cmakelist_path(path=files[0],
                            project_name=bin_name)

    assert generate_project(directory=RUNTIME_DIR/bin_name) == 0

    # Find CMakeLists.txt
    files = find_cmake_files(RUNTIME_DIR)
    assert len(files) == 1
    validate_cmakelist_path(path=files[0],
                            project_name=bin_name)

# Test generation of a two bin project in the same root directory
# But without dependency
# The single bin project in the given directory must be generated and found automatically
def test_generate_bin_default_inner(runtime_dir):
    ## SETUP
    bin_type = "bin"
    bin_name = "my_bin"
    new_project([bin_type, bin_name])
    bin_2_name = "my_bin_2"
    new_inner_project(bin_name, [bin_type, bin_2_name])

    ## TEST
    assert generate_project(directory=RUNTIME_DIR/bin_name) == 0

    # Find CMakeLists.txt
    files = find_cmake_files(RUNTIME_DIR)
    assert len(files) == 1
    validate_cmakelist_path(path=files[0],
                            project_name=bin_name)
    
    assert generate_project(directory=RUNTIME_DIR/bin_name/bin_2_name) == 0

    # Find CMakeLists.txt
    files = find_cmake_files(RUNTIME_DIR)
    assert len(files) == 2
    validate_cmakelist_path(path=files[0],
                            project_name=bin_name)
    validate_cmakelist_path(path=files[1],
                            project_name=bin_2_name)

# Test generation of a two bin project in the same root directory
# bin in root directory depends of inner bin, user must provide the name of the projec to generate
# kiss see both project and can't select which one is the default
def test_generate_bin_no_depends(runtime_dir):
    ## SETUP
    bin_project_type = "bin"
    bin_name = "my_bin"
    new_project([bin_project_type, bin_name])

    # Create 'my_bin_2' inner dependency of 'my_bin'
    bin_2_name = "my_bin_2"
    new_inner_project(bin_name, ["-e", bin_project_type, bin_2_name])

    # Add 'my_bin_2' as dependency of 'my_bin'
    add_dependency(bin_name, [bin_2_name])

    ## TEST
    # If no name is given, kiss must fail
    assert generate_project(directory=RUNTIME_DIR/bin_name) == 1
    
    # user must specify a name to generate
    assert generate_project(directory=RUNTIME_DIR/bin_name,
                            args= ["-p", "my_bin_2"]) == 0

    # Find CMakeLists.txt
    # Only one must be present because my_bin_2 depends on nothing
    files = find_cmake_files(RUNTIME_DIR)
    assert len(files) == 1
    validate_cmakelist_path(path=files[0],
                            project_name=bin_2_name)


# Test generation of a two bin project in the same root directory
# bin in root directory depends of inner bin, user must provide the name of the projec to generate
# kiss see both project and can't select which one is the default
def test_generate_bin_depends(runtime_dir):
    ## SETUP
    bin_project_type = "bin"
    bin_name = "my_bin"
    new_project([bin_project_type, bin_name])

    # Create 'my_bin_2' inner dependency of 'my_bin'
    bin_2_name = "my_bin_2"
    new_inner_project(bin_name, ["-e", bin_project_type, bin_2_name])

    # Add 'my_bin_2' as dependency of 'my_bin'
    add_dependency(bin_name, [bin_2_name])

    ## TEST
    # If no name is given, kiss must fail
    assert generate_project(directory=RUNTIME_DIR/bin_name) == 1
    
    # user must specify a name to generate
    assert generate_project(directory=RUNTIME_DIR/bin_name,
                            args= ["-p", "my_bin"]) == 0

    # Find CMakeLists.txt
    # Only one must be present because my_bin_2 depends on nothing
    files = find_cmake_files(RUNTIME_DIR)
    assert len(files) == 2
    validate_cmakelist_path(path=files[0],
                            project_name=bin_name)
    validate_cmakelist_path(path=files[1],
                            project_name=bin_2_name)


# Test generation of a two bin project in the same root directory
# bin in root directory depends of inner bin, user must provide the name of the projec to generate
# kiss see both project and can't select which one is the default
def test_generate_bin_profile(runtime_dir):
    ## SETUP
    bin_project_type = "bin"
    bin_name = "my_bin"
    new_project([bin_project_type, bin_name])

    # Create 'my_bin_2' inner dependency of 'my_bin'
    bin_2_name = "my_bin_2"
    new_inner_project(bin_name, ["-e", bin_project_type, bin_2_name])

    # Add 'my_bin_2' as dependency of 'my_bin'
    add_dependency(bin_name, [bin_2_name])

    ## TEST
    profile_name = "release"
    assert profile_name != DEFAULT_PROFILE_NAME

    # user must specify a name to generate
    assert generate_project(directory=RUNTIME_DIR/bin_name,
                            args= ["-p", "my_bin", "--profile", profile_name]) == 0

    # Find CMakeLists.txt
    # Only one must be present because my_bin_2 depends on nothing
    files = find_cmake_files(RUNTIME_DIR)
    assert len(files) == 2
    validate_cmakelist_path(path=files[0],
                            project_name=bin_name,
                            profile_name=profile_name)
    validate_cmakelist_path(path=files[1],
                            project_name=bin_2_name,
                            profile_name=profile_name)

# Test generation of a two bin project in the same root directory
# bin in root directory depends of inner bin, user must provide the name of the projec to generate
# kiss see both project and can't select which one is the default
def test_generate_bin_target(runtime_dir):
    ## SETUP
    bin_project_type = "bin"
    bin_name = "my_bin"
    new_project([bin_project_type, bin_name])

    # Create 'my_bin_2' inner dependency of 'my_bin'
    bin_2_name = "my_bin_2"
    new_inner_project(bin_name, ["-e", bin_project_type, bin_2_name])

    # Add 'my_bin_2' as dependency of 'my_bin'
    add_dependency(bin_name, [bin_2_name])

    ## TEST
    target_name = "i686-unknown-linux-gnu"
    assert target_name != DEFAULT_TARGET_NAME
    # user must specify a name to generate
    assert generate_project(directory=RUNTIME_DIR/bin_name,
                            args= ["-p", "my_bin", "--target", "i686-unknown-linux-gnu"]) == 0

    # Find CMakeLists.txt
    # Only one must be present because my_bin_2 depends on nothing
    files = find_cmake_files(RUNTIME_DIR)
    assert len(files) == 2
    validate_cmakelist_path(path=files[0],
                            project_name=bin_name,
                            target_name=target_name)
    validate_cmakelist_path(path=files[1],
                            project_name=bin_2_name,
                            target_name=target_name)


# Test generation of a two bin project in the same root directory
# bin in root directory depends of inner bin, user must provide the name of the projec to generate
# kiss see both project and can't select which one is the default
def test_generate_bin_compiler(runtime_dir):
    ## SETUP
    bin_project_type = "bin"
    bin_name = "my_bin"
    new_project([bin_project_type, bin_name])

    # Create 'my_bin_2' inner dependency of 'my_bin'
    bin_2_name = "my_bin_2"
    new_inner_project(bin_name, ["-e", bin_project_type, bin_2_name])

    # Add 'my_bin_2' as dependency of 'my_bin'
    add_dependency(bin_name, [bin_2_name])

    ## TEST
    compiler_name = "clang"
    assert compiler_name != DEFAULT_COMPILER_NAME
    # user must specify a name to generate
    assert generate_project(directory=RUNTIME_DIR/bin_name,
                            args= ["-p", "my_bin", "--compiler", compiler_name]) == 0

    # Find CMakeLists.txt
    # Only one must be present because my_bin_2 depends on nothing
    files = find_cmake_files(RUNTIME_DIR)
    assert len(files) == 2
    validate_cmakelist_path(path=files[0],
                            project_name=bin_name,
                            compiler_name=compiler_name)
    validate_cmakelist_path(path=files[1],
                            project_name=bin_2_name,
                            compiler_name=compiler_name)
