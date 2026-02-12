import argparse
from pathlib import Path
from typing import Self
import console
from context import Context
from generator import BaseGenerator, GeneratorRegistry
from project import Project
from toolchain import Toolchain, Target, Compiler

class GenerateContext(Context):
    def __init__(self, directory:Path, project: Project, generator_name: str, toolchain: Toolchain, profile: str):
        super().__init__(directory)
        self._project = project
        self._generator_name = generator_name
        self._toolchain = toolchain
        self._profile = profile
    
    @property
    def project(self) -> Project:
        return self._project

    @property
    def profile(self) -> str:
        return self._profile

    @property
    def generator_name(self) -> str:
        return self._generator_name
    
    @property
    def toolchain(self) -> Toolchain:
        return self._toolchain

    @classmethod
    def create(cls, directory: Path, project_name: str, generator_name: str, toolchain: Toolchain, profile: str) -> Self :
        project_to_generate = super().find_target_project(directory, project_name)
        if not project_to_generate:
            console.print_error(f"No project found in {str(directory)}")
            exit(1)
        generator_name = generator_name if generator_name is not None else "cmake"
        return cls(directory=directory, project=project_to_generate, generator_name=generator_name, toolchain=toolchain, profile=profile)


    @classmethod
    def from_cli_args(cls, cli_args: argparse.Namespace) -> Self | None:
        target_name :Target = getattr(cli_args, "target", None) or Target.default_target_name()
        compiler_name : Compiler = getattr(cli_args, "compiler", None) or Compiler.default_compiler_name()
        if( toolchain := Toolchain.create(compiler_name=compiler_name, target_name=target_name)) is None:
            return None
        return cls.create(directory=cli_args.directory,
                          project_name=cli_args.project_name,
                          generator_name=cli_args.generator_name,
                          toolchain=toolchain,
                          profile=cli_args.profile)
       

def cmd_generate(cli_args: argparse.Namespace):
    generator : BaseGenerator = GeneratorRegistry.generators.get(cli_args.generator)
    if not generator:
        console.print_error(f"Generator {cli_args.generator} not found")
        exit(1)
    generator.generate(cli_args)