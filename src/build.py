import argparse
from pathlib import Path
from typing import Self
from builder import BaseBuilder, BuilderRegistry
import cli
import console
from context import Context
from platform_target import PlatformTarget
from project import Project

class BuildContext(Context):
    def __init__(self, directory:Path, project: Project, builder_name: str, platform_target: PlatformTarget):
        super().__init__(directory)
        self._project = project
        self._builder_name = builder_name
        self._platform_target = platform_target

    @property
    def project(self) -> Project:
        return self._project

    @property
    def builder_name(self) -> str:
        return self._builder_name
    
    @property
    def platform_target(self) -> PlatformTarget:
        return self._platform_target

    @classmethod
    def create(cls, directory: Path, project_name: str, builder_name: str, platform_target: PlatformTarget) -> Self :
        project_to_build = super().find_target_project(directory, project_name)
        if not project_to_build:
            console.print_error(f"No project found in {str(directory)}")
            exit(1)
        builder_name = builder_name if builder_name is not None else "cmake"
        return cls(directory=directory, project=project_to_build, builder_name=builder_name, platform_target=platform_target)


    @classmethod
    def from_cli_parser(cls, cli_parser: cli.KissParser) -> Self:
        return cls.create(directory=cli_parser.directory,
                          project_name=cli_parser.project_name,
                          builder_name=cli_parser.builder,
                          platform_target=PlatformTarget.default_target())

def cmd_build(build_params:  argparse.ArgumentParser):
    build_context = BuildContext.from_cli_parser(build_params)
    builder : BaseBuilder = BuilderRegistry.builders.get(build_context.builder_name)
    if not builder:
        console.print_error(f"Builder {build_context.builder_name} not found")
        exit(1)
    builder.build(build_context)