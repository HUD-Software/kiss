import argparse
from pathlib import Path
from typing import Self
from builder import BaseBuilder, BuilderRegistry
import console
from context import Context
from project import Project
from toolchain import Toolchain, Compiler, Target

class BuildContext(Context):
    def __init__(self, directory:Path, project: Project, builder_name: str, toolchain: Toolchain, profile: str):
        super().__init__(directory)
        self._project = project
        self._builder_name = builder_name
        self._toolchain = toolchain
        self._profile = profile
        
    @property
    def project(self) -> Project:
        return self._project

    @property
    def profile(self) -> str:
        return self._profile

    @property
    def builder_name(self) -> str:
        return self._builder_name
    
    @property
    def toolchain(self) -> Toolchain:
        return self._toolchain

    @classmethod
    def create(cls, directory: Path, project_name: str, builder_name: str, toolchain: Toolchain, profile: str) -> Self :
        project_to_build = super().find_target_project(directory, project_name)
        if not project_to_build:
            console.print_error(f"No project '{project_name}' found in {str(directory)}")
            exit(1)
        return BuildContext(directory=directory, 
                            project=project_to_build, 
                            builder_name=builder_name, 
                            toolchain=toolchain,
                            profile=profile)


    @staticmethod
    def from_cli_args(cli_args: argparse.Namespace) -> Self | None:
        target_name :Target = getattr(cli_args, "target", None) or Target.default_target_name()
        compiler_name : Compiler = getattr(cli_args, "compiler", None) or Compiler.default_compiler_name()
        if( toolchain := Toolchain.create(compiler_name=compiler_name, target_name=target_name)) is None:
            return None
        
        # Ensure we request a valid profile
        if not toolchain.is_profile_exist(cli_args.profile):
            console.print_error(f"Profile {cli_args.profile} not found in the toolchain : {{{', '.join(toolchain.profile_name_list())}}}")
            exit(1)
            
        build_context =  BuildContext.create(directory=cli_args.directory,
                                             project_name=cli_args.project_name,
                                             builder_name=cli_args.builder,
                                             toolchain=toolchain,
                                             profile=cli_args.profile)
        
        return build_context

def cmd_build(cli_args: argparse.Namespace):
    builder : BaseBuilder = BuilderRegistry.builders.get(cli_args.builder)
    if not builder:
        console.print_error(f"Builder {cli_args.builder} not found")
        exit(1)
    builder.build(cli_args)