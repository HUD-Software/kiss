import argparse
import os
from pathlib import Path
from typing import Self
from build import BuildContext
from builder import BaseBuilder
from cli import KissParser
from cmake.cmake_context import CMakeContext
from cmake.cmake_generators import CMakeGenerator
from cmake.cmakelists_generator import CMakeListsGenerator
from compiler import Compiler
from config import Config
import console
from generate import GenerateContext
from generator import GeneratorRegistry
from platform_target import PlatformTarget
from process import run_process
from project import Project
from visual_studio import get_windows_latest_toolset

class CMakeBuildContext(BuildContext):
    def __init__(self, directory:Path, project: Project, builder_name: str, platform_target: PlatformTarget, config : Config, compiler : Compiler, generator: CMakeGenerator):
        super().__init__(directory, project, builder_name, platform_target, config, compiler)
        self._generator = generator

    @property
    def generator(self) -> CMakeGenerator:
        return self._generator
    
    @classmethod
    def create(cls, directory: Path, project_name: str, builder_name: str, platform_target: PlatformTarget, config : Config, compiler : Compiler, generator: CMakeGenerator) -> Self :
        project_to_build = super().find_target_project(directory, project_name)
        if not project_to_build:
            console.print_error(f"No project found in {str(directory)}")
            exit(1)
        return CMakeBuildContext(directory=directory, project=project_to_build, builder_name=builder_name, platform_target=platform_target, config=config, compiler=compiler, generator=generator)


    @staticmethod
    def from_cli_args(cli_args: argparse.Namespace) -> Self:
        build_context = BuildContext.from_cli_args(cli_args)
        generator : CMakeGenerator = getattr(cli_args, "generator", None)
        return CMakeBuildContext(directory=build_context.directory,
                                 project=build_context.project,
                                 builder_name=build_context.builder_name,
                                 platform_target=build_context.platform_target,
                                 config=build_context.config,
                                 compiler=build_context.compiler,
                                 generator=generator)

    
class CMakeBuilder(BaseBuilder):
    @classmethod
    def add_cli_argument_to_parser(cls, parser: KissParser):
        def generator_help_string() -> str:
            lines = []
            for target in PlatformTarget:
                generator_str_list = ", ".join(CMakeGenerator.available_generator_for_platform_target(target))
                lines.append(f" - {target.name} -> {{{generator_str_list}}}")
            return "\n".join(lines)
        parser.formatter_class=argparse.RawTextHelpFormatter
        parser.add_argument("-g", "--generator",
                            type=CMakeGenerator,
                            choices=list(CMakeGenerator),
                            default=CMakeGenerator.VisualStudio,
                            help="Choose CMake generator based on platform:\n" + generator_help_string())
           
    def __init__(self):
        super().__init__("cmake", "Build cmake CMakeLists.txt")
    
    def build_project(self, cmake_build_context: CMakeBuildContext):
        # Generate the project
        cmake_generator : CMakeListsGenerator = GeneratorRegistry.generators.get(cmake_build_context.builder_name)
        if not cmake_generator:
            console.print_error(f"Generator {cmake_generator.name} not found")
            exit(1)
        generated_context_list = cmake_generator.generate(GenerateContext.create(directory=cmake_build_context.directory,
                                                            project_name=cmake_build_context.project.name,
                                                            generator_name=cmake_build_context.builder_name,
                                                            platform_target=cmake_build_context.platform_target))
       
        # Get CMake Generator
        context = CMakeContext(current_directory=cmake_build_context.directory, 
                               platform_target=cmake_build_context.platform_target, 
                               project=cmake_build_context.project)
        configure_args = None
        # match self.generator:
        #     case CMakeGenerator.VisualStudio:

        match context.platform_target:
            case PlatformTarget.x86_64_pc_windows_msvc:
                toolset = get_windows_latest_toolset(cmake_build_context.compiler)
                year = toolset.product_year
                if toolset.major_version == 18:
                    year = 2026
                if not year:
                    year = int(toolset.product_line_version)
                cmake_generator_name = f"{toolset.product_name} {toolset.major_version} {year}"
                configure_args = ["--no-warn-unused-cli", "-S", str(context.cmakelists_directory), "-G", cmake_generator_name, "-T", "host=x64", "-A", "x64"]
            case PlatformTarget.x86_64_unknown_linux_gnu:
                cmake_generator_name = "Unix Makefiles"
                cmake_generator_c_arch = "-DCMAKE_C_FLAGS=\"-m64\""
                cmake_generator_cxx_arch = "-DCMAKE_CXX_FLAGS=\"-m64\""
                cmake_generator_c_compiler = "-DCMAKE_C_COMPILER=gcc"
                cmake_generator_cxx_compiler = "-DCMAKE_C_COMPILER=g++"
                configure_args = ["--no-warn-unused-cli", "-S", str(context.cmakelists_directory), "-G", cmake_generator_name, cmake_generator_c_compiler, cmake_generator_cxx_compiler, cmake_generator_c_arch, cmake_generator_cxx_arch]
            case _ : 
                console.print_error(f"Unknown target {context.platform_target}")
                exit(1)
        

        os.makedirs(context.build_directory, exist_ok=True)
        if generated_context_list or not context.cmakecache.exists():
            console.print_step(f"🛠️  CMake configure with {cmake_generator_name}")
            if not run_process("cmake", configure_args, context.build_directory) == 0:
                exit(1)
        else:            
            console.print_step(f"✔️  No CMake configure required") 

        # Build
        console.print_step("🏗️  CMake build...")
        cmake_config = "Debug"
        if cmake_build_context.config.is_release:
            if cmake_build_context.config.is_debug_info:
                cmake_config = "RelWithDebInfo"
            else:
                cmake_config = "Release"

        args = ["--build", ".", "--config", cmake_config]
        if not run_process("cmake", args, context.build_directory) == 0:
            exit(1)

        # Install
        # console.print_step("🏗️  CMake install...")
        # args = ["--install", ".", "--config", cmake_config, "--prefix", context.install_directory]
        # if not run_process("cmake", args, context.build_directory) == 0:
        #     exit(1)

    def build(self, cli_args: argparse.Namespace):
        cmake_build_context = CMakeBuildContext.from_cli_args(cli_args)
        self.build_project(cmake_build_context=cmake_build_context)