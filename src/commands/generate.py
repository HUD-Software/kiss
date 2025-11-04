from kiss_parser import KissParser

class GenerateParams:
    def __init__(self, args: KissParser):
        from generator import GeneratorRegistry, BaseGenerator
        from pathlib import Path
        from platform_target import PlatformTarget
        from project import Project
        self.project_directory:Path = Path(args.directory)
        self.project_name: str = args.project_name if args.project_name else Project.default_project(args.directory)
        self.generator: BaseGenerator = GeneratorRegistry.create(args.generator if args.generator is not None else "cmake", args)
        self.platform_target: PlatformTarget = args.platform_target

def cmd_generate(generate_params: GenerateParams):
    # If the no project name is present, search for the one loadable in the current directory
    import console, sys
    from modules import ModuleRegistry
    console.print_step("Generating build scripts...")
    ModuleRegistry.load_modules(generate_params.project_directory)
    project = ModuleRegistry.get(generate_params.project_name)
    if not project:
        console.print_error(f"Aucun projet trouvé dans le dossier {generate_params.project_directory}")
        sys.exit(2)
    
    generate_params.generator.generate(generate_params, project)        