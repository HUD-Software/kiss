from pathlib import Path
from kiss_parser import KissParser
import console

class ListParams:
    def __init__(self, args: KissParser):
        self.project_directory : Path = Path(args.directory)
        self.recursive: bool = args.recursive
        
def cmd_list(list_params: ListParams):
    from modules import ModuleRegistry
    ModuleRegistry.load_modules(list_params.project_directory, list_params.recursive)
    if len(ModuleRegistry.items()) == 0:
        console.print_error("Aucun projet trouvé !")
    else:
        for name, project in ModuleRegistry.items():
            console.print_success(f"--> Projet trouvé : {name}")
            console.print(f"    - name : {project.name}")
            console.print(f"    - type : {project.type}")
            console.print(f"    - description : {project.description}")
            console.print(f"    - prebuild : {project.prebuild}")
            console.print(f"    - postbuild : {project.postbuild}")
            console.print(f"    - src : {project.src}")
            