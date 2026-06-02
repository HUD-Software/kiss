import subprocess
import typer
from pathlib import Path
from typing import Optional
from cli.utils import load_kiss_yaml, resolve_project_name, ok, info, error, warn


def _find_executable(project_dir: Path, name: str, profile: str) -> Path | None:
    """Search for the compiled binary in common build output locations."""
    candidates = [
        project_dir / "build" / profile / name,
        project_dir / "build" / profile / f"{name}.exe",
        project_dir / "build" / name,
        project_dir / "build" / f"{name}.exe",
    ]
    for c in candidates:
        if c.exists():
            return c
    return None


def run_cmd(
    project_name: Optional[str] = typer.Argument(None, help="Project name (optional if only one project)"),
    profile:      str           = typer.Option("debug", "--profile", "-p", help="Build profile to run"),
    directory:    Optional[str] = typer.Option(".", "--directory", "-d", help="Directory containing kiss.yaml"),
    args:         Optional[str] = typer.Option(None, "--args", "-a", help="Arguments to pass to the executable"),
):
    """Run a compiled binary project."""

    project_dir = Path(directory).resolve()
    kiss_data   = load_kiss_yaml(str(project_dir))
    project     = resolve_project_name(kiss_data, project_name)

    ptype = project.get("_type", "bin")
    if ptype != "bin":
        error(f"project '{project['name']}' is of type '{ptype}', only 'bin' projects can be run")
        raise typer.Exit(1)

    exe = _find_executable(project_dir, project["name"], profile)
    if exe is None:
        error(f"executable not found for '{project['name']}' [{profile}]. Run 'kiss build' first.")
        raise typer.Exit(1)

    cmd = [str(exe)]
    if args:
        cmd += args.split()

    typer.echo(f"\nRunning '{project['name']}' [{profile}]…\n")
    info(f"$ {' '.join(cmd)}")
    typer.echo()

    ret = subprocess.call(cmd)

    typer.echo()
    if ret != 0:
        error(f"process exited with code {ret}")
        raise typer.Exit(ret)
