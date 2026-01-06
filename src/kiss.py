from add import cmd_add
from list import cmd_list
from new import cmd_new
from generate import cmd_generate
from build import cmd_build
import cli

def main():
    args = cli.UserParams.from_args()

    if args.option == "list": 
        cmd_list(list_params=args)
    
    elif args.option == "new":
        cmd_new(new_params=args)
    
    elif args.option == "add": 
        cmd_add(add_params=args)
        
    elif args.option == "generate": 
        cmd_generate(generate_params=args)
    
    elif args.option == "build": 
        cmd_build(build_params=args)
    
    # elif args.option == "run": 
    #     commands.run.cmd_run(run_params=args)
            
if __name__ == "__main__":
    main()

