import argparse
import sys

class KissParser(argparse.ArgumentParser):
    def error(self, message):
        sys.stderr.write('error: %s\n\n' % message)
        self.print_help()
        sys.exit(2)

def add_bin_to_parser(parser: argparse.ArgumentParser):
    parser.add_argument("project_name", help="name of the project to create")
    parser.add_argument("-desc", "--description", help="project description", default="", type=str) 
    parser.add_argument("-cov", "--coverage", help="enable code coverage", action="store_true")
    parser.add_argument("-san", "--sanitizer", help="enable sanitizer", action='store_true')

def add_lib_to_parser(parser: argparse.ArgumentParser):
    parser.add_argument("project_name", help="name of the project to create")
    parser.add_argument("-desc", "--description", help="project description", default="", type=str) 
    parser.add_argument("-cov", "--coverage", help="enable code coverage", action="store_true")
    parser.add_argument("-san", "--sanitizer", help="enable sanitizer", action='store_true')

class UserParams:
    def from_args():
        import argparse
        import sys
        from pathlib import Path
        from project import ProjectType

        parser = KissParser(description=f"{sys.argv[0]} is used to create, run C/C++ project", formatter_class=argparse.RawTextHelpFormatter)
        parser.add_argument(
            "-d", "--dir",
            dest="directory",
            type=lambda p: Path(p).expanduser().resolve(),
            default=Path.cwd(),
            help="Dossier contenant les modules (par défaut current directory)"
        )
        parser.add_argument(
            "-v", "--version",
            action="version",
            version="Kiss 1.0",
            help="Show version information"
        )
        subparsers = parser.add_subparsers(title="choose one of the following options",
                                           dest="option",
                                           help="'list' list projects in directory\n" +
                                                "'new' create a new project\n" +
                                                "'run' build and run the project\n" +
                                                "'build' build the project\n" +
                                                "'test' run tests of the project" )
        
        list_parser = subparsers.add_parser("list", description="list projects in directory")
        list_parser.add_argument("-r", "--recursive", help="iterate over directories", action='store_const', const=True, default=False) 
        new_parser = subparsers.add_parser("new", description="create a new project")
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
                    add_bin_to_parser(new_project_parser)
                # case ProjectType.dyn:
                #     DynProject.add_cli_argument_to_parser(new_project_parser)
                case ProjectType.lib:
                    add_lib_to_parser(new_project_parser)
                # case ProjectType.workspace:
                #     Workspace.add_cli_argument_to_parser(new_project_parser)
    

        # Create the parser to add a dependency to a project
        add_parser = subparsers.add_parser("add", description="add a dependency to project")
        # Target project to which we want to add a dependency
        add_parser.add_argument("dependency_name",help="Name of the dependency", type=str)
        add_parser.add_argument("-p", "--project", required=False, help="Target project", dest="project_name", type=str)
        group = add_parser.add_mutually_exclusive_group()
        group.add_argument("--path", type=Path, help="Path to the dependency project")
        group.add_argument("--git", type=str, help="Git repository URL")
        add_parser.add_argument("--branch", help="Git branch (only with --git)")

        # subcommand : path | git
        # add_subparsers = add_parser.add_subparsers(dest="add_command")
        # # ───────── path ─────────
        # add_path_parser = add_subparsers.add_parser("path", help="Add dependency from a local path")
        # add_path_parser.add_argument("path", help="Path to the dependency project", type=Path)
        # # ───────── git ─────────
        # add_git_parser = add_subparsers.add_parser("git",help="Add dependency from a git repository")
        # add_git_parser.add_argument("url",help="Git repository URL")
        # add_git_parser.add_argument("--branch", default="main",help="Git branch")
    

        # add_bin_parser.add_argument("project_name", help="name of the project to create")
        # add_bin_parser.add_argument("-desc", "--description", help="project description", default="", type=str) 
        # add_bin_parser.add_argument("-cov", "--coverage", help="enable code coverage", action="store_true")
        # add_bin_parser.add_argument("-san", "--sanitizer", help="enable sanitizer", action='store_true')
        # generate_parser = subparsers.add_parser("generate", description="generate files used to build the project")
        # generate_parser.add_argument("-p", "--project", help="name of the project.py to generate", dest="project_name", required=False, type=Path)
        # generate_parser.add_argument("-t", "--target", help="specify the target platform", dest="platform_target", default=PlatformTarget.default_target(), required=False)

        # Create the help string that contains list of all registered generators       
        # generator_help_str = ""
        # for generator in GeneratorRegistry.values():
        #     if generator_help_str:
        #         generator_help_str += "\n"
        #     generator_help_str += f"'{generator.name()}' {generator.short_desc()}"
        # generator_subparser = generate_parser.add_subparsers(title="choose one of the following generator",
        #                                                      dest="generator",
        #                                                      help=generator_help_str)
        
        # Add all generator parser
        # for generator in GeneratorRegistry.values():
        #     generator_parser = generator_subparser.add_parser(generator.name(), description=generator.short_desc())
        #     generator.add_cli_argument_to_parser(parser=generator_parser)


        # builder_parser = subparsers.add_parser("build", description="builder used to build the project")
        # builder_parser.add_argument("-p", "--project", help="name of the project.py to generate", dest="project_name", required=False, type=Path)
        # builder_parser.add_argument("-t", "--target", help="specify the target platform", dest="platform_target", default=PlatformTarget.default_target(), required=False)

        # Create the help string that contains list of all registerd builders
        # builder_help_str = ""
        # for builder in BuilderRegistry.values():
        #     if builder_help_str:
        #         builder_help_str += "\n"
        #     builder_help_str += f"'{builder.name()}' {builder.short_desc()}"
        # builder_subparser = builder_parser.add_subparsers(title="choose one of the following builder",
        #                                                   dest="builder",
        #                                                   help=builder_help_str)
        
        # Add all builder parser
        # for builder in BuilderRegistry.values():
        #     builder_parser = builder_subparser.add_parser(builder.name(), description=builder.short_desc())
        #     builder.add_cli_argument_to_parser(parser=builder_parser)


        # Create the help string that contains list of all registerd runners
        # run_parser = subparsers.add_parser("run", description="Run a project")
        # run_parser.add_argument("-p", "--project", help="name of the project.py to generate", dest="project_name", required=False, type=Path)
        # run_parser.add_argument("-t", "--target", help="specify the target platform", dest="platform_target", default=PlatformTarget.default_target(), required=False)
        # run_help_str = ""
        # for runner in RunnerRegistry.values():
        #     if run_help_str:
        #         run_help_str += "\n"
        #     run_help_str += f"'{runner.name()}' {runner.short_desc()}"
        # runner_subparser = run_parser.add_subparsers(title="choose one of the following runner",
        #                                                         dest="runner",
        #                                                         help=run_help_str)
        
        # Add all runner parser
        # for runner in RunnerRegistry.values():
        #     runner_parser = runner_subparser.add_parser(runner.name(), description=runner.short_desc())
        #     runner.add_cli_argument_to_parser(parser=runner_parser)

        args = parser.parse_args()
        if args.option == "add":
            if args.path and args.branch:
                parser.error("--branch cannot be used with --path")
            # If we are in add command and no subcommand is given, set `path` as default
            if args.path is None and args.git is None:
                args.path = Path(f"{args.dependency_name}")
                    
        return args