import subprocess
import typer
from pathlib import Path
from typing import Optional
from context import KissContext


def _find_executable(project_dir: Path, name: str, profile: str) -> Path | None:
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

# ── kiss run ──────────────────────────────────────────────────────────

def run_cmd(
    ctx:          typer.Context,
    project_name: Optional[str] = typer.Argument(None, help="Project name (optional if only one project)"),
    profile:      Optional[str] = typer.Option(
                      None, "--profile", "-p",
                      help="Profile to run (default: debug). Available profiles loaded from toolchain.",
                  ),
    args:         Optional[str] = typer.Option(None, "--args", "-a", help="Arguments to pass to the executable"),
):
    """Run a compiled binary project."""
    kiss_ctx: KissContext = ctx.obj["ctx"]

    if not kiss_ctx.has_kiss_yaml():
        typer.echo(typer.style("error: no kiss.yaml found in directory", fg=typer.colors.RED), err=True)
        raise typer.Exit(1)

    project     = kiss_ctx.get_project(project_name)
    profile_use = profile or kiss_ctx.kiss_data.get("default-profile", "debug")

    ptype = project.get("_type", "bin")
    if ptype != "bin":
        typer.echo(
            typer.style(f"error: '{project['name']}' is of type '{ptype}', only 'bin' projects can be run", fg=typer.colors.RED),
            err=True,
        )
        raise typer.Exit(1)

    # Validate profile
    names = kiss_ctx.profile_names()
    if profile_use not in names:
        typer.echo(
            typer.style(f"error: unknown profile '{profile_use}'. Available: {', '.join(names)}", fg=typer.colors.RED),
            err=True,
        )
        raise typer.Exit(1)

    exe = _find_executable(kiss_ctx.directory, project["name"], profile_use)
    if exe is None:
        typer.echo(
            typer.style(
                f"error: executable not found for '{project['name']}' [{profile_use}].\n"
                f"  Run 'kiss build' first.",
                fg=typer.colors.RED,
            ),
            err=True,
        )
        raise typer.Exit(1)

    cmd = [str(exe)] + (args.split() if args else [])

    typer.echo(f"\nRunning '{project['name']}' [{profile_use}]…\n")
    typer.echo(typer.style(f"  · $ {' '.join(cmd)}", fg=typer.colors.CYAN))
    typer.echo()

    ret = subprocess.call(cmd)
    typer.echo()
    if ret != 0:
        typer.echo(typer.style(f"  ✗ process exited with code {ret}", fg=typer.colors.RED), err=True)
        raise typer.Exit(ret)
