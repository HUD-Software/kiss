import asyncio
import os
import sys
from colorama import Fore, Style

import console

def print_process(program: str, args: list[str] = [], working_dir: str = os.curdir, env: dict[str, str] = {}):
    if args is None:
        args = []
    if env is None:
        env = {}

    # Construire la ligne de commande lisible
    cmd_str = " ".join([program] + [str(a) for a in args])

    console.print_step(f"🛠  Command: {cmd_str}")
    console.print_step(f"📂 Working directory: {os.path.abspath(working_dir)}")
    
    if env:
        env_str = " ".join(f"{k}={v}" for k, v in env.items())
        console.print_step(f"🌱 Environment: {env_str}")
        
def run_process(program: str, args: list[str] = [], working_dir: str = os.curdir, env: dict[str, str] = {}):
   return asyncio.run(__run_process(program, args, working_dir, env))

async def __run_process(program: str, args: list[str], working_dir: str = os.curdir, env: dict[str, str] = {}):
    if not os.path.exists(working_dir):
        sys.stderr.write(f"Error: Working directory is invalid : {working_dir}\n\n")
        sys.stderr.write(f"Current directory {os.path.abspath(os.curdir)}\n")
        sys.stderr.write(f"Command: {args}\n\n")
        sys.exit(2)
    environ = os.environ.copy()
    environ |= env
    proc = await asyncio.create_subprocess_exec(
        program, 
        *args, 
        stdout=asyncio.subprocess.PIPE, 
        stderr=asyncio.subprocess.PIPE, 
        cwd=working_dir, 
        env=environ
    )

    while True:
        if proc.stdout.at_eof() and proc.stderr.at_eof():
            break
        while not proc.stdout.at_eof() :
            stdout = (await proc.stdout.readline()).decode(errors="replace")
            if stdout.strip() :
                print(f"[{program}] {stdout}", end='', flush=True)
        while not proc.stderr.at_eof():
            stderr = (await proc.stderr.readline()).decode(errors="replace")
            if stderr.strip():
                print(f"[{program}] {Fore.RED} {stderr}{Style.RESET_ALL}", end='', flush=True, file=sys.stderr)
                
    await proc.communicate()
    return proc.returncode