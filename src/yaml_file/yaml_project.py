from abc import abstractmethod
from enum import Enum
from pathlib import Path

import semver


PROJECT_FILE_NAME = "kiss.yaml"

# Enumeration of the project type that is supported
class YamlDependencyType(str, Enum):
    path = "path"
    git = "git"
    
    def __str__(self):
        return self.name
    
# YamlDependency base class
# Helper class used to represent the dependency in the project file
# It is represented by a unique name that identify the dependency
# Sub class add specific information about the dependency
# YamlPathDependency represent a dependency that is in a path 
# GitDependecy represent a git dependency that is a git repository with a branch
class YamlDependency:

    # Initialize a dependency with a name and no associated project
    # The association is done with the project property setter later
    def __init__(self, type: YamlDependencyType, name: str):
        self._name = str(name)
        self._type = type

    # The type of the dependency
    @property
    def type(self) -> str:
        return self._type

    # The unique name of the dependency
    @property
    def name(self) -> str:
        return self._name
    
    
    
# A YamlPathDependency represent a dependency that is in a path 
class YamlPathDependency(YamlDependency):

    # Initialize a dependency with a name and the path
    def __init__(self, name: str, path: Path):
        super().__init__(YamlDependencyType.path, name)
        self._path = Path(path)

    # The path where the project reside
    @property 
    def path(self) -> Path:
        return self._path


# A YamlGitDependency represent a dependency that is in a git repository with a branch
class YamlGitDependency(YamlDependency):

    # Initialize a dependency with a name, a git repository address and a branch
    def __init__(self, name: str, git: str, branch: str):
        super().__init__(YamlDependencyType.git, name)
        self._git = git
        self._branch = str(branch)

    # The git repository address
    @property 
    def git(self) -> str:
        return self._git
    
    # The git branch
    @property 
    def branch(self) -> str:
        return self._branch


# Enumeration of the project type that is supported
class YamlProjectType(str, Enum):
    bin = "bin"
    lib = "lib"
    dyn = "dyn"
    workspace = "workspace"
    
    def __str__(self):
        return self.name


class YamlProject:
    def __init__(self, type: YamlProjectType, file: Path, path: Path, name: str, description :str, version: semver.Version, dependencies :list[YamlDependency]=[]):
        self._type = type
        self._file = file
        self._path = path
        self._name = name
        self._description = description
        self._version = version
        self._dependencies = dependencies

    def __hash__(self):
        return hash((self._type, self._name, self._file))

    def __eq__(self, other):
        if not isinstance(other, YamlProject):
            return False
        return (self._type == other.type and
                self._name == other.name and
                self._file == other.file)
    
    @property
    def type(self) -> YamlProjectType:
        return self._type
    
    @property
    def file(self) -> Path:
        return self._file
    
    @property
    def path(self) -> Path:
        return self._path
    
    @property
    def name(self) -> str:
        return self._name
    
    @property
    def description(self) -> str:
        return self._description
    
    @property
    def version(self) -> semver.Version:
        return self._version
    
    @property
    def dependencies(self) -> list[YamlDependency]:
        return self._dependencies
    
    # Check if the project match the given dependency 
    def is_matching_yaml_dependency(self, dep:YamlDependency) -> bool:
        match dep.type:
            case YamlDependencyType.path:
                dep: YamlPathDependency = dep
                return self.name == dep.name and self.path == dep.path
            case YamlDependencyType.git:
                exit(1) # not implemented
        
    
    def _to_yaml_dict(self) -> dict:
        data: dict = {
            "name": self.name,
            "version": str(self.version)
        }
        # Add the description if present
        if self._description:
            data["description"] = self.description
        # Add the path if different from the project file path
        # Make sure to make it relative if possible
        if self.path != self._file.parent:
            try:
                path = str(self.path.relative_to(self.file.parent))
                if path != self._file.parent:
                    data["path"] = path
            except ValueError:
                data["path"] = str(self.path)
        return data
    
    @abstractmethod
    def to_yaml_dict(self) -> tuple[str, dict]:
        pass

class YamlBinProject(YamlProject):
    def __init__(self, file: Path, path: Path, name: str, description :str, version: semver.Version, sources:list[Path], dependencies :list[YamlDependency]=[]):
        super().__init__(YamlProjectType.bin, 
                         file=file, 
                         path=path,
                         name=name,
                         description=description,
                         version=version,
                         dependencies=dependencies
                         )
        self._sources = sources

    @property
    def sources(self) -> list[Path]:
        return self._sources
    
    def to_yaml_dict(self) -> tuple[str, dict]:
        data = self._to_yaml_dict()
        if self._sources:
            data["sources"] = [str(src) for src in self._sources]
        return str(YamlProjectType.bin), data
    
class YamlLibProject(YamlProject):
    def __init__(self, file: Path, path: Path, name: str, description :str, version: semver.Version, sources:list[Path], interface_directories:list[Path], dependencies :list[YamlDependency]=[]):
        super().__init__(YamlProjectType.lib, 
                         file=file, 
                         path=path,
                         name=name,
                         description=description,
                         version=version,
                         dependencies=dependencies
                         )
        self._sources = sources
        self._interface_directories = interface_directories
        
    @property
    def sources(self) -> list[Path]:
        return self._sources
    
    @property
    def interface_directories(self) -> list[Path]:
        return self._interface_directories
        
    def to_yaml_dict(self) -> tuple[str, dict]:
        data = self._to_yaml_dict()
        if self._sources:
            data["sources"] = [str(src) for src in self._sources]
        if self._interface_directories:
            data["interface_directories"] = [str(dir) for dir in self._interface_directories]
        return str(YamlProjectType.lib), data
    
class YamlDynProject(YamlProject):
    def __init__(self, file: Path, path: Path, name: str, description :str, version: semver.Version, sources:list[Path], interface_directories:list[Path], dependencies :list[YamlDependency]=[]):
        super().__init__(YamlProjectType.dyn, 
                         file=file, 
                         path=path,
                         name=name,
                         description=description,
                         version=version,
                         dependencies=dependencies
                        )
        self._sources = sources
        self._interface_directories = interface_directories

    @property
    def sources(self) -> list[Path]:
        return self._sources
    
    @property
    def interface_directories(self) -> list[Path]:
        return self._interface_directories
    
   
    def to_yaml_dict(self) -> tuple[str, dict]:
        data = self._to_yaml_dict()
        if self._sources:
            data["sources"] = [str(src) for src in self._sources]
        if self._interface_directories:
            data["interface_directories"] = [str(dir) for dir in self._interface_directories]
        return str(YamlProjectType.dyn), data

