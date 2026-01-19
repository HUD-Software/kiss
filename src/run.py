import argparse
from pathlib import Path
from typing import Self
import cli
import console
from context import Context
from generator import BaseGenerator
from platform_target import PlatformTarget
from project import Project, ProjectType
from runner import RunnerRegistry


class RunContext(Context):
    def __init__(self, directory:Path, project: Project, runner_name: str, platform_target: PlatformTarget):
        super().__init__(directory)
        self._project = project
        self._runner_name = runner_name
        self._platform_target = platform_target

    @property
    def project(self) -> Project:
        return self._project

    @property
    def runner_name(self) -> str:
        return self._runner_name
    
    @property
    def platform_target(self) -> PlatformTarget:
        return self._platform_target

    @classmethod
    def create(cls, directory: Path, project_name: str, runner_name: str, platform_target: PlatformTarget) -> Self :
        project_to_run = super().find_target_project(directory, project_name, ProjectType.bin)
        if not project_to_run:
            console.print_error(f"No project found in {str(directory)}")
            exit(1)
        runner_name = runner_name if runner_name is not None else "cmake"
        return cls(directory=directory, project=project_to_run, runner_name=runner_name, platform_target=platform_target)


    @classmethod
    def from_cli_parser(cls, cli_parser: cli.KissParser) -> Self:
        return cls.create(directory=cli_parser.directory,
                          project_name=cli_parser.project_name,
                          runner_name=cli_parser.runner,
                          platform_target=PlatformTarget.default_target())
    

def cmd_run(run_params:  argparse.ArgumentParser):
    run_context = RunContext.from_cli_parser(run_params)
    runner : BaseGenerator = RunnerRegistry.runners.get(run_context.runner_name)
    if not runner:
        console.print_error(f"Runner {run_context.runner_name} not found")
        exit(1)
    runner.run(run_context)