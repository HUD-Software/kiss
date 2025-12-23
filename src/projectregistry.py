
# ProjectRegistry represent all instanciation of project
# A Project is linked with it's file, and a file can contains multiple project
# To find a specific project you must provide a file to differenciate a project A that is in multiple file
from pathlib import Path
import console
from project import Project
from yaml_project import PROJECT_FILE_NAME, YamlDependencyType, YamlFile, YamlGitDependency, YamlPathDependency, YamlProject, YamlProjectType

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


    def _load_yaml_dependency(self, all_yaml_projects: dict[Path, list[YamlProject]], yaml_projects: list[YamlProject]) -> dict[Path, list[YamlProject]]:
        yaml_dependency_projects: dict[Path, list[YamlProject]] = {}

        for yaml_project in yaml_projects:
            for dependency in yaml_project.dependencies:
                match dependency.type:
                    case YamlDependencyType.path:
                        # Check if we have it in the project file instead of the file in the dependency directory
                        path_dependency: YamlPathDependency = dependency
                        
                        # Search for a project with the same path and name
                        yaml_inside_file = next( (p for p in yaml_projects if p.match_dependency(path_dependency)), None)
                                    
                        # If not found in the project file look for a yaml file in the dependency directory 
                        if not yaml_inside_file:
                            file_in_directory = path_dependency.directory / PROJECT_FILE_NAME
                            
                            # Oops… we don’t have a dependency YAML in the project or in the root of the dependency directory.
                            if not file_in_directory.exists():
                                console.print_error(f"Error: Failed to load dependency '{path_dependency.name}' for project '{yaml_project.name}'.\n\n" +
                                                    f"Possible causes:\n" + 
                                                    f"1. The file '{PROJECT_FILE_NAME}' is missing in:\n" + 
                                                    f"   {path_dependency.directory}\n\n" +
                                                    f"2. The dependency '{path_dependency.name}' is not declared in:\n" + 
                                                    f"   {yaml_project.file}\n\n")
                                console.print_tips( f"Tips:\n" + 
                                                    f"Each dependency must:\n"+
                                                    f"  - Have a '{PROJECT_FILE_NAME}' file in its root directory of the dependency, or\n" + 
                                                    f"  - Be declared in the '{PROJECT_FILE_NAME}' of the project that depends on it.")
                                exit(1)
                            else:
                                # Don't reload the file if already loaded
                                if file_in_directory in all_yaml_projects:
                                    continue
                                # Load the yaml
                                yaml = YamlFile(file_in_directory)
                                if not yaml.load_yaml():
                                    console.print_warning(f"Error: Unable to load project file `{file_in_directory}`")
                                    exit(1)
                                
                                # Load yaml projects and save them in the dependency set
                                for yaml_project in yaml.load_yaml_projects():
                                    yaml_dependency_projects.setdefault(file_in_directory, []).append(yaml_project)
                                    

                    case YamlDependencyType.git:
                        # Clone the repo and tr to load yaml file or request for a project in dependent project
                        dependency: YamlGitDependency = dependency
                        pass
        return yaml_dependency_projects

    def load_yaml_projects_in_directory(self, directory: Path, load_dependencies : bool, recursive: bool ) -> dict[Path, list[YamlProject]]:
        all_yaml_projects :dict[Path, list[YamlProject]] = {}

        pattern = f"**/{PROJECT_FILE_NAME}" if recursive else PROJECT_FILE_NAME

        # Load modules
        for file in directory.glob(pattern):
            # # Don't reload if already loaded
            if file in all_yaml_projects:
                continue

            # Load the yaml
            yaml = YamlFile(file)
            if not yaml.load_yaml():
                console.print_warning(f"Error: Unable to load project file `{file}`")
                exit(1)

            # Load yaml projects
            yaml_projects: list[YamlProject] = yaml.load_yaml_projects()
            for yaml_project in yaml_projects:
                all_yaml_projects.setdefault(file, []).append(yaml_project)

            # Load dependencies if requested
            if load_dependencies:
                # Load dependencies of all projects in the file
                yaml_dependency_projects: dict[Path, list[YamlProject]] = self._load_yaml_dependency(all_yaml_projects, yaml_projects)
                # Add all yaml dependencies to the set
                for dependency_file, yaml_dependencies in yaml_dependency_projects.items():
                    for dep in yaml_dependencies:
                        all_yaml_projects.setdefault(dependency_file, []).append(dep)

                while yaml_dependency_projects:
                    # Load all dependencies of dependencies
                    yaml_dependency_projects_old = yaml_dependency_projects
                    yaml_dependency_projects = {}
                    for dependency_file, yaml_dependency in yaml_dependency_projects_old.items():
                        for dependency_file2, yaml_dependencies in self._load_yaml_dependency(all_yaml_projects, yaml_dependency).items():
                            for dep2 in yaml_dependencies:
                                yaml_dependency_projects.setdefault(dependency_file2, []).append(dep2)

        return all_yaml_projects

    def register_all_project_in_directory(self, directory: Path, load_dependencies : bool, recursive: bool ):
        for yaml_project in self.load_yaml_projects_in_directory(directory, load_dependencies, recursive):
            self.register_project(Project.from_yaml_project(yaml_project))

    def projects_in_directory(self, directory: Path) -> list[Project]:
        for path, project_list in self.projects.items():
            if path.parent != directory:
                continue
            return project_list
        return []
            
ProjectRegistry = ProjectRegistry()