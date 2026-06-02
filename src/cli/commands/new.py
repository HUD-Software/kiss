import os
import typer
import yaml
from pathlib import Path
from typing import Optional
from cli.utils import BUILTIN_PROJECT_TYPES, ok, info, error, load_kiss_yaml, get_project_types

# ── C++ source templates ──────────────────────────────────────────────────────

MAIN_BIN = """\
#include <iostream>

int main(int argc, char* argv[])
{{
    std::cout << "Hello from {name}!" << std::endl;
    return 0;
}}
"""

MAIN_LIB = """\
#include "{name}.hpp"
#include <iostream>

void {name}_hello()
{{
    std::cout << "Hello from {name}!" << std::endl;
}}
"""

HEADER_LIB = """\
#pragma once

void {name}_hello();
"""

MAIN_DYN = """\
#include "{name}.hpp"
#include <iostream>

#ifdef _WIN32
#  define {NAME}_API __declspec(dllexport)
#else
#  define {NAME}_API __attribute__((visibility("default")))
#endif

{NAME}_API void {name}_hello()
{{
    std::cout << "Hello from {name} (dynamic library)!" << std::endl;
}}
"""

HEADER_DYN = """\
#pragma once

#ifdef _WIN32
#  ifdef {NAME}_EXPORTS
#    define {NAME}_API __declspec(dllexport)
#  else
#    define {NAME}_API __declspec(dllimport)
#  endif
#else
#  define {NAME}_API __attribute__((visibility("default")))
#endif

{NAME}_API void {name}_hello();
"""


def _write(path: Path, content: str):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content)
    ok(f"created {path}")


def _create_bin(project_dir: Path, name: str):
    _write(project_dir / "src" / "main.cpp", MAIN_BIN.format(name=name))


def _create_lib(project_dir: Path, name: str):
    _write(project_dir / "src" / f"{name}.cpp", MAIN_LIB.format(name=name))
    _write(project_dir / "include" / f"{name}.hpp", HEADER_LIB.format(name=name))


def _create_dyn(project_dir: Path, name: str):
    NAME = name.upper()
    _write(project_dir / "src" / f"{name}.cpp", MAIN_DYN.format(name=name, NAME=NAME))
    _write(project_dir / "include" / f"{name}.hpp", HEADER_DYN.format(name=name, NAME=NAME))


def _kiss_yaml(ptype: str, name: str) -> dict:
    """Build the initial kiss.yaml content for the new project."""
    entry: dict = {"name": name, "version": "0.1.0"}

    if ptype == "bin":
        entry["sources"] = ["src/main.cpp"]
    elif ptype == "lib":
        entry["sources"] = [f"src/{name}.cpp"]
        entry["includes"] = ["include"]
    elif ptype == "dyn":
        entry["sources"] = [f"src/{name}.cpp"]
        entry["includes"] = ["include"]
    else:
        # Custom type: generic sources
        entry["sources"] = ["src/main.cpp"]

    return {ptype: [entry]}


def new_cmd(
    project_type: str,
    project_name: str,
    directory: str,
):
    """Create a new C++ project with a kiss.yaml and starter source files."""

    base_dir = Path(directory).resolve()

    # Determine valid project types
    # If a kiss.yaml already exists in base_dir, load custom types from it
    kiss_yaml_path = base_dir / "kiss.yaml"
    valid_types = set(BUILTIN_PROJECT_TYPES)
    if kiss_yaml_path.exists():
        try:
            existing = load_kiss_yaml(str(base_dir))
            valid_types |= get_project_types(existing)
        except Exception:
            pass

    if project_type not in valid_types:
        error(f"unknown project type '{project_type}'. Valid types: {', '.join(sorted(valid_types))}")
        raise typer.Exit(1)

    project_dir = base_dir / project_name

    if project_dir.exists():
        error(f"directory '{project_dir}' already exists")
        raise typer.Exit(1)

    typer.echo(f"\nCreating {project_type} project '{project_name}'…\n")

    # Create directory structure
    project_dir.mkdir(parents=True)
    ok(f"created {project_dir}/")

    # Generate source files based on type
    if project_type == "bin":
        _create_bin(project_dir, project_name)
    elif project_type == "lib":
        _create_lib(project_dir, project_name)
    elif project_type == "dyn":
        _create_dyn(project_dir, project_name)
    else:
        # Custom type: treat like bin (user can customise)
        _create_bin(project_dir, project_name)
        info(f"custom type '{project_type}' — generated a generic bin layout")

    # Write kiss.yaml
    kiss_content = _kiss_yaml(project_type, project_name)
    kiss_path = project_dir / "kiss.yaml"
    kiss_path.write_text(
        yaml.dump(kiss_content, default_flow_style=False, sort_keys=False)
    )
    ok(f"created {kiss_path}")

    typer.echo()
    typer.echo(typer.style(f"  Project '{project_name}' ready!", fg=typer.colors.GREEN, bold=True))
    typer.echo()
    info(f"cd {project_name}")
    info(f"kiss generate")
    info(f"kiss build")
    if project_type == "bin":
        info(f"kiss run")
    typer.echo()
