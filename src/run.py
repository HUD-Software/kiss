import argparse
from pathlib import Path
from typing import Self
import console
from context import Context
from generator import BaseGenerator
from project import Project, ProjectType
from runner import RunnerRegistry
from toolchain import Toolchain, Compiler, Target, TargetRegistry


class RunContext(Context):
    def __init__(self, directory:Path, project: Project, runner_name: str, toolchain: Toolchain, profile: str):
        super().__init__(directory)
        self._project = project
        self._runner_name = runner_name
        self._toolchain = toolchain
        self._profile = profile

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
    def profile(self) -> str: 
        return self._profile    
    
    @classmethod
    def create(cls, directory: Path, project_name: str, runner_name: str, toolchain: Toolchain, profile: str) -> Self :
        project_to_run = super().find_target_project(directory, project_name, ProjectType.bin)
        if not project_to_run:
            console.print_error(f"No project found in {str(directory)}")
            exit(1)
        return RunContext(directory=directory, project=project_to_run, runner_name=runner_name, toolchain=toolchain, profile=profile)


    @staticmethod
    def from_cli_args(cli_args: argparse.Namespace) -> Self | None:
        target_name: Target = getattr(cli_args, "target", None) or Target.default_target_name()
        compiler_name: Compiler = getattr(cli_args, "compiler", None) or Compiler.default_compiler_name()
        if( toolchain := Toolchain.create(compiler_name=compiler_name, target_name=target_name)) is None:
            return None
        
        # Ensure we request a valid profile
        if not toolchain.is_profile_exist(cli_args.profile):
            console.print_error(f"Profile {cli_args.profile} not found in the toolchain : {{{', '.join(toolchain.profile_name_list())}}}")
            exit(1)
        
        # Ensure target exists
        if not target_name in TargetRegistry:
            console.print_error(f"Target {target_name} not found  : {{{', '.join(TargetRegistry.target_name_list())}}}")
            exit(1)
        run_context: RunContext = RunContext.create(directory=cli_args.directory,
                                                    project_name=cli_args.project_name,
                                                    runner_name=cli_args.runner,
                                                    toolchain=toolchain,
                                                    profile=cli_args.profile)
        
        

        return run_context

    

def cmd_run(cli_args: argparse.Namespace):
    if(run_context := RunContext.from_cli_args(cli_args)) is None:
        return None
    runner : BaseGenerator = RunnerRegistry.runners.get(run_context.runner_name)
    if not runner:
        console.print_error(f"Runner {run_context.runner_name} not found")
        exit(1)
    runner.run(run_context)