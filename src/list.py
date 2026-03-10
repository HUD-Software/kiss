import argparse
from pathlib import Path
from typing import Self
import cli
import console
from context import KissBaseContext
from yaml_file import YamlProjectFile, YamlGitDependency, YamlPathDependency, YamlProjectType


class KissListContext(KissBaseContext):
    def __init__(self, current_directory:Path, recursive:bool, list_dependencies:bool):
        super().__init__(current_directory)
        self._recursive = recursive
        self._list_dependencies = list_dependencies

    @property
    def recursive(self) -> bool : 
        return self._recursive
    
    @property
    def list_dependencies(self) -> bool : 
        return self._list_dependencies
    
    @classmethod
    def from_cli_args(cls, cli_args: argparse.Namespace) -> Self:
        return cls(current_directory=cli_args.directory, recursive=cli_args.recursive, list_dependencies=cli_args.list_dependencies)
    
def cmd_list(cli_args: argparse.Namespace):
    list_context = KissListContext.from_cli_args(cli_args)
    all_yaml_projects = YamlProjectFile.load_yaml_projects_in_directory(directory=list_context.current_directory, recursive=list_context.recursive, load_dependencies=list_context.list_dependencies)
    if not all_yaml_projects:
        console.print_success(f"No project found in '{list_context.current_directory}'")
    else:
        for yaml_project_file, yaml_project_list in all_yaml_projects.items():
            console.print_success(f"File : {str(yaml_project_file)}")
            if not yaml_project_list:
                console.print_error(f"The file {str(yaml_project_file)} does not contains any project")
            else:
                for project in yaml_project_list:
                    match project.type:
                        case YamlProjectType.bin:
                            console.print(f"  - bin")
                        case YamlProjectType.lib:
                            console.print(f"  - lib")
                        case YamlProjectType.dyn:
                            console.print(f"  - dyn")
                    console.print(f"    - name : {project.name}")
                    console.print(f"    - description : {project.description}")
                    console.print(f"    - path : {project.path}")
                    if project.dependencies:
                        console.print(f"    - dependencies : ")
                        for dep in  project.dependencies:
                            console.print(f"      - name : {dep.name}")
                            match dep:
                                case YamlPathDependency():
                                    console.print(f"        path : {dep.path}")
                                case YamlGitDependency():
                                    console.print(f"        git : {dep.git}")
                                    console.print(f"        branch : {dep.branch}")
                    else:
                        console.print(f"    - dependencies : []")
                    match project.type:
                        case YamlProjectType.bin :
                            console.print(f"    - sources : {[str(p) for p in project.sources]}")
                        case YamlProjectType.lib :
                            console.print(f"    - sources : {[str(p) for p in project.sources]}")
                            console.print(f"    - interface directories : {[str(p) for p in project.interface_directories]}")
                        case YamlProjectType.dyn:
                            console.print(f"    - sources : {[str(p) for p in project.sources]}")
                            console.print(f"    - interface directories : {[str(p) for p in project.interface_directories]}")
                    

