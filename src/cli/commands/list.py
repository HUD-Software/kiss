from xml.etree.ElementTree import indent

import typer

from context import KissContext
from toolchain.nodes.node import Node, PropertyBool, PropertyNodeDict, PropertyNodeList, PropertyStr, PropertyStrList

from wcwidth import wcswidth
def flatten_block(block: str, indent: str = "") -> list[str]:
    return [(indent + line) for line in block.split("\n")]

def vis_len(s: str) -> int:
        return wcswidth(s)

def indent_block(block: str, indent: str) -> list[str]:
    return [(indent + line) for line in block.split("\n")]

def box(title: str, lines: list[str]) -> list[str]:
    content_width = max((vis_len(line) for line in lines), default=0)

    title = f" {title} "
    top_width = max(content_width, vis_len(title))

    top = f"╭─{title}" + "─" * (top_width - vis_len(title) + 1) + "╮"
    bottom = "╰" + "─" * (len(top) - 2) + "╯"

    out = [top]

    for line in lines:
        padding = content_width - vis_len(line)
        out.append(f"│ {line}{' ' * padding} │")

    out.append(bottom)
    return out

def inner_box(title: str, lines: list[str]) -> str:
    
    content_width = max((vis_len(line) for line in lines), default=0)

    title = f"{title} "
    top_width = max(content_width, vis_len(title)) + 2

    top = f"{title}" + "─" * (top_width - vis_len(title) + 1) + "╮"
    bottom = "╰" + "─" * (len(top) -2) + "╯"

    out = [top]

    for line in lines:
        padding = content_width - vis_len(line)
        out.append(f"│ {line}{' ' * padding} │")

    out.append(bottom)
    return "\n".join(out)

def split_props(properties):
    leaf = []
    nodes = []

    for prop in properties.values():
        if isinstance(prop, (PropertyStr, PropertyStrList, PropertyBool)):
            leaf.append(prop)
        else:
            nodes.append(prop)

    return leaf, nodes

def node_to_inner_box(node: Node):
    title = node.name
    lines = []

    leaf_props, node_props = split_props(node.properties)

    # LEAF PROPERTIES FIRST ─────────────────────────────
    for prop in leaf_props:

        if isinstance(prop, PropertyStr):
            lines.append(f"{prop.name}: {prop.value!r}")

        elif isinstance(prop, PropertyStrList):
            lines.append(f"{prop.name}: {prop.values}")

        elif isinstance(prop, PropertyBool):
            lines.append(f"{prop.name}: {prop.value}")

    # NODE PROPERTIES AFTER ─────────────────────────────
    for prop in node_props:
        if isinstance(prop, PropertyNodeList):
            for child in prop.nodes:
                child_box = node_to_inner_box(child)
                lines.extend(flatten_block(child_box))
        elif isinstance(prop, PropertyNodeDict):
             for _, child in prop.entries.items():
                child_box = node_to_inner_box(child)
                lines.extend(flatten_block(child_box))
    return inner_box(title, lines)

def node_to_box(node: Node, is_default=False):
    title = node.name + (" (default)" if is_default else "")
    lines = []
    
    leaf_props, node_props = split_props(node.properties)
    
    # LEAF PROPERTIES FIRST ─────────────────────────────
    for prop in leaf_props:
        if isinstance(prop, PropertyStr):
            lines.append(f"{prop.name}: {prop.value!r}")
        elif isinstance(prop, PropertyStrList):
            lines.append(f"{prop.name}: {prop.values}")
        elif isinstance(prop, PropertyBool):
            lines.append(f"{prop.name}: {prop.value}")

    # NODE PROPERTIES AFTER ─────────────────────────────
    for prop in node_props:
        if isinstance(prop, PropertyNodeList):
            inner_lines = []
            for child in prop.nodes:
                child_box = node_to_inner_box(child)
                inner_lines.extend(flatten_block(child_box))

            prop_box = inner_box(prop.name, inner_lines)
            lines.extend(flatten_block(prop_box))
        elif isinstance(prop, PropertyNodeDict):
            inner_lines = []
            for _, child in prop.entries.items():
                child_box = node_to_inner_box(child)
                inner_lines.extend(flatten_block(child_box))

            prop_box = inner_box(prop.name, inner_lines)
            lines.extend(flatten_block(prop_box))

    return box(title, lines)

def print_node_boxed(node, is_default: bool = False, indent: int = 0 ):
    lines = node_to_box(node, is_default)
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
              detail: bool = typer.Option(False, "--detail", "-d", help="Show detailed output")):
    """
    List available project types.
    """

    kiss_ctx: KissContext = ctx.obj["ctx"]

    for t in kiss_ctx.known_project_types():
        if detail:
            print_node_boxed(t)
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
            print_node_boxed(target, is_default)
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
            print_node_boxed(compiler, is_default)
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
            print_node_boxed(linker, is_default)
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
        is_default = kiss_ctx.default_profile() == profile
        if detail:
            print_node_boxed(profile, is_default)
        else:
            if is_default:
                typer.echo(typer.style(f"* {profile.name} (default)", fg=typer.colors.GREEN))
            else:
                typer.echo(f"  {profile.name}")