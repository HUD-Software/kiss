from pathlib import Path
from kiss_parser import KissParser
import console
from project import BinProject, LibProject, DynProject

       
def cmd_list(list_params: KissParser):
    from modules import ModuleRegistry
    ModuleRegistry.load_modules(list_params.directory, list_params.recursive)
    if len(ModuleRegistry.items()) == 0:
        console.print_error(f"Aucun projet trouvé dans {list_params.directory}")
    else:
        for name, project in ModuleRegistry.items():
            console.print_success(f"--> Projet trouvé : {name}")
            console.print(f"    - name : {project.name}")
            console.print(f"    - type : {project.type}")
            console.print(f"    - description : {project.description}")
            console.print(f"    - directory : {project.directory}")
            match project:
                case BinProject() as bin_project:
                    console.print(f"    - sources : {bin_project.sources}")
                case LibProject() as lib_project:
                    console.print(f"    - sources : {lib_project.sources}")
                    console.print(f"    - interface directories : {lib_project.interface_directories}")
                case DynProject() as dyn_project:
                    console.print(f"    - sources : {dyn_project.sources}")
                    console.print(f"    - interface directories : {dyn_project.interface_directories}")


            