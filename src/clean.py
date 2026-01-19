import argparse
from pathlib import Path
from typing import Self
from cleaner import BaseCleaner, CleanerRegistry
import cli
from compiler import Compiler
from config import Config
import console
from context import Context
from platform_target import PlatformTarget
from project import Project, ProjectType
from projectregistry import ProjectRegistry

class CleanContext(Context):
    def __init__(self, directory:Path, project: Project, cleaner_name: str, platform_target: PlatformTarget, config : Config, compiler : Compiler):
        super().__init__(directory)
        self._project = project
        self._cleaner_name = cleaner_name
        self._platform_target = platform_target
        self._config = config
        self._compiler = compiler


    @property
    def project(self) -> Project:
        return self._project

    @property
    def cleaner_name(self) -> str:
        return self._cleaner_name
    
    @property
    def platform_target(self) -> PlatformTarget:
        return self._platform_target
    
    @property
    def config(self) -> Config:
        return self._config
    
    @property
    def compiler(self) -> Compiler:
        return self._compiler
    
    @classmethod
    def create(cls, directory: Path, project_name: str, cleaner_name: str, platform_target: PlatformTarget, config : Config, compiler : Compiler) -> Self :
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
        
        cleaner_name = cleaner_name if cleaner_name is not None else "cmake"

        return CleanContext(directory=directory, project=project_to_clean, cleaner_name=cleaner_name, platform_target=platform_target,  config=config, compiler=compiler)


    @staticmethod
    def from_cli_parser(cli_parser: cli.KissParser) -> Self:
        release :bool = getattr(cli_parser, "release", False) or False
        debug_info :bool = getattr(cli_parser, "debug_info", True) or (True if not release else False)
        config : Config = Config(release, debug_info)
        platform_target: PlatformTarget = PlatformTarget.default_target()
        compiler : Compiler = getattr(cli_parser, "compiler", None) or Compiler.default_compiler(platform_target=platform_target)
        clean_context: CleanContext = CleanContext.create(directory=cli_parser.directory,
                                                    project_name=cli_parser.project_name,
                                                    cleaner_name=cli_parser.cleaner,
                                                    platform_target=platform_target,
                                                    config=config,
                                                    compiler=compiler)
        return clean_context


def cmd_clean(clean_params:  argparse.ArgumentParser):
    clean_context = CleanContext.from_cli_parser(clean_params)
    cleaner : BaseCleaner = CleanerRegistry.cleaners.get(clean_context.cleaner_name)
    if not cleaner:
        console.print_error(f"Cleaner {clean_context.cleaner_name} not found")
        exit(1)
    cleaner.clean(clean_context)