import asyncio
import os
from pathlib import Path
import sys
import console

def print_process(program: Path, args: list[str] = [], working_dir = Path(os.curdir), env: dict[str, str] = {}):
    if args is None:
        args = []
    if env is None:
        env = {}

    # Construire la ligne de commande lisible
    cmd_str = " ".join([str(program)] + [str(a) for a in args])

    console.print_step(f"🛠  Command: {cmd_str}")
    console.print_step(f"  📂 Working directory: {working_dir.absolute()}")
    
    if env:
        env_str = " ".join(f"{k}={v}" for k, v in env.items())
        console.print_step(f"  🌱 Environment: {env_str}")
        
def run_process(program: Path, args: list[str] = [], working_dir= Path(os.curdir), env: dict[str, str] = {}, output_prefix = False):
   print_process(program, args, working_dir, env)
   return asyncio.run(__run_process(program, args, working_dir, env, output_prefix))

async def __run_process(program: Path, args: list[str], working_dir= Path(os.curdir), env: dict[str, str] = {}, output_prefix = False):
    if not working_dir.exists():
        console.print_error(f"  | Error: Working directory does not exist: {working_dir}")
        console.print_error(f"  | Current directory {Path(os.curdir)}")
        console.print_error(f"  | Command: {program} {args}")
        sys.exit(2)
    environ = os.environ.copy()
    environ |= env
    try:
        proc = await asyncio.create_subprocess_exec(
            program, 
            *args, 
            stdout=asyncio.subprocess.PIPE, 
            stderr=asyncio.subprocess.PIPE, 
            cwd=str(working_dir), 
            env=environ
        )
    except FileNotFoundError:
        console.print_error(f"  | Error: Program not found: {program}")
        console.print_error(f"  | Current directory: {Path(os.curdir)}")
        console.print_error(f"  | Command: {program} {args}")
        return 1
    except PermissionError:
        console.print_error(f"  | Error: Permission denied when trying to run: {program}")
        return 1

    while True:
        if proc.stdout.at_eof() and proc.stderr.at_eof():
            break
        while not proc.stdout.at_eof() :
            stdout = (await proc.stdout.readline()).decode(errors="replace")
            if stdout.strip() :
                if not output_prefix:
                    console.print(f"{stdout}", end='')
                else:
                    console.print(f"  > [{program}] {stdout}", end='')
        while not proc.stderr.at_eof():
            stderr = (await proc.stderr.readline()).decode(errors="replace")
            if stderr.strip():
                if not output_prefix:
                    console.print_error(f"{stderr}", end='')
                else:
                    console.print_error(f"  > [{program}] {stderr}", end='')
                
    await proc.communicate()
    return proc.returncode