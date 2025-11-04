import os
import sys
import console
from cmake.cmake_directories import CMakeDirectories
from config import Config

from kiss_parser import KissParser
from project.project import Project
from runner import RunnerRegistry


@RunnerRegistry.register("cmake", "Run project built with cmake")
class RunnerCMake:
    @classmethod
    def add_cli_argument_to_parser(cls, parser: KissParser):
        parser.add_argument("-c", "--config", choices=Config._member_names_, help="specify the build configuration", dest="config", type=Config)

    def __init__(self, parser: KissParser):
        self.config = getattr(parser, "config", None) or Config.debug
        

    def run(self, args : KissParser, project: Project):
        directories = CMakeDirectories (args, project)
        from pathlib import Path
        from artifact import Artifact
        from process import run_process
        from cmake.config_cmake import config_to_cmake_config
        artifact_directory = Path(os.path.join(directories.build_directory, project.name, config_to_cmake_config(self.config)))
        artifact = Artifact(project, args.platform_target, self.config)
        artifact_path = os.path.join(artifact_directory, artifact.name)

        if not artifact.is_executable:
            console.print_error(f"{project.name} is not an executable")
            sys.exit(2)

        run_process(artifact_path)
        
