from build import BuildContext
from builder import BuilderRegistry
from cli import KissParser
from cmake.builder_cmake import BuilderCMake
from cmake.cmake_context import CMakeContext
from compiler import Compiler
from config import Config
import console
from platform_target import PlatformTarget
from process import run_process
from run import RunContext
from runner import BaseRunner


class RunnerCMake(BaseRunner):
    @classmethod
    def add_cli_argument_to_parser(cls, parser: KissParser):
        parser.add_argument("-c", "--config", choices=Config._member_names_, help="specify the build configuration", dest="config", type=Config)
        parser.add_argument("-compiler", choices=Compiler._member_names_, help="specify the compiler to use", type=Compiler)


    def __init__(self, parser: KissParser = None):
        super().__init__("cmake", "Build cmake CMakeLists.txt")
        self.config = getattr(parser, "config", None) or Config.default_config()
        self.compiler = getattr(parser, "compiler", None) or Compiler.default_compiler(platform_target=PlatformTarget.default_target())

    def run_project(self, run_context: RunContext):
        # Build the project
        cmake_builder : BuilderCMake = BuilderRegistry.builders.get(run_context.runner_name)
        if not cmake_builder:
            console.print_error(f"Builder {cmake_builder.name} not found")
            exit(1)
        cmake_builder.build(BuildContext.create(directory=run_context.directory,
                                                            project_name=run_context.project.name,
                                                            builder_name=run_context.runner_name,
                                                            platform_target=run_context.platform_target))
        
        # Run it
        context = CMakeContext(current_directory=run_context.directory, 
                               platform_target=run_context.platform_target, 
                               project=run_context.project)
        #  match context.platform_target:
        #     case PlatformTarget.x86_64_pc_windows_msvc:
        #         executable_path = context.build_directory / f"{context.project.name}.exe"
        # if not run_process("cmake", args, context.build_directory) == 0:
        #     exit(1)
        # run_context.project
    

    
    def run(self, run_context: RunContext):
        self.run_project(run_context=run_context)