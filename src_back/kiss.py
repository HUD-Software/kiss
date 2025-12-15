import params
import commands


def main():
    args = params.UserParams.from_args()

    if args.option == "list": 
        commands.list.cmd_list(list_params=args)
    
    elif args.option == "new":
        commands.new.cmd_new(new_params=args)
    
    elif args.option == "generate": 
        commands.generate.cmd_generate(generate_params=args)
    
    elif args.option == "build": 
        commands.build.cmd_build(build_params=args)
    
    elif args.option == "run": 
        commands.run.cmd_run(run_params=args)
            
if __name__ == "__main__":
    main()