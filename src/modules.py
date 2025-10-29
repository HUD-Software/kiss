import os
import sys
from types import ModuleType
from pathlib import Path
import importlib.util
import inspect
from project import ProjectType

# --- Fonction de chargement dynamique des modules ---
def load_modules(path: Path, recursive: bool = False):
    load_modules = {}
    if not path.exists():
        return load_modules
    
    pattern = "**/*.py" if recursive else "*.py"

    for file in path.glob(pattern):
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
def Bin(name):
    """Décorateur pour enregistrer un projet binaire auprès du moteur"""
    def wrapper(cls):
        cls._project_name = name
        cls._project_type = ProjectType.bin
        # Récupérer le fichier Python où le décorateur est utilisé
        frame = inspect.currentframe()
        caller_frame = frame.f_back
        filename = caller_frame.f_code.co_filename
        cls._project_file = os.path.abspath(filename)
        registered_projects[name] = cls
        return cls
    return wrapper

@register_in_kiss
def Lib(name):
    """Décorateur pour enregistrer un projet libraire statique auprès du moteur"""
    def wrapper(cls):
        cls._project_name = name
        cls._project_type = ProjectType.lib
        # Récupérer le fichier Python où le décorateur est utilisé
        frame = inspect.currentframe()
        caller_frame = frame.f_back
        filename = caller_frame.f_code.co_filename
        cls._project_file = os.path.abspath(filename)
        registered_projects[name] = cls
        return cls
    return wrapper

@register_in_kiss
def Dyn(name):
    """Décorateur pour enregistrer un projet librarie dynamique auprès du moteur"""
    def wrapper(cls):
        cls._project_name = name
        cls._project_type = ProjectType.dyn
        # Récupérer le fichier Python où le décorateur est utilisé
        frame = inspect.currentframe()
        caller_frame = frame.f_back
        filename = caller_frame.f_code.co_filename
        cls._project_file = os.path.abspath(filename)
        registered_projects[name] = cls
        return cls
    return wrapper

@register_in_kiss
def Description(text):
    """Décorateur pour ajouter une description"""
    def wrapper(cls):
        cls._project_description = text
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