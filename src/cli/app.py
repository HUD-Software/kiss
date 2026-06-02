import typer
from cli.commands.new import new_cmd
from cli.commands.generate import generate_cmd
from cli.commands.build import build_cmd
from cli.commands.run import run_cmd

app = typer.Typer(
    name="kiss",
    help="Kiss — a cargo-like build tool for C++",
    no_args_is_help=True,
    pretty_exceptions_show_locals=False,
)
@app.callback()
def global_options(
    ctx: typer.Context,
    directory: str = typer.Option(
        ".",
        "--directory",
        "-d",
        help="Working directory (default: current)",
    ),
):
    """
    Global options for the Kiss CLI.
    """
    ctx.obj = {
        "directory": directory,
    }

@app.command("new")
def new_cmd_cli(
    ctx: typer.Context,
    project_type: str = typer.Argument(..., help="Project type: bin, lib, dyn or a custom type from kiss.yaml"),
    project_name: str = typer.Argument(..., help="Project name"),
):
    new_cmd(project_type, project_name, ctx.obj["directory"])

app.command("generate")(generate_cmd)
app.command("build")(build_cmd)
app.command("run")(run_cmd)
