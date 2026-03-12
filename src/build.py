import argparse
from pathlib import Path
from typing import Optional, Self
from builder import BaseBuilder, BuilderRegistry
import console
from context import KissBaseContext
from project import Project
from toolchain import Toolchain, Compiler, Target, TargetRegistry

class KissBuildContext(KissBaseContext):
    def __init__(self, current_directory:Path, project: Project, builder_name: str, toolchain: Toolchain, profile_name: str):
        super().__init__(current_directory)
        self._project = project
        self._builder_name = builder_name
        self._toolchain = toolchain
        self._profile_name = profile_name
        
    @property
    def project(self) -> Project:
        return self._project

    @property
    def profile_name(self) -> str:
        return self._profile_name

    @property
    def builder_name(self) -> str:
        return self._builder_name
    
    @property
    def toolchain(self) -> Toolchain:
        return self._toolchain

    @classmethod
    def create(cls, current_directory: Path, project_name: str, builder_name: str, toolchain: Toolchain, profile_name: str) -> Optional[Self] :
        project_to_build = super().find_target_project(current_directory, project_name)
        if not project_to_build:
            console.print_error(f"No project '{project_name}' found in {str(current_directory)}")
            return None
        return KissBuildContext(current_directory=current_directory, 
                            project=project_to_build, 
                            builder_name=builder_name, 
                            toolchain=toolchain,
                            profile_name=profile_name)


    @staticmethod
    def from_cli_args(cli_args: argparse.Namespace) -> Optional[Self]:
        target_name :Target = getattr(cli_args, "target", None) or Target.default_target_name()
        compiler_name : Compiler = getattr(cli_args, "compiler", None) or Compiler.default_compiler_name()
        if( toolchain := Toolchain.create(compiler_name=compiler_name, target_name=target_name)) is None:
            return None
        
        # Ensure we request a valid profile
        if not toolchain.is_profile_exist(cli_args.profile):
            console.print_error(f"Profile {cli_args.profile} not found in the toolchain : {{{', '.join(toolchain.profile_name_list())}}}")
            return None
        
        # Ensure target exists
        if not target_name in TargetRegistry:
            console.print_error(f"Target {target_name} not found  : {{{', '.join(TargetRegistry.target_name_list())}}}")
            return None
            
        return KissBuildContext.create(current_directory=cli_args.directory,
                                        project_name=cli_args.project_name,
                                        builder_name=cli_args.builder,
                                        toolchain=toolchain,
                                        profile_name=cli_args.profile)

def cmd_build(cli_args: argparse.Namespace) -> bool:
    if( builder := BuilderRegistry.builders.get(cli_args.builder)) is None:
        console.print_error(f"Builder {cli_args.builder} not found")
        return False
    
    if(kiss_build_context := KissBuildContext.from_cli_args(cli_args=cli_args)) is None:
        return None
    
    console.print_step(f"Building '{kiss_build_context.project.name}' with \n"
                       f" - Builder : {builder.name}\n"
                       f" - Profile : {kiss_build_context.profile_name}\n"
                       f" - Target : {kiss_build_context.toolchain.target.name}\n"
                       f" - Compiler : {kiss_build_context.toolchain.compiler.name}")

    return builder.build(kiss_build_context=kiss_build_context, 
                         cli_args=cli_args) 