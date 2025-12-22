from pathlib import Path
from typing import Optional
import console
import semver
from semver import Version
from enum import Enum


PROJECT_FILE_NAME = "kiss.yaml"

class Dependency:
    def __init__(self, name: str):
        self._name = name

    @property
    def name(self) -> str:
        return self._name

    @property
    def project(self) -> "Project":
        return self._project
    
    @project.setter
    def project(self, value : "Project"):
        self._project = value
    
    @property
    def directory(self) -> Path:
        return self._directory
        
class PathDependency(Dependency):
    def __init__(self, name: str, directory: Path):
        super().__init__(name)
        self._directory = directory

    @property 
    def directory(self) -> Path:
        return self._directory

class GitDependency(Dependency):
    def __init__(self, name: str, git: str, branch: str):
        super().__init__( name)
        self._git = git
        self._branch = branch

    @property 
    def git(self) -> str:
        return self._git
    
    @property 
    def branch(self) -> str:
        return self._branch
    
class ProjectType(str, Enum):
    bin = "bin"
    lib = "lib"
    dyn = "dyn"
    workspace = "workspace"
    
    def __str__(self):
        return self.name

class Project:
    def __init__(self, file: Path, directory: Path, name: str, description :str, version: Version, dependencies :list[Dependency]=[]):
        self._file = file
        self._directory = directory
        self._name = name
        self._description = description
        self._version = version
        self._dependencies = dependencies

    @property
    def file(self):
        return self._file
    
    @property
    def name(self):
        return self._name
    
    @property
    def description(self): 
        return self._description
    
    @property
    def version(self):
        return self._version
    
    @property 
    def directory(self) -> Path:
        return self._directory
    
    @property
    def dependencies(self) -> list[Dependency]:
        return self._dependencies

class BinProject(Project):
    def __init__(self, file: Path, directory: Path,name: str, description :str, version: Version, sources: list[Path] = [],  dependencies :list[Dependency]=[]):
        super().__init__(file, directory, name, description, version, dependencies)
        self._sources = sources

    @property
    def sources(self) -> list[Path]:
        return self._sources


class LibProject(Project):
    def __init__(self, file: Path, directory: Path,name: str, description :str, version: Version, sources: list[Path] = [], interface_directories: list[Path] = [], dependencies :list[Dependency]=[]):
        super().__init__(file, directory, name, description, version, dependencies)
        self._sources = sources
        self._interface_directories = interface_directories

    @property
    def sources(self) -> list[Path]:
        return self._sources
    
    @property
    def interface_directories(self) -> list[Path]:
        return self._interface_directories
    
class DynProject(Project):
    def __init__(self, file: Path, directory: Path,name: str, description :str, version: Version, sources: list[Path] = [], interface_directories: list[Path] = [],  dependencies :list[Dependency]=[]):
        super().__init__(file, directory, name, description, version, dependencies)
        self._sources = sources
        self._interface_directories = interface_directories

    @property
    def sources(self) -> list[Path]:
        return self._sources
    
    @property
    def interface_directories(self) -> list[Path]:
        return self._interface_directories
    
class ProjectYAML:
    # Valid root keys in the YAML file
    VALID_ROOT = ["bin", "dyn", "lib", "workspace"]

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
        import yaml
        try:
            with self.file.open() as f:
                self._yaml = yaml.safe_load(f)
            return True
        except (OSError, yaml.YAMLError) as e:
            console.print_error(f"Error: When loading {self.file} file: {e}")
            return False
        
    # Save the current yaml dictionary to the file
    def save_yaml(self) -> bool:
        import yaml
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
            console.print_error(f"Error: When saving {self.file} file: {e}")
            return False
    
    # load projects from a yaml file
    def load_projects(self) -> list[Project]:
        if not self.yaml:
            return []

        projects = list[Project]()

        for key, value in self.yaml.items():
            if key not in ProjectYAML.VALID_ROOT:
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
                    dependencies:list[Dependency] = []
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
                            dependencies.append(GitDependency(dep_name, dep_git, branch))

                        # If no path is given, the default behaviour is that path is the name of dependency
                        elif dep_path:
                            dep_path = Path(dep_path)
                            dependencies.append(PathDependency(dep_name, dep_path if dep_path.is_absolute() else (self.file.parent / dep_path).resolve(strict=False)))
                        else:
                            dependencies.append(PathDependency(dep_name, self.file.parent / Path(dep_name)))
        
                    # Create project
                    match key:
                        case ProjectType.bin:
                            sources = [self.file.parent / src for src in item.get("sources", [])]
                            projects.append(BinProject(file=self.file, directory=project_directory, name=name, description=description, sources=sources, version=version, dependencies=dependencies))
                        case ProjectType.lib:
                            sources = [self.file.parent / src for src in item.get("sources", [])]
                            interface_dirs = [self.file.parent / src for src in item.get("interface_directories", [])]
                            projects.append(LibProject(file=self.file,  directory=project_directory, name=name, description=description, sources=sources, interface_directories=interface_dirs, version=version, dependencies=dependencies))
                        case ProjectType.dyn:
                            sources = [self.file.parent / src for src in item.get("sources", [])]
                            interface_dirs = [self.file.parent / src for src in item.get("interface_directories", [])]
                            projects.append(DynProject(file=self.file,  directory=project_directory, name=name, description=description, sources=sources, interface_directories=interface_dirs, version=version, dependencies=dependencies))

        return projects
    
    # Check if a project with the same name and path already exists in the yaml file
    def is_project_present(self, project: Project) -> bool:
        if self.yaml is None:
            return False
        for key, value in self.yaml.items():
            if key not in ProjectYAML.VALID_ROOT:
                continue
            for item in value:
                if isinstance(item, dict):
                    if item.get("name") == project.name:
                        return True
        return False
    
    def get_yaml_project_with_dependency(self, dependency_name: str) -> dict | None:
        if self.yaml is None:
            return None
        for key, value in self.yaml.items():
            if key not in ProjectYAML.VALID_ROOT:
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
            if key not in ProjectYAML.VALID_ROOT:
                continue
            for item in value:
                if isinstance(item, dict):
                    name = item.get("name")
                    if name == project_name:
                        return True
        return False
    
    # Convert a project to a yaml dictionary
    def project_to_yaml_dict(self, project: Project) -> dict:
        data: dict = {
            "name": project.name,
            "version": str(project.version)
        }
        # Add the description if present
        if project.description:
            data["description"] = project.description
        # Add the path if different from the project file directory
        # Make sure to make it relative if possible
        if project.directory != project.file.parent:
            try:
                path = str(project.directory.relative_to(project.file.parent))
                if path != project.file.parent:
                    data["path"] = path
            except ValueError:
                data["path"] = str(project.directory)
        if isinstance(project, BinProject):
            if project.sources:
                data["sources"] = [str(src) for src in project.sources]
        elif isinstance(project, LibProject):
            if project.sources:
                data["sources"] = [str(src) for src in project.sources]
            if project.interface_directories:
                data["interface_directories"] = [str(dir) for dir in project.interface_directories]
        elif isinstance(project, DynProject):
            if project.sources:
                data["sources"] = [str(src) for src in project.sources]
            if project.interface_directories:
                data["interface_directories"] = [str(dir) for dir in project.interface_directories]
        return data
    
    # Add a project to the yaml file
    def add_project(self, project: Project) -> bool:
        # If the yaml is not loaded, initialize it
        if self.yaml is None:
            self._yaml = {}
         
        # Check if project is not already present
        if self.is_project_present(project):
            console.print_error(f"⚠️  Error: Project `{project.name}` already exists in {self.file}")
            return False
        
        project_yaml = self.project_to_yaml_dict(project)
        match project:
            case BinProject():
                key = str(ProjectType.bin)
                if key not in self.yaml:
                    self.yaml[key] = []
                self.yaml[key].append(project_yaml)
            case LibProject():
                key = str(ProjectType.lib)
                if key not in self.yaml:
                    self.yaml[key] = []
                self.yaml[key].append(project_yaml)
            case DynProject():
                key = str(ProjectType.dyn)
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
            if key not in ProjectYAML.VALID_ROOT:
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
        

class ProjectRegistry:
    def __init__(self):
        self.projects_: dict[Path, list[Project]] = {}

    def __contains__(self, path: Path) -> bool:
        return path in self.projects_

    def __iter__(self):
        return iter(self.projects_)
    
    def items(self):
        return self.projects_.items()
    
    @property
    def projects(self) -> dict[Path, list[Project]]:
        return self.projects_
    
    def paths(self):
        return self.projects_.keys()
    
    def register_project(self, project: Project):
        if project.file not in self.projects_:
            self.projects_[project.file] = list[Project]()
        if project in self.projects_[project.file]:
            console.print_warning(f"⚠️  Warning: Project already registered: {project.file}")
        else:
            self.projects_[project.file].append(project)

    def is_file_loaded(self, filepath:Path) -> bool:
        return filepath in self.projects_
    
    def load_project_from_file(self, file: Path, load_dependencies:bool):
        if self.is_file_loaded(file):
           return 
        
        # Load the yaml
        yaml = ProjectYAML(file)
        if not yaml.load_yaml():
            console.print_warning(f"Error: Unable to load project file `{file}`")
            exit(1)

        # Load the project
        projects = yaml.load_projects()

        # Register loaded projects
        for project in projects :
            self.register_project(project)

        # Load all project dependencies
        if load_dependencies:
            for project in projects :
                for dependency in project.dependencies:
                    match dependency:
                        case PathDependency() as path_dependency:
                            loaded = False
                            file = None
                            # Check if the project is declared in the project that depends on it.
                            for dep_project in projects:
                                if dep_project.name == path_dependency.name:
                                    loaded = True
                                    file = project.file
                                    break

                            # If we don't found it load the file
                            if not loaded:
                                dependency_file = path_dependency.directory / PROJECT_FILE_NAME
                                # If the file is not loaded load it
                                if not self.projects.get(dependency_file):
                                    if dependency_file.exists():
                                        self.load_project_from_file(dependency_file, load_dependencies)
                                        for p in ProjectRegistry.projects.get(dependency_file):
                                            if p.name == path_dependency.name and path_dependency.directory == p.directory:
                                                loaded = True
                                                file = dependency_file            
                                else:
                                    loaded = True
                                    file = dependency_file

                            # If project is loaded link the dependency with the project that depends on it
                            if loaded and file:
                                for p in ProjectRegistry.projects.get(file):
                                    if p.name == path_dependency.name:
                                        path_dependency.project = p 
                            else:
                                console.print_error(f"Error: Failed to load dependency '{path_dependency.name}' for project '{project.name}'.\n\n" +
                                                    f"Possible causes:\n" + 
                                                    f"1. The file '{PROJECT_FILE_NAME}' is missing in:\n" + 
                                                    f"   {path_dependency.directory}\n\n" +
                                                    f"2. The dependency '{path_dependency.name}' is not declared in:\n" + 
                                                    f"   {project.file}\n\n")
                                console.print_tips(f"Tips:\n" + 
                                                    f"Each dependency must:\n"+
                                                    f"  - Have a '{PROJECT_FILE_NAME}' file in its root directory of the dependency, or\n" + 
                                                    f"  - Be declared in the '{PROJECT_FILE_NAME}' of the project that depends on it.")
                                exit(1)
                        case GitDependency():
                            # Clone the repo and tr to load yaml file or request for a project in dependent project
                            pass
                            
                            
                            
    def load_projects_in_directory(self, directory: Path, load_dependencies : bool = True, recursive: bool = False ):
        pattern = f"**/{PROJECT_FILE_NAME}" if recursive else PROJECT_FILE_NAME

        # Load modules
        for file in directory.glob(pattern):
            self.load_project_from_file(file, load_dependencies)

    def projects_in_directory(self, directory: Path) -> list[Project]:
        for path, project_list in self.projects.items():
            if path.parent != directory:
                continue
            return project_list
        return []
            

            



ProjectRegistry = ProjectRegistry()

