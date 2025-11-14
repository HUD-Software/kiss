
from pathlib import Path
from kiss_parser import KissParser
from project import Project, ProjectType

class Workspace(Project):
    def __init__(self, name:str, file: Path,directory: Path, description: str = None, projects: list[Project] = []):
        super().__init__(name=name, 
                         directory=directory,
                         type=ProjectType.workspace, 
                         file=file,
                         description=description)
        self._projects = projects

    @classmethod
    def add_cli_argument_to_parser(cls, parser: KissParser):
        parser.add_argument("workspace_name", help="name of the workspace to create")
        parser.add_argument("-desc", "--description", help="project description", default="", type=str) 
        parser.add_argument("-p","--projects", nargs='+', help="name(s) of the project(s) to add to the workspace")

    @property
    def projects(self)-> list[str]:
        return self._projects
    
    def to_new_manifest_str(self) -> str:
        # Add Import statements
        content = f"from modules import Workspace"
        if self.description:
            content += ", Description\n"
        else:
            content += "\n"
        #Add line separate after the import statements
        content += "\n"

        # Add decorator statement
        content += f'@Workspace("{self.name}")\n'
        if self.description:
            content += f'@Description("{self.description}")\n'

        # Format class name properly (e.g. my_project → MyProject)
        content += f"class {Project.to_pascal(self.name)}:\n"

        # Add project directories
        project_list = ",".join([f'"{project.name}"' for project in self.projects])
        content += f"\n\t# List all projects in the PROJECTS variable\n"
        content += f"\tPROJECTS=[{project_list}]\n"

        return content