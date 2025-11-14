import os
import sys
from types import ModuleType
from pathlib import Path
import importlib.util
import inspect
from project import ProjectType, Project

MODULE_FILENAME = "kiss.py"

class ModuleLoader:
    def __init__(self):
        self.cls_project : dict[type, Project]= {}

    def get_cls_instance(self, cls) -> Project:
        if cls not in self.cls_project:
            instance = cls()
            self.cls_project[cls] = instance
        return self.cls_project[cls]
    
    def replace_cls_instance(self, cls, instance):
        self.cls_project[cls] = instance

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

    def projects_names(self):
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
        pattern = f"**/{MODULE_FILENAME}" if recursive else MODULE_FILENAME

        for file in path.glob(pattern):
            module_name = file.stem
            spec = importlib.util.spec_from_file_location(module_name, file)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
        
        for project in ModuleLoader.projects():
            self.add(project.name, project)

ModuleRegistry = ModuleRegistry()

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

def project_file_from_frame() -> Path:
    frame = inspect.currentframe()
    caller_frame = frame.f_back.f_back
    filename = caller_frame.f_code.co_filename
    return Path(filename).absolute()

@register_in_kiss
def Bin(name):
    """Décorateur pour enregistrer un projet binaire auprès du moteur"""
    def wrapper(cls):
        instance = ModuleLoader.get_cls_instance(cls)

        # Now that we now the type of the project replace it's instance
        from project import BinProject
        if not isinstance(instance, BinProject):
            project_file = project_file_from_frame()
            bin_instance = BinProject(name=name,
                                      directory=project_file.parent,
                                      file = project_file, 
                                      description= instance.description if hasattr(instance, "description") else None,
                                      sources = cls.SOURCES if hasattr(cls, "SOURCES") else [],
                                      prebuild = cls.prebuild if hasattr(cls, "prebuild") else None,
                                      postbuild = cls.postbuild if hasattr(cls, "postbuild") else None)
            ModuleLoader.replace_cls_instance(cls, bin_instance)
            instance = bin_instance
        return cls
    return wrapper

@register_in_kiss
def Lib(name):
    """Décorateur pour enregistrer un projet libraire statique auprès du moteur"""
    def wrapper(cls):
        instance = ModuleLoader.get_cls_instance(cls)
        
        # Now that we now the type of the project replace it's instance
        from project import LibProject
        if not isinstance(instance, LibProject):
            project_file = project_file_from_frame()
            lib_instance = LibProject(name= name,
                                      directory=project_file.parent,
                                      file = project_file, 
                                      description= instance.description if hasattr(instance, "description") else None,
                                      sources= cls.SOURCES if hasattr(cls, "SOURCES") else [],
                                      interface_directories= cls.INTERFACES if hasattr(cls, "INTERFACES") else [])
            ModuleLoader.replace_cls_instance(cls, lib_instance)
            instance = lib_instance
        return cls
    return wrapper

@register_in_kiss
def Dyn(name):
    """Décorateur pour enregistrer un projet librarie dynamique auprès du moteur"""
    def wrapper(cls):
        instance = ModuleLoader.get_cls_instance(cls)

        # Now that we now the type of the project replace it's instance
        from project import DynProject
        if not isinstance(instance, DynProject):
            project_file = project_file_from_frame()
            dyn_instance = DynProject(name= name,
                                      directory=project_file.parent,
                                      file = project_file,
                                      description= instance.description if hasattr(instance, "description") else None,
                                      sources= cls.SOURCES if hasattr(cls, "SOURCES") else [],
                                      interface_directories= cls.INTERFACES if hasattr(cls, "INTERFACES") else [])
        
            ModuleLoader.replace_cls_instance(cls, dyn_instance)
            instance = dyn_instance
        return cls
    return wrapper

@register_in_kiss
def Workspace(name):
    """Décorateur pour enregistrer un workspace auprès du moteur"""
    def wrapper(cls):
        instance = ModuleLoader.get_cls_instance(cls)

        # Now that we now the type of the project replace it's instance
        from project import Workspace
        if not isinstance(instance, Workspace):
            project_file = project_file_from_frame()
            workspace = Workspace(name= name,
                                  directory=project_file.parent,
                                  file = project_file, 
                                  description= instance.description if hasattr(instance, "description") else None,
                                  projects= cls.PROJECTS if hasattr(cls, "PROJECTS") else [])
            ModuleLoader.replace_cls_instance(cls, workspace)
            instance = workspace
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
