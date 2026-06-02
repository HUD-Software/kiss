import typer
from typing import Optional
from context import KissContext
from generator import get_generator, available_generators

# ── kiss generate ──────────────────────────────────────────────────────────
def generate_cmd(
    ctx:          typer.Context,
    project_name: Optional[str] = typer.Argument(None, help="Project name (optional if only one project)"),
    generator:    Optional[str] = typer.Option(
                      None, "--generator", "-g",
                      help=f"Generator to use (default: cmake). Available: {', '.join(available_generators())}",
                  ),
):
    """Generate build files (CMakeLists.txt, …) for a project."""
    kiss_ctx: KissContext = ctx.obj["ctx"]

    if not kiss_ctx.has_kiss_yaml():
        typer.echo(typer.style("error: no kiss.yaml found in directory", fg=typer.colors.RED), err=True)
        raise typer.Exit(1)

    project  = kiss_ctx.get_project(project_name)
    gen_name = generator or kiss_ctx.kiss_data.get("generator", "cmake")

    try:
        gen = get_generator(gen_name)
    except ValueError as e:
        typer.echo(typer.style(f"error: {e}", fg=typer.colors.RED), err=True)
        raise typer.Exit(1)

    typer.echo(f"\nGenerating '{project['name']}' with {gen_name}…\n")
    gen.generate(project, kiss_ctx.directory)

    typer.echo(typer.style(f"  ✓ CMakeLists.txt written to {kiss_ctx.directory}", fg=typer.colors.GREEN))
    typer.echo()
    typer.echo(typer.style(f"  · Next: kiss build {project['name']}", fg=typer.colors.CYAN))
    typer.echo()
