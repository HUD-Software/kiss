from tests.common import *

# Test build of a single dyn project
# The single dyn project must be build and found automatically
def test_build_dyn_default(runtime_dir):
    dyn_type = "dyn"
    dyn_name = "my_dyn"
    new_project([dyn_type, dyn_name])

    assert build_project(directory=RUNTIME_DIR/dyn_name) == 0

    files = find_cmake_files(RUNTIME_DIR)
    assert len(files) == 1
    toolchain  = Toolchain.create(compiler_name=DEFAULT_COMPILER_NAME, 
                                  target_name=DEFAULT_TARGET_NAME, 
                                  profile_name=DEFAULT_PROFILE_NAME)
    cmake_generator_name =  CMakeGeneratorName.create(toolchain=toolchain)
    validate_build(cmake_filepath=files[0],
                   project_name=dyn_name,
                   project_type=dyn_type,
                   toolchain=toolchain,
                   cmake_generator_name=cmake_generator_name)
    
# Test build of a two dyn project in the same root directory
# But without dependency
# The single dyn project in the given directory must be build and found automatically
def test_build_dyn_default_inner(runtime_dir):
    ## SETUP
    dyn_type = "dyn"
    dyn_name = "my_dyn"
    new_project([dyn_type, dyn_name])
    dyn_2_name = "my_inner_dyn"
    new_inner_project(dyn_name, [dyn_type, dyn_2_name])

    ## TEST
    assert build_project(directory=RUNTIME_DIR/dyn_name) == 0

    # Find CMakeLists.txt
    files = find_cmake_files(RUNTIME_DIR)
    assert len(files) == 1
    toolchain  = Toolchain.create(compiler_name=DEFAULT_COMPILER_NAME, 
                                  target_name=DEFAULT_TARGET_NAME,
                                  profile_name=DEFAULT_PROFILE_NAME)
    cmake_generator_name =  CMakeGeneratorName.create(toolchain=toolchain)

    validate_build(cmake_filepath=files[0],
                   project_name=dyn_name,
                   project_type=dyn_type,
                   toolchain=toolchain,
                   cmake_generator_name=cmake_generator_name)
    
    assert build_project(directory=RUNTIME_DIR/dyn_name/dyn_2_name) == 0

    # Find CMakeLists.txt
    files = find_cmake_files(RUNTIME_DIR)
    assert len(files) == 2
    toolchain  = Toolchain.create(compiler_name=DEFAULT_COMPILER_NAME, 
                                  target_name=DEFAULT_TARGET_NAME,
                                  profile_name=DEFAULT_PROFILE_NAME)
    cmake_generator_name =  CMakeGeneratorName.create(toolchain=toolchain)
    if cmake_generator_name.is_single_profile():
        dyn_file = [f for f in files if dyn_name in str(f.parent.parent.name)]
        validate_build(cmake_filepath=dyn_file[0],
                    project_name=dyn_name,
                    project_type=dyn_type,
                    toolchain=toolchain,
                    cmake_generator_name=cmake_generator_name)
        dyn_2_file = [f for f in files if dyn_2_name in str(f.parent.parent.name)]
        validate_build(cmake_filepath=dyn_2_file[0],
                    project_name=dyn_2_name,
                    project_type=dyn_type,
                    toolchain=toolchain,
                    cmake_generator_name=cmake_generator_name)
    elif cmake_generator_name.is_multi_profile():
        dyn_file = [f for f in files if dyn_name in str(f.parent.name)]
        validate_build(cmake_filepath=dyn_file[0],
                    project_name=dyn_name,
                    project_type=dyn_type,
                    toolchain=toolchain,
                    cmake_generator_name=cmake_generator_name)
        dyn_2_file = [f for f in files if dyn_2_name in str(f.parent.name)]
        validate_build(cmake_filepath=dyn_2_file[0],
                    project_name=dyn_2_name,
                    project_type=dyn_type,
                    toolchain=toolchain,
                    cmake_generator_name=cmake_generator_name)
    else:
        assert False



# Test build of a two dyn project in the same root directory
# dyn in root directory depends of inner dyn, user must provide the name of the projec to build
# kiss see both project and can't select which one is the default
def test_build_dyn_no_depends(runtime_dir):
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
    assert build_project(directory=RUNTIME_DIR/dyn_name) == 1
    
    # user must specify a name to build
    assert build_project(directory=RUNTIME_DIR/dyn_name,
                            args= ["-p", "my_inner_dyn"]) == 0

    # Find CMakeLists.txt
    # Only one must be present because my_inner_dyn depends on nothing
    files = find_cmake_files(RUNTIME_DIR)
    assert len(files) == 1
    toolchain  = Toolchain.create(compiler_name=DEFAULT_COMPILER_NAME, 
                                  target_name=DEFAULT_TARGET_NAME,
                                  profile_name=DEFAULT_PROFILE_NAME)
    cmake_generator_name =  CMakeGeneratorName.create(toolchain=toolchain)
    validate_build(cmake_filepath=files[0],
                   project_name=dyn_2_name,
                   project_type=dyn_type,
                   toolchain=toolchain,
                   cmake_generator_name=cmake_generator_name)
    
# Test build of a two dyn project in the same root directory
# dyn in root directory depends of inner dyn, user must provide the name of the projec to build
# kiss see both project and can't select which one is the default
def test_build_dyn_depends(runtime_dir):
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
    assert build_project(directory=RUNTIME_DIR/dyn_name) == 1
    
    # user must specify a name to build
    assert build_project(directory=RUNTIME_DIR/dyn_name,
                            args= ["-p", "my_dyn"]) == 0

    # Find CMakeLists.txt
    # Only one must be present because my_inner_dyn depends on nothing
    files = find_cmake_files(RUNTIME_DIR)
    assert len(files) == 2
    toolchain  = Toolchain.create(compiler_name=DEFAULT_COMPILER_NAME, 
                                  target_name=DEFAULT_TARGET_NAME,
                                  profile_name=DEFAULT_PROFILE_NAME)
    cmake_generator_name =  CMakeGeneratorName.create(toolchain=toolchain)
    if cmake_generator_name.is_single_profile():
        dyn_file = [f for f in files if dyn_name in str(f.parent.parent.name)]
        validate_build(cmake_filepath=dyn_file[0],
                    project_name=dyn_name,
                    project_type=dyn_type,
                    toolchain=toolchain,
                    cmake_generator_name=cmake_generator_name)
        dyn_2_file = [f for f in files if dyn_2_name in str(f.parent.parent.name)]
        validate_build(cmake_filepath=dyn_2_file[0],
                    project_name=dyn_2_name,
                    project_type=dyn_type,
                    toolchain=toolchain,
                    cmake_generator_name=cmake_generator_name)
    elif cmake_generator_name.is_multi_profile():
        dyn_file = [f for f in files if dyn_name in str(f.parent.name)]
        validate_build(cmake_filepath=dyn_file[0],
                    project_name=dyn_name,
                    project_type=dyn_type,
                    toolchain=toolchain,
                    cmake_generator_name=cmake_generator_name)
        dyn_2_file = [f for f in files if dyn_2_name in str(f.parent.name)]
        validate_build(cmake_filepath=dyn_2_file[0],
                    project_name=dyn_2_name,
                    project_type=dyn_type,
                    toolchain=toolchain,
                    cmake_generator_name=cmake_generator_name)
    else:
        assert False

# Test build of a two dyn project in the same root directory
# dyn in root directory depends of inner dyn, user must provide the name of the projec to build
# kiss see both project and can't select which one is the default
def test_build_dyn_profile(runtime_dir):
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

    # user must specify a name to build
    assert build_project(directory=RUNTIME_DIR/dyn_name,
                            args= ["-p", "my_dyn", "--profile", profile_name]) == 0

    # Find CMakeLists.txt
    # Only one must be present because my_inner_dyn depends on nothing
    files = find_cmake_files(RUNTIME_DIR)
    assert len(files) == 2
    toolchain  = Toolchain.create(compiler_name=DEFAULT_COMPILER_NAME, 
                                  target_name=DEFAULT_TARGET_NAME,
                                  profile_name=profile_name)
    cmake_generator_name =  CMakeGeneratorName.create(toolchain=toolchain)
    if cmake_generator_name.is_single_profile():
        dyn_file = [f for f in files if dyn_name in str(f.parent.parent.name)]
        validate_build(cmake_filepath=dyn_file[0],
                       project_name=dyn_name,
                       project_type=dyn_type,
                       toolchain=toolchain,
                       cmake_generator_name=cmake_generator_name)
        dyn_2_file = [f for f in files if dyn_2_name in str(f.parent.parent.name)]
        validate_build(cmake_filepath=dyn_2_file[0],
                       project_name=dyn_2_name,
                       project_type=dyn_type,
                       toolchain=toolchain,
                       cmake_generator_name=cmake_generator_name)
    elif cmake_generator_name.is_multi_profile():
        dyn_file = [f for f in files if dyn_name in str(f.parent.name)]
        validate_build(cmake_filepath=dyn_file[0],
                       project_name=dyn_name,
                       project_type=dyn_type,
                       toolchain=toolchain,
                       cmake_generator_name=cmake_generator_name)
        dyn_2_file = [f for f in files if dyn_2_name in str(f.parent.name)]
        validate_build(cmake_filepath=dyn_2_file[0],
                       project_name=dyn_2_name,
                       project_type=dyn_type,
                       toolchain=toolchain,
                       cmake_generator_name=cmake_generator_name)
    else:
        assert False


# Test build of a two dyn project in the same root directory
# dyn in root directory depends of inner dyn, user must provide the name of the projec to build
# kiss see both project and can't select which one is the default
def test_build_dyn_target(runtime_dir):
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
    if platform.system() == "Windows":
        target_name = "i686-pc-windows-msvc"
    else:
        target_name = "i686-unknown-linux-gnu"
    assert target_name != DEFAULT_TARGET_NAME
    # user must specify a name to build
    assert build_project(directory=RUNTIME_DIR/dyn_name,
                            args= ["-p", "my_dyn", "--target", target_name]) == 0

    # Find CMakeLists.txt
    # Only one must be present because my_inner_dyn depends on nothing
    files = find_cmake_files(RUNTIME_DIR)
    assert len(files) == 2
    toolchain  = Toolchain.create(compiler_name=DEFAULT_COMPILER_NAME, 
                                  target_name=target_name,
                                  profile_name=DEFAULT_PROFILE_NAME)
    cmake_generator_name =  CMakeGeneratorName.create(toolchain=toolchain)
    if cmake_generator_name.is_single_profile():
        dyn_file = [f for f in files if dyn_name in str(f.parent.parent.name)]
        validate_build(cmake_filepath=dyn_file[0],
                       project_name=dyn_name,
                       project_type=dyn_type,
                       toolchain=toolchain,
                       cmake_generator_name=cmake_generator_name)
        dyn_2_file = [f for f in files if dyn_2_name in str(f.parent.parent.name)]
        validate_build(cmake_filepath=dyn_2_file[0],
                       project_name=dyn_2_name,
                       project_type=dyn_type,
                       toolchain=toolchain,
                       cmake_generator_name=cmake_generator_name)
    elif cmake_generator_name.is_multi_profile():
        dyn_file = [f for f in files if dyn_name in str(f.parent.name)]
        validate_build(cmake_filepath=dyn_file[0],
                       project_name=dyn_name,
                       project_type=dyn_type,
                       toolchain=toolchain,
                       cmake_generator_name=cmake_generator_name)
        dyn_2_file = [f for f in files if dyn_2_name in str(f.parent.name)]
        validate_build(cmake_filepath=dyn_2_file[0],
                       project_name=dyn_2_name,
                       project_type=dyn_type,
                       toolchain=toolchain,
                       cmake_generator_name=cmake_generator_name)
    else:
        assert False
    
# Test build of a two dyn project in the same root directory
# dyn in root directory depends of inner dyn, user must provide the name of the projec to build
# kiss see both project and can't select which one is the default
def test_build_dyn_compiler(runtime_dir):
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
    if platform.system() == "Windows":
        compiler_name = "clangcl"
    else:
        compiler_name = "clang"
    assert compiler_name != DEFAULT_COMPILER_NAME
    # user must specify a name to build
    assert build_project(directory=RUNTIME_DIR/dyn_name,
                            args= ["-p", "my_dyn", "--compiler", compiler_name]) == 0

    # Find CMakeLists.txt
    # Only one must be present because my_inner_dyn depends on nothing
    files = find_cmake_files(RUNTIME_DIR)
    assert len(files) == 2
    toolchain  = Toolchain.create(compiler_name=compiler_name, 
                                  target_name=DEFAULT_TARGET_NAME,
                                  profile_name=DEFAULT_PROFILE_NAME)
    cmake_generator_name =  CMakeGeneratorName.create(toolchain=toolchain)
    if cmake_generator_name.is_single_profile():
        dyn_file = [f for f in files if dyn_name in str(f.parent.parent.name)]
        validate_build(cmake_filepath=dyn_file[0],
                       project_name=dyn_name,
                       project_type=dyn_type,
                       toolchain=toolchain,
                       cmake_generator_name=cmake_generator_name)
        dyn_2_file = [f for f in files if dyn_2_name in str(f.parent.parent.name)]
        validate_build(cmake_filepath=dyn_2_file[0],
                       project_name=dyn_2_name,
                       project_type=dyn_type,
                       toolchain=toolchain,
                       cmake_generator_name=cmake_generator_name)
    elif cmake_generator_name.is_multi_profile():
        dyn_file = [f for f in files if dyn_name in str(f.parent.name)]
        validate_build(cmake_filepath=dyn_file[0],
                       project_name=dyn_name,
                       project_type=dyn_type,
                       toolchain=toolchain,
                       cmake_generator_name=cmake_generator_name)
        dyn_2_file = [f for f in files if dyn_2_name in str(f.parent.name)]
        validate_build(cmake_filepath=dyn_2_file[0],
                       project_name=dyn_2_name,
                       project_type=dyn_type,
                       toolchain=toolchain,
                       cmake_generator_name=cmake_generator_name)
    else:
        assert False


def test_build_dyn_all(runtime_dir):
    profiles = ["debug", "release", "asan"]
    if platform.system() == "Windows":
        compilers = ["clangcl", "cl"]
        targets = ["x86_64-pc-windows-msvc", "i686-pc-windows-msvc"]
    elif platform.system() == "Linux":
        compilers = ["clang", "gcc"]
        targets = ["x86_64-unknown-linux-gnu", "i686-unknown-linux-gnu"]
    else:
        assert False
    
    
    for target in  targets:
        for compiler in compilers:
            for profile in profiles:
                delete_runtime_dir()

                dyn_type = "dyn"
                dyn_name = "my_dyn"
                new_project([dyn_type, dyn_name])


                assert build_project(directory=RUNTIME_DIR/dyn_name,
                                     args= ["-p", "my_dyn", "--compiler", compiler, "--target", target, "--profile", profile]) == 0
                files = find_cmake_files(RUNTIME_DIR)
                assert len(files) == 1
                toolchain  = Toolchain.create(compiler_name=compiler, 
                                              target_name=target, 
                                              profile_name=profile)
                cmake_generator_name =  CMakeGeneratorName.create(toolchain=toolchain)
                validate_build(cmake_filepath=files[0],
                               project_name=dyn_name,
                               project_type=dyn_type,
                               toolchain=toolchain,
                               cmake_generator_name=cmake_generator_name)
        

        