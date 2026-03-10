
from pathlib import Path
import subprocess


def new_project(args: list[str]):
    result = subprocess.run(
        ["python", "src/kiss.py", "-d", "runtime", "new"] + args,
        capture_output=True,
        text=True,
    )
    print(result.stdout, flush=True)
    print(result.stderr, flush=True)
    assert result.returncode == 0

def new_inner_project(project_name :str, args: list[str]):
    result = subprocess.run(
        ["python", "src/kiss.py", "-d", str(Path("runtime") / project_name), "new"] + args,
        capture_output=True,
        text=True,
    )
    print(result.stdout, flush=True)
    print(result.stderr, flush=True)
    assert result.returncode == 0

def add_dependency(project_name :str, args : list[str]):
    result = subprocess.run(
        ["python", "src/kiss.py", "-d", str(Path("runtime") / project_name), "add"] + args,
        capture_output=True,
        text=True,
    )
    print(result.stdout, flush=True)
    print(result.stderr, flush=True)
    assert result.returncode == 0