from tests.runtime_fixture import runtime_dir
from tests.common import *

# Test build of a single bin project
# The single bin project must be build and found automatically
def test_build_bin_default(runtime_dir):
    bin_type = "bin"
    bin_name = "my_bin"
    new_project([bin_type, bin_name])

    assert build_project(directory=RUNTIME_DIR/bin_name) == 0

    files = find_cmake_files(RUNTIME_DIR)
    assert len(files) == 1
    
    
    toolchain  = Toolchain.create(compiler_name=DEFAULT_COMPILER_NAME, target_name=DEFAULT_TARGET_NAME)
    cmake_generator_name =  CMakeGeneratorName.create(toolchain=toolchain)
    validate_build(cmake_filepath=files[0],
                   project_name=bin_name,
                   project_type=bin_type,
                   cmake_generator_name=cmake_generator_name)
    
# Test build of a two bin project in the same root directory
# But without dependency
# The single bin project in the given directory must be build and found automatically
def test_build_bin_default_inner(runtime_dir):
    ## SETUP
    bin_type = "bin"
    bin_name = "my_bin"
    new_project([bin_type, bin_name])
    bin_2_name = "my_inner_bin"
    new_inner_project(bin_name, [bin_type, bin_2_name])

    ## TEST
    assert build_project(directory=RUNTIME_DIR/bin_name) == 0

    # Find CMakeLists.txt
    files = find_cmake_files(RUNTIME_DIR)
    assert len(files) == 1
    toolchain  = Toolchain.create(compiler_name=DEFAULT_COMPILER_NAME, target_name=DEFAULT_TARGET_NAME)
    cmake_generator_name =  CMakeGeneratorName.create(toolchain=toolchain)

    validate_build(cmake_filepath=files[0],
                   project_name=bin_name,
                   project_type=bin_type,
                   cmake_generator_name=cmake_generator_name)
    
    assert build_project(directory=RUNTIME_DIR/bin_name/bin_2_name) == 0

    # Find CMakeLists.txt
    files = find_cmake_files(RUNTIME_DIR)
    assert len(files) == 2
    toolchain  = Toolchain.create(compiler_name=DEFAULT_COMPILER_NAME, target_name=DEFAULT_TARGET_NAME)
    cmake_generator_name =  CMakeGeneratorName.create(toolchain=toolchain)
    if cmake_generator_name.is_single_profile():
        bin_file = [f for f in files if bin_name in str(f.parent.parent.name)]
        validate_build(cmake_filepath=bin_file[0],
                    project_name=bin_name,
                    project_type=bin_type,
                   cmake_generator_name=cmake_generator_name)
        bin_2_file = [f for f in files if bin_2_name in str(f.parent.parent.name)]
        validate_build(cmake_filepath=bin_2_file[0],
                    project_name=bin_2_name,
                    project_type=bin_type,
                   cmake_generator_name=cmake_generator_name)
    elif cmake_generator_name.is_multi_profile():
        bin_file = [f for f in files if bin_name in str(f.parent.name)]
        validate_build(cmake_filepath=bin_file[0],
                    project_name=bin_name,
                    project_type=bin_type,
                    cmake_generator_name=cmake_generator_name)
        bin_2_file = [f for f in files if bin_2_name in str(f.parent.name)]
        validate_build(cmake_filepath=bin_2_file[0],
                    project_name=bin_2_name,
                    project_type=bin_type,
                    cmake_generator_name=cmake_generator_name)
    else:
        assert False



# Test build of a two bin project in the same root directory
# bin in root directory depends of inner bin, user must provide the name of the projec to build
# kiss see both project and can't select which one is the default
def test_build_bin_no_depends(runtime_dir):
    ## SETUP
    bin_type = "bin"
    bin_name = "my_bin"
    new_project([bin_type, bin_name])

    # Create 'my_inner_bin' inner dependency of 'my_bin'
    bin_2_name = "my_inner_bin"
    new_inner_project(bin_name, ["-e", bin_type, bin_2_name])

    # Add 'my_inner_bin' as dependency of 'my_bin'
    add_dependency(bin_name, [bin_2_name])

    ## TEST
    # If no name is given, kiss must fail
    assert build_project(directory=RUNTIME_DIR/bin_name) == 1
    
    # user must specify a name to build
    assert build_project(directory=RUNTIME_DIR/bin_name,
                            args= ["-p", "my_inner_bin"]) == 0

    # Find CMakeLists.txt
    # Only one must be present because my_inner_bin depends on nothing
    files = find_cmake_files(RUNTIME_DIR)
    assert len(files) == 1
    toolchain  = Toolchain.create(compiler_name=DEFAULT_COMPILER_NAME, target_name=DEFAULT_TARGET_NAME)
    cmake_generator_name =  CMakeGeneratorName.create(toolchain=toolchain)
    validate_build(cmake_filepath=files[0],
                   project_name=bin_2_name,
                   project_type=bin_type,
                   cmake_generator_name=cmake_generator_name)
    
# Test build of a two bin project in the same root directory
# bin in root directory depends of inner bin, user must provide the name of the projec to build
# kiss see both project and can't select which one is the default
def test_build_bin_depends(runtime_dir):
    ## SETUP
    bin_type = "bin"
    bin_name = "my_bin"
    new_project([bin_type, bin_name])

    # Create 'my_inner_bin' inner dependency of 'my_bin'
    bin_2_name = "my_inner_bin"
    new_inner_project(bin_name, ["-e", bin_type, bin_2_name])

    # Add 'my_inner_bin' as dependency of 'my_bin'
    add_dependency(bin_name, [bin_2_name])

    ## TEST
    # If no name is given, kiss must fail
    assert build_project(directory=RUNTIME_DIR/bin_name) == 1
    
    # user must specify a name to build
    assert build_project(directory=RUNTIME_DIR/bin_name,
                            args= ["-p", "my_bin"]) == 0

    # Find CMakeLists.txt
    # Only one must be present because my_inner_bin depends on nothing
    files = find_cmake_files(RUNTIME_DIR)
    assert len(files) == 2
    toolchain  = Toolchain.create(compiler_name=DEFAULT_COMPILER_NAME, target_name=DEFAULT_TARGET_NAME)
    cmake_generator_name =  CMakeGeneratorName.create(toolchain=toolchain)
    if cmake_generator_name.is_single_profile():
        bin_file = [f for f in files if bin_name in str(f.parent.parent.name)]
        validate_build(cmake_filepath=bin_file[0],
                    project_name=bin_name,
                    project_type=bin_type,
                    cmake_generator_name=cmake_generator_name)
        bin_2_file = [f for f in files if bin_2_name in str(f.parent.parent.name)]
        validate_build(cmake_filepath=bin_2_file[0],
                    project_name=bin_2_name,
                    project_type=bin_type,
                    cmake_generator_name=cmake_generator_name)
    elif cmake_generator_name.is_multi_profile():
        bin_file = [f for f in files if bin_name in str(f.parent.name)]
        validate_build(cmake_filepath=bin_file[0],
                    project_name=bin_name,
                    project_type=bin_type,
                    cmake_generator_name=cmake_generator_name)
        bin_2_file = [f for f in files if bin_2_name in str(f.parent.name)]
        validate_build(cmake_filepath=bin_2_file[0],
                    project_name=bin_2_name,
                    project_type=bin_type,
                    cmake_generator_name=cmake_generator_name)
    else:
        assert False

# Test build of a two bin project in the same root directory
# bin in root directory depends of inner bin, user must provide the name of the projec to build
# kiss see both project and can't select which one is the default
def test_build_bin_profile(runtime_dir):
    ## SETUP
    bin_type = "bin"
    bin_name = "my_bin"
    new_project([bin_type, bin_name])

    # Create 'my_inner_bin' inner dependency of 'my_bin'
    bin_2_name = "my_inner_bin"
    new_inner_project(bin_name, ["-e", bin_type, bin_2_name])

    # Add 'my_inner_bin' as dependency of 'my_bin'
    add_dependency(bin_name, [bin_2_name])

    ## TEST
    profile_name = "release"
    assert profile_name != DEFAULT_PROFILE_NAME

    # user must specify a name to build
    assert build_project(directory=RUNTIME_DIR/bin_name,
                            args= ["-p", "my_bin", "--profile", profile_name]) == 0

    # Find CMakeLists.txt
    # Only one must be present because my_inner_bin depends on nothing
    files = find_cmake_files(RUNTIME_DIR)
    assert len(files) == 2
    toolchain  = Toolchain.create(compiler_name=DEFAULT_COMPILER_NAME, target_name=DEFAULT_TARGET_NAME)
    cmake_generator_name =  CMakeGeneratorName.create(toolchain=toolchain)
    if cmake_generator_name.is_single_profile():
        bin_file = [f for f in files if bin_name in str(f.parent.parent.name)]
        validate_build(cmake_filepath=bin_file[0],
                    project_name=bin_name,
                    project_type=bin_type,
                    profile_name=profile_name,
                    cmake_generator_name=cmake_generator_name)
        bin_2_file = [f for f in files if bin_2_name in str(f.parent.parent.name)]
        validate_build(cmake_filepath=bin_2_file[0],
                    project_name=bin_2_name,
                    project_type=bin_type,
                    profile_name=profile_name,
                    cmake_generator_name=cmake_generator_name)
    elif cmake_generator_name.is_multi_profile():
        bin_file = [f for f in files if bin_name in str(f.parent.name)]
        validate_build(cmake_filepath=bin_file[0],
                    project_name=bin_name,
                    project_type=bin_type,
                    profile_name=profile_name,
                    cmake_generator_name=cmake_generator_name)
        bin_2_file = [f for f in files if bin_2_name in str(f.parent.name)]
        validate_build(cmake_filepath=bin_2_file[0],
                    project_name=bin_2_name,
                    project_type=bin_type,
                    profile_name=profile_name,
                    cmake_generator_name=cmake_generator_name)
    else:
        assert False


# Test build of a two bin project in the same root directory
# bin in root directory depends of inner bin, user must provide the name of the projec to build
# kiss see both project and can't select which one is the default
def test_build_bin_target(runtime_dir):
    ## SETUP
    bin_type = "bin"
    bin_name = "my_bin"
    new_project([bin_type, bin_name])

    # Create 'my_inner_bin' inner dependency of 'my_bin'
    bin_2_name = "my_inner_bin"
    new_inner_project(bin_name, ["-e", bin_type, bin_2_name])

    # Add 'my_inner_bin' as dependency of 'my_bin'
    add_dependency(bin_name, [bin_2_name])

    ## TEST
    if platform.system() == "Windows":
        target_name = "i686-pc-windows-msvc"
    else:
        target_name = "i686-unknown-linux-gnu"

    assert target_name != DEFAULT_TARGET_NAME
    # user must specify a name to build
    assert build_project(directory=RUNTIME_DIR/bin_name,
                            args= ["-p", "my_bin", "--target", target_name]) == 0

    # Find CMakeLists.txt
    # Only one must be present because my_inner_bin depends on nothing
    files = find_cmake_files(RUNTIME_DIR)
    assert len(files) == 2
    toolchain  = Toolchain.create(compiler_name=DEFAULT_COMPILER_NAME, target_name=DEFAULT_TARGET_NAME)
    cmake_generator_name =  CMakeGeneratorName.create(toolchain=toolchain)
    if cmake_generator_name.is_single_profile():
        bin_file = [f for f in files if bin_name in str(f.parent.parent.name)]
        validate_build(cmake_filepath=bin_file[0],
                    project_name=bin_name,
                    project_type=bin_type,
                    target_name=target_name,
                    cmake_generator_name=cmake_generator_name)
        bin_2_file = [f for f in files if bin_2_name in str(f.parent.parent.name)]
        validate_build(cmake_filepath=bin_2_file[0],
                    project_name=bin_2_name,
                    project_type=bin_type,
                    target_name=target_name,
                    cmake_generator_name=cmake_generator_name)
    elif cmake_generator_name.is_multi_profile():
        bin_file = [f for f in files if bin_name in str(f.parent.name)]
        validate_build(cmake_filepath=bin_file[0],
                    project_name=bin_name,
                    project_type=bin_type,
                    target_name=target_name,
                    cmake_generator_name=cmake_generator_name)
        bin_2_file = [f for f in files if bin_2_name in str(f.parent.name)]
        validate_build(cmake_filepath=bin_2_file[0],
                    project_name=bin_2_name,
                    project_type=bin_type,
                    target_name=target_name,
                    cmake_generator_name=cmake_generator_name)
    else:
        assert False
    
# Test build of a two bin project in the same root directory
# bin in root directory depends of inner bin, user must provide the name of the projec to build
# kiss see both project and can't select which one is the default
def test_build_bin_compiler(runtime_dir):
    ## SETUP
    bin_type = "bin"
    bin_name = "my_bin"
    new_project([bin_type, bin_name])

    # Create 'my_inner_bin' inner dependency of 'my_bin'
    bin_2_name = "my_inner_bin"
    new_inner_project(bin_name, ["-e", bin_type, bin_2_name])

    # Add 'my_inner_bin' as dependency of 'my_bin'
    add_dependency(bin_name, [bin_2_name])

    ## TEST
    if platform.system() == "Windows":
        compiler_name = "clangcl"
    else:
        compiler_name = "clang"
    assert compiler_name != DEFAULT_COMPILER_NAME
    # user must specify a name to build
    assert build_project(directory=RUNTIME_DIR/bin_name,
                            args= ["-p", "my_bin", "--compiler", compiler_name]) == 0

    # Find CMakeLists.txt
    # Only one must be present because my_inner_bin depends on nothing
    files = find_cmake_files(RUNTIME_DIR)
    assert len(files) == 2
    toolchain  = Toolchain.create(compiler_name=DEFAULT_COMPILER_NAME, target_name=DEFAULT_TARGET_NAME)
    cmake_generator_name =  CMakeGeneratorName.create(toolchain=toolchain)
    if cmake_generator_name.is_single_profile():
        bin_file = [f for f in files if bin_name in str(f.parent.parent.name)]
        validate_build(cmake_filepath=bin_file[0],
                    project_name=bin_name,
                    project_type=bin_type,
                    compiler_name=compiler_name,
                    cmake_generator_name=cmake_generator_name)
        bin_2_file = [f for f in files if bin_2_name in str(f.parent.parent.name)]
        validate_build(cmake_filepath=bin_2_file[0],
                    project_name=bin_2_name,
                    project_type=bin_type,
                    compiler_name=compiler_name,
                    cmake_generator_name=cmake_generator_name)
    elif cmake_generator_name.is_multi_profile():
        bin_file = [f for f in files if bin_name in str(f.parent.name)]
        validate_build(cmake_filepath=bin_file[0],
                    project_name=bin_name,
                    project_type=bin_type,
                    compiler_name=compiler_name,
                    cmake_generator_name=cmake_generator_name)
        bin_2_file = [f for f in files if bin_2_name in str(f.parent.name)]
        validate_build(cmake_filepath=bin_2_file[0],
                    project_name=bin_2_name,
                    project_type=bin_type,
                    compiler_name=compiler_name,
                    cmake_generator_name=cmake_generator_name)
    else:
        assert False


def test_build_bin_asan(runtime_dir):
    bin_type = "bin"
    bin_name = "my_bin"
    new_project([bin_type, bin_name])

    if platform.system() == "Windows":
        assert build_project(directory=RUNTIME_DIR/bin_name,
                             args= ["-p", "my_bin", "--compiler", "clangcl", "--target", "x86_64-pc-windows-msvc", "--profile", "debug"]) == 0
        assert build_project(directory=RUNTIME_DIR/bin_name,
                             args= ["-p", "my_bin", "--compiler", "clangcl", "--target", "x86_64-pc-windows-msvc", "--profile", "release"]) == 0
        assert build_project(directory=RUNTIME_DIR/bin_name,
                             args= ["-p", "my_bin", "--compiler", "clangcl", "--target", "x86_64-pc-windows-msvc", "--profile", "asan"]) == 0
        assert build_project(directory=RUNTIME_DIR/bin_name,
                             args= ["-p", "my_bin", "--compiler", "clangcl", "--target", "i686-pc-windows-msvc", "--profile", "debug"]) == 0
        assert build_project(directory=RUNTIME_DIR/bin_name,
                             args= ["-p", "my_bin", "--compiler", "clangcl", "--target", "i686-pc-windows-msvc", "--profile", "release"]) == 0
        # ASAN is not supported with clangcl targeting i686 builds
        assert build_project(directory=RUNTIME_DIR/bin_name,
                             args= ["-p", "my_bin", "--compiler", "clangcl", "--target", "i686-pc-windows-msvc", "--profile", "asan"]) == 0
        
        assert build_project(directory=RUNTIME_DIR/bin_name,
                             args= ["-p", "my_bin", "--compiler", "cl", "--target", "x86_64-pc-windows-msvc", "--profile", "debug"]) == 0
        assert build_project(directory=RUNTIME_DIR/bin_name,
                             args= ["-p", "my_bin", "--compiler", "cl", "--target", "x86_64-pc-windows-msvc", "--profile", "release"]) == 0
        assert build_project(directory=RUNTIME_DIR/bin_name,
                             args= ["-p", "my_bin", "--compiler", "cl", "--target", "x86_64-pc-windows-msvc", "--profile", "asan"]) == 0
        assert build_project(directory=RUNTIME_DIR/bin_name,
                             args= ["-p", "my_bin", "--compiler", "cl", "--target", "i686-pc-windows-msvc", "--profile", "debug"]) == 0
        assert build_project(directory=RUNTIME_DIR/bin_name,
                             args= ["-p", "my_bin", "--compiler", "cl", "--target", "i686-pc-windows-msvc", "--profile", "release"]) == 0
        assert build_project(directory=RUNTIME_DIR/bin_name,
                             args= ["-p", "my_bin", "--compiler", "cl", "--target", "i686-pc-windows-msvc", "--profile", "asan"]) == 0

        