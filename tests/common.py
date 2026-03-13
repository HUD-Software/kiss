import os
from pathlib import Path
import platform
import subprocess
from src.cmake.cmake_generator_name import CMakeGeneratorName
from src.toolchain.toolchain import Toolchain
from src.toolchain.target import Target
from src.toolchain.compiler import Compiler

cwd = os.getcwd()
print("Current working directory:", cwd)
if platform.system() == "Windows":
    Toolchain.load_all_toolchains_in_directory(Path("toolchains/windows"))
else:
    Toolchain.load_all_toolchains_in_directory(Path("toolchains/linux"))

RUNTIME_DIR = Path("tests/runtime")
DEFAULT_PROFILE_NAME = "debug"
DEFAULT_COMPILER_NAME  = Compiler.default_compiler_name()
DEFAULT_TARGET_NAME = Target.default_target_name()

def new_project(args: list[str]):
    result = subprocess.run(["python", "src/kiss.py", "-d", RUNTIME_DIR, "new"] + args)
    assert result.returncode == 0

def new_inner_project(project_name :str, args: list[str]):
    result = subprocess.run(["python", "src/kiss.py", "-d", str(RUNTIME_DIR / project_name), "new"] + args)
    assert result.returncode == 0

def add_dependency(project_name :str, args : list[str]):
    result = subprocess.run(["python", "src/kiss.py", "-d", str(RUNTIME_DIR/ project_name), "add"] + args)
    assert result.returncode == 0


def generate_project(directory: str, args: list[str] = []) -> int:
    result = subprocess.run(["python", "src/kiss.py", "-d", str(directory), "generate"] + args)
    return result.returncode

def get_cmake_generator_name(target_name:str, 
                             compiler_name:str,
                             profile_name:str) ->  CMakeGeneratorName:
    toolchain  = Toolchain.create(compiler_name=compiler_name, 
                                  target_name=target_name, 
                                  profile_name=profile_name)
    return CMakeGeneratorName.create(toolchain=toolchain)

def find_cmake_files(root):
    return list(Path(root).rglob("CMakeLists.txt"))

def validate_cmakelist_path(cmake_filepath: Path,
                            project_name:str, 
                            profile_name:str = DEFAULT_PROFILE_NAME, 
                            target_name:str=DEFAULT_TARGET_NAME, 
                            compiler_name:str= DEFAULT_COMPILER_NAME):
    
    assert cmake_filepath.exists()
    assert cmake_filepath.name == "CMakeLists.txt"
    cmake_generator_name = get_cmake_generator_name(compiler_name=compiler_name,
                                                    target_name=target_name,
                                                    profile_name=profile_name)
    if cmake_generator_name.is_single_profile():
        assert cmake_filepath.parent.name == profile_name
        assert project_name in cmake_filepath.parent.parent.name
        assert cmake_filepath.parent.parent.parent.name == "cmake"
        assert cmake_filepath.parent.parent.parent.parent.name == compiler_name
        assert cmake_filepath.parent.parent.parent.parent.parent.name == target_name
    elif cmake_generator_name.is_multi_profile():
        assert project_name in cmake_filepath.parent.name
        assert cmake_filepath.parent.parent.name == "cmake"
        assert cmake_filepath.parent.parent.parent.name == compiler_name
        assert cmake_filepath.parent.parent.parent.parent.name == target_name
    else:
        assert False


def build_project(directory: str, args: list[str] = []) -> int:
    result = subprocess.run(["python", "src/kiss.py", "-d", str(directory), "build"] + args)
    return result.returncode

def validate_build( cmake_filepath: Path, 
                    project_name:str,
                    project_type:str,
                    cmake_generator_name:CMakeGeneratorName,
                    profile_name:str = DEFAULT_PROFILE_NAME, 
                    target_name:str=DEFAULT_TARGET_NAME, 
                    compiler_name:str= DEFAULT_COMPILER_NAME,
                    ):

    validate_cmakelist_path(cmake_filepath=cmake_filepath,
                            project_name=project_name,
                            profile_name=profile_name,
                            target_name=target_name,
                            compiler_name=compiler_name)
    if cmake_generator_name.is_single_profile():
        match project_type:
            case "bin":
                artifact_path = cmake_filepath.parent / project_name
                assert artifact_path.exists()
            case "dyn":
                artifact_path = cmake_filepath.parent / f"{project_name}.so"
                assert artifact_path.exists()
            case "lib":
                artifact_path = cmake_filepath.parent / f"{project_name}.a"
                assert artifact_path.exists()
    elif cmake_generator_name.is_multi_profile():
        match project_type:
            case "bin":
                artifact_path = cmake_filepath.parent / profile_name / f"{project_name}.exe"
                assert artifact_path.exists()
            case "dyn":
                artifact_path = cmake_filepath.parent / profile_name / f"{project_name}.dll"
                assert artifact_path.exists()
            case "lib":
                artifact_path = cmake_filepath.parent / profile_name / f"{project_name}.lib"
                assert artifact_path.exists()
    else:
        assert False


def run_project(directory: str, args: list[str] = []) -> int:
    result = subprocess.run(["python", "src/kiss.py", "-d", str(directory), "run"] + args)
    return result.returncode


def validate_run( cmake_filepath: Path, 
                    project_name:str,
                    project_type:str,
                    cmake_generator_name:CMakeGeneratorName,
                    profile_name:str = DEFAULT_PROFILE_NAME, 
                    target_name:str=DEFAULT_TARGET_NAME, 
                    compiler_name:str= DEFAULT_COMPILER_NAME,
                    ):
    validate_build(cmake_filepath=cmake_filepath,
                   project_type=project_type,
                   cmake_generator_name=cmake_generator_name,
                   project_name=project_name,
                   profile_name=profile_name,
                   target_name=target_name,
                   compiler_name=compiler_name)