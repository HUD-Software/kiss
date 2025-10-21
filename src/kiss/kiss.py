import argparse
from pathlib import Path
from commands.list import cmd_list
from commands.new import cmd_new, NewArgs
from commands.build import cmd_build
from commands.generate import cmd_generate

def call_new_command(args):
    cmd_new(NewArgs(args.directory, args.name, args.type))
    
def path_absolute(p):
    return Path(p).expanduser().resolve()

# --- CLI minimale ---
def main():
    #Read arguments
    parser = argparse.ArgumentParser(
        prog="kiss",
        description="Description:\n  Kiss is used to create, run C/C++ project\n\nUsage:\n  Cli [command] [options]\n",
        formatter_class=argparse.RawTextHelpFormatter
    )
    parser.add_argument(
        "-d", "--dir",
        dest="directory",
        type=lambda p: Path(p).expanduser().resolve(),
        default=Path.cwd(),
        help="Dossier contenant les modules (par défaut current directory)"
    )
    parser.add_argument(
        "-v", "--version",
        action="version",
        version="Kiss 1.0",
        help="Show version information"
    )
    subparsers = parser.add_subparsers(title="Commands", dest="command")
    
    # --- new command ---
    parser_new = subparsers.add_parser(
        "new",
        help="create a new project"
    )
    parser_new.add_argument(
        "type",
        choices=["bin", "dyn", "lib"],
        help="Type of project (bin|dyn|lib)"
    )
    parser_new.add_argument(
        "name",
        help="Name of the project"
    )
    parser_new.set_defaults(func=call_new_command)

    # --- generate command ---
    parser_generate = subparsers.add_parser(
        "generate",
        help="Generate build scripts of a project"
    )
    parser_generate.set_defaults(func=cmd_generate)

    # --- build command ---
    parser_build = subparsers.add_parser(
        "build",
        help="Build a project"
    )
    parser_build.add_argument(
        "name",
        help="Name of the project to build"
    )
    parser_build.set_defaults(func=cmd_build)

    # --- list command ---  
    parser_list = subparsers.add_parser(
        "list",
        help="List projects"
    )
    parser_list.set_defaults(func=cmd_list)

    # --- parse args ---
    args = parser.parse_args()
    
    # --- Call the associated command --- 
    if hasattr(args, "func"):
        args.func(args)
    else:
        parser.print_help()
    
  

if __name__ == "__main__":
    main()