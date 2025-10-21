import modules

def cmd_list(args):
    modules_list = modules.load_modules(args.directory)
    if not modules.registered_projects:
        print("Aucun projet trouvé !")
    else:
        for name, cls in modules.registered_projects.items():
            print(f"Projet trouvé : {name}, description : {getattr(cls, '_kiss_description', '')}")
            instance = cls()
            if hasattr(instance, "prebuild"):
                instance.prebuild()
            if hasattr(instance, "postbuild"):
                instance.postbuild()