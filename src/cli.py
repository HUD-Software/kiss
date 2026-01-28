import argparse
from pathlib import Path
import re
import sys
from builder import BuilderRegistry
from cleaner import CleanerRegistry
from compiler import Compiler
import console
from generator import GeneratorRegistry
from platform_target import PlatformTarget
from project import ProjectType
from runner import RunnerRegistry

_NAME_REGEX = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")

def valid_project_name(name: str) -> str:
    if not _NAME_REGEX.fullmatch(name):
        raise argparse.ArgumentTypeError(
            f"\n  Invalid project name '{name}'.\n"
            "   - Only ASCII letters, digits, underscore;\n"
            "   - Must not start with a digit; '-' is not allowed.\n")
    return name

class KissParser(argparse.ArgumentParser):
    def error(self, message):
        console.print_error(f"Error : {message}")
        self.print_help()
        sys.exit(2)

def _add_list_command(parser : argparse.ArgumentParser):
    list_parser = parser.add_parser("list", description="list projects in directory")
    list_parser.add_argument("-r", "--recursive", help="iterate over directories", action='store_const', const=True, default=False) 
    list_parser.add_argument("-d", "--list-dependencies", help="list all dependencies", action='store_const', const=True, default=False) 

def _add_bin_to_parser(parser: argparse.ArgumentParser):
    parser.add_argument("project_name", help="name of the project to create", type=valid_project_name)
    parser.add_argument("-desc", "--description", help="project description", default="", type=str) 
    parser.add_argument("-cov", "--coverage", help="enable code coverage", action="store_true")
    parser.add_argument("-san", "--sanitizer", help="enable sanitizer", action='store_true')
    parser.add_argument("-e", "--empty", help="do not create defaut source code", action='store_true')

def _add_lib_to_parser(parser: argparse.ArgumentParser):
    parser.add_argument("project_name", help="name of the project to create", type=valid_project_name)
    parser.add_argument("-desc", "--description", help="project description", default="", type=str) 
    parser.add_argument("-cov", "--coverage", help="enable code coverage", action="store_true")
    parser.add_argument("-san", "--sanitizer", help="enable sanitizer", action='store_true')
    parser.add_argument("-e", "--empty", help="do not create defaut source code", action='store_true')

def _add_dyn_to_parser(parser: argparse.ArgumentParser):
    parser.add_argument("project_name", help="name of the project to create", type=valid_project_name)
    parser.add_argument("-desc", "--description", help="project description", default="", type=str) 
    parser.add_argument("-cov", "--coverage", help="enable code coverage", action="store_true")
    parser.add_argument("-san", "--sanitizer", help="enable sanitizer", action='store_true')
    parser.add_argument("-e", "--empty", help="do not create defaut source code", action='store_true')

def _add_new_command(parser : argparse.ArgumentParser):
    new_parser = parser.add_parser("new", description="create a new project")
    new_parser.add_argument("-e", "--existing", help="use existing directory if exists", action='store_const', const=True, default=False)
    # Create the help string that contains list of all project types
    project_type_help_str = ""
    for projet_type in ProjectType:
        if project_type_help_str:
            project_type_help_str += "\n"
        project_type_help_str += projet_type.value
    new_subparser = new_parser.add_subparsers(title="project type", dest="project_type", help=project_type_help_str)

    # Add all project type
    for projet_type in ProjectType:
        new_project_parser = new_subparser.add_parser(projet_type, description=f"{projet_type} project")
        match projet_type:
            case ProjectType.bin:
                _add_bin_to_parser(new_project_parser)
            case ProjectType.lib:
                _add_lib_to_parser(new_project_parser)
            case ProjectType.dyn:
                _add_dyn_to_parser(new_project_parser)

def _add_add_command(parser : argparse.ArgumentParser):
    # Create the parser to add a dependency to a project
    add_parser = parser.add_parser("add", description="add a dependency to project")
    # Target project to which we want to add a dependency
    add_parser.add_argument("dependency_name",help="Name of the dependency", type=valid_project_name)
    add_parser.add_argument("-p", "--project", required=False, help="Target project", dest="project_name", type=valid_project_name)
    group = add_parser.add_mutually_exclusive_group()
    group.add_argument("--path", type=Path, help="Path to the dependency project")
    group.add_argument("--git", type=str, help="Git repository URL")
    add_parser.add_argument("--branch", help="Git branch (only with --git)")

def _add_generate_command(parser : argparse.ArgumentParser):
    from cmake.cmakelists_generator import CMakeListsGenerator
    GeneratorRegistry.register(CMakeListsGenerator())
    
    generate_parser = parser.add_parser("generate", description="generate files used to build the project")
    generate_parser.add_argument("-p", "--project", help="name of the project to generate", dest="project_name", required=False, type=valid_project_name)
    generate_parser.add_argument("-t", "--target", help="specify the target platform", dest="platform_target", default=PlatformTarget.default_target(), required=False)

    # Create the help string that contains list of all registered generators  
    generator_help_str = ""
    for generator in GeneratorRegistry.generators.values():
        if generator_help_str:
            generator_help_str += "\n"
        generator_help_str += f"'{generator.name}' {generator.description}"
    generator_subparser = generate_parser.add_subparsers(title="choose one of the following generator",
                                                            dest="generator_name",
                                                            help=generator_help_str)
    
    # Use "CMake" as default generator
    generate_parser.set_defaults(generator="cmake")

    # Add all generator parser
    for generator in GeneratorRegistry.generators.values():
        generator_parser = generator_subparser.add_parser(generator.name, description=generator.description)
        generator.add_cli_argument_to_parser(parser=generator_parser)

def _add_build_command(parser : argparse.ArgumentParser):
    from cmake.cmake_builder import CMakeBuilder
    BuilderRegistry.register(CMakeBuilder())
    
    build_parser = parser.add_parser("build", description="build files used to build the project")
    build_parser.add_argument("-p", "--project", help="name of the project to build", dest="project_name", required=False, type=valid_project_name)
    build_parser.add_argument("-t", "--target", help="specify the target platform", dest="platform_target", default=PlatformTarget.default_target(), required=False)
    build_parser.add_argument("-r", "--release", action='store_const', const=True, help="release build", dest="release")
    build_parser.add_argument("-compiler", choices=Compiler._member_names_, help="specify the compiler to use", type=Compiler)
    build_parser.add_argument("-d", "--debug_info", action='store_const', const=True, help="enable debug information", dest="debug_info")

    # Create the help string that contains list of all registered builders
    builder_help_str = ""
    for builder in BuilderRegistry.builders.values():
        if builder_help_str:
            builder_help_str += "\n"
        builder_help_str += f"'{builder.name}' {builder.description}"
    builder_subparser = build_parser.add_subparsers(title="choose one of the following builder",
                                                    dest="builder",
                                                    help=builder_help_str)

    # Add all generator parser
    for builder in BuilderRegistry.builders.values():
        builder_parser = builder_subparser.add_parser(builder.name, description=builder.description)
        builder.add_cli_argument_to_parser(parser=builder_parser)

    # Use "CMake" as default builder
    build_parser.set_defaults(builder="cmake")

def _add_run_command(parser : argparse.ArgumentParser):
    from cmake.cmake_runner import CMakeRunner
    RunnerRegistry.register(CMakeRunner())

    run_parser = parser.add_parser("run", description="run the project")
    run_parser.add_argument("-p", "--project", help="name of the project to run", dest="project_name", required=False, type=valid_project_name)
    run_parser.add_argument("-t", "--target", help="specify the target platform", dest="platform_target", default=PlatformTarget.default_target(), required=False)
    run_parser.add_argument("-r", "--release", action='store_const', const=True, help="release build", dest="release")
    run_parser.add_argument("-compiler", choices=Compiler._member_names_, help="specify the compiler to use", type=Compiler)
    run_parser.add_argument("-d", "--debug_info", action='store_const', const=True, help="enable debug information", dest="debug_info")

    # Create the help string that contains list of all registered runners
    runner_help_str = ""
    for runner in RunnerRegistry.runners.values():
        if runner_help_str:
            runner_help_str += "\n"
        runner_help_str += f"'{runner.name}' {runner.description}"
    runner_subparser = run_parser.add_subparsers(title="choose one of the following runner",
                                                 dest="runner",
                                                 help=runner_help_str)

    # Use "CMake" as default runner
    run_parser.set_defaults(runner="cmake")

    # Add all runner parser
    for runner in RunnerRegistry.runners.values():
        runner_parser = runner_subparser.add_parser(runner.name, description=runner.description)
        runner.add_cli_argument_to_parser(parser=runner_parser)

def _add_clean_command(parser : argparse.ArgumentParser):
    from cmake.cmake_cleaner import CMakeCleaner
    CleanerRegistry.register(CMakeCleaner())

    clean_parser = parser.add_parser("clean", description="clean the project")
    clean_parser.add_argument("-p", "--project", help="name of the project to clean", dest="project_name", required=False, type=valid_project_name)

    # Create the help string that contains list of all registered runners
    cleaner_help_str = ""
    for cleaner in CleanerRegistry.cleaners.values():
        if cleaner_help_str:
            cleaner_help_str += "\n"
        cleaner_help_str += f"'{cleaner.name}' {cleaner.description}"
    cleaner_subparser = clean_parser.add_subparsers(title="choose one of the following cleaner",
                                                 dest="cleaner",
                                                 help=cleaner_help_str)

    # Use "CMake" as default runner
    clean_parser.set_defaults(cleaner="cmake")

    # Add all cleaner parser
    for cleaner in CleanerRegistry.cleaners.values():
        cleaner_parser = cleaner_subparser.add_parser(cleaner.name, description=cleaner.description)
        cleaner.add_cli_argument_to_parser(parser=cleaner_parser)

class UserParams:
    def from_args():
        import argparse
        import sys
        from pathlib import Path

        parser = KissParser(description=f"{sys.argv[0]} is used to create, run C/C++ project", formatter_class=argparse.RawTextHelpFormatter)

        # We can specify a current directory
        parser.add_argument(
            "-d", "--dir",
            dest="directory",
            type=lambda p: Path(p).expanduser().resolve(),
            default=Path.cwd(),
            help="Dossier contenant les modules (par défaut current directory)"
        )

        # Show the version of kiss
        parser.add_argument(
            "-v", "--version",
            action="version",
            version="Kiss 1.0",
            help="Show version information"
        )

        # Add command list | new | add | run | build | test
        subparsers = parser.add_subparsers(title="choose one of the following options",
                                           dest="option",
                                           help="'list' list projects in directory\n" +
                                                "'new' create a new project\n" +
                                                "'add' add a dependency to an existing project\n" +
                                                "'run' build and run the project\n" +
                                                "'build' build the project\n" +
                                                "'test' run tests of the project" )
        
        _add_list_command(subparsers)
        _add_new_command(subparsers)
        _add_add_command(subparsers)    
        _add_generate_command(subparsers)
        _add_build_command(subparsers)
        _add_run_command(subparsers)
        _add_clean_command(subparsers)

        args = parser.parse_args()
        if args.option == "add":
            if args.path and args.branch:
                parser.error("--branch cannot be used with --path")
            # If we are in add command and no subcommand is given, set `path` as default
            if args.path is None and args.git is None:
                args.path = Path(f"{args.dependency_name}")
                    
        return args