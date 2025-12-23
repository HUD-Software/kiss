
from abc import abstractmethod
from enum import Enum
from pathlib import Path
import traceback
from typing import Optional
import semver
import console
import yaml

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
# YamlPathDependency represent a dependency that is in a directory 
# GitDependecy represent a git dependency that is a git repository with a branch
class YamlDependency:

    # Initialize a dependency with a name and no associated project
    # The association is done with the project property setter later
    def __init__(self, type: YamlDependencyType, name: str):
        self._name = str(name)
        self._project = None
        self._type = type

    # The type of the dependency
    @property
    def type(self) -> str:
        return self._type

    # The unique name of the dependency
    @property
    def name(self) -> str:
        return self._name
    
    # # The project associated, could not exist if the project is not found in the loaded project
    # @property
    # def project(self) -> Optional["YamlFile"]:
    #     return self._project
    
    # # The associated project to set ( Should correspond )
    # @project.setter
    # def project(self, value : "YamlFile"):
    #     self._project = value
    
# A YamlPathDependency represent a dependency that is in a directory 
class YamlPathDependency(YamlDependency):

    # Initialize a dependency with a name and the directory
    def __init__(self, name: str, directory: Path):
        super().__init__(YamlDependencyType.path, name)
        self._directory = Path(directory)

    # The directory where the project reside
    @property 
    def directory(self) -> Path:
        return self._directory
    

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

# Valid root keys in the YAML file
_VALID_YAML_ROOT = [str(YamlProjectType.bin), str(YamlProjectType.dyn), str(YamlProjectType.lib), str(YamlProjectType.workspace)]

class YamlProject:
    def __init__(self, type: YamlProjectType, file: Path, directory: Path, name: str, description :str, version: semver.Version, dependencies :list[YamlDependency]=[]):
        self._file = file
        self._directory = directory
        self._name = name
        self._description = description
        self._version = version
        self._type = type
        self._dependencies = dependencies

    @property
    def type(self) -> YamlProjectType:
        return self._type
    
    @property
    def file(self) -> Path:
        return self._file
    
    @property
    def directory(self) -> Path:
        return self._directory
    
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
    def match_dependency(self, dep:YamlDependency) -> bool:
        match dep.type:
            case YamlDependencyType.path:
                dep: YamlPathDependency = dep
                return self.name == dep.name and self.directory == dep.directory
            case YamlDependencyType.git:
                exit(1) # not implemented
        
    
    def _to_yaml_dict(self) -> dict:
        data: dict = {
            "name": self.name,
            "version": str(self._version)
        }
        # Add the description if present
        if self._description:
            data["description"] = self._description
        # Add the path if different from the project file directory
        # Make sure to make it relative if possible
        if self._directory != self._file.parent:
            try:
                path = str(self._directory.relative_to(self._file.parent))
                if path != self._file.parent:
                    data["path"] = path
            except ValueError:
                data["path"] = str(self._directory)
        return data
    
    @abstractmethod
    def to_yaml_dict(self) -> tuple[str, dict]:
        pass



class YamlBinProject(YamlProject):
    def __init__(self, file: Path, directory: Path, name: str, description :str, version: semver.Version, sources:list[Path], dependencies :list[YamlDependency]=[]):
        super().__init__(YamlProjectType.bin, 
                         file=file, 
                         directory=directory,
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
    def __init__(self, file: Path, directory: Path, name: str, description :str, version: semver.Version, sources:list[Path], interface_directories:list[Path], dependencies :list[YamlDependency]=[]):
        super().__init__(YamlProjectType.lib, 
                         file=file, 
                         directory=directory,
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
    def __init__(self, file: Path, directory: Path, name: str, description :str, version: semver.Version, sources:list[Path], interface_directories:list[Path], dependencies :list[YamlDependency]=[]):
        super().__init__(YamlProjectType.dyn, 
                         file=file, 
                         directory=directory,
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

# YamlFile is the instanciation of one kiss.yaml file.
# It is use to load, read, modify and save the yaml file.
class YamlFile:
   
    # Initialize with the project file path
    def __init__(self, file: Path):
        self._file = file
        self._yaml : Optional[dict] = {}
        
    # Get the project file path
    @property
    def file(self) -> Path:
        return self._file
    
    # Get the loaded yaml dictionary
    @property
    def yaml(self) -> dict | None:
        return self._yaml
    
    # Load the yaml file into a dictionary
    def load_yaml(self) -> bool:
        try:
            with self.file.open() as f:
                self._yaml = yaml.safe_load(f)
            return True
        except (OSError, yaml.YAMLError) as e:
            console.print_error(f"Error: When loading {self.file} file: {e}\n{traceback.format_exc()}")
            return False
        
    # Save the current yaml dictionary to the file
    def save_yaml(self) -> bool:
        try:
            self.file.parent.mkdir(parents=True, exist_ok=True)
            with self.file.open("w", encoding="utf-8") as f:
                yaml.safe_dump(self.yaml, f, sort_keys=False,
                    allow_unicode=True,
                    default_flow_style=False,
                    default_style=None,
                    indent=2,      
                )
            return True

        except (OSError, yaml.YAMLError) as e:
            console.print_error(f"Error: When saving {self.file} file: {e}\n{traceback.format_exc()}")
            return False
    
    # load projects from a yaml file
    def load_yaml_projects(self) -> list[YamlProject]:
        if not self.yaml:
            return []

        projects = list[YamlProject]()

        for key, value in self.yaml.items():
            if key not in _VALID_YAML_ROOT:
                console.print_error (f"⚠️  Error: Invalid project type '{key}' in {self.file}")
                exit(1)

            for item in value:
                if isinstance(item, dict):
                    # Read 'name'
                    name = item.get("name")
                    if not name:
                        console.print_error(f"⚠️  Error: Project name is missing in {self.file} under '{key}'")
                        exit(1)
                    # Read 'version' as semver version
                    version = item.get("version")
                    if not version:
                        console.print_error(f"⚠️  Error: Project name is missing in {self.file} under '{key}'")
                        exit(1)
                    try:
                        version = semver.VersionInfo.parse(version)
                    except Exception as e:
                        console.print_error(f"⚠️  Error: Invalid version format in {self.file} under '{key}': {e}")
                        exit(1)

                    # Read 'description'
                    description = item.get("description", "")

                    # Read 'path', make it absolute if relative to the project file
                    project_directory = Path(item.get("path", self.file.parent))
                    project_directory = project_directory if project_directory.is_absolute() else self.file.parent / project_directory

                    # Read 'dependencies'
                    dependencies:list[YamlDependency] = []
                    for dependency in item.get("dependencies", []):
                        # Read dependency 'name'
                        dep_name = dependency.get("name")
                        if not dep_name:
                            console.print_error(f"⚠️  Error: Project name is missing in {self.file} under '{key}'")
                            exit(1)
                        dep_path = dependency.get("path")
                        dep_git = dependency.get("git")
                        
                        # Path and git are exclusive
                        if dep_path and dep_git:
                            console.print_error(
                                f"⚠️  Error: Dependency '{dep_name}' cannot define both 'path' and 'git' in {self.file} under '{key}'"
                            )
                            exit(1)
                        
                        # Read git if any
                        if dep_git:
                            branch = dependency.get("branch")
                            dependencies.append(YamlGitDependency(dep_name, dep_git, branch))

                        # If no path is given, the default behaviour is that path is the name of dependency
                        elif dep_path:
                            dep_path = Path(dep_path)
                            dependencies.append(YamlPathDependency(dep_name, dep_path if dep_path.is_absolute() else (self.file.parent / dep_path).resolve(strict=False)))
                        else:
                            dependencies.append(YamlPathDependency(dep_name, self.file.parent / Path(dep_name)))
        
                    # Create project
                    match key:
                        case YamlProjectType.bin:
                            sources = [self.file.parent / src for src in item.get("sources", [])]
                            projects.append(YamlBinProject(file=self.file, directory=project_directory, name=name, description=description, sources=sources, version=version, dependencies=dependencies))
                        case YamlProjectType.lib:
                            sources = [self.file.parent / src for src in item.get("sources", [])]
                            interface_dirs = [self.file.parent / src for src in item.get("interface_directories", [])]
                            projects.append(YamlLibProject(file=self.file,  directory=project_directory, name=name, description=description, sources=sources, interface_directories=interface_dirs, version=version, dependencies=dependencies))
                        case YamlProjectType.dyn:
                            sources = [self.file.parent / src for src in item.get("sources", [])]
                            interface_dirs = [self.file.parent / src for src in item.get("interface_directories", [])]
                            projects.append(YamlDynProject(file=self.file,  directory=project_directory, name=name, description=description, sources=sources, interface_directories=interface_dirs, version=version, dependencies=dependencies))

        return projects
    
    # Check if a project with the given name exists
    def is_project_in_yaml(self, project_name: str) -> bool:
        if self.yaml is None:
            return False
        for key, value in self.yaml.items():
            if key not in _VALID_YAML_ROOT:
                continue
            for item in value:
                if isinstance(item, dict):
                    if item.get("name") == project_name:
                        return True
        return False
    
    def get_yaml_project_with_dependency(self, dependency_name: str) -> dict | None:
        if self.yaml is None:
            return None
        for key, value in self.yaml.items():
            if key not in _VALID_YAML_ROOT:
                continue
            for item in value:
                if isinstance(item, dict):
                    dependencies = item.get("dependencies", [])
                    for dependency in dependencies:
                        if dependency.get("name") == dependency_name:
                            return item
        return None
    
    # Check if a project with the same name already exists in the yaml file
    def is_project_name_present(self, project_name: str) -> bool:
        if self.yaml is None:
            return False
        for key, value in self.yaml.items():
            if key not in _VALID_YAML_ROOT:
                continue
            for item in value:
                if isinstance(item, dict):
                    name = item.get("name")
                    if name == project_name:
                        return True
        return False
    
    # Add a project to the yaml file
    def add_yaml_project(self, project: YamlProject) -> bool:
        # If the yaml is not loaded, initialize it
        if self.yaml is None:
            self._yaml = {}
         
        # Check if project is not already present
        if self.is_project_in_yaml(project.name):
            console.print_error(f"⚠️  Error: Project `{project.name}` already exists in {self.file}")
            return False
        
        key, project_yaml = project.to_yaml_dict()
        if key not in self.yaml:
            self.yaml[key] = []
        self.yaml[key].append(project_yaml)
        return True

    def path_depencendies_to_yaml_dict(self, dependency_name: str, dependency_path: Path) -> dict:
        data: dict = {
            "name": dependency_name,
        }
        if str(dependency_path) != dependency_name:
            data["path"] = str(dependency_path)
        return data
    
    def git_depencendies_to_yaml_dict(self, dependency_name: str, dependency_path: Path) -> dict:
        data: dict = {
            "name": dependency_name,
            "git": str(dependency_path)
        }
        return data

    def add_dependency_to_project(self, project_name: str, dependency_yaml:dict) -> bool:
        if self.yaml is None:
            console.print_error(f"⚠️  Error: YAML not loaded for {self.file}")
            return False
    
        for key, value in self.yaml.items():
            if key not in _VALID_YAML_ROOT:
                continue
            for item in value:
                if isinstance(item, dict) and item.get("name") == project_name:
                    if not item.get("dependencies"):
                        item["dependencies"] = []

                    # Vérifier si la dépendance existe déjà
                    dep_names = [dep.get("name") for dep in item["dependencies"]]
                    if dependency_yaml.get("name") in dep_names:
                        console.print_error(
                            f"⚠️  Error: Dependency `{dependency_yaml.get('name')}` already exists in project `{project_name}`"
                        )
                        return False

                    # Check that we don't have the same path or git already present
                    for existing_dep in item["dependencies"]:
                        if "path" in dependency_yaml and existing_dep.get("path") == dependency_yaml.get("path"):
                            console.print_error(
                                f"⚠️  Error: Dependency `{existing_dep.get('name')}` already exists with the same path `{dependency_yaml.get('path')}` in project `{project_name}`"
                            )
                            return False
                        if "git" in dependency_yaml and existing_dep.get("git") == dependency_yaml.get("git"):
                            console.print_error(
                                f"⚠️  Error: Dependency `{existing_dep.get('name')}` already exists with the same git `{dependency_yaml.get('git')}` in project `{project_name}`"
                            )
                            return False
                    item["dependencies"].append(dependency_yaml)
                    return True

        console.print_error(f"⚠️  Error: Project `{project_name}` not found in {self.file}")
        return False
        