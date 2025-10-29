import re
import console
from project import ProjectType
from typing import Callable, Optional

class Project:

    @property
    def name(self) -> str:
        return self._name
    
    @property
    def description(self) -> str:
        return self._description
    
    @property
    def type(self) -> ProjectType:
        return self._type
    
    @property
    def file(self) -> str:
        return self._file
    
    @property
    def prebuild(self) -> Optional[Callable[[], None]]:
        return self._prebuild_callable
    
    @property
    def postbuild(self) -> Optional[Callable[[], None]]:
        return self._postbuild_callable
    
    @staticmethod
    def to_pascal(name: str) -> str:
        """
        Convert a string like "my_project", "my-project", "myProject",
        "my project" -> "MyProject".
        """
        if not name:
            return ""

        # 1) Turn camelCase into snake-ish by inserting '_' before Upper after lower/digit:
        s = re.sub(r'([a-z0-9])([A-Z])', r'\1_\2', name)

        # 2) Replace separators (space, dash, multiple underscores) by a single non-alnum split
        parts = re.split(r'[^0-9A-Za-z]+', s)

        # 3) Capitalize each part and join
        return ''.join(part.capitalize() for part in parts if part)

    @staticmethod
    def default_project(directory:str) -> str|None:
        from modules import ModuleRegistry
        ModuleRegistry.load_modules(directory)
        if len(ModuleRegistry.items()) == 0:
            return None 
        default_project_name ,default_project = next(iter(ModuleRegistry.items()))
        # Warn the user if we found more than 1 project
        if len(ModuleRegistry.items()) > 1:
            console.print_warning(f"We found more than 1 projet in the directory {directory}.")
            for project_name ,project in ModuleRegistry.items():
                console.print_warning(f"- {project_name} : {project._project_file}")
            console.print_warning(f"\nUse {default_project_name} : {default_project._project_file}")
        return default_project_name
