import argparse
from pathlib import Path
from typing import Self
from cleaner import BaseCleaner, CleanerRegistry
from config import Config
import console
from context import Context
from project import Project
from projectregistry import ProjectRegistry
from toolchain import Toolchain, Compiler, Target

class CleanContext(Context):
    def __init__(self, directory:Path, project: Project, cleaner_name: str, toolchain : Toolchain, config : Config):
        super().__init__(directory)
        self._project = project
        self._cleaner_name = cleaner_name
        self._toolchain = toolchain
        self._config = config

    @property
    def project(self) -> Project:
        return self._project

    @property
    def cleaner_name(self) -> str:
        return self._cleaner_name
    
    @property
    def toolchain(self) -> Toolchain:
        return self._toolchain
    
    @property
    def config(self) -> Config:
        return self._config
    
    @classmethod
    def create(cls, directory: Path, project_name: str, cleaner_name: str, toolchain : Toolchain, config : Config) -> Self :
        #### Find the project to generate
        ProjectRegistry.load_and_register_all_project_in_directory(directory=directory, load_dependencies=True, recursive=False)
        projects_in_directory = ProjectRegistry.projects_in_directory(directory=directory)
        if len(projects_in_directory) == 0:
            console.print_error(f"No project found in {str(directory)}")
            exit(0)

        project_to_clean: Project = None
        if project_name:
            for project in projects_in_directory:
                if project.name == project_name:
                    project_to_clean = project
                    break
        
        return CleanContext(directory=directory, project=project_to_clean, cleaner_name=cleaner_name, toolchain=toolchain,  config=config)


    @staticmethod
    def from_cli_args(cli_args: argparse.Namespace) -> Self | None:
        release :bool = getattr(cli_args, "release", False) or False
        debug_info :bool = getattr(cli_args, "debug_info", True) or (True if not release else False)
        config : Config = Config(release, debug_info)
        target_name :Target = getattr(cli_args, "target", None) or Target.default_target_name()
        compiler_name : Compiler = getattr(cli_args, "compiler", None) or Compiler.default_compiler_name()
        if( toolchain := Toolchain.create(compiler_name=compiler_name, target_name=target_name)) is None:
            return None
        clean_context: CleanContext = CleanContext.create(directory=cli_args.directory,
                                                    project_name=cli_args.project_name,
                                                    cleaner_name=cli_args.cleaner,
                                                    toolchain=toolchain,
                                                    config=config)
        return clean_context


def cmd_clean(cli_args: argparse.Namespace):
    clean_context = CleanContext.from_cli_args(cli_args)
    cleaner : BaseCleaner = CleanerRegistry.cleaners.get(clean_context.cleaner_name)
    if not cleaner:
        console.print_error(f"Cleaner {clean_context.cleaner_name} not found")
        exit(1)
    cleaner.clean(clean_context)