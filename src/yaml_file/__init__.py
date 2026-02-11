

# YamlProjectFile is the instanciation of one kiss.yaml file.
# It is use to load, read, modify and save the yaml file.
from pathlib import Path
from typing import Optional, Self
import semver
import yaml
import console
from yaml_file.yaml_project import PROJECT_FILE_NAME, YamlBinProject, YamlDependency, YamlDependencyType, YamlDynProject, YamlGitDependency, YamlLibProject, YamlPathDependency, YamlProject, YamlProjectType

# Valid root keys in the YAML file
_VALID_YAML_ROOT = [str(YamlProjectType.bin), str(YamlProjectType.dyn), str(YamlProjectType.lib), str(YamlProjectType.workspace)]


class YamlProjectFile:
   
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
            console.print_error(f"Error: When loading {self.file} file: {e}")
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
            console.print_error(f"Error: When saving {self.file} file: {e}")
            return False
    

    def _read_project(self, project_type_key: YamlProjectType, yaml_project: dict) -> YamlProject:
        # Read 'name'
        name = yaml_project.get("name")
        if not name:
            console.print_error(f"⚠️  Error: Project name is missing in {self.file} under '{project_type_key}'")
            exit(1)
        # Read 'version' as semver version
        version = yaml_project.get("version")
        if not version:
            console.print_error(f"⚠️  Error: Project name is missing in {self.file} under '{project_type_key}'")
            exit(1)
        try:
            version = semver.VersionInfo.parse(version)
        except Exception as e:
            console.print_error(f"⚠️  Error: Invalid version format in {self.file} under '{project_type_key}': {e}")
            exit(1)

        # Read 'description'
        description = yaml_project.get("description", "")

        # Read 'path', make it absolute if relative to the project file
        project_path = Path(yaml_project.get("path", self.file.parent))
        project_path = project_path if project_path.is_absolute() else self.file.parent / project_path

        # Read 'dependencies'
        dependencies:list[YamlDependency] = []
        for dependency in yaml_project.get("dependencies", []) or []:
            # Read dependency 'name'
            dep_name = dependency.get("name")
            if not dep_name:
                console.print_error(f"⚠️  Error: Project name is missing in {self.file} under '{project_type_key}'")
                exit(1)
            dep_path = dependency.get("path")
            dep_git = dependency.get("git")
            
            # Path and git are exclusive
            if dep_path and dep_git:
                console.print_error(
                    f"⚠️  Error: Dependency '{dep_name}' cannot define both 'path' and 'git' in {self.file} under '{project_type_key}'"
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
                dep_path = Path(dep_name)
                dependencies.append(YamlPathDependency(dep_name, (self.file.parent / dep_path).resolve(strict=False)))

        # Create project
        match project_type_key:
            case YamlProjectType.bin:
                sources = []
                for src in yaml_project.get("sources", []) or []:
                    src_path = Path(src)
                    if src_path.is_absolute():
                        sources.append(src_path)
                    else:
                        sources.append(project_path / src_path)
                return YamlBinProject(file=self.file, path=project_path, name=name, description=description, sources=sources, version=version, dependencies=dependencies)
            case YamlProjectType.lib:
                sources = []
                for src in yaml_project.get("sources", []) or []:
                    src_path = Path(src)
                    if src_path.is_absolute():
                        sources.append(src_path)
                    else:
                        sources.append(project_path / src_path)
                interface_dirs = []
                for dir in yaml_project.get("interface_directories", []) or []:
                    dir_path = Path(dir)
                    if dir_path.is_absolute():
                        interface_dirs.append(dir_path)
                    else:
                        interface_dirs.append(project_path / dir_path)
                return YamlLibProject(file=self.file,  path=project_path, name=name, description=description, sources=sources, interface_directories=interface_dirs, version=version, dependencies=dependencies)
            case YamlProjectType.dyn:
                sources = []
                for src in yaml_project.get("sources", [])or []:
                    src_path = Path(src)
                    if src_path.is_absolute():
                        sources.append(src_path)
                    else:
                        sources.append(project_path / src_path)
                interface_dirs = []
                for dir in yaml_project.get("interface_directories", []) or []:
                    dir_path = Path(dir)
                    if dir_path.is_absolute():
                        interface_dirs.append(dir_path)
                    else:
                        interface_dirs.append(project_path / dir_path)
                return YamlDynProject(file=self.file,  path=project_path, name=name, description=description, sources=sources, interface_directories=interface_dirs, version=version, dependencies=dependencies)

    # load projects from a yaml file
    def _read_all_projects_in_file(self) -> list[YamlProject]:
        if not self.yaml:
            return []

        projects = list[YamlProject]()

        for project_type_key, yaml_project_list in self.yaml.items():
            if project_type_key not in _VALID_YAML_ROOT:
                console.print_error (f"⚠️  Error: Invalid project type '{project_type_key}' in {self.file}")
                exit(1)
            for yaml_project in yaml_project_list:
                project = self._read_project(YamlProjectType(project_type_key), yaml_project)
                projects.append(project)
          
        return projects
    
    @classmethod
    def _load_yaml_dependency(cls, loaded_yaml_projects: dict[Path, list[YamlProject]], yaml_projects_in_file: list[YamlProject]) -> dict[Path, list[YamlProject]]:
        yaml_dependency_projects: dict[Path, list[YamlProject]] = {}

        for yaml_project in yaml_projects_in_file:
            for dependency in yaml_project.dependencies:
                match dependency.type:
                    case YamlDependencyType.path:
                        # Check if we have it in the project file instead of the file in the dependency path
                        path_dependency: YamlPathDependency = dependency
                        
                        # Search for a project with the same path and name
                        yaml_inside_file = next( (p for p in yaml_projects_in_file if p.is_matching_yaml_dependency(path_dependency)), None)
                                    
                        # If not found in the project file look for a yaml file in the dependency path 
                        if not yaml_inside_file:
                            file_in_directory = path_dependency.path / PROJECT_FILE_NAME
                            
                            # Oops… we don’t have a dependency YAML in the project or in the root of the dependency path.
                            if not file_in_directory.exists():
                                console.print_error(f"Error: Failed to load dependency '{path_dependency.name}' for project '{yaml_project.name}'.\n\n" +
                                                    f"Possible causes:\n" + 
                                                    f"1. The file '{PROJECT_FILE_NAME}' is missing in:\n" + 
                                                    f"   {path_dependency.path}\n\n" +
                                                    f"2. The dependency '{path_dependency.name}' is not declared in:\n" + 
                                                    f"   {yaml_project.file}\n" +
                                                    f"   or the 'path' attributs is not set.\n\n")
  
                                console.print_tips( f"Tips:\n" + 
                                                    f"Each dependency must:\n"+
                                                    f"  - Have a '{PROJECT_FILE_NAME}' file in its root path of the dependency, or\n" + 
                                                    f"  - Be declared in the '{PROJECT_FILE_NAME}' of the project that depends on it. note that 'path' is required in this case.")
                                exit(1)
                            else:
                                # Don't reload the file if already loaded
                                if file_in_directory in loaded_yaml_projects or file_in_directory in yaml_dependency_projects:
                                    continue
                                
                                # Load the yaml
                                yaml = YamlProjectFile(file_in_directory)
                                if not yaml.load_yaml():
                                    console.print_error(f"⚠️ Error: Unable to load project file `{file_in_directory}`")
                                    exit(1)

                                # Load yaml projects and save them in the dependency set
                                for yaml_project_deps in yaml._read_all_projects_in_file():
                                    yaml_dependency_projects.setdefault(file_in_directory, []).append(yaml_project_deps)
                                    

                    case YamlDependencyType.git:
                        # Clone the repo and tr to load yaml file or request for a project in dependent project
                        dependency: YamlGitDependency = dependency
                        pass
        return yaml_dependency_projects

    # Load all YamlProject in a file and add them to yaml_projects
    # When load_dependencies is True, also load YamlProject of dependencies
    @staticmethod
    def load_yaml_projects(yaml_file: Self, loaded_yaml_projects: dict[Path, list[YamlProject]], load_dependencies : bool):
        # Load yaml projects
        new_yaml_projects_in_file: list[YamlProject] = yaml_file._read_all_projects_in_file()
        for yaml_project in new_yaml_projects_in_file:
            loaded_yaml_projects.setdefault(yaml_file.file, []).append(yaml_project)

        # Load dependencies if requested
        if load_dependencies:
            # Load dependencies of all projects in the file
            yaml_dependency_projects: dict[Path, list[YamlProject]] = YamlProjectFile._load_yaml_dependency(loaded_yaml_projects, new_yaml_projects_in_file)

            while yaml_dependency_projects:
                # Add all yaml dependencies to the set
                for dependency_file, yaml_dependencies in yaml_dependency_projects.items():
                    for dep in yaml_dependencies:
                        loaded_yaml_projects.setdefault(dependency_file, []).append(dep)

                # Load all dependencies of dependencies
                yaml_dependency_projects_old = yaml_dependency_projects
                yaml_dependency_projects = {}
                for dependency_file, yaml_dependency in yaml_dependency_projects_old.items():
                    for dependency_file2, yaml_dependencies in YamlProjectFile._load_yaml_dependency(loaded_yaml_projects, yaml_dependency).items():
                        for dep2 in yaml_dependencies:
                            yaml_dependency_projects.setdefault(dependency_file2, []).append(dep2)

    # Load all YamlProject in a directory.
    # When load_dependencies is True, also load YamlProject of dependencies
    # When recursive is true, also load YamlProject in child directories 
    @staticmethod
    def load_yaml_projects_in_directory(directory: Path, load_dependencies : bool, recursive: bool) -> dict[Path, list[YamlProject]]:
        loaded_yaml_projects :dict[Path, list[YamlProject]] = {}

        pattern = f"**/{PROJECT_FILE_NAME}" if recursive else PROJECT_FILE_NAME

        # Load modules
        for file in directory.glob(pattern):
            # Don't reload if already loaded
            if file in loaded_yaml_projects:
                continue
            # Load the yaml
            yaml = YamlProjectFile(file)
            if not yaml.load_yaml():
                console.print_error(f"⚠️ Error: Unable to load project file `{file}`")
                exit(1)
            # Load project in the YAML file
            YamlProjectFile.load_yaml_projects(yaml, loaded_yaml_projects, load_dependencies)

        return loaded_yaml_projects
    
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
        