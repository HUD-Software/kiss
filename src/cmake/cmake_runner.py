import os
from pathlib import Path
import platform
from builder import BuilderRegistry
from cli import KissParser
from cmake.cmake_builder import CMakeBuildContext, CMakeBuilder
from cmake.cmake_context import CMakeContext
import console
from process import run_process
from project import ProjectType
from run import RunContext
from runner import BaseRunner


class CMakeRunner(BaseRunner):
    @classmethod
    def add_cli_argument_to_parser(cls, parser: KissParser):
        pass 

    def __init__(self):
        super().__init__("cmake", "Run a binary build with CMake")

    def run_project(self, run_context: RunContext):
        # Ensure the the project is a binary
        if run_context.project.type != ProjectType.bin:
            console.print_error(f"Project {run_context.project.name} is not a binary project")
            exit(1)
            
        # Build the project
        cmake_builder : CMakeBuilder = BuilderRegistry.builders.get(run_context.runner_name)
        if not cmake_builder:
            console.print_error(f"Builder {cmake_builder.name} not found")
            exit(1)
        cmake_build_context = CMakeBuildContext.create(directory=run_context.directory,
                                                        project_name=run_context.project.name,
                                                        builder_name=run_context.runner_name,
                                                        toolchain=run_context.toolchain,
                                                        config=run_context.config,
                                                        generator=cmake_builder.name)
        cmake_builder.build_project(cmake_build_context)
        
        context = CMakeContext(current_directory=run_context.directory, 
                            toolchain=run_context.toolchain, 
                            project=run_context.project)
        
  
        # Add DLL path to PATH on Windows
        if run_context.toolchain.target.is_windows_os():
            project_list = context.project.topological_sort_projects()
            dll_paths = []
            for project in project_list:
                if project.type == ProjectType.dyn:
                    proj_context = CMakeContext(current_directory=run_context.directory, 
                                                toolchain=run_context.toolchain, 
                                                project=project)
                    dll_paths.append(proj_context.output_directory_for_config("debug"))  

            existing_path = os.environ.get("PATH", "")
            os.environ["PATH"] = ";".join(dll_paths + [existing_path])
            binary_path = Path(cmake_build_context.output_directory_for_config("debug")) / f"{run_context.project.name}.exe"
        else:
            binary_path = Path(cmake_build_context.output_directory_for_config("debug")) / run_context.project.name

        # Run the project
        console.print_step(f"▶ Run {binary_path.name}...")
        if not run_process(binary_path, output_prefix=False, print_command=False) == 0:
            exit(1)
            
    def run(self, run_context: RunContext):
        self.run_project(run_context=run_context)