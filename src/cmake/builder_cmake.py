from build import BuildContext
from builder import BaseBuilder
from cli import KissParser
from cmake.cmake_context import CMakeContext
from cmake.generator_cmake import GeneratorCMake
from compiler import Compiler
from config import Config
import console
from generate import GenerateContext
from generator import GeneratorRegistry
from platform_target import PlatformTarget
from process import run_process
from visual_studio import get_windows_latest_toolset

class BuilderCMake(BaseBuilder):
    @classmethod
    def add_cli_argument_to_parser(cls, parser: KissParser):
        parser.add_argument("-c", "--config", choices=Config._member_names_, help="specify the build configuration", dest="config", type=Config)
        parser.add_argument("-compiler", choices=Compiler._member_names_, help="specify the compiler to use", type=Compiler)
        parser.add_argument("-d", "--debug", action='store_const', const=True, help="enable debug information", dest="debug_info")
        parser.add_argument("-cov", "--coverage", help="enable code coverage", action='store_const', const=True)
        parser.add_argument("-san", "--sanitizer", help="enable sanitizer", action='store_const', const=True)


    def __init__(self, parser: KissParser = None):
        super().__init__("cmake", "Build cmake CMakeLists.txt")
        self.config = getattr(parser, "config", None) or Config.default_config()
        self.compiler = getattr(parser, "compiler", None) or Compiler.default_compiler(platform_target=PlatformTarget.default_target())
        self.debug = getattr(parser, "debug", None) or False
        self.coverage = getattr(parser, "coverage", None) or False
        self.sanitizer = getattr(parser, "sanitizer", None) or False
    
    def build_project(self, build_context: BuildContext):
        # Generate the project
        cmake_generator : GeneratorCMake = GeneratorRegistry.generators.get(build_context.builder_name)
        if not cmake_generator:
            console.print_error(f"Generator {build_context.builder_name} not found")
            exit(1)
        generated_context_list = cmake_generator.generate(GenerateContext.create(directory=build_context.directory,
                                                            project_name=build_context.project.name,
                                                            generator_name=build_context.builder_name,
                                                            platform_target=build_context.platform_target))
       
        # Get Visual studio CMake Generator
        toolset = get_windows_latest_toolset(self.compiler)
        year = toolset.product_year
        if toolset.major_version == 18:
            year = 2026
        if not year:
            year = int(toolset.product_line_version)
        cmake_generator_name = f"{toolset.product_name} {toolset.major_version} {year}"

        # Configure only if we change the CMakeLists.txt
        if generated_context_list:
            for generated_context in generated_context_list:
                console.print_step(f"🛠️ CMake configure with {cmake_generator_name} ...")
                args = ["--no-warn-unused-cli", "-S", generated_context.cmakelists_directory, "-G", cmake_generator_name, "-T", "host=x64", "-A", "x64"]
                if not run_process("cmake", args, generated_context.cmakelists_directory) == 0:
                    exit(1)
        
        # Build
        console.print_step("🏗️ CMake build...")
        match self.config:
            case Config.debug:
                cmake_config = "Debug"
            case Config.release:
                cmake_config = "Release"

        args = ["--build", ".", "--config", cmake_config]
        context = CMakeContext(project_directory=build_context.directory, 
                               platform_target=build_context.platform_target, 
                               project=build_context.project)
        run_process("cmake", args, context.cmakelists_directory)

    def build(self, build_context: BuildContext):
        self.build_project(build_context=build_context)