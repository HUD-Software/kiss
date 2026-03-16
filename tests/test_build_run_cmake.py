from tests.common import *

# Test run of a single bin project
# The single bin project must be run and found automatically
def test_run_bin_default(runtime_dir):
    bin_type = "bin"
    bin_name = "my_bin"
    new_project([bin_type, bin_name])

    assert run_project(directory=RUNTIME_DIR/bin_name) == 0

    files = find_cmake_files(RUNTIME_DIR)
    assert len(files) == 1
    
    
    toolchain  = Toolchain.create(compiler_name=DEFAULT_COMPILER_NAME, 
                                  target_name=DEFAULT_TARGET_NAME, 
                                  profile_name=DEFAULT_PROFILE_NAME)
    cmake_generator_name =  CMakeGeneratorName.create(toolchain=toolchain)
    validate_run(cmake_filepath=files[0],
                 project_name=bin_name,
                 project_type=bin_type,
                 toolchain=toolchain,
                 cmake_generator_name=cmake_generator_name)
    
# Test run of a two bin project in the same root directory
# But without dependency
# The single bin project in the given directory must be run and found automatically
def test_run_bin_default_inner(runtime_dir):
    ## SETUP
    bin_type = "bin"
    bin_name = "my_bin"
    new_project([bin_type, bin_name])
    bin_2_name = "my_inner_bin"
    new_inner_project(bin_name, [bin_type, bin_2_name])

    ## TEST
    assert run_project(directory=RUNTIME_DIR/bin_name) == 0

    # Find CMakeLists.txt
    files = find_cmake_files(RUNTIME_DIR)
    assert len(files) == 1
    toolchain  = Toolchain.create(compiler_name=DEFAULT_COMPILER_NAME, target_name=DEFAULT_TARGET_NAME)
    cmake_generator_name =  CMakeGeneratorName.create(toolchain=toolchain)

    validate_run(cmake_filepath=files[0],
                 project_name=bin_name,
                 project_type=bin_type,
                 toolchain=toolchain,
                 cmake_generator_name=cmake_generator_name)
    
    assert run_project(directory=RUNTIME_DIR/bin_name/bin_2_name) == 0

    # Find CMakeLists.txt
    files = find_cmake_files(RUNTIME_DIR)
    assert len(files) == 2
    toolchain  = Toolchain.create(compiler_name=DEFAULT_COMPILER_NAME, target_name=DEFAULT_TARGET_NAME)
    cmake_generator_name =  CMakeGeneratorName.create(toolchain=toolchain)
    if cmake_generator_name.is_single_profile():
        bin_file = [f for f in files if bin_name in str(f.parent.parent.name)]
        validate_run(cmake_filepath=bin_file[0],
                    project_name=bin_name,
                    project_type=bin_type,
                   cmake_generator_name=cmake_generator_name)
        bin_2_file = [f for f in files if bin_2_name in str(f.parent.parent.name)]
        validate_run(cmake_filepath=bin_2_file[0],
                    project_name=bin_2_name,
                    project_type=bin_type,
                   cmake_generator_name=cmake_generator_name)
    elif cmake_generator_name.is_multi_profile():
        bin_file = [f for f in files if bin_name in str(f.parent.name)]
        validate_run(cmake_filepath=bin_file[0],
                    project_name=bin_name,
                    project_type=bin_type,
                    cmake_generator_name=cmake_generator_name)
        bin_2_file = [f for f in files if bin_2_name in str(f.parent.name)]
        validate_run(cmake_filepath=bin_2_file[0],
                    project_name=bin_2_name,
                    project_type=bin_type,
                    cmake_generator_name=cmake_generator_name)
    else:
        assert False



# # Test run of a two bin project in the same root directory
# # bin in root directory depends of inner bin, user must provide the name of the projec to run
# # kiss see both project and can't select which one is the default
# def test_run_bin_no_depends(runtime_dir):
#     ## SETUP
#     bin_type = "bin"
#     bin_name = "my_bin"
#     new_project([bin_type, bin_name])

#     # Create 'my_inner_bin' inner dependency of 'my_bin'
#     bin_2_name = "my_inner_bin"
#     new_inner_project(bin_name, ["-e", bin_type, bin_2_name])

#     # Add 'my_inner_bin' as dependency of 'my_bin'
#     add_dependency(bin_name, [bin_2_name])

#     ## TEST
#     # If no name is given, kiss must fail
#     assert run_project(directory=RUNTIME_DIR/bin_name) == 1
    
#     # user must specify a name to run
#     assert run_project(directory=RUNTIME_DIR/bin_name,
#                             args= ["-p", "my_inner_bin"]) == 0

#     # Find CMakeLists.txt
#     # Only one must be present because my_inner_bin depends on nothing
#     files = find_cmake_files(RUNTIME_DIR)
#     assert len(files) == 1
#     toolchain  = Toolchain.create(compiler_name=DEFAULT_COMPILER_NAME, target_name=DEFAULT_TARGET_NAME)
#     cmake_generator_name =  CMakeGeneratorName.create(toolchain=toolchain)
#     validate_run(cmake_filepath=files[0],
#                    project_name=bin_2_name,
#                    project_type=bin_type,
#                    cmake_generator_name=cmake_generator_name)
    
# # Test run of a two bin project in the same root directory
# # bin in root directory depends of inner bin, user must provide the name of the projec to run
# # kiss see both project and can't select which one is the default
# def test_run_bin_depends(runtime_dir):
#     ## SETUP
#     bin_type = "bin"
#     bin_name = "my_bin"
#     new_project([bin_type, bin_name])

#     # Create 'my_inner_bin' inner dependency of 'my_bin'
#     bin_2_name = "my_inner_bin"
#     new_inner_project(bin_name, ["-e", bin_type, bin_2_name])

#     # Add 'my_inner_bin' as dependency of 'my_bin'
#     add_dependency(bin_name, [bin_2_name])

#     ## TEST
#     # If no name is given, kiss must fail
#     assert run_project(directory=RUNTIME_DIR/bin_name) == 1
    
#     # user must specify a name to run
#     assert run_project(directory=RUNTIME_DIR/bin_name,
#                             args= ["-p", "my_bin"]) == 0

#     # Find CMakeLists.txt
#     # Only one must be present because my_inner_bin depends on nothing
#     files = find_cmake_files(RUNTIME_DIR)
#     assert len(files) == 2
#     toolchain  = Toolchain.create(compiler_name=DEFAULT_COMPILER_NAME, target_name=DEFAULT_TARGET_NAME)
#     cmake_generator_name =  CMakeGeneratorName.create(toolchain=toolchain)
#     if cmake_generator_name.is_single_profile():
#         bin_file = [f for f in files if bin_name in str(f.parent.parent.name)]
#         validate_run(cmake_filepath=bin_file[0],
#                     project_name=bin_name,
#                     project_type=bin_type,
#                     cmake_generator_name=cmake_generator_name)
#         bin_2_file = [f for f in files if bin_2_name in str(f.parent.parent.name)]
#         validate_run(cmake_filepath=bin_2_file[0],
#                     project_name=bin_2_name,
#                     project_type=bin_type,
#                     cmake_generator_name=cmake_generator_name)
#     elif cmake_generator_name.is_multi_profile():
#         bin_file = [f for f in files if bin_name in str(f.parent.name)]
#         validate_run(cmake_filepath=bin_file[0],
#                     project_name=bin_name,
#                     project_type=bin_type,
#                     cmake_generator_name=cmake_generator_name)
#         bin_2_file = [f for f in files if bin_2_name in str(f.parent.name)]
#         validate_run(cmake_filepath=bin_2_file[0],
#                     project_name=bin_2_name,
#                     project_type=bin_type,
#                     cmake_generator_name=cmake_generator_name)
#     else:
#         assert False

# # Test run of a two bin project in the same root directory
# # bin in root directory depends of inner bin, user must provide the name of the projec to run
# # kiss see both project and can't select which one is the default
# def test_run_bin_profile(runtime_dir):
#     ## SETUP
#     bin_type = "bin"
#     bin_name = "my_bin"
#     new_project([bin_type, bin_name])

#     # Create 'my_inner_bin' inner dependency of 'my_bin'
#     bin_2_name = "my_inner_bin"
#     new_inner_project(bin_name, ["-e", bin_type, bin_2_name])

#     # Add 'my_inner_bin' as dependency of 'my_bin'
#     add_dependency(bin_name, [bin_2_name])

#     ## TEST
#     profile_name = "release"
#     assert profile_name != DEFAULT_PROFILE_NAME

#     # user must specify a name to run
#     assert run_project(directory=RUNTIME_DIR/bin_name,
#                             args= ["-p", "my_bin", "--profile", profile_name]) == 0

#     # Find CMakeLists.txt
#     # Only one must be present because my_inner_bin depends on nothing
#     files = find_cmake_files(RUNTIME_DIR)
#     assert len(files) == 2
#     toolchain  = Toolchain.create(compiler_name=DEFAULT_COMPILER_NAME, target_name=DEFAULT_TARGET_NAME)
#     cmake_generator_name =  CMakeGeneratorName.create(toolchain=toolchain)
#     if cmake_generator_name.is_single_profile():
#         bin_file = [f for f in files if bin_name in str(f.parent.parent.name)]
#         validate_run(cmake_filepath=bin_file[0],
#                     project_name=bin_name,
#                     project_type=bin_type,
#                     profile_name=profile_name,
#                     cmake_generator_name=cmake_generator_name)
#         bin_2_file = [f for f in files if bin_2_name in str(f.parent.parent.name)]
#         validate_run(cmake_filepath=bin_2_file[0],
#                     project_name=bin_2_name,
#                     project_type=bin_type,
#                     profile_name=profile_name,
#                     cmake_generator_name=cmake_generator_name)
#     elif cmake_generator_name.is_multi_profile():
#         bin_file = [f for f in files if bin_name in str(f.parent.name)]
#         validate_run(cmake_filepath=bin_file[0],
#                     project_name=bin_name,
#                     project_type=bin_type,
#                     profile_name=profile_name,
#                     cmake_generator_name=cmake_generator_name)
#         bin_2_file = [f for f in files if bin_2_name in str(f.parent.name)]
#         validate_run(cmake_filepath=bin_2_file[0],
#                     project_name=bin_2_name,
#                     project_type=bin_type,
#                     profile_name=profile_name,
#                     cmake_generator_name=cmake_generator_name)
#     else:
#         assert False


# # Test run of a two bin project in the same root directory
# # bin in root directory depends of inner bin, user must provide the name of the projec to run
# # kiss see both project and can't select which one is the default
# def test_run_bin_target(runtime_dir):
#     ## SETUP
#     bin_type = "bin"
#     bin_name = "my_bin"
#     new_project([bin_type, bin_name])

#     # Create 'my_inner_bin' inner dependency of 'my_bin'
#     bin_2_name = "my_inner_bin"
#     new_inner_project(bin_name, ["-e", bin_type, bin_2_name])

#     # Add 'my_inner_bin' as dependency of 'my_bin'
#     add_dependency(bin_name, [bin_2_name])

#     ## TEST
#     if platform.system() == "Windows":
#         target_name = "i686-pc-windows-msvc"
#     else:
#         target_name = "i686-unknown-linux-gnu"

#     assert target_name != DEFAULT_TARGET_NAME
#     # user must specify a name to run
#     assert run_project(directory=RUNTIME_DIR/bin_name,
#                             args= ["-p", "my_bin", "--target", target_name]) == 0

#     # Find CMakeLists.txt
#     # Only one must be present because my_inner_bin depends on nothing
#     files = find_cmake_files(RUNTIME_DIR)
#     assert len(files) == 2
#     toolchain  = Toolchain.create(compiler_name=DEFAULT_COMPILER_NAME, target_name=DEFAULT_TARGET_NAME)
#     cmake_generator_name =  CMakeGeneratorName.create(toolchain=toolchain)
#     if cmake_generator_name.is_single_profile():
#         bin_file = [f for f in files if bin_name in str(f.parent.parent.name)]
#         validate_run(cmake_filepath=bin_file[0],
#                     project_name=bin_name,
#                     project_type=bin_type,
#                     target_name=target_name,
#                     cmake_generator_name=cmake_generator_name)
#         bin_2_file = [f for f in files if bin_2_name in str(f.parent.parent.name)]
#         validate_run(cmake_filepath=bin_2_file[0],
#                     project_name=bin_2_name,
#                     project_type=bin_type,
#                     target_name=target_name,
#                     cmake_generator_name=cmake_generator_name)
#     elif cmake_generator_name.is_multi_profile():
#         bin_file = [f for f in files if bin_name in str(f.parent.name)]
#         validate_run(cmake_filepath=bin_file[0],
#                     project_name=bin_name,
#                     project_type=bin_type,
#                     target_name=target_name,
#                     cmake_generator_name=cmake_generator_name)
#         bin_2_file = [f for f in files if bin_2_name in str(f.parent.name)]
#         validate_run(cmake_filepath=bin_2_file[0],
#                     project_name=bin_2_name,
#                     project_type=bin_type,
#                     target_name=target_name,
#                     cmake_generator_name=cmake_generator_name)
#     else:
#         assert False
    
# # Test run of a two bin project in the same root directory
# # bin in root directory depends of inner bin, user must provide the name of the projec to run
# # kiss see both project and can't select which one is the default
# def test_run_bin_compiler(runtime_dir):
#     ## SETUP
#     bin_type = "bin"
#     bin_name = "my_bin"
#     new_project([bin_type, bin_name])

#     # Create 'my_inner_bin' inner dependency of 'my_bin'
#     bin_2_name = "my_inner_bin"
#     new_inner_project(bin_name, ["-e", bin_type, bin_2_name])

#     # Add 'my_inner_bin' as dependency of 'my_bin'
#     add_dependency(bin_name, [bin_2_name])

#     ## TEST
#     if platform.system() == "Windows":
#         compiler_name = "clangcl"
#     else:
#         compiler_name = "clang"
#     assert compiler_name != DEFAULT_COMPILER_NAME
#     # user must specify a name to run
#     assert run_project(directory=RUNTIME_DIR/bin_name,
#                             args= ["-p", "my_bin", "--compiler", compiler_name]) == 0

#     # Find CMakeLists.txt
#     # Only one must be present because my_inner_bin depends on nothing
#     files = find_cmake_files(RUNTIME_DIR)
#     assert len(files) == 2
#     toolchain  = Toolchain.create(compiler_name=DEFAULT_COMPILER_NAME, target_name=DEFAULT_TARGET_NAME)
#     cmake_generator_name =  CMakeGeneratorName.create(toolchain=toolchain)
#     if cmake_generator_name.is_single_profile():
#         bin_file = [f for f in files if bin_name in str(f.parent.parent.name)]
#         validate_run(cmake_filepath=bin_file[0],
#                     project_name=bin_name,
#                     project_type=bin_type,
#                     compiler_name=compiler_name,
#                     cmake_generator_name=cmake_generator_name)
#         bin_2_file = [f for f in files if bin_2_name in str(f.parent.parent.name)]
#         validate_run(cmake_filepath=bin_2_file[0],
#                     project_name=bin_2_name,
#                     project_type=bin_type,
#                     compiler_name=compiler_name,
#                     cmake_generator_name=cmake_generator_name)
#     elif cmake_generator_name.is_multi_profile():
#         bin_file = [f for f in files if bin_name in str(f.parent.name)]
#         validate_run(cmake_filepath=bin_file[0],
#                     project_name=bin_name,
#                     project_type=bin_type,
#                     compiler_name=compiler_name,
#                     cmake_generator_name=cmake_generator_name)
#         bin_2_file = [f for f in files if bin_2_name in str(f.parent.name)]
#         validate_run(cmake_filepath=bin_2_file[0],
#                     project_name=bin_2_name,
#                     project_type=bin_type,
#                     compiler_name=compiler_name,
#                     cmake_generator_name=cmake_generator_name)
#     else:
#         assert False


# def test_run_bin_asan(runtime_dir):
#     bin_type = "bin"
#     bin_name = "my_bin"
#     new_project([bin_type, bin_name])

    
#     profiles = ["debug", "release", "asan"]
#     if platform.system() == "Windows":
#         compilers = ["clangcl", "cl"]
#         targets = ["x86_64-pc-windows-msvc", "i686-pc-windows-msvc"]
#     elif platform.system() == "Linux":
#         compilers = ["clang", "gcc"]
#         targets = ["x86_64-unknown-linux-gnu", "i686-unknown-linux-gnu"]
#     else:
#         assert False
    
    
#     for target in  targets:
#         for compiler in compilers:
#             for profile in profiles:
#                 assert run_project(directory=RUNTIME_DIR/bin_name,
#                                      args= ["-p", "my_bin", "--compiler", compiler, "--target", target, "--profile", profile]) == 0
  

    # # Trigger ASAN
    # # Modifiy the main and add code that trigger the ASAN
    # with open(RUNTIME_DIR/bin_name/"src/main.cpp", "w", encoding="utf-8") as f:
    #     f.write("#include <iostream>\n")
    #     f.write("int main() {\n")
    #     f.write("  std::cout << \"Hello, Bin World!\" << std::endl;\n")
    #     f.write("  int* p = new int[1];\n")
    #     f.write("  p[1] = 42;  // overflow\n")
    #     f.write("  delete[] p;\n")
    #     f.write("  return 0;\n")
    #     f.write("}\n")


    # if platform.system() == "Windows":
    #     assert run_project(directory=RUNTIME_DIR/bin_name,
    #                          args= ["-p", "my_bin", "--compiler", "clangcl", "--target", "x86_64-pc-windows-msvc", "--profile", "debug"]) == 1
    #     assert run_project(directory=RUNTIME_DIR/bin_name,
    #                          args= ["-p", "my_bin", "--compiler", "clangcl", "--target", "x86_64-pc-windows-msvc", "--profile", "release"]) == 1
    #     assert run_project(directory=RUNTIME_DIR/bin_name,
    #                          args= ["-p", "my_bin", "--compiler", "clangcl", "--target", "x86_64-pc-windows-msvc", "--profile", "asan"]) == 1
    #     assert run_project(directory=RUNTIME_DIR/bin_name,
    #                          args= ["-p", "my_bin", "--compiler", "clangcl", "--target", "i686-pc-windows-msvc", "--profile", "debug"]) == 1
    #     assert run_project(directory=RUNTIME_DIR/bin_name,
    #                          args= ["-p", "my_bin", "--compiler", "clangcl", "--target", "i686-pc-windows-msvc", "--profile", "release"]) == 1
    #     assert run_project(directory=RUNTIME_DIR/bin_name,
    #                          args= ["-p", "my_bin", "--compiler", "clangcl", "--target", "i686-pc-windows-msvc", "--profile", "asan"]) == 1
        
    #     assert run_project(directory=RUNTIME_DIR/bin_name,
    #                          args= ["-p", "my_bin", "--compiler", "cl", "--target", "x86_64-pc-windows-msvc", "--profile", "debug"]) == 1
    #     assert run_project(directory=RUNTIME_DIR/bin_name,
    #                          args= ["-p", "my_bin", "--compiler", "cl", "--target", "x86_64-pc-windows-msvc", "--profile", "release"]) == 1
    #     assert run_project(directory=RUNTIME_DIR/bin_name,
    #                          args= ["-p", "my_bin", "--compiler", "cl", "--target", "x86_64-pc-windows-msvc", "--profile", "asan"]) == 1
    #     assert run_project(directory=RUNTIME_DIR/bin_name,
    #                          args= ["-p", "my_bin", "--compiler", "cl", "--target", "i686-pc-windows-msvc", "--profile", "debug"]) == 1
    #     assert run_project(directory=RUNTIME_DIR/bin_name,
    #                          args= ["-p", "my_bin", "--compiler", "cl", "--target", "i686-pc-windows-msvc", "--profile", "release"]) == 1
    #     assert run_project(directory=RUNTIME_DIR/bin_name,
    #                          args= ["-p", "my_bin", "--compiler", "cl", "--target", "i686-pc-windows-msvc", "--profile", "asan"]) == 1
        

        