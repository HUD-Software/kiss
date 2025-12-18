from pathlib import Path
from typing import Optional
import console
import semver
from semver import Version
from enum import Enum


PROJECT_FILE_NAME = "kiss.yaml"

class Dependency:
    def __init__(self, name :str):
        self.name_ = name

    @property
    def name(self) -> str:
        return self.name_

class PathDependency(Dependency):
    def __init__(self, name: str, path: Path):
        super().__init__( name)
        self.path_ = path

    @property 
    def path(self) -> Path:
        return self.path_

class GitDependency(Dependency):
    def __init__(self, name: str, git: str, branch: str):
        super().__init__( name)
        self.git_ = git
        self.branch_ = branch

    @property 
    def git(self) -> str:
        return self.git_
    
    @property 
    def branch(self) -> str:
        return self.branch_
    
class ProjectType(str, Enum):
    bin = "bin"
    lib = "lib"
    dyn = "dyn"
    workspace = "workspace"
    
    def __str__(self):
        return self.name

class Project:
    def __init__(self, file: Path, path: Path, name: str, description :str, version: Version, dependencies :list[Dependency]=[]):
        self.file_ = file
        self.path_ = path
        self.name_ = name
        self.description_ = description
        self.version_ = version
        self.dependencies_ = dependencies

    @property
    def file(self):
        return self.file_
    
    @property
    def name(self):
        return self.name_
    
    @property
    def description(self): 
        return self.description_
    
    @property
    def version(self):
        return self.version_
    
    @property 
    def path(self) -> Path:
        return self.path_
    
    @property
    def dependencies(self) -> list[Dependency]:
        return self.dependencies_

class BinProject(Project):
    def __init__(self, file: Path, path: Path,name: str, description :str, version: Version, sources: list[Path] = [],  dependencies :list[Dependency]=[]):
        super().__init__(file, path,name, description, version, dependencies)
        self.sources_ = sources

    @property
    def sources(self) -> list[Path]:
        return self.sources_


class LibProject(Project):
    def __init__(self, file: Path, path: Path,name: str, description :str, version: Version, sources: list[Path] = [], interface_directories: list[Path] = [], dependencies :list[Dependency]=[]):
        super().__init__(file, path, name, description, version, dependencies)
        self.sources_ = sources
        self.interface_directories_ = interface_directories

    @property
    def sources(self) -> list[Path]:
        return self.sources_
    
    @property
    def interface_directories(self) -> list[Path]:
        return self.interface_directories_
    
class DynProject(Project):
    def __init__(self, file: Path, path: Path,name: str, description :str, version: Version, sources: list[Path] = [], interface_directories: list[Path] = [],  dependencies :list[Dependency]=[]):
        super().__init__(file, path, name, description, version, dependencies)
        self.sources_ = sources
        self.interface_directories_ = interface_directories

    @property
    def sources(self) -> list[Path]:
        return self.sources_
    
    @property
    def interface_directories(self) -> list[Path]:
        return self.interface_directories_
    
class ProjectYAML:
    # Valid root keys in the YAML file
    VALID_ROOT = ["bin", "dyn", "lib", "workspace"]

    # Initialize with the project file path
    def __init__(self, file: Path):
        self.file_ = file
        self.yaml_ : Optional[dict] = None
        
    # Get the project file path
    @property
    def file(self) -> Path:
        return self.file_
    
    # Get the loaded yaml dictionary
    @property
    def yaml(self) -> dict | None:
        return self.yaml_
    
    # Load the yaml file into a dictionary
    def load_yaml(self) -> bool:
        import yaml
        try:
            with self.file.open() as f:
                self.yaml_ = yaml.safe_load(f)
            return True
        except (OSError, yaml.YAMLError) as e:
            console.print_error(f"Erreur lors du chargement de {self.file}: {e}")
            return False
        
    # Save the current yaml dictionary to the file
    def save_yaml(self) -> bool:
        import yaml
        try:
            with self.file.open("w", encoding="utf-8") as f:
                yaml.safe_dump(self.yaml_, f, sort_keys=False,
                    allow_unicode=True,
                    default_flow_style=False,
                    default_style=None,
                    indent=2,      
                )
            return True

        except (OSError, yaml.YAMLError) as e:
            console.print_error(f"Erreur lors de l'écriture de {self.file}: {e}")
            return False
    
    # load projects from a yaml file
    def load_projects(self) -> list[Project] | None:
        if not self.yaml:
            return []

        projects = list[Project]()

        for key, value in self.yaml.items():
            if key not in ProjectYAML.VALID_ROOT:
                console.print_error (f"⚠️  Error: invalid project type '{key}' in {self.file}")
                return None

            for item in value:
                if isinstance(item, dict):
                    # Read 'name'
                    name = item.get("name")
                    if not name:
                        console.print_error(f"⚠️  Error: Project name is missing in {self.file} under '{key}'")
                        return None
                    # Read 'version' as semver version
                    version = item.get("version")
                    if not version:
                        console.print_error(f"⚠️  Error: Project name is missing in {self.file} under '{key}'")
                        return None
                    try:
                        version = semver.VersionInfo.parse(version)
                    except Exception as e:
                        console.print_error(f"⚠️  Error: Invalid version format in {self.file} under '{key}': {e}")
                        return None

                    # Read 'description'
                    description = item.get("description", "")

                    # Read 'path', make it absolute if relative to the project file
                    path = Path(item.get("path", self.file.parent))
                    path = path if path.is_absolute() else self.file.parent / path

                    # Read 'dependencies'
                    dependencies:list[Dependency] = []
                    for dependency in item.get("dependencies", []):
                        # Read dependency 'name'
                        name = dependency.get("name")
                        if not name:
                            console.print_error(f"⚠️  Error: Project name is missing in {self.file} under '{key}'")
                            return None
                        path = dependency.get("path")
                        git = dependency.get("git")

                        # We need at least git or path
                        if not path and not git:
                            console.print_error(
                                f"⚠️  Error: Dependency '{name}' must define either 'path' or 'git' in {self.file} under '{key}'"
                            )
                            return None

                        # empêcher les deux à la fois
                        if path and git:
                            console.print_error(
                                f"⚠️  Error: Dependency '{name}' cannot define both 'path' and 'git' in {self.file} under '{key}'"
                            )
                            return None
                        
                        if path:
                            dependencies.append(PathDependency(name, path))
                        elif git:
                            branch = dependency.get("branch")
                            dependencies.append(GitDependency(name, git, branch))

                                            
                    # Create project
                    match key:
                        case ProjectType.bin:
                            sources = [self.file.parent / src for src in item.get("sources", [])]
                            projects.append(BinProject(file=self.file, path=path,name=name, description=description, sources=sources, version=version, dependencies=dependencies))
                        case ProjectType.lib:
                            sources = [self.file.parent / src for src in item.get("sources", [])]
                            interface_dirs = [self.file.parent / src for src in item.get("interface_directories", [])]
                            projects.append(LibProject(file=self.file,  path=path,name=name, description=description, sources=sources, interface_directories=interface_dirs, version=version, dependencies=dependencies))
                        case ProjectType.dyn:
                            sources = [self.file.parent / src for src in item.get("sources", [])]
                            interface_dirs = [self.file.parent / src for src in item.get("interface_directories", [])]
                            projects.append(DynProject(file=self.file,  path=path,name=name, description=description, sources=sources, interface_directories=interface_dirs, version=version, dependencies=dependencies))
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
        if project.path != project.file.parent:
            try:
                path = str(project.path.relative_to(project.file.parent))
                if path != project.file.parent:
                    data["path"] = path
            except ValueError:
                data["path"] = str(project.path)
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
        if self.yaml_ is None:
            self.yaml_ = {}
         
        # Check if project is not already present
        if self.is_project_present(project):
            console.print_error(f"⚠️  Error: Project `{project.name}` already exists in {self.file}")
            return False
        
        project_yaml = self.project_to_yaml_dict(project)
        match project:
            case BinProject():
                key = str(ProjectType.bin)
                if key not in self.yaml_:
                    self.yaml_[key] = []
                self.yaml_[key].append(project_yaml)
            case LibProject():
                key = str(ProjectType.lib)
                if key not in self.yaml_:
                    self.yaml_[key] = []
                self.yaml_[key].append(project_yaml)
            case DynProject():
                key = str(ProjectType.dyn)
                if key not in self.yaml_:
                    self.yaml_[key] = []
                self.yaml_[key].append(project_yaml)
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
        if self.yaml_ is None:
            console.print_error(f"⚠️  Error: YAML not loaded for {self.file}")
            return False
    
        for key, value in self.yaml_.items():
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
        return iter(self.projects_.items())
    
    def items(self):
        return self.projects_.items()
    
    @property
    def project(self) -> dict[Path, list[Project]]:
        return self.projects_
    # def projects(self) -> list[Project]:
    #     all_projects: list[Project] = []
    #     for project_list in self.registry_.values():
    #         all_projects.extend(project_list)
    #     return all_projects
    
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
    
    def load_projects_in_directory(self, path: Path, recursive: bool = False):
        pattern = f"**/{PROJECT_FILE_NAME}" if recursive else PROJECT_FILE_NAME

        # Load modules
        for file in path.glob(pattern):
            if self.is_file_loaded(file):
                continue
            yaml = ProjectYAML(file)
            yaml.load_yaml()
            for project in yaml.load_projects() :
                self.register_project(project)

ProjectRegistry = ProjectRegistry()

