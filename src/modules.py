import os
import sys
from types import ModuleType
from pathlib import Path
import importlib.util
import inspect
from project import ProjectType, Project

class ModuleLoader:
    def __init__(self):
        self.cls_project : dict[type, Project]= {}

    def get_cls_instance(self, cls) -> Project:
        if cls not in self.cls_project:
            instance = cls()
            self.cls_project[cls] = instance
        return self.cls_project[cls]
    
    def projects(self):
        """
        Retourne les classes des Project enregistrés.

        Returns:
            ValuesView[Project]: Vue sur les valeurs du registre (les classes Project).
        """
        return self.cls_project.values()
    

ModuleLoader = ModuleLoader()



class ModuleRegistry:
    def __init__(self):
        self._registry: dict[str, Project] = {}

    def get(self, name: str) -> Project|None:
        """
        Récupère le projet associé au nom.

        Args:
            name (str): Nom unique projet à rechercher.

        Returns:
            Project|None: La classe du générateur si trouvée, sinon None.
        """
        return self._registry.get(name)

    def add(self, name: str, project: ProjectType):
        """
        Ajoute un projet associé avec son nom

        Args:
            name (str): Nom du projet à ajouter.
            project (ProjectType): Le projet à ajouter
        """
        if name not in self._registry:
            self._registry[name] = project

    def __contains__(self, name):
        """
        Vérifie si un projet est enregistré.

        Args:
            name (str): Nom du projet à vérifier.

        Returns:
            bool: True si le projet existe dans le registre, False sinon.
        """
        return name in self._registry

    def __iter__(self):
        """
        Permet d’itérer sur les paires (nom, ProjectType) des projet enregistrés.

        Returns:
            Iterator[Tuple[str, ProjectType]]: Itérateur sur les couples (nom, ProjectType).
        """
        return iter(self._registry.items())

    def projects_name(self):
        """
        Retourne les noms des projets enregistrés.

        Returns:
            KeysView[str]: Vue sur les clés du registre.
        """
        return self._registry.keys()

    def projects(self):
        """
        Retourne les classes des ProjectType enregistrés.

        Returns:
            ValuesView[ProjectType]: Vue sur les valeurs du registre (les classes de ProjectType).
        """
        return self._registry.values()

    def items(self):
        """
        Retourne les paires (nom, ProjectType) des ProjectType enregistrés.

        Returns:
            ItemsView[Tuple[str, ProjectType]]: Vue sur les items du registre.
        """
        return self._registry.items()
    
    def load_modules(self, path: Path, recursive: bool = False):
        pattern = "**/*.py" if recursive else "*.py"

        for file in path.glob(pattern):
            module_name = file.stem
            spec = importlib.util.spec_from_file_location(module_name, file)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
        
        for project in ModuleLoader.projects():
            self.add(project.name, project)

ModuleRegistry = ModuleRegistry()


# # --- Fonction de chargement dynamique des modules ---
# def load_modules(path: Path, recursive: bool = False):
#     pattern = "**/*.py" if recursive else "*.py"

#     for file in path.glob(pattern):
#         module_name = file.stem
#         spec = importlib.util.spec_from_file_location(module_name, file)
#         module = importlib.util.module_from_spec(spec)
#         spec.loader.exec_module(module)
    
#     for project in cls_project.values():
#         ModuleRegistry.add(project.name, project)






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

# Si la classe n'hérite pas déjà de Project → on la "wrap"
def add_inheritance_to_project_class(cls):
    from project import Project
    if not issubclass(cls, Project):
        cls = type(cls.__name__, (Project, cls), dict(cls.__dict__))
    return cls

def project_file() -> str:
    frame = inspect.currentframe()
    caller_frame = frame.f_back.f_back
    filename = caller_frame.f_code.co_filename
    return os.path.abspath(filename)

@register_in_kiss
def Bin(name):
    """Décorateur pour enregistrer un projet binaire auprès du moteur"""
    def wrapper(cls):
        instance = ModuleLoader.get_cls_instance(cls)
        instance.name = name
        instance.type = ProjectType.bin
        instance.file = project_file()
        instance.prebuild = cls.prebuild if hasattr(cls, "prebuild") else None
        instance.postbuild = cls.postbuild if hasattr(cls, "postbuild") else None
        return cls
    return wrapper

@register_in_kiss
def Lib(name):
    """Décorateur pour enregistrer un projet libraire statique auprès du moteur"""
    def wrapper(cls):
        instance = ModuleLoader.get_cls_instance(cls)
        instance.name = name
        instance.type = ProjectType.lib
        instance.file = project_file()
        instance.prebuild = cls.prebuild if hasattr(cls, "prebuild") else None
        instance.postbuild = cls.postbuild if hasattr(cls, "postbuild") else None
        return cls
    return wrapper

@register_in_kiss
def Dyn(name):
    """Décorateur pour enregistrer un projet librarie dynamique auprès du moteur"""
    def wrapper(cls):
        instance = ModuleLoader.get_cls_instance(cls)
        instance.name = name
        instance.type = ProjectType.dyn
        instance.file = project_file()
        instance.prebuild = cls.prebuild if hasattr(cls, "prebuild") else None
        instance.postbuild = cls.postbuild if hasattr(cls, "postbuild") else None
        return cls
    return wrapper

@register_in_kiss
def Description(desc):
    """Décorateur pour ajouter une description"""
    def wrapper(cls):
        instance = ModuleLoader.get_cls_instance(cls)
        instance.description = desc
        return cls
    return wrapper

# @register_in_kiss
# def run_prebuild(name):
#     project_cls = registered_projects.get(name)
#     if project_cls:
#         instance = project_cls()
#         if hasattr(instance, "prebuild"):
#             instance.prebuild()
#         else:
#             print(f"{name} n'a pas de méthode prebuild")

# @register_in_kiss
# def run_postbuild(name):
#     project_cls = registered_projects.get(name)
#     if project_cls:
#         instance = project_cls()
#         if hasattr(instance, "postbuild"):
#             instance.postbuild()
#         else:
#             print(f"{name} n'a pas de méthode postbuild")