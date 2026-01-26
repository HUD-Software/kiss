from abc import abstractmethod
from collections import defaultdict, deque
import hashlib
from pathlib import Path
from typing import Self
from semver import Version
from enum import Enum

import console
from yaml_file import YamlBinProject, YamlDynProject, YamlLibProject, YamlProject, YamlProjectType

# Enumeration of the project type that is supported
class ProjectType(str, Enum):
    bin = YamlProjectType.bin
    lib = YamlProjectType.lib
    dyn = YamlProjectType.dyn
    workspace = YamlProjectType.workspace
    
    def __str__(self):
        return self.name

# A Project is an instanciation of a project that is describe in the 'kiss.yaml' file
# This is the base class of different project type like binary, library or dynamic library
# It is represented by :
# - The file 'kiss.yaml' that describe this project
# - The directory where the project reside (Kiss allow to have a 'kiss.yaml' file in another directory than the project it self that contains sources)
class Project:
   
    # Initialize a project with the following informations:
    # - The file 'kiss.yaml' that describe this project
    # - The path where the project reside (Kiss allow to have a 'kiss.yaml' file in another path than the project it self that contains sources)
    # - A Description that describe the project
    # - Version of the project
    # - List of dependencie
    def __init__(self, type: ProjectType, file: Path, path: Path, name: str, description :str, version: Version):
        self._type = type
        self._file = file
        self._filehash = int.from_bytes(hashlib.sha256(str(file).encode()).digest()[:4], "little" )
        self._path = path
        self._name = name
        self._description = description
        self._version = version
        self._dependencies: list[Project]= []

    def __hash__(self):
        return hash((self._type, self._name, self._file))

    def __eq__(self, other):
        if not isinstance(other, YamlProject):
            return False
        return (self._type == other.type and
                self._name == other.name and
                self._file == other.file)
    # The type of the project
    @property
    def type(self) -> YamlProjectType:
        return self._type
    
    # The file where the project is described
    @property
    def file(self):
        return self._file
    
    # The hash of the file where the project is described
    @property
    def filehash(self):
        return self._filehash
    
    # The short hash of the file where the project is described
    @property
    def filehash_short(self):
        return self._filehash & 0xFFFFFFFF
    
    # The name of the project
    @property
    def name(self):
        return self._name
    
    # The description of the project
    @property
    def description(self): 
        return self._description
    
    # The version of the project
    @property
    def version(self):
        return self._version
    
    # The path where the project reside (Kiss allow to have a 'kiss.yaml' file in another path than the project it self that contains sources)
    @property 
    def path(self) -> Path:
        return self._path
    
    # List of dependencies
    @property
    def dependencies(self) -> list[Self]:
        return self._dependencies
    
    @abstractmethod
    def to_yaml_project(self):
        pass

    @classmethod 
    def from_yaml_project(cls, yaml_project:YamlProject) -> YamlProject:
        match yaml_project.type:
            case YamlProjectType.bin:
                return BinProject.from_yaml_project(yaml_project)
            case YamlProjectType.lib:
                return LibProject.from_yaml_project(yaml_project)
            case YamlProjectType.dyn:
                return DynProject.from_yaml_project(yaml_project)
        console.print_error("Invalid project type")
        exit(1)

    def topological_sort_projects(self) -> list[Self]:
        """
        Kahn Algorithm
        Returns a list of this project and its dependencies sorted by priority order (if A depends on B, A comes after B).

        @return:
        - list of projects in dependency order
        - exit(1) if the graph contains a dependency cycle
        """
        # 1. Collecte du sous-graphe (DFS)
        all_projects: set[Project] = set()
        visiting_stack: list[Project] = []

        def collect(project :Project, parent_project: Project):
            # Detect cyclic dependency
            if project in visiting_stack:
                console.print_error(f"⚠️ Error: Cyclic dependency between '{project.name}' and '{parent_project.name}'")
                console.print_error(f"         {' -> '.join([p.name for p in visiting_stack] + [project.name])}")
                exit(1)

            # Visit the project only once
            if project in all_projects:
                return
            visiting_stack.append(project)

            # Visit dependency
            for dep_project in project.dependencies:
                collect(dep_project, project)
            
            # Remove visited project
            visiting_stack.pop()
            all_projects.add(project)
        collect(self,  None)

        # 2. Construction du graphe inversé
        graph = defaultdict(list)     # dep -> [dependants]
        in_degree = defaultdict(int)  # nombre de dépendances restantes

        for project in all_projects:
            in_degree[project] = 0
        for project in all_projects:
            for dep_project in project.dependencies:
                graph[dep_project].append(project)
                in_degree[project] += 1

        # 3. Kahn : leaf en premier
        queue = deque(
            project for project in all_projects if in_degree[project] == 0
        )

        ordered = []

        while queue:
            project = queue.popleft()
            ordered.append(project)

            for dependant in graph[project]:
                in_degree[dependant] -= 1
                if in_degree[dependant] == 0:
                    queue.append(dependant)

        return ordered

        

# BinProject represent a project that is a binary project (elf or .exe file)
class BinProject(Project):
    # Initialize a project with the following informations:
    # - The file 'kiss.yaml' that describe this project
    # - The path where the project reside (Kiss allow to have a 'kiss.yaml' file in another path than the project it self that contains sources)
    # - A Description that describe the project
    # - Version of the project
    # - List of source file to compile
    # - List of dependencies
    def __init__(self, file: Path, path: Path,name: str, description :str, version: Version, sources: list[Path] = []):
        super().__init__(ProjectType.bin, file, path, name, description, version)
        self._sources = sources

    # List of sources to compile
    @property
    def sources(self) -> list[Path]:
        return self._sources
    
    @classmethod 
    def from_yaml_project(cls, yaml_project:YamlBinProject) -> Self:
        return BinProject(
            file= yaml_project.file,
            path=yaml_project.path,
            name=yaml_project.name,
            description=yaml_project.description,
            version = yaml_project.version,
            sources=yaml_project.sources
        )

   
    def to_yaml_project(self) -> YamlBinProject:
        return YamlBinProject(
            file= self.file,
            path=self.path,
            name=self.name,
            description=self.description,
            version=self.version,
            sources=self.sources,
            dependencies=self.dependencies
        )

# LibProject represent a project that is a static library project (.a or .lib file)
class LibProject(Project):
    # Initialize a project with the following informations:
    # - The file 'kiss.yaml' that describe this project
    # - The path where the project reside (Kiss allow to have a 'kiss.yaml' file in another path than the project it self that contains sources)
    # - A Description that describe the project
    # - Version of the project
    # - List of source file to compile
    # - List of interface path used to interface with the library
    # - List of dependencies
    def __init__(self, file: Path, path: Path,name: str, description :str, version: Version, sources: list[Path] = [], interface_directories: list[Path] = []):
        super().__init__(ProjectType.lib,  file, path, name, description, version)
        self._sources = sources
        self._interface_directories = interface_directories

    # List of sources to compile
    @property
    def sources(self) -> list[Path]:
        return self._sources
    
    # List of interface path used to interface with the library
    @property
    def interface_directories(self) -> list[Path]:
        return self._interface_directories
    
    @classmethod 
    def from_yaml_project(cls, yaml_project:YamlLibProject) -> Self:
        return LibProject(
            file= yaml_project.file,
            path=yaml_project.path,
            name=yaml_project.name,
            description=yaml_project.description,
            version = yaml_project.version,
            sources=yaml_project.sources,
            interface_directories=yaml_project.interface_directories
        )
    
    def to_yaml_project(self) -> YamlLibProject:
        return YamlLibProject(
            file= self.file,
            path=self.path,
            name=self.name,
            description=self.description,
            version=self.version,
            sources=self.sources,
            interface_directories=self.interface_directories,
            dependencies=self.dependencies
        )
    
# DynProject represent a project that is a dynamic library project (.so or .dll file)
class DynProject(Project):
    # Initialize a project with the following informations:
    # - The file 'kiss.yaml' that describe this project
    # - The path where the project reside (Kiss allow to have a 'kiss.yaml' file in another path than the project it self that contains sources)
    # - A Description that describe the project
    # - Version of the project
    # - List of source file to compile
    # - List of interface path used to interface with the library
    # - List of dependencies
    def __init__(self, file: Path, path: Path,name: str, description :str, version: Version, sources: list[Path] = [], interface_directories: list[Path] = []):
        super().__init__(ProjectType.dyn, file, path, name, description, version)
        self._sources = sources
        self._interface_directories = interface_directories
    
    # List of sources to compile
    @property
    def sources(self) -> list[Path]:
        return self._sources
    
    # List of interface path used to interface with the library
    @property
    def interface_directories(self) -> list[Path]:
        return self._interface_directories
    
    @classmethod 
    def from_yaml_project(cls, yaml_project:YamlDynProject) -> Self:
        return DynProject(
            file= yaml_project.file,
            path=yaml_project.path,
            name=yaml_project.name,
            description=yaml_project.description,
            version = yaml_project.version,
            sources=yaml_project.sources,
            interface_directories=yaml_project.interface_directories
        )
    
    def to_yaml_project(self) -> YamlDynProject:
        return YamlDynProject(
            file= self.file,
            path=self.path,
            name=self.name,
            description=self.description,
            version=self.version,
            sources=self.sources,
            interface_directories=self.interface_directories,
            dependencies=self.dependencies
        )

