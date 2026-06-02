"""
cli/app.py
----------
Typer app with a global --directory / -d option.
The context (KissContext) is loaded once in the main callback
and stored in typer's obj so every sub-command can access it.
"""

import typer
from typing import Optional
from cli.commands.new      import new_cmd
from cli.commands.generate import generate_cmd
from cli.commands.build    import build_cmd
from cli.commands.run      import run_cmd
from cli.commands.list     import list_app
app = typer.Typer(
    name="kiss",
    help="Kiss — a cargo-like build tool for C++",
    no_args_is_help=True,
    pretty_exceptions_show_locals=False,
)


@app.callback()
def main_callback(
    ctx: typer.Context,
    directory: Optional[str] = typer.Option(
        ".",
        "--directory", "-d",
        help="Working directory (default: current). kiss.yaml is looked up here.",
        is_eager=False,
    ),
):
    """Kiss — a cargo-like build tool for C++"""
    from context import load_context
    ctx.ensure_object(dict)
    ctx.obj["ctx"] = load_context(directory)


app.add_typer(list_app, name="list")
app.command("new")(new_cmd)
app.command("generate")(generate_cmd)
app.command("build")(build_cmd)
app.command("run")(run_cmd)
