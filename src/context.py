from pathlib import Path
from typing import Optional
import console
from project import Project, ProjectType
from projectregistry import ProjectRegistry


class Context:
    def __init__(self, directory):
        self._directory = Path(directory)

    @property
    def directory(self) -> Path:
        return self._directory
    
    def find_target_project(directory: Path, project_name: str, filter: ProjectType = None) -> Optional[Project]:
        #### Find the project to generate
        ProjectRegistry.load_and_register_all_project_in_directory(directory=directory, load_dependencies=True, recursive=False)
        projects_in_directory = ProjectRegistry.projects_in_directory(directory=directory)
        if len(projects_in_directory) == 0:
            console.print_error(f"No project found in {str(directory)}")
            return None

        # If user provide a project name find it
        if project_name:
            if(project := ProjectRegistry.get_project(project_name)) is None:
                return None
            return project
        # If the user dont provide a project name, find the default project
        else:
            if filter:
                projects_in_directory = [project for project in projects_in_directory if project.type == filter]
            if len(projects_in_directory) > 1:
                console.print_error(f"Multiple project found in {str(directory)}")
                projects_in_directory_names = [project.name for project in projects_in_directory]
                for name in projects_in_directory_names:
                    console.print_error(f"  - {name}")
                choices = " | ".join(projects_in_directory_names)
                console.print_error(f"Unable to select a default project. You must provide a project with --project [{choices}]")
                return None
            else:
                return projects_in_directory[0]  

        


        