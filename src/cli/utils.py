import os
import sys
import typer
import yaml
from pathlib import Path

# Built-in project types always available (even without kiss.yaml)
BUILTIN_PROJECT_TYPES = {"bin", "lib", "dyn"}


def find_kiss_yaml(directory: str) -> Path:
    """Locate kiss.yaml in the given directory. Exits with error if not found."""
    path = Path(directory) / "kiss.yaml"
    if not path.exists():
        typer.echo(typer.style(f"error: kiss.yaml not found in '{directory}'", fg=typer.colors.RED), err=True)
        raise typer.Exit(1)
    return path


def load_kiss_yaml(directory: str) -> dict:
    """Load and return the parsed kiss.yaml from directory."""
    path = find_kiss_yaml(directory)
    with open(path, encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


def get_project_types(kiss_data: dict) -> set[str]:
    """Return all known project types: built-in + custom from kiss.yaml."""
    custom = set()
    for p in kiss_data.get("project-types", []):
        if "name" in p:
            custom.add(p["name"])
    return BUILTIN_PROJECT_TYPES | custom


def get_all_projects(kiss_data: dict) -> list[dict]:
    """Return a flat list of all project entries across all types."""
    project_types = get_project_types(kiss_data)
    projects = []
    for ptype in project_types:
        for entry in kiss_data.get(ptype, []):
            projects.append({**entry, "_type": ptype})
    return projects


def resolve_project_name(kiss_data: dict, project_name: str | None) -> dict:
    """
    Resolve the target project entry.
    - If project_name is given, find it across all types.
    - If omitted and only one project exists, use it.
    - Otherwise error.
    """
    all_projects = get_all_projects(kiss_data)

    if project_name:
        matches = [p for p in all_projects if p["name"] == project_name]
        if not matches:
            typer.echo(typer.style(f"error: project '{project_name}' not found in kiss.yaml", fg=typer.colors.RED), err=True)
            raise typer.Exit(1)
        return matches[0]

    if len(all_projects) == 1:
        return all_projects[0]

    if len(all_projects) == 0:
        typer.echo(typer.style("error: no projects defined in kiss.yaml", fg=typer.colors.RED), err=True)
        raise typer.Exit(1)

    names = ", ".join(p["name"] for p in all_projects)
    typer.echo(typer.style(f"error: multiple projects found, specify one: {names}", fg=typer.colors.RED), err=True)
    raise typer.Exit(1)


def ok(msg: str):
    typer.echo(typer.style(f"  ✓ {msg}", fg=typer.colors.GREEN))

def info(msg: str):
    typer.echo(typer.style(f"  · {msg}", fg=typer.colors.CYAN))

def warn(msg: str):
    typer.echo(typer.style(f"  ! {msg}", fg=typer.colors.YELLOW))

def error(msg: str):
    typer.echo(typer.style(f"  ✗ {msg}", fg=typer.colors.RED), err=True)
