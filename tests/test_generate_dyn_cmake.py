from tests.runtime_fixture import runtime_dir, RUNTIME_DIR
from tests.common import *

# Test generation of a single dyn project
# The single dyn project must be generated and found automatically
def test_generate_dyn_default(runtime_dir):
    dyn_type = "dyn"
    dyn_name = "my_dyn"
    new_project([dyn_type, dyn_name])

    assert generate_project(directory=RUNTIME_DIR/dyn_name) == 0

    # Find CMakeLists.txt
    files = find_cmake_files(RUNTIME_DIR)
    assert len(files) == 1
    validate_cmakelist_path(path=files[0],
                            project_name=dyn_name)

    assert generate_project(directory=RUNTIME_DIR/dyn_name) == 0

    # Find CMakeLists.txt
    files = find_cmake_files(RUNTIME_DIR)
    assert len(files) == 1
    validate_cmakelist_path(path=files[0],
                            project_name=dyn_name)

# Test generation of a two dyn project in the same root directory
# But without dependency
# The single dyn project in the given directory must be generated and found automatically
def test_generate_dyn_default_inner(runtime_dir):
    ## SETUP
    dyn_type = "dyn"
    dyn_name = "my_dyn"
    new_project([dyn_type, dyn_name])
    dyn_2_name = "my_inner_dyn"
    new_inner_project(dyn_name, [dyn_type, dyn_2_name])

    ## TEST
    assert generate_project(directory=RUNTIME_DIR/dyn_name) == 0

    # Find CMakeLists.txt
    files = find_cmake_files(RUNTIME_DIR)
    assert len(files) == 1
    validate_cmakelist_path(path=files[0],
                            project_name=dyn_name)
    
    assert generate_project(directory=RUNTIME_DIR/dyn_name/dyn_2_name) == 0

    # Find CMakeLists.txt
    files = find_cmake_files(RUNTIME_DIR)
    assert len(files) == 2
    dyn_file = [f for f in files if dyn_name in str(f.parent.parent.name)]
    validate_cmakelist_path(path=dyn_file[0],
                            project_name=dyn_name)
    dyn_2_file = [f for f in files if dyn_2_name in str(f.parent.parent.name)]
    validate_cmakelist_path(path=dyn_2_file[0],
                            project_name=dyn_2_name)

# Test generation of a two dyn project in the same root directory
# dyn in root directory depends of inner dyn, user must provide the name of the projec to generate
# kiss see both project and can't select which one is the default
def test_generate_dyn_no_depends(runtime_dir):
    ## SETUP
    dyn_type = "dyn"
    dyn_name = "my_dyn"
    new_project([dyn_type, dyn_name])

    # Create 'my_inner_dyn' inner dependency of 'my_dyn'
    dyn_2_name = "my_inner_dyn"
    new_inner_project(dyn_name, ["-e", dyn_type, dyn_2_name])

    # Add 'my_inner_dyn' as dependency of 'my_dyn'
    add_dependency(dyn_name, [dyn_2_name])

    ## TEST
    # If no name is given, kiss must fail
    assert generate_project(directory=RUNTIME_DIR/dyn_name) == 1
    
    # user must specify a name to generate
    assert generate_project(directory=RUNTIME_DIR/dyn_name,
                            args= ["-p", "my_inner_dyn"]) == 0

    # Find CMakeLists.txt
    # Only one must be present because my_inner_dyn depends on nothing
    files = find_cmake_files(RUNTIME_DIR)
    assert len(files) == 1
    validate_cmakelist_path(path=files[0],
                            project_name=dyn_2_name)


# Test generation of a two dyn project in the same root directory
# dyn in root directory depends of inner dyn, user must provide the name of the projec to generate
# kiss see both project and can't select which one is the default
def test_generate_dyn_depends(runtime_dir):
    ## SETUP
    dyn_type = "dyn"
    dyn_name = "my_dyn"
    new_project([dyn_type, dyn_name])

    # Create 'my_inner_dyn' inner dependency of 'my_dyn'
    dyn_2_name = "my_inner_dyn"
    new_inner_project(dyn_name, ["-e", dyn_type, dyn_2_name])

    # Add 'my_inner_dyn' as dependency of 'my_dyn'
    add_dependency(dyn_name, [dyn_2_name])

    ## TEST
    # If no name is given, kiss must fail
    assert generate_project(directory=RUNTIME_DIR/dyn_name) == 1
    
    # user must specify a name to generate
    assert generate_project(directory=RUNTIME_DIR/dyn_name,
                            args= ["-p", "my_dyn"]) == 0

    # Find CMakeLists.txt
    # Only one must be present because my_inner_dyn depends on nothing
    files = find_cmake_files(RUNTIME_DIR)
    assert len(files) == 2
    dyn_file = [f for f in files if dyn_name in str(f.parent.parent.name)]
    validate_cmakelist_path(path=dyn_file[0],
                            project_name=dyn_name)
    dyn_2_file = [f for f in files if dyn_2_name in str(f.parent.parent.name)]
    validate_cmakelist_path(path=dyn_2_file[0],
                            project_name=dyn_2_name)


# Test generation of a two dyn project in the same root directory
# dyn in root directory depends of inner dyn, user must provide the name of the projec to generate
# kiss see both project and can't select which one is the default
def test_generate_dyn_profile(runtime_dir):
    ## SETUP
    dyn_type = "dyn"
    dyn_name = "my_dyn"
    new_project([dyn_type, dyn_name])

    # Create 'my_inner_dyn' inner dependency of 'my_dyn'
    dyn_2_name = "my_inner_dyn"
    new_inner_project(dyn_name, ["-e", dyn_type, dyn_2_name])

    # Add 'my_inner_dyn' as dependency of 'my_dyn'
    add_dependency(dyn_name, [dyn_2_name])

    ## TEST
    profile_name = "release"
    assert profile_name != DEFAULT_PROFILE_NAME

    # user must specify a name to generate
    assert generate_project(directory=RUNTIME_DIR/dyn_name,
                            args= ["-p", "my_dyn", "--profile", profile_name]) == 0

    # Find CMakeLists.txt
    # Only one must be present because my_inner_dyn depends on nothing
    files = find_cmake_files(RUNTIME_DIR)
    assert len(files) == 2
    dyn_file = [f for f in files if dyn_name in str(f.parent.parent.name)]
    validate_cmakelist_path(path=dyn_file[0],
                            project_name=dyn_name,
                            profile_name=profile_name)
    dyn_2_file = [f for f in files if dyn_2_name in str(f.parent.parent.name)]
    validate_cmakelist_path(path=dyn_2_file[0],
                            project_name=dyn_2_name,
                            profile_name=profile_name)

# Test generation of a two dyn project in the same root directory
# dyn in root directory depends of inner dyn, user must provide the name of the projec to generate
# kiss see both project and can't select which one is the default
def test_generate_dyn_target(runtime_dir):
    ## SETUP
    dyn_type = "dyn"
    dyn_name = "my_dyn"
    new_project([dyn_type, dyn_name])

    # Create 'my_inner_dyn' inner dependency of 'my_dyn'
    dyn_2_name = "my_inner_dyn"
    new_inner_project(dyn_name, ["-e", dyn_type, dyn_2_name])

    # Add 'my_inner_dyn' as dependency of 'my_dyn'
    add_dependency(dyn_name, [dyn_2_name])

    ## TEST
    target_name = "i686-unknown-linux-gnu"
    assert target_name != DEFAULT_TARGET_NAME
    # user must specify a name to generate
    assert generate_project(directory=RUNTIME_DIR/dyn_name,
                            args= ["-p", "my_dyn", "--target", "i686-unknown-linux-gnu"]) == 0

    # Find CMakeLists.txt
    # Only one must be present because my_inner_dyn depends on nothing
    files = find_cmake_files(RUNTIME_DIR)
    assert len(files) == 2
    dyn_file = [f for f in files if dyn_name in str(f.parent.parent.name)]
    validate_cmakelist_path(path=dyn_file[0],
                            project_name=dyn_name,
                            target_name=target_name)
    dyn_2_file = [f for f in files if dyn_2_name in str(f.parent.parent.name)]
    validate_cmakelist_path(path=dyn_2_file[0],
                            project_name=dyn_2_name,
                            target_name=target_name)


# Test generation of a two dyn project in the same root directory
# dyn in root directory depends of inner dyn, user must provide the name of the projec to generate
# kiss see both project and can't select which one is the default
def test_generate_dyn_compiler(runtime_dir):
    ## SETUP
    dyn_type = "dyn"
    dyn_name = "my_dyn"
    new_project([dyn_type, dyn_name])

    # Create 'my_inner_dyn' inner dependency of 'my_dyn'
    dyn_2_name = "my_inner_dyn"
    new_inner_project(dyn_name, ["-e", dyn_type, dyn_2_name])

    # Add 'my_inner_dyn' as dependency of 'my_dyn'
    add_dependency(dyn_name, [dyn_2_name])

    ## TEST
    compiler_name = "clang"
    assert compiler_name != DEFAULT_COMPILER_NAME
    # user must specify a name to generate
    assert generate_project(directory=RUNTIME_DIR/dyn_name,
                            args= ["-p", "my_dyn", "--compiler", compiler_name]) == 0

    # Find CMakeLists.txt
    # Only one must be present because my_inner_dyn depends on nothing
    files = find_cmake_files(RUNTIME_DIR)
    assert len(files) == 2
    dyn_file = [f for f in files if dyn_name in str(f.parent.parent.name)]
    validate_cmakelist_path(path=dyn_file[0],
                            project_name=dyn_name,
                            compiler_name=compiler_name)
    dyn_2_file = [f for f in files if dyn_2_name in str(f.parent.parent.name)]
    validate_cmakelist_path(path=dyn_2_file[0],
                            project_name=dyn_2_name,
                            compiler_name=compiler_name)
