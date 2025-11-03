import os
from builder import BuilderRegistry
from cmake.cmake_directories import CMakeDirectories
from compiler import Compiler
from config import Config
from kiss_parser import KissParser
from process import print_process, run_process
from project.project import Project
import console


@BuilderRegistry.register("cmake", "Build cmake CMakeLists.txt")
class BuilderCMake:
    @classmethod
    def add_cli_argument_to_parser(cls, parser: KissParser):
        parser.add_argument("-c", "--config", choices=Config._member_names_, help="specify the build configuration", dest="config", type=Config)
        parser.add_argument("-compiler", choices=Compiler._member_names_, help="specify the compiler to use", type=Compiler)
        parser.add_argument("-d", "--debug", action='store_const', const=True, help="enable debug information", dest="debug_info")
        parser.add_argument("-cov", "--coverage", help="enable code coverage", action='store_const', const=True)
        parser.add_argument("-san", "--sanitizer", help="enable sanitizer", action='store_const', const=True)

    def __init__(self, parser: KissParser):
        self.config = getattr(parser, "config", Config.debug)
        self.compiler = getattr(parser, "compiler", Compiler.cl)
        self.debug = getattr(parser, "debug", False)
        self.coverage = getattr(parser, "coverage", False)
        self.sanitizer = getattr(parser, "sanitizer", False)

    def __config_to_cmake_config(self, config: Config):
        match config:
            case Config.debug:
                return "Debug"
            case Config.release:
                return "Release"
            
    def __configure(self,  directories:CMakeDirectories, project: Project):
        console.print_step("CMake configure...")
        # Configure
        args = ["--no-warn-unused-cli", "-S", directories.cmakelists_directory, "-G", "Visual Studio 17 2022", "-T", "host=x64", "-A", "x64"]
        print_process("cmake", args, directories.cmakelists_directory)
        run_process("cmake", args, directories.cmakelists_directory)

        console.print_step("CMake build...")
        # Build
        args = ["--build", ".", "--config", self.__config_to_cmake_config(self.config)]
        run_process("cmake", args, directories.cmakelists_directory)

    def build(self, args : KissParser, project: Project):
        directories = CMakeDirectories (args, project)
        self.__configure(directories, project)
