import sys
from types import ModuleType
from pathlib import Path
import importlib.util

# --- Fonction de chargement dynamique des modules ---
def load_modules(path: Path):
    load_modules = {}
    if not path.exists():
        return load_modules
    
    for file in path.glob("*.py"):
        module_name = file.stem
        spec = importlib.util.spec_from_file_location(module_name, file)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        load_modules[module_name] = module
    return load_modules

registered_projects = {}

# --- décorateur pour créer automatiquement le module kiss ---
def register_in_kiss(func):
    """
    Décorateur qui ajoute la fonction/décorateur dans sys.modules['kiss'].
    """
    # créer le module kiss s'il n'existe pas encore
    if "kiss" not in sys.modules:
        kiss_module = ModuleType("kiss")
        sys.modules["kiss"] = kiss_module
    else:
        kiss_module = sys.modules["kiss"]
    
    # ajouter la fonction/décorateur dans le module kiss
    setattr(kiss_module, func.__name__, func)
    return func

@register_in_kiss
def KissProject(name):
    """Décorateur pour enregistrer un projet auprès du moteur"""
    def wrapper(cls):
        cls._kiss_name = name
        registered_projects[name] = cls
        return cls
    return wrapper

@register_in_kiss
def Description(text):
    """Décorateur pour ajouter une description"""
    def wrapper(cls):
        cls._kiss_description = text
        return cls
    return wrapper

@register_in_kiss
def run_prebuild(name):
    project_cls = registered_projects.get(name)
    if project_cls:
        instance = project_cls()
        if hasattr(instance, "prebuild"):
            instance.prebuild()
        else:
            print(f"{name} n'a pas de méthode prebuild")

@register_in_kiss
def run_postbuild(name):
    project_cls = registered_projects.get(name)
    if project_cls:
        instance = project_cls()
        if hasattr(instance, "postbuild"):
            instance.postbuild()
        else:
            print(f"{name} n'a pas de méthode postbuild")