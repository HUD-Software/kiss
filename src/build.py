import argparse
from pathlib import Path
from typing import Self
from builder import BaseBuilder, BuilderRegistry
from config import Config
import console
from context import Context
from project import Project
from toolchain import Toolchain, Compiler, Target

class BuildContext(Context):
    def __init__(self, directory:Path, project: Project, builder_name: str, toolchain: Toolchain, config : Config):
        super().__init__(directory)
        self._project = project
        self._builder_name = builder_name
        self._toolchain = toolchain
        self._config = config

    @property
    def project(self) -> Project:
        return self._project

    @property
    def builder_name(self) -> str:
        return self._builder_name
    
    @property
    def toolchain(self) -> Toolchain:
        return self._toolchain

    @property
    def config(self) -> Config:
        return self._config

    @classmethod
    def create(cls, directory: Path, project_name: str, builder_name: str, toolchain: Toolchain, config : Config) -> Self :
        project_to_build = super().find_target_project(directory, project_name)
        if not project_to_build:
            console.print_error(f"No project'found in {str(directory)}")
            exit(1)
        return BuildContext(directory=directory, 
                            project=project_to_build, 
                            builder_name=builder_name, 
                            toolchain=toolchain, 
                            config=config)


    @staticmethod
    def from_cli_args(cli_args: argparse.Namespace) -> Self | None:
        release :bool = getattr(cli_args, "release", False) or False
        debug_info :bool = getattr(cli_args, "debug_info", True) or (True if not release else False)
        config : Config = Config(release, debug_info)
        target_name :Target = Target.default_target_name()
        compiler_name : Compiler = getattr(cli_args, "compiler", None) or Toolchain.default_compiler_name()
        if( toolchain := Toolchain.create(compiler_name==compiler_name, target_name==target_name)) is None:
            return None
        build_context =  BuildContext.create(directory=cli_args.directory,
                                             project_name=cli_args.project_name,
                                             builder_name=cli_args.builder,
                                             toolchain=toolchain,
                                             config=config)

        return build_context

def cmd_build(cli_args: argparse.Namespace):
    builder : BaseBuilder = BuilderRegistry.builders.get(cli_args.builder)
    if not builder:
        console.print_error(f"Builder {cli_args.builder} not found")
        exit(1)
    builder.build(cli_args)