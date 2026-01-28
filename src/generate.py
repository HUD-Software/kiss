import argparse
from pathlib import Path
from typing import Self
import cli
import console
from context import Context
from generator import BaseGenerator, GeneratorRegistry
from platform_target import PlatformTarget
from project import Project

class GenerateContext(Context):
    def __init__(self, directory:Path, project: Project, generator_name: str, platform_target: PlatformTarget):
        super().__init__(directory)
        self._project = project
        self._generator_name = generator_name
        self._platform_target = platform_target

    @property
    def project(self) -> Project:
        return self._project

    @property
    def generator_name(self) -> str:
        return self._generator_name
    
    @property
    def platform_target(self) -> PlatformTarget:
        return self._platform_target

    @classmethod
    def create(cls, directory: Path, project_name: str, generator_name: str, platform_target: PlatformTarget) -> Self :
        project_to_generate = super().find_target_project(directory, project_name)
        if not project_to_generate:
            console.print_error(f"No project found in {str(directory)}")
            exit(1)
        generator_name = generator_name if generator_name is not None else "cmake"
        return cls(directory=directory, project=project_to_generate, generator_name=generator_name, platform_target=platform_target)


    @classmethod
    def from_cli_args(cls, cli_args: argparse.Namespace) -> Self:
        return cls.create(directory=cli_args.directory,
                          project_name=cli_args.project_name,
                          generator_name=cli_args.generator_name,
                          platform_target=cli_args.platform_target)
       

def cmd_generate(cli_args: argparse.Namespace):
    generator : BaseGenerator = GeneratorRegistry.generators.get(cli_args.generator)
    if not generator:
        console.print_error(f"Generator {cli_args.generator} not found")
        exit(1)
    generator.generate(cli_args)