

class UserParams:
    def from_args():
        import argparse
        import sys
        from pathlib import Path
        from project import ProjectType
        from kiss_parser import KissParser
        from generator import GeneratorRegistry

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
        new_parser.add_argument("type", help="project type", choices=ProjectType._member_names_, default=ProjectType.bin, type=ProjectType)
        new_parser.add_argument("project_name", help="name of the project to generate")
        new_parser.add_argument("-desc", "--description", help="project description", default="", type=str) 
        new_parser.add_argument("-cov", "--coverage", help="enable code coverage", action="store_true")
        new_parser.add_argument("-san", "--sanitizer", help="enable sanitizer", action='store_true')
        
        generate_parser = subparsers.add_parser("generate", description="generate files used to build the project")

        # Create the help string that contains list of all registered generators
        generator_help_str = ""
        for generator in GeneratorRegistry.values():
            if generator_help_str:
                generator_help_str += "\n"
            generator_help_str += f"'{generator.name()}' {generator.short_desc()}"
        generator_subparser = generate_parser.add_subparsers(title="choose one of the following generator",
                                                                dest="generator",
                                                                help=generator_help_str, required=True)
        
        # Add all generatr parser
        for generator in GeneratorRegistry.values():
            generator_parser = generator_subparser.add_parser(generator.name(), description=generator.short_desc())
            generator.add_cli_argument_to_parser(parser=generator_parser)


        # build_parser = subparsers.add_parser("build", description="build the project")
        # build_parser.add_argument("-p", "--path", help="specify the project path to build", dest="root", required=False)
        # build_parser.add_argument("-t", "--target", help="specify the target platform", dest="platform_target", default=SupportedTarget.default_target(), required=False)
        # build_parser.add_argument("-b", "--build_dir",  help="specify the build directory", dest="build_dir", default=UserParams.default_build_dir)
        # build_parser.add_argument("-c", "--config", choices=Config._member_names_, help="specify the build configuration", dest="config", type=Config)
        # build_parser.add_argument("-compiler", choices=Compiler._member_names_, help="specify the compiler to use", type=Compiler)
        # build_parser.add_argument("-d", "--debug", action='store_const', const=True, help="enable debug information", dest="debug_info")
        # build_parser.add_argument("-cov", "--coverage", help="enable code coverage", action='store_const', const=True)
        # build_parser.add_argument("-san", "--sanitizer", help="enable sanitizer", action='store_const', const=True)

        # run_parser = subparsers.add_parser("run", description="build and run the project")
        # run_parser.add_argument("-p", "--path", help="specify the project path to build", dest="root", required=False)
        # run_parser.add_argument("-t", "--target", help="specify the target platform", dest="platform_target", default=SupportedTarget.default_target(), required=False)
        # run_parser.add_argument("-b", "--build_dir",  help="specify the build directory", dest="build_dir", default=UserParams.default_build_dir)
        # run_parser.add_argument("-c", "--config", choices=Config._member_names_, help="specify the build configuration", dest="config", type=Config)
        # run_parser.add_argument("-compiler", choices=Compiler._member_names_, help="specify the compiler to use", type=Compiler)
        # run_parser.add_argument("-d", "--debug", action='store_const', const=True, help="enable debug information", dest="debug_info")
        # run_parser.add_argument("-cov", "--coverage", help="enable code coverage", action='store_const', const=True)
        # run_parser.add_argument("-san", "--sanitizer", help="enable sanitizer", action='store_const', const=True)

        # test_parser = subparsers.add_parser("test", description="Run test of a project")
        # test_parser.add_argument("-p", "--path", help="specify the project path to build", dest="root", required=False)
        # test_parser.add_argument("-t", "--target", help="specify the target platform", dest="platform_target", default=SupportedTarget.default_target(), required=False)
        # test_parser.add_argument("-b", "--build_dir",  help="specify the build directory", dest="build_dir", default=UserParams.default_build_dir)
        # test_parser.add_argument("-c", "--config", choices=Config._member_names_, help="specify the build configuration", dest="config", type=Config)
        # test_parser.add_argument("-compiler", choices=Compiler._member_names_, help="specify the compiler to use", type=Compiler)
        # test_parser.add_argument("-d", "--debug", action='store_const', const=True, help="enable debug information", dest="debug_info")
        # test_parser.add_argument("-cov", "--coverage", help="enable code coverage", action='store_const', const=True)
        # test_parser.add_argument("-san", "--sanitizer", help="enable sanitizer", action='store_const', const=True)

        args = parser.parse_args()

       
        if args.option == "list": 
            from commands import ListParams
            return ListParams(directory=args.directory, recursive=args.recursive)
        
        if args.option == "new": 
            from commands import NewParams
            return NewParams(directory=args.directory, 
                            project_name=args.project_name, 
                            project_type=args.type, 
                            coverage_enabled=args.coverage, 
                            sanitizer_enabled=args.sanitizer,
                            description=args.description)
        
        if args.option == "generate": 
            from commands import GenerateParams
            return GenerateParams(directory=args.directory, project_name=args.project_name, generator=GeneratorRegistry.create(args.generator), platform_target=args.platform_target)
        # build_config = args.config if args.config is not None else UserParams.default_build_configuration
        # compiler = args.compiler if args.compiler is not None else Compiler.cl
        # debug_info = args.debug_info if args.debug_info is not None else False
        # coverage = args.coverage if args.coverage is not None else False
        # sanitizer = args.sanitizer if args.sanitizer is not None else False

        # toolset = Toolset.get_latest_toolset(compiler)
        # build_params = BuildParams(build_config=build_config, 
        #                             toolset=toolset, 
        #                             debug_info=debug_info, 
        #                             coverage_enabled=coverage, 
        #                             sanitizer_enabled=sanitizer)
        
        # if args.option == "build": return build_params
        # if args.option == "run": return RunParams(build_params)
        # if args.option == "test": return TestParams(build_params)