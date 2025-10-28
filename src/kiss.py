import params
import console
import commands

def main():
    # Retrieves user configuration
    userparams = params.UserParams.from_args()   
    match userparams:
        case params.ListParams():
            commands.list.cmd_list(listParams=userparams)

        case params.NewParams():
            commands.new.cmd_new(newParams=userparams)
            # match conf.project_type :
            #     case params.ProjectType.bin:
            #         console.print_error("TBD")
            #     case params.ProjectType.lib:
            #         cmake.lib.new(project_name=conf.project_name, 
            #                     project_type=conf.project_type, 
            #                     enable_coverage=conf.coverage_enabled, 
            #                     enable_sanitizer=conf.sanitizer_enabled,
            #                     populate=True)
            #     case params.ProjectType.dyn:
            #         console.print_error("TBD")
                    
        # case params.RunParams():
        #     cmake.command.run(toolset=conf.build_params.toolset,
        #                 config=conf.build_params.build_config,
        #                 debug_info=conf.build_params.debug_info,
        #                 coverage_enabled=conf.build_params.coverage_enabled,
        #                 sanitizer_enabled=conf.build_params.sanitizer_enabled)

        # case params.BuildParams():
        #     cmake.command.build(toolset=conf.toolset,
        #                 build_config=conf.build_config,
        #                 debug_info=conf.debug_info,
        #                 coverage_enabled=conf.coverage_enabled,
        #                 sanitizer_enabled=conf.sanitizer_enabled)

        # case params.TestParams():
        #     cmake.command.test(toolset=conf.build_params.toolset,
        #                 build_config=conf.build_params.build_config,
        #                 debug_info=conf.build_params.debug_info,
        #                 coverage_enabled=conf.build_params.coverage_enabled,
        #                 sanitizer_enabled=conf.build_params.sanitizer_enabled)

if __name__ == "__main__":
    main()