from abc import abstractmethod
from pathlib import Path
from typing import Self
from semver import Version
from enum import Enum

import console
from yaml_project import YamlBinProject, YamlDependency, YamlDynProject, YamlLibProject, YamlProject, YamlProjectType

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
    # - The directory where the project reside (Kiss allow to have a 'kiss.yaml' file in another directory than the project it self that contains sources)
    # - A Description that describe the project
    # - Version of the project
    # - List of dependencie
    def __init__(self, type: ProjectType, file: Path, directory: Path, name: str, description :str, version: Version):
        self._type = type
        self._file = file
        self._directory = directory
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
    
    # The directory where the project reside (Kiss allow to have a 'kiss.yaml' file in another directory than the project it self that contains sources)
    @property 
    def directory(self) -> Path:
        return self._directory
    
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

        

# BinProject represent a project that is a binary project (elf or .exe file)
class BinProject(Project):
    # Initialize a project with the following informations:
    # - The file 'kiss.yaml' that describe this project
    # - The directory where the project reside (Kiss allow to have a 'kiss.yaml' file in another directory than the project it self that contains sources)
    # - A Description that describe the project
    # - Version of the project
    # - List of source file to compile
    # - List of dependencies
    def __init__(self, file: Path, directory: Path,name: str, description :str, version: Version, sources: list[Path] = []):
        super().__init__(ProjectType.bin, file, directory, name, description, version)
        self._sources = sources

    # List of sources to compile
    @property
    def sources(self) -> list[Path]:
        return self._sources
    
    @classmethod 
    def from_yaml_project(cls, yaml_project:YamlBinProject) -> Self:
        return BinProject(
            file= yaml_project.file,
            directory=yaml_project.directory,
            name=yaml_project.name,
            description=yaml_project.description,
            version = yaml_project.version,
            sources=yaml_project.sources
        )

   
    def to_yaml_project(self) -> YamlBinProject:
        return YamlBinProject(
            file= self.file,
            directory=self.directory,
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
    # - The directory where the project reside (Kiss allow to have a 'kiss.yaml' file in another directory than the project it self that contains sources)
    # - A Description that describe the project
    # - Version of the project
    # - List of source file to compile
    # - List of interface directory used to interface with the library
    # - List of dependencies
    def __init__(self, file: Path, directory: Path,name: str, description :str, version: Version, sources: list[Path] = [], interface_directories: list[Path] = []):
        super().__init__(ProjectType.lib,  file, directory, name, description, version)
        self._sources = sources
        self._interface_directories = interface_directories

    # List of sources to compile
    @property
    def sources(self) -> list[Path]:
        return self._sources
    
    # List of interface directory used to interface with the library
    @property
    def interface_directories(self) -> list[Path]:
        return self._interface_directories
    
    @classmethod 
    def from_yaml_project(cls, yaml_project:YamlLibProject) -> Self:
        return LibProject(
            file= yaml_project.file,
            directory=yaml_project.directory,
            name=yaml_project.name,
            description=yaml_project.description,
            version = yaml_project.version,
            sources=yaml_project.sources,
            interface_directories=yaml_project.interface_directories
        )
    
    def to_yaml_project(self) -> YamlLibProject:
        return YamlLibProject(
            file= self.file,
            directory=self.directory,
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
    # - The directory where the project reside (Kiss allow to have a 'kiss.yaml' file in another directory than the project it self that contains sources)
    # - A Description that describe the project
    # - Version of the project
    # - List of source file to compile
    # - List of interface directory used to interface with the library
    # - List of dependencies
    def __init__(self, file: Path, directory: Path,name: str, description :str, version: Version, sources: list[Path] = [], interface_directories: list[Path] = []):
        super().__init__(ProjectType.dyn, file, directory, name, description, version)
        self._sources = sources
        self._interface_directories = interface_directories
    
    # List of sources to compile
    @property
    def sources(self) -> list[Path]:
        return self._sources
    
    # List of interface directory used to interface with the library
    @property
    def interface_directories(self) -> list[Path]:
        return self._interface_directories
    
    @classmethod 
    def from_yaml_project(cls, yaml_project:YamlDynProject) -> Self:
        return DynProject(
            file= yaml_project.file,
            directory=yaml_project.directory,
            name=yaml_project.name,
            description=yaml_project.description,
            version = yaml_project.version,
            sources=yaml_project.sources
        )
    
    def to_yaml_project(self) -> YamlDynProject:
        return YamlDynProject(
            file= self.file,
            directory=self.directory,
            name=self.name,
            description=self.description,
            version=self.version,
            sources=self.sources,
            interface_directories=self.interface_directories,
            dependencies=self.dependencies
        )

