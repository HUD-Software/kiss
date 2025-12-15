import sys
from colorama import Fore, Style


def print(s: str, end='\n'):
    sys.stdout.write(f"{Fore.WHITE}{s}{Style.RESET_ALL}{end}")

def print_error(s: str, end='\n'):
    sys.stderr.write(f"{Fore.RED}{s}{Style.RESET_ALL}{end}")

def print_success(s: str, end='\n'):
    sys.stdout.write(f"{Fore.GREEN}{s}{Style.RESET_ALL}{end}")

def print_step(s: str, end='\n'):
    sys.stdout.write(f"{Fore.BLUE}{s}{Style.RESET_ALL}{end}")

def print_tips(s: str, end='\n'):
    sys.stdout.write(f"{Fore.CYAN}{s}{Style.RESET_ALL}{end}")

def print_warning(s: str, end='\n'):
    sys.stdout.write(f"{Fore.YELLOW}{s}{Style.RESET_ALL}{end}")