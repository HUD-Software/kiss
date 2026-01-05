
import argparse
from pathlib import Path
from typing import Self
import cli
import console
from context import Context
from generator import BaseGenerator, GeneratorRegistry
from platform_target import PlatformTarget
from project import Project
from projectregistry import ProjectRegistry


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
    def from_cli_parser(cls, cli_parser: cli.KissParser) -> Self:
        #### Find the project to generate
        ProjectRegistry.load_and_register_all_project_in_directory(directory=cli_parser.directory, load_dependencies=True, recursive=False)
        project_to_generate = None
        projects_in_directory = ProjectRegistry.projects_in_directory(directory=cli_parser.directory)
        if len(projects_in_directory) == 0:
            console.print_error(f"No project found in {str(cli_parser.directory)}")
            exit(1)

        # If user provide a project name find it
        if cli_parser.project_name:
            for project in projects_in_directory:
                if project.name == cli_parser.project_name:
                    project_to_generate = project
                    break
        # If the user dont provide a project name, find the default project
        else:
            if len(projects_in_directory) > 1:
                console.print_error(f"Multiple project found in {str(cli_parser.directory)}")
                projects_in_directory_names = [project.name for project in projects_in_directory]
                for name in projects_in_directory_names:
                    console.print_error(f"  - {name}")
                choices = " | ".join(projects_in_directory_names)
                console.print_error(f"Unable to select a default project. You must provide a project with --project [{choices}]")
                exit(1)
            else:
                project_to_generate = projects_in_directory[0]
                
        if not project_to_generate:
            console.print_error(f"No project found in {str(cli_parser.directory)}")
            exit(1)

        #### Select generator to use
        generator_name = cli_parser.generator if cli_parser.generator is not None else "cmake"

        #### Select the platform target to use
        platform_target = PlatformTarget.default_target()

        return cls(directory=cli_parser.directory, project=project_to_generate, generator_name=generator_name, platform_target=platform_target)


def cmd_generate(generate_params:  argparse.ArgumentParser):
    generate_context = GenerateContext.from_cli_parser(generate_params)
    generator : BaseGenerator = GeneratorRegistry.generators.get(generate_context.generator_name)
    if not generator:
        console.print_error(f"Generator {generate_context.generator_name} not found")
        exit(1)
    generator.generate(generate_context)

    # console.print_step("Generating build scripts...")
    # ModuleRegistry.load_modules(generate_params.project_directory)
    # project = ModuleRegistry.get(generate_params.project_name)
    # if not project:
    #     console.print_error(f"Aucun projet trouvé dans le dossier {generate_params.project_directory}")
    #     sys.exit(2)
    
    # generate_params.generator.generate(generate_params, project)        