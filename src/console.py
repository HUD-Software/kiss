import sys
from colorama import Fore, Style


def print(s: str):
    sys.stderr.write(f"{Fore.WHITE}{s}{Style.RESET_ALL}\n")

def print_error(s: str):
    sys.stderr.write(f"{Fore.RED}{s}{Style.RESET_ALL}\n")

def print_success(s: str):
    sys.stdout.write(f"{Fore.GREEN}{s}{Style.RESET_ALL}\n")

def print_step(s: str):
    sys.stdout.write(f"{Fore.BLUE}{s}{Style.RESET_ALL}\n")

def print_tips(s: str):
    sys.stdout.write(f"{Fore.CYAN}{s}{Style.RESET_ALL}\n")

def print_warning(s: str):
    sys.stdout.write(f"{Fore.YELLOW}{s}{Style.RESET_ALL}\n")