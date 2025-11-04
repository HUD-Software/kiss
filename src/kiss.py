import params
import commands


def main():
    userparams = params.UserParams.from_args()   
    from commands import ListParams,NewParams, GenerateParams, BuildParams, RunParams
    match userparams:
        case ListParams():
            commands.list.cmd_list(list_params=userparams)

        case NewParams():
            commands.new.cmd_new(new_params=userparams)

        case GenerateParams():
            commands.generate.cmd_generate(generate_params=userparams)
        
        case BuildParams():
            commands.build.cmd_build(build_params=userparams)
        
        case RunParams():
            commands.run.cmd_run(run_params=userparams)
            
if __name__ == "__main__":
    main()