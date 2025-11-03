import params
import commands


def main():
    userparams = params.UserParams.from_args()   
    from commands import ListParams,NewParams, GenerateParams, BuildParams
    match userparams:
        case ListParams():
            commands.list.cmd_list(listParams=userparams)

        case NewParams():
            commands.new.cmd_new(newParams=userparams)

        case GenerateParams():
            commands.generate.cmd_generate(generateParams=userparams)
        
        case BuildParams():
            commands.build.cmd_build(buildParams=userparams)
            
if __name__ == "__main__":
    main()