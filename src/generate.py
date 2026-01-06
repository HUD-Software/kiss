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
    def from_cli_parser(cls, cli_parser: cli.KissParser) -> Self:
        return cls.create(directory=cli_parser.directory,
                          project_name=cli_parser.project_name,
                          generator_name=cli_parser.generator,
                          platform_target=PlatformTarget.default_target())
       
    
  
def cmd_generate(generate_params:  argparse.ArgumentParser):
    generate_context = GenerateContext.from_cli_parser(generate_params)
    generator : BaseGenerator = GeneratorRegistry.generators.get(generate_context.generator_name)
    if not generator:
        console.print_error(f"Generator {generate_context.generator_name} not found")
        exit(1)
    generator.generate(generate_context)