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

# --- CLI minimale ---
def main():
    #Read arguments
    parser = argparse.ArgumentParser(description="KISS - Build system Python prototype")
    parser.add_argument("--list", action="store_true", help="Lister les plugins disponibles")
    parser.add_argument("modules_dir", nargs="?", default="modules", help="Dossier contenant les modules")
    args = parser.parse_args()
    
    # Set current directory
    base_dir = Path.cwd()
    modules_dir = Path(args.modules_dir)
    if not modules_dir.is_absolute():
        modules_dir = base_dir / modules_dir
    print(modules_dir)
    load_plugins(Path(args .modules_dir))

    if args.list:
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

if __name__ == "__main__":
    main()