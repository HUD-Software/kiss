# ProjectRegistry represent all instanciation of project
# A Project is linked with it's file, and a file can contains multiple project
# To find a specific project you must provide a file to differenciate a project A that is in multiple file
from pathlib import Path
import console
from project import Project
from yaml_file import YamlProjectFile, YamlProject

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
    
    def load_and_register_all_project_in_directory(self, directory: Path, load_dependencies : bool, recursive: bool ):
        # Load all yaml projects
        list_all_yaml_project = YamlProjectFile.load_yaml_projects_in_directory(directory, load_dependencies, recursive).values()
            
        # Create all projects
        all_projects: set[(YamlProject, Project)] = set()
        for yaml_project_list in list_all_yaml_project:
            for yaml_project in yaml_project_list:
                all_projects.add((yaml_project, Project.from_yaml_project(yaml_project)))

        # Resolve dependencies match yaml dependency with corresponding projects
        for yaml_project, project in all_projects:
            for yaml_dep in yaml_project.dependencies:
                resolved = False
                for yaml_project_dep, project_dep in all_projects:
                    # Check if Yaml match ( means we have a kiss.yaml in the depencency directory)
                    # Or if the Yaml don't match, check if the yaml dependency name match the project name and the directory of that project (Where the kiss.yaml is)match the file directory of the project
                    # We add this extra test to allow user to add a project as a dependency if this project is defined as a inner project (A/kiss.yml define a project 'B' in A/B directory)
                    if yaml_project_dep.is_matching_yaml_dependency(yaml_dep) or (yaml_dep.name == project_dep.name and project_dep.file.parent == yaml_dep.path):
                        project.dependencies.append(project_dep)
                        resolved = True
                        break
                if not resolved:
                    console.print_error(f"Failed to find project that match the {yaml_dep.type} dependency '{yaml_dep.name}' for the project '{yaml_project.name}' in file {yaml_project.file}")
                    exit(1)
                    
        # Register projects
        for _, project in all_projects:
            self.register_project(project)
        
    def projects_in_directory(self, directory: Path) -> list[Project]:
        for path, project_list in self.projects.items():
            if path.parent != directory:
                continue
            return project_list
        return []
            
ProjectRegistry = ProjectRegistry()