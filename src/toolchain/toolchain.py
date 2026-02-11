

from pathlib import Path
from typing import Self
import console
from toolchain.compiler import Compiler
from toolchain.target import Target
from toolchain.target.target_registry import TargetRegistry
from toolchain.toolchain_yaml_loader import ToolchainYamlFile


class Toolchain:
    def __init__(self, compiler: Compiler, target: Target):
        self.compiler = compiler
        self.target = target

    @staticmethod
    def create(compiler_name: str, target_name : str)-> Self | None:
        # Find the compiler
        compiler = Compiler.create(compiler_name)
        if not compiler:
            console.print_error(f"Fail to create toolchain with compiler {compiler_name} and target {target_name}")
            return None
        
        console.print_success(compiler)

        # Find the target
        target = TargetRegistry.get(target_name)

        console.print_success(target)
        
        return Toolchain(compiler, target)

    @staticmethod
    def load_all_toolchains_in_directory(directory: Path) -> bool :
        # Load the yaml file in this directory
        for file in directory.glob("**/*.yaml",):
            toolchain_file = ToolchainYamlFile(file);
            toolchain_file.load_yaml()

        
    @staticmethod
    def default_target_name() -> Target:
        return Target.default_target_name()
    
    @staticmethod
    def default_compiler_name() -> str:
        return Compiler.default_compiler_name()
    
    @staticmethod
    def available_target_list() -> list[Target]:
        return list(TargetRegistry)
    
    @classmethod
    def default_toolchain(cls) -> Self | None:
        if not hasattr(cls, "_default_toolchain"):
            target = Toolchain.default_target()
            if(compiler := Toolchain.default_compiler(target)) is None:
                console.print_error(f"Default toolchain not found")
                return None
            cls._default_toochain = Toolchain(compiler=compiler, 
                                              target=target)
        return cls._default_toolchain
    
    

