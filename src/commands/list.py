from pathlib import Path
from kiss_parser import KissParser
import console

       
def cmd_list(list_params: KissParser):
    from modules import ModuleRegistry
    ModuleRegistry.load_modules(list_params.directory, list_params.recursive)
    if len(ModuleRegistry.items()) == 0:
        console.print_error("Aucun projet trouvé !")
    else:
        for name, project in ModuleRegistry.items():
            console.print_success(f"--> Projet trouvé : {name}")
            console.print(f"    - name : {project.name}")
            console.print(f"    - type : {project.type}")
            console.print(f"    - description : {project.description}")
            