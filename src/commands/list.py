import modules
import console
import params

def cmd_list(listParams: params.ListParams):
    modules.load_modules(listParams.directory, listParams.recursive)
    if not modules.registered_projects:
        console.print_error("Aucun projet trouvé !")
    else:
        for name, cls in modules.registered_projects.items():
            console.print_success(f"--> Projet trouvé : {name}")
            console.print_step(   f"    - description : {getattr(cls, '_kiss_description', '')}")
            console.print_step(   f"    - prebuild : {hasattr(cls, "prebuild")}")
            console.print_step(   f"    - postbuild : {hasattr(cls, "postbuild")}")