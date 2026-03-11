import os
from pathlib import Path
import platform
import subprocess
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
    result = subprocess.run(
        ["python", "src/kiss.py", "-d", RUNTIME_DIR, "new"] + args,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    print(result.stdout, flush=True)
    print(result.stderr, flush=True)
    assert result.returncode == 0

def new_inner_project(project_name :str, args: list[str]):
    result = subprocess.run(
        ["python", "src/kiss.py", "-d", str(RUNTIME_DIR / project_name), "new"] + args,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    print(result.stdout, flush=True)
    print(result.stderr, flush=True)
    assert result.returncode == 0

def add_dependency(project_name :str, args : list[str]):
    result = subprocess.run(
        ["python", "src/kiss.py", "-d", str(RUNTIME_DIR/ project_name), "add"] + args,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    print(result.stdout, flush=True)
    print(result.stderr, flush=True)
    assert result.returncode == 0


def generate_project(directory: str, args: list[str] = []) -> int:
    result = subprocess.run(
        ["python", "src/kiss.py", "-d", str(directory), "generate"] + args,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    print(result.stdout, flush=True)
    print(result.stderr, flush=True)
    return result.returncode

def find_cmake_files(root):
    return list(Path(root).rglob("CMakeLists.txt"))

def validate_cmakelist_path(path: Path, 
                            project_name:str, 
                            profile_name:str = DEFAULT_PROFILE_NAME, 
                            target_name:str=DEFAULT_TARGET_NAME, 
                            compiler_name:str= DEFAULT_COMPILER_NAME):
    assert path.exists()
    assert path.name == "CMakeLists.txt"
    assert path.parent.name == profile_name
    assert project_name in path.parent.parent.name
    assert path.parent.parent.parent.name == "cmake"
    assert path.parent.parent.parent.parent.name == compiler_name
    assert path.parent.parent.parent.parent.parent.name == target_name


def build_project(directory: str, args: list[str] = []) -> int:
    result = subprocess.run(
        ["python", "src/kiss.py", "-d", str(directory), "build"] + args,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    print(result.stdout, flush=True)
    print(result.stderr, flush=True)
    return result.returncode

def is_elf(file_path) -> bool:
    try:
        with open(file_path, "rb") as f:
            return f.read(4) == b"\x7fELF"
    except Exception:
        return False

def is_dyn(file_path) -> bool:
    path = Path(file_path)
    return path.suffix in [".so",".dll"] or is_elf(file_path)

def is_lib(file_path) -> bool:
    path = Path(file_path)
    return path.suffix in [".a", ".lib"] and not is_elf(file_path)


def validate_build( path: Path, 
                    project_name:str,
                    project_type:str,
                    profile_name:str = DEFAULT_PROFILE_NAME, 
                    target_name:str=DEFAULT_TARGET_NAME, 
                    compiler_name:str= DEFAULT_COMPILER_NAME):

    validate_cmakelist_path(path=path,
                            project_name=project_name,
                            profile_name=profile_name,
                            target_name=target_name,
                            compiler_name=compiler_name)
    # Assert artifact exist ( near CMakeList.txt )
    artifact_path = path.parent / project_name
    assert artifact_path.exists()
    # Assert type is correct
    match project_type:
        case "bin":
            assert is_elf(artifact_path)
        case "dyn":
            assert is_dyn(artifact_path)
        case "lib":
            assert is_lib(artifact_path)