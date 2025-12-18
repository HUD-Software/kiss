import cli
import console
from project import BinProject, DynProject, GitDependency, LibProject, PathDependency, ProjectRegistry


def cmd_list(list_params: cli.KissParser):
    ProjectRegistry.load_projects_in_directory(path=list_params.directory, recursive=list_params.recursive)
    if len(ProjectRegistry.items()) == 0:
        console.print_error(f"Aucun projet trouvé dans {list_params.directory}")
    else:
        for project in ProjectRegistry.projects():
                console.print_success(f"--> Projet trouvé : {project.file}")
                console.print(f"    - name : {project.name}")
                console.print(f"    - description : {project.description}")
                console.print(f"    - path : {project.path}")
                if project.dependencies:
                    console.print(f"    - dependencies : ")
                    for dep in  project.dependencies:
                        console.print(f"      - name : {dep.name}")
                        match dep:
                            case PathDependency():
                                console.print(f"      - path : {dep.name}")
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
                

