import typer

from context import KissContext


project_app = typer.Typer(
    help="List project information.",
)

# ── kiss list project ──────────────────────────────────────────────────────────

@project_app.callback(invoke_without_command=True)
def project_cmd(ctx: typer.Context):
    """
    List detailed information about all projects.
    """

    if ctx.invoked_subcommand is not None:
        return

    kiss_ctx: KissContext = ctx.obj["ctx"]

    projects = [
        kiss_ctx.get_project(name)
        for name in kiss_ctx.project_names()
    ]

    if not projects:
        typer.echo("No projects defined.")
        return

    for project in projects:
        typer.echo(f"Name    : {project['name']}")
        typer.echo(f"Type    : {project['_type']}")
        typer.echo(f"Version : {project.get('version', '-')}")
        typer.echo()

# ── kiss list project name ──────────────────────────────────────────────────────────
@project_app.command("name")
def project_name_cmd(ctx: typer.Context):
    """
    List project names only.
    """

    kiss_ctx: KissContext = ctx.obj["ctx"]

    names = sorted(kiss_ctx.project_names())

    if not names:
        typer.echo("No projects defined.")
        return

    for name in names:
        typer.echo(name)


list_app = typer.Typer(
    help="List available objects."
)

@list_app.callback(invoke_without_command=True)
def list_callback(ctx: typer.Context):
    if ctx.invoked_subcommand is None:
        typer.echo(ctx.get_help())
        raise typer.Exit()
    
list_app.add_typer(
    project_app,
    name="project",
)

# ── kiss list type ──────────────────────────────────────────────────────────
@list_app.command("types")
def types_cmd(ctx: typer.Context):
    """
    List available project types.
    """

    kiss_ctx: KissContext = ctx.obj["ctx"]

    for project_type in sorted(kiss_ctx.known_project_types()):
        typer.echo(project_type)

@list_app.command("targets")
def targets_cmd(ctx: typer.Context):
    """
    List available project targets.
    """

    kiss_ctx: KissContext = ctx.obj["ctx"]

    for target in kiss_ctx.known_targets():
        if target == kiss_ctx.default_target():
            typer.echo(typer.style(f"* {target['name']} (default)", fg=typer.colors.GREEN))
        else:
            typer.echo(f"  {target['name']}")

@list_app.command("compilers")
def compilers_cmd(ctx: typer.Context):
    """
    List available compilers.
    """

    kiss_ctx: KissContext = ctx.obj["ctx"]
    lists = kiss_ctx.known_compilers()
    for compiler in lists:
        if compiler == kiss_ctx.default_compiler():
            typer.echo(typer.style(f"* {compiler['name']} (default)", fg=typer.colors.GREEN))
        else:
            typer.echo(f"  {compiler['name']}")


@list_app.command("linkers")
def linkers_cmd(ctx: typer.Context):
    """
    List available linkers.
    """

    kiss_ctx: KissContext = ctx.obj["ctx"]
    lists = kiss_ctx.known_linkers()
    for linker in lists:
        if linker == kiss_ctx.default_linker():
            typer.echo(typer.style(f"* {linker['name']} (default)", fg=typer.colors.GREEN))
        else:
            typer.echo(f"  {linker['name']}")