import typer
from typing import Optional
from context import KissContext
from generator import get_generator, available_generators

# ── kiss build ──────────────────────────────────────────────────────────
def build_cmd(
    ctx:          typer.Context,
    project_name: Optional[str] = typer.Argument(None, help="Project name (optional if only one project)"),
    profile:      Optional[str] = typer.Option(
                      None, "--profile", "-p",
                      help="Build profile (e.g. debug, release, asan). Loaded from toolchain.",
                  ),
    target:       Optional[str] = typer.Option(
                      None, "--target", "-t",
                      help="Target triple (e.g. x86_64-pc-windows-msvc). Loaded from targets.yaml.",
                  ),
    compiler:     Optional[str] = typer.Option(
                      None, "--compiler", "-c",
                      help="Compiler to use (e.g. cl, clangcl). Loaded from compilers.yaml.",
                  ),
    generator:    Optional[str] = typer.Option(
                      None, "--generator", "-g",
                      help=f"Generator. Available: {', '.join(available_generators())}",
                  ),
):
    """Build a project."""
    kiss_ctx: KissContext = ctx.obj["ctx"]

    if not kiss_ctx.has_kiss_yaml():
        typer.echo(typer.style("error: no kiss.yaml found in directory", fg=typer.colors.RED), err=True)
        raise typer.Exit(1)

    project     = kiss_ctx.get_project(project_name)
    gen_name    = generator or kiss_ctx.kiss_data.get("generator", "cmake")
    profile_use = profile   or kiss_ctx.kiss_data.get("default-profile", "debug")
    target_use  = target    or kiss_ctx.default_target()
    compiler_use= compiler  or kiss_ctx.default_compiler(target_use)

    # Validate against loaded data
    _validate_profile(kiss_ctx, profile_use)
    _validate_target(kiss_ctx, target_use)
    _validate_compiler(kiss_ctx, compiler_use, target_use)

    try:
        gen = get_generator(gen_name)
    except ValueError as e:
        typer.echo(typer.style(f"error: {e}", fg=typer.colors.RED), err=True)
        raise typer.Exit(1)

    # Auto-generate if build files are missing
    cmake_file = kiss_ctx.directory / "CMakeLists.txt"
    if not cmake_file.exists():
        typer.echo(typer.style("  · CMakeLists.txt not found, running generate first…", fg=typer.colors.CYAN))
        gen.generate(project, kiss_ctx.directory)

    typer.echo(f"\nBuilding '{project['name']}' [{profile_use}] [{compiler_use}] [{target_use}]…\n")

    ret = gen.build(project, kiss_ctx.directory, profile_use)

    typer.echo()
    if ret == 0:
        typer.echo(typer.style(f"  ✓ build succeeded  [{profile_use}]", fg=typer.colors.GREEN))
        if project.get("_type") == "bin":
            typer.echo(typer.style(f"  · Next: kiss run {project['name']}", fg=typer.colors.CYAN))
    else:
        typer.echo(typer.style(f"  ✗ build failed (exit code {ret})", fg=typer.colors.RED), err=True)
        raise typer.Exit(ret)
    typer.echo()


def _validate_profile(kiss_ctx: KissContext, name: str):
    names = kiss_ctx.profile_names()
    if name not in names:
        typer.echo(
            typer.style(f"error: unknown profile '{name}'. Available: {', '.join(names)}", fg=typer.colors.RED),
            err=True,
        )
        raise typer.Exit(1)


def _validate_target(kiss_ctx: KissContext, name: str):
    names = kiss_ctx.target_names()
    if name not in names:
        typer.echo(
            typer.style(f"error: unknown target '{name}'. Available: {', '.join(names)}", fg=typer.colors.RED),
            err=True,
        )
        raise typer.Exit(1)


def _validate_compiler(kiss_ctx: KissContext, name: str, target_name: str):
    target = next((t for t in kiss_ctx.targets if t["name"] == target_name), {})
    supported = target.get("supported-compilers", [])
    if name not in supported:
        typer.echo(
            typer.style(
                f"error: compiler '{name}' not supported for target '{target_name}'.\n"
                f"  Supported: {', '.join(supported)}",
                fg=typer.colors.RED,
            ),
            err=True,
        )
        raise typer.Exit(1)
