import os
from build import BuildContext
from builder import BuilderRegistry
from cli import KissParser
from cmake.builder_cmake import BuilderCMake
from cmake.cmake_context import CMakeContext
from config import Config
import console
from process import run_process
from run import RunContext
from runner import BaseRunner


class RunnerCMake(BaseRunner):
    @classmethod
    def add_cli_argument_to_parser(cls, parser: KissParser):
        pass

    def __init__(self, parser: KissParser = None):
        super().__init__("cmake", "Run a binary build with CMake")

    def run_project(self, run_context: RunContext):
        # Build the project
        cmake_builder : BuilderCMake = BuilderRegistry.builders.get(run_context.runner_name)
        if not cmake_builder:
            console.print_error(f"Builder {cmake_builder.name} not found")
            exit(1)

        cmake_builder.build(BuildContext.create(directory=run_context.directory,
                                                            project_name=run_context.project.name,
                                                            builder_name=run_context.runner_name,
                                                            platform_target=run_context.platform_target,
                                                            config=run_context.config,
                                                            compiler=run_context.compiler))
        
        context = CMakeContext(current_directory=run_context.directory, 
                            platform_target=run_context.platform_target, 
                            project=run_context.project)
        
        # Add DLL path to PATH on Windows
        if run_context.platform_target.is_windows():
            project_list = context.project.topological_sort_projects()
            dll_paths = []
            for proj_context in project_list:
                proj_context = CMakeContext(current_directory=run_context.directory, 
                                            platform_target=run_context.platform_target, 
                                            project=proj_context)
                dll_paths.append(str(proj_context.output_directory(run_context.config).resolve()))  

            existing_path = os.environ.get("PATH", "")
            os.environ["PATH"] = ";".join(dll_paths + [existing_path])
        
        # Get binary path
        if context.platform_target.is_windows():
            binary_path = context.output_directory(run_context.config) / f"{run_context.project.name}.exe"
        else:
            binary_path = context.output_directory(run_context.config) / run_context.project.name

        # Run the project
        console.print_step(f"▶ Run {binary_path.name}...")
        if not run_process(binary_path, output_prefix=False, print_command=False) == 0:
            exit(1)
            
    def run(self, run_context: RunContext):
        self.run_project(run_context=run_context)