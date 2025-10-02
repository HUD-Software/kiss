import argparse
import importlib.util
from pathlib import Path
import sys
from registry import registered_projects
import modules

# --- Fonction de chargement dynamique des plugins ---
def load_plugins(path: Path):
    plugins = {}
    if not path.exists():
        return plugins
    
    for file in path.glob("*.py"):
        module_name = file.stem
        spec = importlib.util.spec_from_file_location(module_name, file)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        plugins[module_name] = module
    return plugins

def cmd_new(args):
    print(f"Creating a new {args.type} project named {args.name}")

def cmd_generate(args):
    print("Generating build scripts...")

def cmd_build(args):
    print(f"Building project {args.name}...")

def cmd_list(args):
    print("Listing all projects...")

def cmd_list(args):
    load_plugins(args.directory)

    if not registered_projects:
        print("Aucun projet trouvé !")
    else:
        for name, cls in registered_projects.items():
            print(f"Projet trouvé : {name}, description : {getattr(cls, '_kiss_description', '')}")
            instance = cls()
            if hasattr(instance, "prebuild"):
                instance.prebuild()
            if hasattr(instance, "postbuild"):
                instance.postbuild()


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
    parser_new.set_defaults(func=cmd_new)

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