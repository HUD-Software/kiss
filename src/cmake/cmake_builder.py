import argparse
from multiprocessing import context
import os
from pathlib import Path
from typing import Optional, Self
from build import KissBuildContext
from builder import BaseBuilder
from cli import KissParser
from cmake.cmake_context import CMakeContext
from cmake.cmake_generator_name import CMakeGeneratorName
from cmake.cmakelists_generator import CMakeListsGenerateContext, CMakeListsGenerator
import console
from generator import GeneratorRegistry
from process import run_process
from project import Project
from toolchain import Toolchain


class CMakeBuildContext(KissBuildContext):
    def __init__(self, current_directory:Path, project: Project, builder_name: str, toolchain: Toolchain, profile_name: str, cmake_generator_name:str):
        super().__init__(current_directory=current_directory, 
                         project=project, 
                         builder_name=builder_name, 
                         toolchain=toolchain, 
                         profile_name=profile_name)
        self._cmakelist_generate_context = CMakeListsGenerateContext.create(current_directory=current_directory,
                                                                            project_name=project.name,
                                                                            generator_name=builder_name,
                                                                            toolchain=toolchain,
                                                                            profile_name=profile_name,
                                                                            cmake_generator_name=cmake_generator_name)

    @property
    def cmakelist_generate_context(self) -> CMakeListsGenerateContext:
        return self._cmakelist_generate_context
    @property
    def cmake_generator_name(self) -> CMakeGeneratorName :
        return self.cmakelist_generate_context.cmake_generator_name
    
    @property
    def profile_name(self) -> str:
        return self._cmakelist_generate_context.profile_name

    def output_directory_for_config(self, config: str) -> str: 
        return self.cmakelist_generate_context.output_directory_for_config(config)
    
    @classmethod
    def create(cls, current_directory: Path, project_name: str, builder_name: str, toolchain: Toolchain, profile_name: str, cmake_generator_name:str) -> Optional[Self] :
        project_to_build = super().find_target_project(current_directory, project_name)
        if not project_to_build:
            console.print_error(f"No project found in {str(current_directory)}")
            return None
        return CMakeBuildContext(current_directory=current_directory, 
                                 project=project_to_build, 
                                 builder_name=builder_name, 
                                 toolchain=toolchain, 
                                 profile_name=profile_name, 
                                 cmake_generator_name=cmake_generator_name)


    @staticmethod
    def from_cli_args(kiss_build_context: KissBuildContext, cli_args: argparse.Namespace) -> Optional[Self] :
        cmake_generator_name  = getattr(cli_args, "generator", None)
        return CMakeBuildContext(current_directory=kiss_build_context.current_directory,
                                 project=kiss_build_context.project,
                                 builder_name=kiss_build_context.builder_name,
                                 toolchain=kiss_build_context.toolchain,
                                 profile_name=kiss_build_context.profile_name,
                                 cmake_generator_name=cmake_generator_name)

    
class CMakeBuilder(BaseBuilder):
    @classmethod
    def add_cli_argument_to_parser(cls, parser: KissParser):
        generator_name_list = list[str]()
        def generator_help_string() -> str:
            lines = []
            for target in Toolchain.available_target_list():
                list_names = CMakeGeneratorName.available_generator_for_platform_target(target)
                generator_name_list.extend(list_names)
                lines.append(f" - {target.name} -> {{{', '.join(list_names)}}}")
            return "\n".join(lines)
        parser.formatter_class=argparse.RawTextHelpFormatter
        parser.add_argument("-g", "--generator",
                            type=str,
                            choices=generator_name_list,
                            help="Choose CMake generator based on platform:\n" + generator_help_string())
           
    def __init__(self):
        super().__init__("cmake", "Build cmake CMakeLists.txt")

    def _get_visual_studio_configure_args(self, cmake_generator_name: str, context: CMakeContext) -> list[str] | None:
        # Determine -T
        is_x64_host = context.toolchain.is_host_x86_64()
        if context.toolchain.compiler.is_clangcl_based():
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
        
    def build_project(self, cmake_build_context: CMakeBuildContext) -> bool:
        # Generate the project
        cmakelists_generator : CMakeListsGenerator = GeneratorRegistry.generators.get(cmake_build_context.builder_name)
        if not cmakelists_generator:
            console.print_error(f"Generator {cmakelists_generator.name} not found")
            return False
        
        generate_context = cmake_build_context.cmakelist_generate_context
        generated_context_list = cmakelists_generator.generate_project(generate_context)

        # Configure the generated CMakelists.txt
        context = CMakeContext(current_directory=cmake_build_context.current_directory, 
                               toolchain=cmake_build_context.toolchain, 
                               project=cmake_build_context.project,
                               profile_name=cmake_build_context.profile_name,
                               cmake_generator_name=cmake_build_context.cmake_generator_name)
        
        if generate_context.cmake_generator_name.is_visual_studio():
            if (configure_args := self._get_visual_studio_configure_args(generate_context.cmake_generator_name.name, context=context) ) is None:
                return False
        elif generate_context.cmake_generator_name.is_unix_makefiles():
            if (configure_args := self._get_linux_gnu_configure_args(generate_context.cmake_generator_name.name,context=context)) is None:
                return False
        else:
            console.print_error(f"Unknown target {context.toolchain.target.name}")
            return False       
        

        os.makedirs(context.build_directory, exist_ok=True)
        if generated_context_list or not context.cmakecache.exists():
            context.toolchain.compiler.name
            context.toolchain.target.name
            console.print_step(f"🛠️  CMake configure...")
            if not run_process("cmake", configure_args, context.build_directory) == 0:
                return False
        else:            
            console.print_step(f"✔️  No CMake configure required") 

        # Build
        console.print_step("🏗️  CMake build...")
        args = ["--build", ".", "--config", cmake_build_context.profile_name]
        if not run_process("cmake", args, context.build_directory) == 0:
            return False

        # Install
        # console.print_step("🏗️  CMake install...")
        # args = ["--install", ".", "--config", cmake_config, "--prefix", context.install_directory]
        # if not run_process("cmake", args, context.build_directory) == 0:
        #     exit(1)

        return True

    def build(self, kiss_build_context: KissBuildContext, cli_args: argparse.Namespace) -> bool:
        if( cmake_build_context := CMakeBuildContext.from_cli_args(kiss_build_context, cli_args)) is None:
            return False
        
        console.print_step(f" - CMake Generator :  {cmake_build_context.cmake_generator_name.name}\n")
        return self.build_project(cmake_build_context=cmake_build_context)