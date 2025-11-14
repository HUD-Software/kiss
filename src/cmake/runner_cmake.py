from pathlib import Path
import sys
from cmake.builder_cmake import BuilderCMake
import console
from cmake.cmake_directories import CMakeDirectories
from config import Config

from kiss_parser import KissParser
from modules import ModuleRegistry
from platform_target import PlatformTarget
from project import Project, Workspace
from runner import RunnerRegistry


@RunnerRegistry.register("cmake", "Run project built with cmake")
class RunnerCMake:
    @classmethod
    def add_cli_argument_to_parser(cls, parser: KissParser):
        parser.add_argument("-c", "--config", choices=Config._member_names_, help="specify the build configuration", dest="config", type=Config)

    def __init__(self, parser: KissParser):
        self.config = getattr(parser, "config", None) or Config.debug
        
    def run_project(self,project_directory:Path, platform_target: PlatformTarget, project:Project):

        # Build before
        builder = BuilderCMake ()
        builder.build_project(project_directory,platform_target,project)

        # Run now
        directories = CMakeDirectories(project_directory=project_directory,
                                       platform_target=platform_target, 
                                       project=project)
        from artifact import Artifact
        from process import run_process
        from cmake.config_cmake import config_to_cmake_config

        artifact_directory = directories.build_directory / project.name / config_to_cmake_config(self.config)
        artifact = Artifact(project, platform_target, self.config)
        artifact_path = artifact_directory / artifact.name

        if not artifact.is_executable:
            console.print_error(f"{project.name} is not an executable")
            sys.exit(2)

        run_process(artifact_path)

    def run(self, args : KissParser, project: Project):
        if isinstance(project, Workspace):
            for project_path in project.project_paths:
                ModuleRegistry.load_modules(project_path)
            bin_list:list[Project] = ModuleRegistry.all_bin()
            if len(bin_list)> 1:
                console.print_error(f"`kiss run` requires that a binary target is available.")
                names = ", ".join(b.name for b in bin_list)
                console.print_error(f"multiple binary targets found: {names}")
                sys.exit(2)
            project = bin_list[0]
            self.run_project(project_directory=project.directory,
                       platform_target=args.platform_target,
                       project=project)
        else:
            self.run_project(project_directory=args.project_directory,
                        platform_target=args.platform_target,
                        project=project)
            
        
