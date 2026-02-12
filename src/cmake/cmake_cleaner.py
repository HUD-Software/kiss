import argparse
from pathlib import Path
from typing import Self
from clean import CleanContext
from cleaner import BaseCleaner
from cli import KissParser
from cmake.cmake_context import CMakeContext
from cmake.cmake_generators import CMakeGenerator
from config import Config
import console
from project import Project
from toolchain.toolchain import Toolchain

class CMakeCleanContext(CleanContext):
    def __init__(self, directory:Path, project: Project, builder_name: str, toolchain: Toolchain, config : Config, generator: CMakeGenerator):
        super().__init__(directory, project, builder_name, toolchain, config)
        self._generator = generator

    @property
    def generator(self) -> CMakeGenerator:
        return self._generator
    
    @classmethod
    def create(cls, directory: Path, project_name: str, builder_name: str, toolchain: Toolchain, config : Config, generator: CMakeGenerator) -> Self :
        project_to_build = super().find_target_project(directory, project_name)
        if not project_to_build:
            console.print_error(f"No project found in {str(directory)}")
            exit(1)
        return CMakeCleanContext(directory=directory, project=project_to_build, builder_name=builder_name, toolchain=toolchain, config=config, generator=generator)


    @staticmethod
    def from_cli_args(cli_args: argparse.Namespace) -> Self:
        clean_context = CleanContext.from_cli_args(cli_args)
        return CMakeCleanContext(directory=clean_context.directory,
                                 project=clean_context.project,
                                 builder_name=clean_context.builder_name,
                                 toolchain=clean_context.toolchain,
                                 config=clean_context.config,
                                 generator=cli_args.generator)

class CMakeCleaner(BaseCleaner):
    @classmethod
    def add_cli_argument_to_parser(cls, parser: KissParser):
        pass

    def __init__(self):
        super().__init__("cmake", "Clean cmake CMakeLists.txt")

    def clean_project(self, clean_context: CleanContext):
        # If the user specifyed a project, clean only that project
        if clean_context.project :
            # Clean the project
            context = CMakeContext(current_directory=clean_context.directory, 
                                toolchain=clean_context.toolchain, 
                                project=clean_context.project)
            
            # Delete build directory
            if context.build_directory.exists():
                console.print_step(f"Removing build directory: {str(context.build_directory)}")
                import shutil
                shutil.rmtree(context.build_directory)

            # Delete output directory
            if context.output_directory(clean_context.config).exists():
                console.print_step(f"Removing output directory: {str(context.output_directory(clean_context.config))}")
                import shutil
                shutil.rmtree(context.output_directory(clean_context.config))

            # Delete CMakeLists.txt file
            if context.cmakefile.exists():
                console.print_step(f"Removing CMakeLists.txt: {str(context.cmakefile)}")
                context.cmakefile.unlink()

            # If the directory is empty, remove it
            if context.build_directory.parent.exists() and len(list(context.build_directory.parent.iterdir())) == 0:
                console.print_step(f"Removing empty build parent directory: {str(context.build_directory.parent)}")
                context.build_directory.parent.rmdir()

        # Else, clean the whole build directory
        else:
            if CMakeContext.resolveRootBuildDirectory(current_directory=clean_context.directory).exists():
                console.print_step(f"Removing build directory: {str(CMakeContext.resolveRootBuildDirectory(clean_context.directory))}")
                import shutil
                shutil.rmtree(CMakeContext.resolveRootBuildDirectory(clean_context.directory))
            
            
    def clean(self, clean_context: CleanContext):
        self.clean_project(clean_context=clean_context)