from artifact import Artifact
from kiss_parser import KissParser


class RunParams:
    def __init__(self, args: KissParser):
        from pathlib import Path
        from runner import RunnerRegistry,BaseRunner 
        from project import Project
        from platform_target import PlatformTarget
        self.project_directory = args.directory / args.project_name
        self.project_name = Path(args.project_name).name if args.project_name else Project.default_project(args.directory)
        self.runner: BaseRunner = RunnerRegistry.create(args.runner if args.runner is not None else "cmake", args)
        self.platform_target: PlatformTarget = args.platform_target


def cmd_run(run_params: RunParams):
    run_params = RunParams(run_params)
    import console, sys
    from modules import ModuleRegistry
    from project import ProjectType, Project
    ModuleRegistry.load_modules(run_params.project_directory)
    project:Project = ModuleRegistry.get(run_params.project_name)
    if not project:
        console.print_error(f"Aucun projet trouvé dans le dossier {run_params.project_directory}")
        sys.exit(2)
    
    console.print_step(f"Running project {project.name} in {project.file}...")
    run_params.runner.run(run_params, project)