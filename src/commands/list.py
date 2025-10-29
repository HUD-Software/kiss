from pathlib import Path
from modules import ModuleRegistry
import console

class ListParams:
    def __init__(self, directory:Path, recursive:bool):
        self.directory = directory
        self.recursive = recursive
        
def cmd_list(listParams: ListParams):
    ModuleRegistry.load_modules(listParams.directory, listParams.recursive)
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
            #console.print(f"    - src : {getattr(cls, 'src', None)}")
            