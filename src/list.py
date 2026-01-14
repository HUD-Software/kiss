from pathlib import Path
from typing import Self
import cli
import console
from context import Context
from yaml_file import YamlFile, YamlGitDependency, YamlPathDependency, YamlProjectType


class ListContext(Context):
    def __init__(self, directory:Path, recursive:bool, list_dependencies:bool):
        super().__init__(directory)
        self._recursive = recursive
        self._list_dependencies = list_dependencies

    @property
    def recursive(self) -> bool : 
        return self._recursive
    
    @property
    def list_dependencies(self) -> bool : 
        return self._list_dependencies
    
    @classmethod
    def from_cli_parser(cls, cli_parser: cli.KissParser) -> Self:
        return cls(directory=cli_parser.directory, recursive=cli_parser.recursive, list_dependencies=cli_parser.list_dependencies)
    
def cmd_list(list_params: cli.KissParser):
    list_context = ListContext.from_cli_parser(list_params)
    all_yaml_projects = YamlFile.load_yaml_projects_in_directory(directory=list_context.directory, recursive=list_context.recursive, load_dependencies=list_context.list_dependencies)
    if not all_yaml_projects:
        console.print_success(f"No project found in '{list_context.directory}'")
    else:
        for file, projects in all_yaml_projects.items():
            console.print_success(f"File : {file}")
            if not projects:
                console.print_error(f"The file {file} does not contains any project")
            else:
                for project in projects:
                    match project.type:
                        case YamlProjectType.bin:
                            console.print(f"  - bin")
                        case YamlProjectType.lib:
                            console.print(f"  - lib")
                        case YamlProjectType.dyn:
                            console.print(f"  - dyn")
                    console.print(f"    - name : {project.name}")
                    console.print(f"    - description : {project.description}")
                    console.print(f"    - path : {project.directory}")
                    if project.dependencies:
                        console.print(f"    - dependencies : ")
                        for dep in  project.dependencies:
                            console.print(f"      - name : {dep.name}")
                            match dep:
                                case YamlPathDependency():
                                    console.print(f"      - path : {dep.directory}")
                                case YamlGitDependency():
                                    console.print(f"      - git : {dep.git}")
                                    console.print(f"      - branch : {dep.branch}")
                    else:
                        console.print(f"    - dependencies : []")
                    match project.type:
                        case YamlProjectType.bin :
                            console.print(f"    - sources : {project.sources}")
                        case YamlProjectType.lib :
                            console.print(f"    - sources : {project.sources}")
                            console.print(f"    - interface directories : {project.interface_directories}")
                        case YamlProjectType.dyn:
                            console.print(f"    - sources : {project.sources}")
                            console.print(f"    - interface directories : {project.interface_directories}")
                

