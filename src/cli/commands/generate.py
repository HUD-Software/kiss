import typer
from pathlib import Path
from typing import Optional
from cli.utils import load_kiss_yaml, resolve_project_name, ok, info, error
from generator import get_generator, available_generators


def generate_cmd(
    project_name: Optional[str] = typer.Argument(None, help="Project name (optional if only one project)"),
    generator:    Optional[str] = typer.Option(None, "--generator", "-g",
                                    help=f"Generator to use. Available: {', '.join(available_generators())}"),
    directory:    Optional[str] = typer.Option(".", "--directory", "-d", help="Directory containing kiss.yaml"),
):
    """Generate build files (CMakeLists.txt, …) for a project."""

    project_dir = Path(directory).resolve()
    kiss_data   = load_kiss_yaml(str(project_dir))
    project     = resolve_project_name(kiss_data, project_name)

    # Resolve generator: explicit arg > kiss.yaml > default cmake
    gen_name = generator or kiss_data.get("generator", "cmake")

    try:
        gen = get_generator(gen_name)
    except ValueError as e:
        error(str(e))
        raise typer.Exit(1)

    typer.echo(f"\nGenerating '{project['name']}' with {gen_name}…\n")

    gen.generate(project, project_dir)

    ok(f"CMakeLists.txt written to {project_dir}")
    typer.echo()
    info(f"Next: kiss build {project['name']}")
    typer.echo()
