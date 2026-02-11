import argparse
from pathlib import Path
from typing import Self
from config import Config
import console
from context import Context
from generator import BaseGenerator
from project import Project, ProjectType
from runner import RunnerRegistry
from toolchain import Toolchain, Compiler, Target


class RunContext(Context):
    def __init__(self, directory:Path, project: Project, runner_name: str, toolchain: Toolchain, config : Config):
        super().__init__(directory)
        self._project = project
        self._runner_name = runner_name
        self._toolchain = toolchain
        self._config = config


    @property
    def project(self) -> Project:
        return self._project

    @property
    def runner_name(self) -> str:
        return self._runner_name
    
    @property
    def toolchain(self) -> Toolchain:
        return self._toolchain
    
    @property
    def config(self) -> Config:
        return self._config
    
    @classmethod
    def create(cls, directory: Path, project_name: str, runner_name: str, toolchain: Toolchain, config : Config) -> Self :
        project_to_run = super().find_target_project(directory, project_name, ProjectType.bin)
        if not project_to_run:
            console.print_error(f"No project found in {str(directory)}")
            exit(1)
        return RunContext(directory=directory, project=project_to_run, runner_name=runner_name, toolchain=toolchain, config=config)


    @staticmethod
    def from_cli_args(cli_args: argparse.Namespace) -> Self | None:
        release :bool = getattr(cli_args, "release", False) or False
        debug_info :bool = getattr(cli_args, "debug_info", True) or (True if not release else False)
        config : Config = Config(release, debug_info)
        target_name :Target = Target.default_target_name()
        compiler_name : Compiler = getattr(cli_args, "compiler", None) or Toolchain.default_compiler_name()
        if( toolchain := Toolchain.create(compiler_name=compiler_name, target_name=target_name)) is None:
            return None
        run_context: RunContext = RunContext.create(directory=cli_args.directory,
                                                    project_name=cli_args.project_name,
                                                    runner_name=cli_args.runner,
                                                    toolchain=toolchain,
                                                    config=config)
        return run_context

    

def cmd_run(cli_args: argparse.Namespace):
    if(run_context := RunContext.from_cli_args(cli_args)) is None:
        return None
    runner : BaseGenerator = RunnerRegistry.runners.get(run_context.runner_name)
    if not runner:
        console.print_error(f"Runner {run_context.runner_name} not found")
        exit(1)
    runner.run(run_context)