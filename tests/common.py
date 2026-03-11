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
    assert project_name in str(path)
    assert profile_name in str(path)
    assert target_name in str(path)
    assert compiler_name in str(path)