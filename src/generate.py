import argparse
from pathlib import Path
from typing import Optional, Self
import console
from context import KissBaseContext
from generator import BaseGenerator, GeneratorRegistry
from project import Project
from toolchain import Toolchain, Target, Compiler, TargetRegistry

class KissGenerateContext(KissBaseContext):
    def __init__(self, current_directory:Path, project: Project, generator_name: str, toolchain: Toolchain):
        super().__init__(current_directory)
        self._project = project
        self._generator_name = generator_name
        self._toolchain = toolchain
    
    @property
    def project(self) -> Project:
        return self._project

    @property
    def generator_name(self) -> str:
        return self._generator_name
    
    @property
    def toolchain(self) -> Toolchain:
        return self._toolchain

    @classmethod
    def create(cls, current_directory: Path, project_name: str, generator_name: str, toolchain: Toolchain) -> Optional[Self] :
        project_to_generate = super().find_target_project(current_directory, project_name)
        if not project_to_generate:
            return None
        generator_name = generator_name if generator_name is not None else "cmake"
        return KissGenerateContext(current_directory=current_directory,
                                   project=project_to_generate,
                                   generator_name=generator_name,
                                   toolchain=toolchain)


    @staticmethod
    def from_cli_args(cli_args: argparse.Namespace) -> Optional[Self]:
        target_name: Target = getattr(cli_args, "target", None) or Target.default_target_name()
        compiler_name: Compiler = getattr(cli_args, "compiler", None) or Compiler.default_compiler_name()
        if( toolchain := Toolchain.create(compiler_name=compiler_name, 
                                          target_name=target_name, 
                                          profile_name=cli_args.profile)) is None:
            return None
            
        return KissGenerateContext.create(current_directory=cli_args.directory,
                          project_name=cli_args.project_name,
                          generator_name=cli_args.generator_name,
                          toolchain=toolchain)
       

def cmd_generate(cli_args: argparse.Namespace) -> bool:
    generator : BaseGenerator = GeneratorRegistry.generators.get(cli_args.generator)
    if not generator:
        console.print_error(f"Generator {cli_args.generator} not found")
        return False
    
    if(kiss_generate_context := KissGenerateContext.from_cli_args(cli_args=cli_args)) is None:
        return None
    
    console.print_step(f"Generating '{kiss_generate_context.project.name}' with \n"
                       f" - Builder : {generator.name}\n"
                       f" - Profile : {kiss_generate_context.toolchain.profile.name}\n"
                       f" - Target : {kiss_generate_context.toolchain.target.name}\n"
                       f" - Compiler : {kiss_generate_context.toolchain.compiler.name}")
    
    is_generate_success = generator.generate(kiss_generate_context=kiss_generate_context, 
                                             cli_args=cli_args)

    if is_generate_success:
        console.print_success(f"'{kiss_generate_context.project.name}' build successfully") 
    else:
        console.print_error(f"'{kiss_generate_context.project.name}' build error") 
    return is_generate_success
