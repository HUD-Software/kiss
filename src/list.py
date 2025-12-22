from pathlib import Path
from typing import Self
import cli
import console
from context import Context
from project import BinProject, DynProject, GitDependency, LibProject, PathDependency, ProjectRegistry


class ListContext(Context):
    def __init__(self, directory:Path, recursive:bool):
        super().__init__(directory)
        self._recursive = recursive

    @property
    def recursive(self) -> bool : 
        return self._recursive
    
    @classmethod
    def from_cli_parser(cls, cli_parser: cli.KissParser) -> Self:
        return cls(directory=cli_parser.directory, recursive=cli_parser.recursive)
    
def cmd_list(list_params: cli.KissParser):
    list_context = ListContext.from_cli_parser(list_params)
    ProjectRegistry.load_projects_in_directory(directory=list_context.directory, recursive=list_context.recursive, load_dependencies=False)
    if len(ProjectRegistry.items()) == 0:
        console.print_error(f"No project found in '{list_context.directory}'")
    else:
        for file, projects in ProjectRegistry:
                console.print_success(f"File : {file}")
                if not projects:
                    console.print_error(f"The file {file} does not contains any project")
                else:
                    for project in projects:
                        match project:
                            case BinProject() as bin_project:
                                console.print(f"  - bin")
                            case LibProject() as lib_project:
                                console.print(f"  - lib")
                            case DynProject() as dyn_project:
                                console.print(f"  - dyn")
                        console.print(f"    - name : {project.name}")
                        console.print(f"    - description : {project.description}")
                        console.print(f"    - path : {project.directory}")
                        if project.dependencies:
                            console.print(f"    - dependencies : ")
                            for dep in  project.dependencies:
                                console.print(f"      - name : {dep.name}")
                                match dep:
                                    case PathDependency():
                                        console.print(f"      - path : {dep.path}")
                                    case GitDependency():
                                        console.print(f"      - git : {dep.git}")
                                        console.print(f"      - branch : {dep.branch}")
                        else:
                            console.print(f"    - dependencies : []")
                        match project:
                            case BinProject() as bin_project:
                                console.print(f"    - sources : {bin_project.sources}")
                            case LibProject() as lib_project:
                                console.print(f"    - sources : {lib_project.sources}")
                                console.print(f"    - interface directories : {lib_project.interface_directories}")
                            case DynProject() as dyn_project:
                                console.print(f"    - sources : {dyn_project.sources}")
                                console.print(f"    - interface directories : {dyn_project.interface_directories}")
                

