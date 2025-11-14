
from pathlib import Path
from kiss_parser import KissParser
from project import Project, ProjectType

class Workspace(Project):
    def __init__(self, name:str, file: Path, directory: Path, description: str = None, project_paths: list[Path] = []):
        super().__init__(name=name, 
                         directory=directory,
                         type=ProjectType.workspace, 
                         file=file,
                         description=description)
        self._project_paths = []
        for p in project_paths:
            p = Path(p)
            self._project_paths.append(p if p.is_absolute() else directory / p)

    @classmethod
    def add_cli_argument_to_parser(cls, parser: KissParser):
        parser.add_argument("workspace_name", help="name of the workspace to create", type=Path)
        parser.add_argument("-desc", "--description", help="project description", default="", type=str) 
        parser.add_argument("-p","--projects", nargs='+', help="name(s) of the project(s) to add to the workspace", type=Path)

    @property
    def project_paths(self)-> list[Project]:
        return self._project_paths
    
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
        project_list = ",".join([f'"{project.directory.relative_to(self.directory)}"' for project in self.projects])
        content += f"\n\t# List all projects in the PROJECTS variable\n"
        content += f"\tPROJECTS=[{project_list}]\n"

        return content