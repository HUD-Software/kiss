import typer
from pathlib import Path
from typing import Optional
from cli.utils import load_kiss_yaml, resolve_project_name, ok, info, error, warn
from generator import get_generator, available_generators


def build_cmd(
    project_name: Optional[str] = typer.Argument(None, help="Project name (optional if only one project)"),
    profile:      str           = typer.Option("debug", "--profile", "-p", help="Build profile: debug, release, asan…"),
    generator:    Optional[str] = typer.Option(None, "--generator", "-g",
                                    help=f"Generator to use. Available: {', '.join(available_generators())}"),
    directory:    Optional[str] = typer.Option(".", "--directory", "-d", help="Directory containing kiss.yaml"),
):
    """Build a project (runs generate if needed, then compiles)."""

    project_dir = Path(directory).resolve()
    kiss_data   = load_kiss_yaml(str(project_dir))
    project     = resolve_project_name(kiss_data, project_name)

    gen_name = generator or kiss_data.get("generator", "cmake")

    try:
        gen = get_generator(gen_name)
    except ValueError as e:
        error(str(e))
        raise typer.Exit(1)

    # Auto-generate if CMakeLists.txt is missing
    cmake_file = project_dir / "CMakeLists.txt"
    if not cmake_file.exists():
        info("CMakeLists.txt not found, running generate first…")
        gen.generate(project, project_dir)
        ok("generated build files")

    typer.echo(f"\nBuilding '{project['name']}' [{profile}] with {gen_name}…\n")

    ret = gen.build(project, project_dir, profile)

    if ret == 0:
        typer.echo()
        ok(f"build succeeded  [{profile}]")
        if project.get("_type") == "bin":
            info(f"Next: kiss run {project['name']} --profile {profile}")
    else:
        typer.echo()
        error(f"build failed (exit code {ret})")
        raise typer.Exit(ret)

    typer.echo()
