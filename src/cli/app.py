import os

import typer
import yaml
from cli.commands.new import new_cmd
from cli.commands.generate import generate_cmd
from cli.commands.build import build_cmd
from cli.commands.run import run_cmd
from toolchain.parsers.compiler_parser import parse_compiler
from toolchain.parsers.linker_parser import parse_linker
from toolchain.parsers.profile_parser import parse_profile
from toolchain.parsers.project_parser import parse_project
from toolchain.parsers.target_parser import parse_target

app = typer.Typer(
    name="kiss",
    help="Kiss — a cargo-like build tool for C++",
    no_args_is_help=True,
    pretty_exceptions_show_locals=False,
)

def load_all_yaml(data_dir: str):
    """Charge tous les fichiers .yaml d'un répertoire."""
    result = {}

    compilers = []
    linkers  = []
    profiles = []
    projects = []
    targets = []
    for filename in os.listdir(data_dir):
        if filename.endswith(".yaml"):
            path = os.path.join(data_dir, filename)
            
            with open(path, "r") as f:
                data = yaml.safe_load(f)

                """Load and parse compilers.yaml, returning a list of CompilerNode."""
                for compiler_data in data.get("compilers", []):
                    compilers.append(parse_compiler(compiler_data))

                """Load and parse linkers.yaml, returning a list of LinkerNode."""
                for linker_data in data.get("linkers", []):
                    linkers.append(parse_linker(linker_data))
                
                """Load and parse profiles.yaml, returning a list of ProfileNode."""
                for profile_data in data.get("profiles", []):
                    profiles.append(parse_profile(profile_data))
                
                """Load and parse projects.yaml, returning a list of ProjectNode."""
                for project_data in data.get("projects", []):
                    projects.append(parse_project(project_data))
                
                """Load and parse targets.yaml, returning a list of TargetNode."""
                for target_data in data.get("targets", []):
                    targets.append(parse_target(target_data))

    # print_section("COMPILERS", compilers)
    # print_section("LINKERS",   linkers)
    # print_section("PROFILES",  profiles)
    # print_section("PROJECTS",  projects)
    # print_section("TARGETS",   targets)
    return result

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

    load_all_yaml("data")
    load_all_yaml(directory)


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
