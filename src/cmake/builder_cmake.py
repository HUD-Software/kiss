from pathlib import Path
import sys
from builder import BuilderRegistry
from cmake.cmake_directories import CMakeDirectories
from cmake.generator_cmake import GeneratorCMake
from compiler import Compiler
from config import Config
import console
from kiss_parser import KissParser
from modules import ModuleRegistry
from platform_target import PlatformTarget
from project import Project, Workspace



@BuilderRegistry.register("cmake", "Build cmake CMakeLists.txt")
class BuilderCMake:
    @classmethod
    def add_cli_argument_to_parser(cls, parser: KissParser):
        parser.add_argument("-c", "--config", choices=Config._member_names_, help="specify the build configuration", dest="config", type=Config)
        parser.add_argument("-compiler", choices=Compiler._member_names_, help="specify the compiler to use", type=Compiler)
        parser.add_argument("-d", "--debug", action='store_const', const=True, help="enable debug information", dest="debug_info")
        parser.add_argument("-cov", "--coverage", help="enable code coverage", action='store_const', const=True)
        parser.add_argument("-san", "--sanitizer", help="enable sanitizer", action='store_const', const=True)

    def __init__(self, parser: KissParser = None):      
        self.config = getattr(parser, "config", None) or Config.default_config()
        self.compiler = getattr(parser, "compiler", None) or Compiler.default_compiler()
        self.debug = getattr(parser, "debug", None) or False
        self.coverage = getattr(parser, "coverage", None) or False
        self.sanitizer = getattr(parser, "sanitizer", None) or False

    def build_project(self, project_directory: Path, platform_target:PlatformTarget, project: Project):
        # Generate before
        generator = GeneratorCMake ()
        generator.generate_project(project_directory,platform_target,project)
     
        # Build Now
        directories = CMakeDirectories(project_directory, platform_target,project)
        from process import run_process
        import console
        from cmake.config_cmake import config_to_cmake_config

        # Configure
        console.print_step("CMake configure...")
        args = ["--no-warn-unused-cli", "-S", directories.cmakelists_directory, "-G", "Visual Studio 17 2022", "-T", "host=x64", "-A", "x64"]
        run_process("cmake", args, directories.cmakelists_directory)
        
        # Build
        console.print_step("CMake build...")
        args = ["--build", ".", "--config", config_to_cmake_config(self.config)]
        run_process("cmake", args, directories.cmakelists_directory)

    def build(self, args : KissParser, project: Project):
        if isinstance(project, Workspace):
            for project_path in project.project_paths:
                ModuleRegistry.load_modules(project_path)
                project = ModuleRegistry.get_from_dir(project_path)
                if not project:
                    console.print_error(f"Project {project_path} not found.")
                    sys.exit(2)
                self.build_project(project_directory=project.directory,
                             platform_target=args.platform_target,
                             project=project)
        else:
            self.build_project(project_directory = args.project_directory,
                        platform_target= args.platform_target,
                        project=project)
