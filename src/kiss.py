from pathlib import Path
import platform
from add import cmd_add
from clean import cmd_clean
from list import cmd_list
from new import cmd_new
from generate import cmd_generate
from build import cmd_build
import cli
from run import cmd_run
from toolchain import Toolchain

def main():
    if platform.system() == "Windows":
        Toolchain.load_all_toolchains_in_directory(Path("toolchains/windows"))
    else:
        Toolchain.load_all_toolchains_in_directory(Path("toolchains/linux"))
    
    # if not toolchain:
    #     exit
    args = cli.UserParams.from_args()

    if args.option == "list": 
        cmd_list(cli_args=args)
    
    elif args.option == "new":
        cmd_new(cli_args=args)
    
    elif args.option == "add": 
        cmd_add(cli_args=args)
        
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

