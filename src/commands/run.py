from kiss_parser import KissParser

class RunParams:
    def __init__(self, args: KissParser):
        from pathlib import Path
        from runner import RunnerRegistry,BaseRunner 
        from project import Project
        from platform_target import PlatformTarget
        self.project_directory:Path=Path(args.directory)
        self.project_name:str = args.project_name if args.project_name else Project.default_project(args.directory)
        self.runner: BaseRunner = RunnerRegistry.create(args.runner if args.runner is not None else "cmake", args)
        self.platform_target: PlatformTarget = args.platform_target


def cmd_run(run_params: RunParams):
    import console, sys
    from modules import ModuleRegistry
    ModuleRegistry.load_modules(run_params.project_directory)
    project = ModuleRegistry.get(run_params.project_name)
    if not project:
        console.print_error(f"Aucun projet trouvé dans le dossier {run_params.project_directory}")
        sys.exit(2)
    
    console.print_step(f"Building project {project.name} in {project.file}...")

    import platform
    from compiler import Compiler
    console.print(f"directory = {run_params.project_directory}")
    console.print(f"project_name = {run_params.project_name}")
    console.print(f"runner = {run_params.runner.name()}")
    console.print(f"platform_target = {run_params.platform_target}")
    if platform.system() == "Windows":
        from toolset import VSToolset
        console.print(f"latest_toolset = {VSToolset.get_latest_toolset(Compiler.cl)}")

    run_params.runner.run(run_params, project)