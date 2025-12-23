
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

    def register_all_project_in_directory(self, directory: Path, load_dependencies : bool, recursive: bool ):
        for yaml_projects in YamlFile.load_yaml_projects_in_directory(directory, load_dependencies, recursive).values():
            for yaml_project in yaml_projects:
                self.register_project(Project.from_yaml_project(yaml_project))

    def projects_in_directory(self, directory: Path) -> list[Project]:
        for path, project_list in self.projects.items():
            if path.parent != directory:
                continue
            return project_list
        return []
            
ProjectRegistry = ProjectRegistry()