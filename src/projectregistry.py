
# ProjectRegistry represent all instanciation of project
# A Project is linked with it's file, and a file can contains multiple project
# To find a specific project you must provide a file to differenciate a project A that is in multiple file
from pathlib import Path
from typing import TypeAlias
import console
from project import Project
from yaml_project import YamlDependency, YamlFile, YamlProject

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
    
    def register_all_project_in_directory(self, directory: Path, load_dependencies : bool, recursive: bool ):
        # Load all yaml projects
        list_all_yaml_project = YamlFile.load_yaml_projects_in_directory(directory, load_dependencies, recursive).values()
            
        # Create projects
        all_projects: list[Project] = []
        for yaml_project_list in list_all_yaml_project:
            for yaml_project in yaml_project_list:
                all_projects.append(Project.from_yaml_project(yaml_project))


        # Resolve dependencies
        # project_by_key: dict[tuple[str, Path], Project] = {}
        # for project in all_projects:
        #     key = (project.name, project.directory)
        #     project_by_key[key] = project

        # for yaml_project_list in list_all_yaml_project:
        #     for yaml_project in yaml_project_list:
        #         for dep in yaml_project.dependencies:
        #             dep_key = (dep.name, dep.directory)
        #             dep_project = project_by_key.get(dep_key)
        #             if not dep_project:
        #                 raise RuntimeError(
        #                     f"Dependency '{dep.name}' in '{dep.directory}' not found among loaded projects"
        #                 )
        #             console.print_success(f"{project.name} depends on {dep_project.name}")

        for project in all_projects:
            # Register projects
            self.register_project(project)
        
    def projects_in_directory(self, directory: Path) -> list[Project]:
        for path, project_list in self.projects.items():
            if path.parent != directory:
                continue
            return project_list
        return []
            
ProjectRegistry = ProjectRegistry()