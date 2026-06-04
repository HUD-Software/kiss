import typer

from context import KissContext
from toolchain.nodes.node import PropertyBool, PropertyNodeDict, PropertyNodeList, PropertyStr, PropertyStrList


def print_node(node, is_default: bool = False, indent: int = 0 ):
    """Recursively print a node and its properties."""
    prefix = "  " * indent
    if is_default:
        print(typer.style(f"{prefix}{node.name!r} (default)", fg=typer.colors.GREEN))
    else:
        print(f"{prefix}{node.name!r}")

    for prop in node.properties.values():
        if isinstance(prop, PropertyNodeList):
            print(f"{prefix}  .{prop.name}:")
            for child in prop.nodes:
                print_node(child, indent=indent + 2)
        elif isinstance(prop, PropertyNodeDict):
            print(f"{prefix}  .{prop.name}:")
            for key, child in prop.entries.items():
                print_node(child, indent=indent + 2)
        elif isinstance(prop, PropertyStrList):
            print(f"{prefix}  .{prop.name}: {prop.values}")
        elif isinstance(prop, PropertyStr):
            print(f"{prefix}  .{prop.name}: {prop.value!r}")
        elif isinstance(prop, PropertyBool):
            print(f"{prefix}  .{prop.name}: {prop.value}")
#         
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
    
    ctx.ensure_object(dict)


    if ctx.invoked_subcommand is None:
        typer.echo(ctx.get_help())
        raise typer.Exit()

    
list_app.add_typer(
    project_app,
    name="project",
)

# ── kiss list type ──────────────────────────────────────────────────────────
@list_app.command("types")
def types_cmd(ctx: typer.Context,
              detail: bool = typer.Option(False, "--detail", "-d", help="Show detailed output")):
    """
    List available project types.
    """

    kiss_ctx: KissContext = ctx.obj["ctx"]

    for t in kiss_ctx.known_project_types():
        if detail:
            print_node(t)
        else:
            typer.echo(f"{t.icon} {t.name}")

@list_app.command("targets")
def targets_cmd(ctx: typer.Context,
                detail: bool = typer.Option(False, "--detail", "-d", help="Show detailed output")):
    """
    List available project targets.
    """

    kiss_ctx: KissContext = ctx.obj["ctx"]

    for target in kiss_ctx.known_targets():
        is_default = target == kiss_ctx.default_target()
        if detail:
            print_node(target, is_default)
        else:
            if is_default:  
                typer.echo(typer.style(f"* {target.name} (default)", fg=typer.colors.GREEN))
            else:
                typer.echo(f"  {target.name}")

@list_app.command("compilers")
def compilers_cmd(ctx: typer.Context,
                  detail: bool = typer.Option(False, "--detail", "-d", help="Show detailed output")):
    """
    List available compilers.
    """

    kiss_ctx: KissContext = ctx.obj["ctx"]
    lists = kiss_ctx.known_compilers()
    for compiler in lists:
        is_default = (compiler == kiss_ctx.default_compiler(kiss_ctx.default_target().name))
        if detail:
            print_node(compiler, is_default)
        else:
            if is_default:
                typer.echo(typer.style(f"* {compiler.name} (default)", fg=typer.colors.GREEN))
            else:
                typer.echo(f"  {compiler.name}")


@list_app.command("linkers")
def linkers_cmd(ctx: typer.Context,
                detail: bool = typer.Option(False, "--detail", "-d", help="Show detailed output")):
    """
    List available linkers.
    """

    kiss_ctx: KissContext = ctx.obj["ctx"]
    lists = kiss_ctx.known_linkers()
    for linker in lists:
        is_default = (linker == kiss_ctx.default_compiler(kiss_ctx.default_target().name))
        if detail:
            print_node(linker, is_default)
        else:
            if is_default:
                typer.echo(typer.style(f"* {linker.name} (default)", fg=typer.colors.GREEN))
            else:
                typer.echo(f"  {linker.name}")


@list_app.command("profiles")
def linkers_cmd(ctx: typer.Context,
                detail: bool = typer.Option(False, "--detail", "-d", help="Show detailed output")):
    """
    List available profiles.
    """

    kiss_ctx: KissContext = ctx.obj["ctx"]
    lists = kiss_ctx.known_profiles()
    for profile in lists:
        is_default = kiss_ctx.default_profile()
        if detail:
            print_node(profile, is_default)
        else:
            if is_default:
                typer.echo(typer.style(f"* {profile.name} (default)", fg=typer.colors.GREEN))
            else:
                typer.echo(f"  {profile.name}")