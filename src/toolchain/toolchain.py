

from pathlib import Path
from typing import Self
import console
from toolchain.compiler import Compiler
from toolchain.target import Target
from toolchain.target.target_info import TargetInfoRegistry
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
            console.print_error(f"❌ Fail to create toolchain with compiler {compiler_name} and target {target_name}")
            return None
        # Find the target
        target = TargetInfoRegistry.get(target_name)

        return Toolchain(compiler, target)

    @staticmethod
    def load_all_toolchains_in_directory(directory: Path) -> bool :
        # Load the yaml file in this directory
        for file in directory.glob("**/*.yaml",):
            toolchain_file = ToolchainYamlFile(file);
            toolchain_file.load_yaml()


