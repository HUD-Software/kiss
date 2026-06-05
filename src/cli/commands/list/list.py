from collections.abc import Iterable
import json
import typer
from cli.commands.list.formatter import format_node_to_boxed_lines, format_node_to_json, format_node_to_lines
from context import KissContext
from enum import Enum
from toolchain.nodes.node import PropertyDict

# Output mode used when list --mode is invoked ────────────────────────────────────
class OutputMode(str, Enum):
    plain = "plain"
    detail = "detail"
    boxed = "boxed"
    json = "json"


# Print all nodes in the correct mode ─────────────────────────────────────────────
def _print(it :Iterable[PropertyDict], mode: OutputMode = OutputMode.plain):
    if mode == OutputMode.json:
        data = [format_node_to_json(t) for t in it]
        typer.echo(json.dumps(data, indent=2))
    for node in it:
        if mode == OutputMode.plain:
            typer.echo(node.name)
        elif mode == OutputMode.detail:
            lines = format_node_to_lines(node)
            for line in lines:
                typer.echo(line)
        elif mode == OutputMode.boxed:
            lines = format_node_to_boxed_lines(node)
            for line in lines:
                typer.echo(line)
            
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
              mode: OutputMode = typer.Option(OutputMode.plain, "--mode", "-m", help="Select the output mode")):
    """
    List available project types.
    """
    kiss_ctx: KissContext = ctx.obj["ctx"]
    known_projects = kiss_ctx.known_project_types()
    if mode == OutputMode.plain:
        for project_type in known_projects:
            typer.echo(f"{project_type.icon} {project_type.name}")
    else:
        _print(known_projects, mode=mode)


@list_app.command("targets")
def targets_cmd(ctx: typer.Context,
                mode: OutputMode = typer.Option(OutputMode.plain, "--mode", "-m", help="Select the output mode")):
    """
    List available project targets.
    """

    kiss_ctx: KissContext = ctx.obj["ctx"]
    known_targets = kiss_ctx.known_targets()
    if mode == OutputMode.plain:
        for target in known_targets:
            is_default = target == kiss_ctx.default_target()
            if is_default:
                typer.echo(typer.style(f"* {target.name} (default)", fg=typer.colors.GREEN))
            else:
                typer.echo(f"  {target.name}")
    else:
        _print(known_targets, mode=mode)

        
@list_app.command("compilers")
def compilers_cmd(ctx: typer.Context,
                  mode: OutputMode = typer.Option(OutputMode.plain, "--mode", "-m", help="Select the output mode")):
    """
    List available compilers.
    """

    kiss_ctx: KissContext = ctx.obj["ctx"]
    known_compilers = kiss_ctx.known_compilers()
    if mode == OutputMode.plain:
        for compiler in known_compilers:
            is_default = compiler == kiss_ctx.default_compiler(kiss_ctx.default_target().name)
            if is_default:
                typer.echo(typer.style(f"* {compiler.name} (default)", fg=typer.colors.GREEN))
            else:
                typer.echo(f"  {compiler.name}")
    else:
        _print(known_compilers, mode=mode)

@list_app.command("linkers")
def linkers_cmd(ctx: typer.Context,
                mode: OutputMode = typer.Option(OutputMode.plain, "--mode", "-m", help="Select the output mode")):
    """
    List available linkers.
    """

    kiss_ctx: KissContext = ctx.obj["ctx"]
    known_linkers = kiss_ctx.known_linkers()
    if mode == OutputMode.plain:
        for linker in known_linkers:
            is_default = linker == kiss_ctx.default_linker(kiss_ctx.default_target().name)
            if is_default:
                typer.echo(typer.style(f"* {linker.name} (default)", fg=typer.colors.GREEN))
            else:
                typer.echo(f"  {linker.name}")
    else:
        _print(known_linkers, mode=mode)


@list_app.command("profiles")
def profiles_cmd(ctx: typer.Context,
                 mode: OutputMode = typer.Option(OutputMode.plain, "--mode", "-m", help="Select the output mode")):
    """
    List available profiles.
    """

    kiss_ctx: KissContext = ctx.obj["ctx"]
    known_profiles = kiss_ctx.known_profiles()
    if mode == OutputMode.plain:
        for profile in known_profiles:
            is_default = profile == kiss_ctx.default_profile()
            if is_default:
                typer.echo(typer.style(f"* {profile.name} (default)", fg=typer.colors.GREEN))
            else:
                typer.echo(f"  {profile.name}")
    else:
        _print(known_profiles, mode=mode)