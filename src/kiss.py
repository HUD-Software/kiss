from pathlib import Path
from add import cmd_add
from clean import cmd_clean
from list import cmd_list
from new import cmd_new
from generate import cmd_generate
from build import cmd_build
import cli
from run import cmd_run
from target import TargetRegistry

def main():
    TargetRegistry.load_and_register_all_target_in_directory(Path("platforms"))
    args = cli.UserParams.from_args()

    if args.option == "list": 
        cmd_list(list_params=args)
    
    elif args.option == "new":
        cmd_new(new_params=args)
    
    elif args.option == "add": 
        cmd_add(add_params=args)
        
    elif args.option == "generate": 
        cmd_generate(cli_args=args)
    
    elif args.option == "build": 
        cmd_build(cli_args=args)
    
    elif args.option == "run": 
        cmd_run(cli_args=args)

    elif args.option == "clean": 
        cmd_clean(cli_args=args)

    elif args.option == "test": 
        pass
    elif args.option == "install":    
        pass 
    elif args.option == "package": 
        pass
            
if __name__ == "__main__":
    main()

