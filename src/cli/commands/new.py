import typer
import yaml
from pathlib import Path
from typing import Optional
from context import KissContext

MAIN_BIN = '''\
#include <iostream>

int main(int argc, char* argv[])
{{
    std::cout << "Hello from {name}!" << std::endl;
    return 0;
}}
'''

MAIN_LIB = '''\
#include "{name}.hpp"
#include <iostream>

void {name}_hello()
{{
    std::cout << "Hello from {name}!" << std::endl;
}}
'''

HEADER_LIB = '''\
#pragma once

void {name}_hello();
'''

MAIN_DYN = '''\
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
'''

HEADER_DYN = '''\
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
'''


def _write(path: Path, content: str):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content)
    typer.echo(typer.style(f"  ✓ created {path}", fg=typer.colors.GREEN))


def _create_sources(ptype: str, project_dir: Path, name: str):
    if ptype == "bin":
        _write(project_dir / "src" / "main.cpp", MAIN_BIN.format(name=name))
    elif ptype == "lib":
        _write(project_dir / "src" / f"{name}.cpp", MAIN_LIB.format(name=name))
        _write(project_dir / "include" / f"{name}.hpp", HEADER_LIB.format(name=name))
    elif ptype == "dyn":
        NAME = name.upper()
        _write(project_dir / "src" / f"{name}.cpp", MAIN_DYN.format(name=name, NAME=NAME))
        _write(project_dir / "include" / f"{name}.hpp", HEADER_DYN.format(name=name, NAME=NAME))
    else:
        # Custom type: generic bin layout
        _write(project_dir / "src" / "main.cpp", MAIN_BIN.format(name=name))
        typer.echo(typer.style(f"  · custom type '{ptype}' — generated a generic bin layout", fg=typer.colors.CYAN))


def _kiss_yaml(ptype: str, name: str) -> dict:
    entry: dict = {"name": name, "version": "0.1.0"}
    if ptype == "bin":
        entry["sources"] = ["src/main.cpp"]
    elif ptype in ("lib", "dyn"):
        entry["sources"] = [f"src/{name}.cpp"]
        entry["includes"] = ["include"]
    else:
        entry["sources"] = ["src/main.cpp"]
    return {ptype: [entry]}


# ── kiss new ──────────────────────────────────────────────────────────

def new_cmd(
    ctx:          typer.Context,
    project_type: str           = typer.Argument(..., help="Project type (use 'kiss new --help' for available types)"),
    project_name: str           = typer.Argument(..., help="Name of the new project"),
):
    """Create a new C++ project with kiss.yaml and starter source files."""
    kiss_ctx: KissContext = ctx.obj["ctx"]

    valid_types = set(ptype.name for ptype in kiss_ctx.known_project_types())

    if project_type not in valid_types:
        typer.echo(
            typer.style(
                f"error: unknown project type '{project_type}'.\n"
                f"  Available: {', '.join(sorted(valid_types))}",
                fg=typer.colors.RED,
            ), err=True
        )
        raise typer.Exit(1)

    project_dir = kiss_ctx.directory / project_name

    if project_dir.exists():
        typer.echo(typer.style(f"error: '{project_dir}' already exists", fg=typer.colors.RED), err=True)
        raise typer.Exit(1)

    typer.echo(f"\nCreating {project_type} project '{project_name}'…\n")

    project_dir.mkdir(parents=True)
    typer.echo(typer.style(f"  ✓ created {project_dir}/", fg=typer.colors.GREEN))

    _create_sources(project_type, project_dir, project_name)

    kiss_path = project_dir / "kiss.yaml"
    kiss_path.write_text(yaml.dump(_kiss_yaml(project_type, project_name), default_flow_style=False, sort_keys=False))
    typer.echo(typer.style(f"  ✓ created {kiss_path}", fg=typer.colors.GREEN))

    typer.echo()
    typer.echo(typer.style(f"  Project '{project_name}' ready!", fg=typer.colors.GREEN, bold=True))
    typer.echo()
    typer.echo(typer.style(f"  · cd {project_name}", fg=typer.colors.CYAN))
    typer.echo(typer.style(f"  · kiss generate", fg=typer.colors.CYAN))
    typer.echo(typer.style(f"  · kiss build", fg=typer.colors.CYAN))
    if project_type == "bin":
        typer.echo(typer.style(f"  · kiss run", fg=typer.colors.CYAN))
    typer.echo()
