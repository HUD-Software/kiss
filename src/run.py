import argparse
from pathlib import Path
from typing import Self
import cli
from compiler import Compiler
from config import Config
import console
from context import Context
from generator import BaseGenerator
from platform_target import PlatformTarget
from project import Project, ProjectType
from runner import RunnerRegistry


class RunContext(Context):
    def __init__(self, directory:Path, project: Project, runner_name: str, platform_target: PlatformTarget, config : Config, compiler : Compiler):
        super().__init__(directory)
        self._project = project
        self._runner_name = runner_name
        self._platform_target = platform_target
        self._config = config
        self._compiler = compiler


    @property
    def project(self) -> Project:
        return self._project

    @property
    def runner_name(self) -> str:
        return self._runner_name
    
    @property
    def platform_target(self) -> PlatformTarget:
        return self._platform_target
    
    @property
    def config(self) -> Config:
        return self._config
    
    @property
    def compiler(self) -> Compiler:
        return self._compiler
    
    @classmethod
    def create(cls, directory: Path, project_name: str, runner_name: str, platform_target: PlatformTarget, config : Config, compiler : Compiler) -> Self :
        project_to_run = super().find_target_project(directory, project_name, ProjectType.bin)
        if not project_to_run:
            console.print_error(f"No project found in {str(directory)}")
            exit(1)
        return RunContext(directory=directory, project=project_to_run, runner_name=runner_name, platform_target=platform_target,  config=config, compiler=compiler)


    @staticmethod
    def from_cli_args(cli_args: argparse.Namespace) -> Self:
        release :bool = getattr(cli_args, "release", False) or False
        debug_info :bool = getattr(cli_args, "debug_info", True) or (True if not release else False)
        config : Config = Config(release, debug_info)
        platform_target: PlatformTarget = PlatformTarget.default_target()
        compiler : Compiler = "cl"
        run_context: RunContext = RunContext.create(directory=cli_args.directory,
                                                    project_name=cli_args.project_name,
                                                    runner_name=cli_args.runner,
                                                    platform_target=platform_target,
                                                    config=config,
                                                    compiler=compiler)
        return run_context

    

def cmd_run(cli_args: argparse.Namespace):
    run_context = RunContext.from_cli_args(cli_args)
    runner : BaseGenerator = RunnerRegistry.runners.get(run_context.runner_name)
    if not runner:
        console.print_error(f"Runner {run_context.runner_name} not found")
        exit(1)
    runner.run(run_context)