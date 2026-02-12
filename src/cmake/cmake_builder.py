import argparse
from multiprocessing import context
import os
from pathlib import Path
from typing import Self
from build import BuildContext
from builder import BaseBuilder
from cli import KissParser
from cmake.cmake_context import CMakeContext
from cmake.cmake_generators import CMakeGenerator
from cmake.cmakelists_generator import CMakeListsGenerateContext, CMakeListsGenerator
from config import Config
import console
from generator import GeneratorRegistry
from process import run_process
from project import Project
from toolchain import Toolchain


class CMakeBuildContext(BuildContext):
    def __init__(self, directory:Path, project: Project, builder_name: str, toolchain: Toolchain, config : Config, generator: CMakeGenerator):
        super().__init__(directory, project, builder_name, toolchain, config)
        self._generator = generator
        self._cmakelist_generate_context = CMakeListsGenerateContext.create( directory=directory,
                                                                            project_name=project.name,
                                                                            generator_name=builder_name,
                                                                            toolchain=toolchain,
                                                                            config=config)

    @property
    def cmakelist_generate_context(self) -> CMakeListsGenerateContext:
        return self._cmakelist_generate_context

    @property
    def generator(self) -> CMakeGenerator:
        return self._generator
    
    def output_directory_for_config(self, config: str) -> str: 
        return self.cmakelist_generate_context.output_directory_for_config(config)
    
    @classmethod
    def create(cls, directory: Path, project_name: str, builder_name: str, toolchain: Toolchain, config : Config, generator: CMakeGenerator) -> Self :
        project_to_build = super().find_target_project(directory, project_name)
        if not project_to_build:
            console.print_error(f"No project found in {str(directory)}")
            exit(1)
        return CMakeBuildContext(directory=directory, project=project_to_build, builder_name=builder_name, toolchain=toolchain, config=config, generator=generator)


    @staticmethod
    def from_cli_args(cli_args: argparse.Namespace) -> Self:
        build_context = BuildContext.from_cli_args(cli_args=cli_args)
        generator : CMakeGenerator = getattr(cli_args, "generator", None)
        return CMakeBuildContext(directory=build_context.directory,
                                 project=build_context.project,
                                 builder_name=build_context.builder_name,
                                 toolchain=build_context.toolchain,
                                 config=build_context.config,
                                 generator=generator)

    
class CMakeBuilder(BaseBuilder):
    @classmethod
    def add_cli_argument_to_parser(cls, parser: KissParser):
        def generator_help_string() -> str:
            lines = []
            for target in Toolchain.available_target_list():
                generator_str_list = ", ".join(CMakeGenerator.available_generator_for_platform_target(target))
                lines.append(f" - {target.name} -> {{{generator_str_list}}}")
            return "\n".join(lines)
        parser.formatter_class=argparse.RawTextHelpFormatter
        parser.add_argument("-g", "--generator",
                            type=CMakeGenerator,
                            choices=list(CMakeGenerator),
                            help="Choose CMake generator based on platform:\n" + generator_help_string())
           
    def __init__(self):
        super().__init__("cmake", "Build cmake CMakeLists.txt")

    def _get_visual_studio_configure_args(self, cmake_generator_name: str, context: CMakeContext) -> list[str] | None:
        # Determine -T
        arch = os.environ.get("PROCESSOR_ARCHITECTURE", "").lower()
        arch_w6432 = os.environ.get("PROCESSOR_ARCHITEW6432", "").lower()
        is_x64_host = arch_w6432 or arch in ("amd64", "x86_64")
        if context.toolchain.compiler.is_derived_from("clangcl"):
            host_arch = f"ClangCL,host={'x64' if is_x64_host else 'Win32'}"
        else:
            host_arch = f"host={'x64' if is_x64_host else 'Win32'}"

        # Determine -A
        arch_map = {
            "x86_64": "x64",
            "i686": "Win32",
            "aarch64": "ARM64",
            "arm": "ARM"
        }
        if( arch_target := arch_map.get(context.toolchain.target.arch, None)) is None:
            console.print_error(f"Unsupported target architecture: {context.toolchain.target.arch_name()}")
            return None

        # Complete x86_64-pc-windows-msvc cmake generation list
        return ["--no-warn-unused-cli", "-S", str(context.cmakelists_directory), "-G", cmake_generator_name, "-T", host_arch, "-A", arch_target]
    
    def _get_linux_gnu_configure_args(self, cmake_generator_name: str, context: CMakeContext) -> list[str]:
        # Get the arch flags
        if context.toolchain.target.is_x86_64():
            cmake_generator_c_arch = "-DCMAKE_C_FLAGS=-m64"
            cmake_generator_cxx_arch = "-DCMAKE_CXX_FLAGS=-m64"
        elif context.toolchain.target.is_i686():
            cmake_generator_c_arch = "-DCMAKE_C_FLAGS=-m32"
            cmake_generator_cxx_arch = "-DCMAKE_CXX_FLAGS=-m32"
        elif context.toolchain.target.is_aarch64():
            cmake_generator_c_arch = "-DCMAKE_C_FLAGS=-march=armv8-a"
            cmake_generator_cxx_arch = "-DCMAKE_CXX_FLAGS=-march=armv8-a"
        elif context.toolchain.target.is_arm():
            cmake_generator_c_arch = "-DCMAKE_C_FLAGS=-march=armv7-a"
            cmake_generator_cxx_arch = "-DCMAKE_CXX_FLAGS=-march=armv7-a"
        # Set compiler path
        cmake_generator_c_compiler = f"-DCMAKE_C_COMPILER={context.toolchain.compiler.c_path}"
        cmake_generator_cxx_compiler = f"-DCMAKE_CXX_COMPILER={context.toolchain.compiler.cxx_path}"
        return ["--no-warn-unused-cli", "-S", str(context.cmakelists_directory), "-G", cmake_generator_name, cmake_generator_c_compiler, cmake_generator_cxx_compiler, cmake_generator_c_arch, cmake_generator_cxx_arch]
        
    def build_project(self, cmake_build_context: CMakeBuildContext):
        # Generate the project
        cmakelists_generator : CMakeListsGenerator = GeneratorRegistry.generators.get(cmake_build_context.builder_name)
        if not cmakelists_generator:
            console.print_error(f"Generator {cmakelists_generator.name} not found")
            exit(1)
        
        generate_context = cmake_build_context.cmakelist_generate_context
        generated_context_list = cmakelists_generator.generate_project(generate_context)

        # Configure the generated CMakelists.txt
        context = CMakeContext(current_directory=cmake_build_context.directory, 
                               toolchain=cmake_build_context.toolchain, 
                               project=cmake_build_context.project)
        
        if generate_context.cmake_generator_name.is_visual_studio():
            if (configure_args := self._get_visual_studio_configure_args(generate_context.cmake_generator_name.name, context=context) ) is None:
                exit(1)
        elif generate_context.cmake_generator_name.is_unix_makefiles():
            if (configure_args := self._get_linux_gnu_configure_args(generate_context.cmake_generator_name.name,context=context)) is None:
                exit(1)
        else:
            console.print_error(f"Unknown target {context.toolchain.target.name}")
            exit(1)                
        

        os.makedirs(context.build_directory, exist_ok=True)
        if generated_context_list or not context.cmakecache.exists():
            console.print_step(f"🛠️  CMake configure...")
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