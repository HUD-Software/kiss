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
        runner_name = runner_name if runner_name is not None else "cmake"
        return RunContext(directory=directory, project=project_to_run, runner_name=runner_name, platform_target=platform_target,  config=config, compiler=compiler)


    @staticmethod
    def from_cli_parser(cli_parser: cli.KissParser) -> Self:
        release :bool = getattr(cli_parser, "release", False) or False
        debug_info :bool = getattr(cli_parser, "debug_info", True) or (True if not release else False)
        config : Config = Config(release, debug_info)
        platform_target: PlatformTarget = PlatformTarget.default_target()
        compiler : Compiler = getattr(cli_parser, "compiler", None) or Compiler.default_compiler(platform_target=platform_target)
        run_context: RunContext = RunContext.create(directory=cli_parser.directory,
                                                    project_name=cli_parser.project_name,
                                                    runner_name=cli_parser.runner,
                                                    platform_target=platform_target,
                                                    config=config,
                                                    compiler=compiler)
        return run_context

    

def cmd_run(run_params:  argparse.ArgumentParser):
    run_context = RunContext.from_cli_parser(run_params)
    runner : BaseGenerator = RunnerRegistry.runners.get(run_context.runner_name)
    if not runner:
        console.print_error(f"Runner {run_context.runner_name} not found")
        exit(1)
    runner.run(run_context)