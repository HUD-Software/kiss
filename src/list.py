import cli
import console
from project import BinProject, DynProject, LibProject, ProjectRegistry


def cmd_list(list_params: cli.KissParser):
    ProjectRegistry.load_projects_in_directory(path=list_params.directory, recursive=list_params.recursive)
    if len(ProjectRegistry.items()) == 0:
        console.print_error("Aucun projet trouvé !")
    else:
        for project in ProjectRegistry.projects():
                console.print_success(f"--> Projet trouvé : {project.file}")
                console.print(f"    - name : {project.name}")
                console.print(f"    - description : {project.description}")
                console.print(f"    - path : {project.path}")
                match project:
                    case BinProject() as bin_project:
                        console.print(f"    - sources : {bin_project.sources}")
                    case LibProject() as lib_project:
                        console.print(f"    - sources : {lib_project.sources}")
                        console.print(f"    - interface directories : {lib_project.interface_directories}")
                    case DynProject() as dyn_project:
                        console.print(f"    - sources : {dyn_project.sources}")
                        console.print(f"    - interface directories : {dyn_project.interface_directories}")
