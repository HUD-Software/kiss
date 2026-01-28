import argparse
from pathlib import Path
from typing import Self
from builder import BaseBuilder, BuilderRegistry
import cli
from compiler import Compiler
from config import Config
import console
from context import Context
from platform_target import PlatformTarget
from project import Project

class BuildContext(Context):
    def __init__(self, directory:Path, project: Project, builder_name: str, platform_target: PlatformTarget, config : Config, compiler : Compiler):
        super().__init__(directory)
        self._project = project
        self._builder_name = builder_name
        self._platform_target = platform_target
        self._config = config
        self._compiler = compiler

    @property
    def project(self) -> Project:
        return self._project

    @property
    def builder_name(self) -> str:
        return self._builder_name
    
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
    def create(cls, directory: Path, project_name: str, builder_name: str, platform_target: PlatformTarget, config : Config, compiler : Compiler) -> Self :
        project_to_build = super().find_target_project(directory, project_name)
        if not project_to_build:
            console.print_error(f"No project'found in {str(directory)}")
            exit(1)
        return BuildContext(directory=directory, project=project_to_build, builder_name=builder_name, platform_target=platform_target, config=config, compiler=compiler)


    @staticmethod
    def from_cli_args(cli_args: argparse.Namespace) -> Self:
        release :bool = getattr(cli_args, "release", False) or False
        debug_info :bool = getattr(cli_args, "debug_info", True) or (True if not release else False)
        config : Config = Config(release, debug_info)
        platform_target: PlatformTarget = PlatformTarget.default_target()
        compiler : Compiler = getattr(cli_args, "compiler", None) or Compiler.default_compiler(platform_target=platform_target)
        build_context =  BuildContext.create(directory=cli_args.directory,
                                                    project_name=cli_args.project_name,
                                                    builder_name=cli_args.builder,
                                                    platform_target=platform_target,
                                                    config=config,
                                                    compiler=compiler)

        return build_context

def cmd_build(cli_args: argparse.Namespace):
    builder : BaseBuilder = BuilderRegistry.builders.get(cli_args.builder)
    if not builder:
        console.print_error(f"Builder {cli_args.builder} not found")
        exit(1)
    builder.build(cli_args)