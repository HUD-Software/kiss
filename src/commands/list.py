from pathlib import Path
import modules
import console

class ListParams:
    def __init__(self, directory:Path, recursive:bool):
        self.directory = directory
        self.recursive = recursive
        
def cmd_list(listParams: ListParams):
    modules.load_modules(listParams.directory, listParams.recursive)
    if not modules.registered_projects:
        console.print_error("Aucun projet trouvé !")
    else:
        for name, cls in modules.registered_projects.items():
            console.print_success(f"--> Projet trouvé : {name}")
            console.print(f"    - description : {getattr(cls, '_project_description', '')}")
            console.print(f"    - prebuild : {hasattr(cls, 'prebuild')}")
            console.print(f"    - postbuild : {hasattr(cls, 'postbuild')}")
            console.print(f"    - src : {getattr(cls, 'src', None)}")
            