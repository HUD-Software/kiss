import json
from platform import node
from statistics import mode
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

def node_to_lines(node: Node, indent: int = 0) -> list[str]:
    prefix = "  " * indent
    lines = []

    leaf_props, node_props = split_props(node.properties)

    #  NODE HEADER ─────────────────────────────
    lines.append(f"{prefix}{node.name}")

    # LEAF PROPS FIRST ─────────────────────────
    for prop in leaf_props:
        if isinstance(prop, PropertyStr):
            lines.append(f"{prefix}  {prop.name}: {prop.value!r}")
        elif isinstance(prop, PropertyStrList):
            lines.append(f"{prefix}  {prop.name}: {prop.values}")
        elif isinstance(prop, PropertyBool):
            lines.append(f"{prefix}  {prop.name}: {prop.value}")

    # NODE PROPS AFTER ────────────────────────
    for prop in node_props:
        if isinstance(prop, PropertyNodeList):
            lines.append(f"{prefix}  {prop.name}:")

            for child in prop.nodes:
                lines.extend(node_to_lines(child, indent + 2))
        elif isinstance(prop, PropertyNodeDict):
            lines.append(f"{prefix}  {prop.name}:")

            for key, child in prop.entries.items():
                lines.append(f"{prefix}    {key}:")
                lines.extend(node_to_lines(child, indent + 3))

    return lines

def node_to_json(node: Node) -> dict:
    leaf_props, node_props = split_props(node.properties)

    result = {
        "name": node.name,
    }

    # LEAF PROPERTIES ─────────────────────────────
    for prop in leaf_props:
        if isinstance(prop, PropertyStr):
            result[prop.name] = prop.value
        elif isinstance(prop, PropertyStrList):
            result[prop.name] = prop.values
        elif isinstance(prop, PropertyBool):
            result[prop.name] = prop.value

    # NODE LISTS ─────────────────────────────
    for prop in node_props:
        if isinstance(prop, PropertyNodeList):
            result[prop.name] = []
            for node in prop.nodes:
                result[prop.name].append(node_to_json(node))
        elif isinstance(prop, PropertyNodeDict):
            result[prop.name] = {}
            for name, node in prop.entries.items():
                result[prop.name][name] = node_to_json(node)

    return result

from enum import Enum

class OutputMode(str, Enum):
    plain = "plain"
    detail = "detail"
    boxed = "boxed"
    json = "json"

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
    if mode == OutputMode.json:
        data = [node_to_json(t) for t in kiss_ctx.known_project_types()]
        typer.echo(json.dumps(data, indent=2, ensure_ascii=False))
    else:
        for project_type in kiss_ctx.known_project_types():
            if mode == OutputMode.plain:
                typer.echo(f"{project_type.icon} {project_type.name}")
            elif mode == OutputMode.detail:
                lines = node_to_lines(project_type)
                for line in lines:
                    typer.echo(line)
            elif mode == OutputMode.boxed:
                print_node_boxed(project_type)

@list_app.command("targets")
def targets_cmd(ctx: typer.Context,
                mode: OutputMode = typer.Option(OutputMode.plain, "--mode", "-m", help="Select the output mode")):
    """
    List available project targets.
    """

    kiss_ctx: KissContext = ctx.obj["ctx"]

    for target in kiss_ctx.known_targets():
        if mode == OutputMode.plain:
            is_default = target == kiss_ctx.default_target()
            if is_default:
                typer.echo(typer.style(f"* {target.name} (default)", fg=typer.colors.GREEN))
            else:
                typer.echo(f"  {target.name}")
        elif mode == OutputMode.detail:
            lines = node_to_lines(target)
            for line in lines:
                typer.echo(line)
        elif mode == OutputMode.boxed:
            print_node_boxed(target)
        elif mode == OutputMode.json:
            data = node_to_json(target)
            typer.echo(json.dumps(data, indent=2, ensure_ascii=False))
        
@list_app.command("compilers")
def compilers_cmd(ctx: typer.Context,
                  mode: OutputMode = typer.Option(OutputMode.plain, "--mode", "-m", help="Select the output mode")):
    """
    List available compilers.
    """

    kiss_ctx: KissContext = ctx.obj["ctx"]
    lists = kiss_ctx.known_compilers()
    for compiler in lists:
        if mode == OutputMode.plain:
            is_default = (compiler == kiss_ctx.default_compiler(kiss_ctx.default_target().name))
            if is_default:
                typer.echo(typer.style(f"* {compiler.name} (default)", fg=typer.colors.GREEN))
            else:
                typer.echo(f"  {compiler.name}")
        elif mode == OutputMode.detail:
            lines = node_to_lines(compiler)
            for line in lines:
                typer.echo(line)
        elif mode == OutputMode.boxed:
            print_node_boxed(compiler)
        elif mode == OutputMode.json:
            data = node_to_json(compiler)
            typer.echo(json.dumps(data, indent=2, ensure_ascii=False))

@list_app.command("linkers")
def linkers_cmd(ctx: typer.Context,
                mode: OutputMode = typer.Option(OutputMode.plain, "--mode", "-m", help="Select the output mode")):
    """
    List available linkers.
    """

    kiss_ctx: KissContext = ctx.obj["ctx"]
    lists = kiss_ctx.known_linkers()
    for linker in lists:
        if mode == OutputMode.plain:
            is_default = (linker == kiss_ctx.default_compiler(kiss_ctx.default_target().name))
            if is_default:
                typer.echo(typer.style(f"* {linker.name} (default)", fg=typer.colors.GREEN))
            else:
                typer.echo(f"  {linker.name}")
        elif mode == OutputMode.detail:
            lines = node_to_lines(linker)
            for line in lines:
                typer.echo(line)
        elif mode == OutputMode.boxed:
            print_node_boxed(linker)
        elif mode == OutputMode.json:
            data = node_to_json(linker)
            typer.echo(json.dumps(data, indent=2, ensure_ascii=False))


@list_app.command("profiles")
def profiles_cmd(ctx: typer.Context,
                 mode: OutputMode = typer.Option(OutputMode.plain, "--mode", "-m", help="Select the output mode")):
    """
    List available profiles.
    """

    kiss_ctx: KissContext = ctx.obj["ctx"]
    lists = kiss_ctx.known_profiles()
    for profile in lists:
        if mode == OutputMode.plain:
            is_default = kiss_ctx.default_profile() == profile
            if is_default:
                typer.echo(typer.style(f"* {profile.name} (default)", fg=typer.colors.GREEN))
            else:
                typer.echo(f"  {profile.name}")
        elif mode == OutputMode.detail:
            lines = node_to_lines(profile)
            for line in lines:
                typer.echo(line)
        elif mode == OutputMode.boxed:
            print_node_boxed(profile)
        elif mode == OutputMode.json:
            data = node_to_json(profile)
            typer.echo(json.dumps(data, indent=2, ensure_ascii=False))