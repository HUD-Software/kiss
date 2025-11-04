from pathlib import Path
from kiss_parser import KissParser


class BuildParams:
    def __init__(self, args: KissParser):
        from builder import BuilderRegistry, BaseBuilder
        from platform_target import PlatformTarget
        from project.project import Project
        self.project_directory:Path = Path(args.directory)
        self.project_name:str = args.project_name if args.project_name else Project.default_project(args.directory)
        self.builder: BaseBuilder = BuilderRegistry.create(args.builder if args.builder is not None else "cmake", args)
        self.platform_target: PlatformTarget = args.platform_target

def cmd_build(build_params: BuildParams):
    import console, sys
    from modules import ModuleRegistry
    ModuleRegistry.load_modules(build_params.project_directory)
    project = ModuleRegistry.get(build_params.project_name)
    if not project:
        console.print_error(f"Aucun projet trouvé dans le dossier {build_params.project_directory}")
        sys.exit(2)
    
    console.print_step(f"Building project {project.name} in {project.file}...")

    import platform
    from compiler import Compiler

    console.print(f"directory = {build_params.project_directory}")
    console.print(f"project_name = {build_params.project_name}")
    console.print(f"builder = {build_params.builder.name()}")
    console.print(f"platform_target = {build_params.platform_target}")
    if platform.system() == "Windows":
        from toolset import VSToolset
        console.print(f"latest_toolset = {VSToolset.get_latest_toolset(Compiler.cl)}")

    build_params.builder.build(build_params, project)