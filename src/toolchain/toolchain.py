

import os
from pathlib import Path
from typing import Self
import console
from toolchain.compiler import Compiler
from toolchain.compiler.compiler_registry import Profile
from toolchain.target import Target
from toolchain.target.target_registry import TargetRegistry
from toolchain.toolchain_yaml_loader import ToolchainYamlFile


class Toolchain:
    def __init__(self, compiler: Compiler, target: Target):
        self.compiler = compiler
        self.target = target
    
    def get_profile(self, profile_name: str) -> Profile | None:
        return self.compiler.get_profile(profile_name)
    
    def is_profile_exist(self, profile_name: str) -> bool:
        return self.compiler.is_profile_exist(profile_name)
    
    def profile_name_list(self) -> list[str] : 
        return self.compiler.profile_name_list()
    
    #
    # Detects if the host machine is a 64-bit x86 architecture (x86_64/AMD64) on Windows.
    # PROCESSOR_ARCHITECTURE indicates the current process architecture.
    # PROCESSOR_ARCHITEW6432 is set if a 32-bit process runs on 64-bit Windows.
    #
    @staticmethod
    def is_host_x86_64():
        arch = os.environ.get("PROCESSOR_ARCHITECTURE", "").lower()
        arch_w6432 = os.environ.get("PROCESSOR_ARCHITEW6432", "").lower()
        # PROCESSOR_ARCHITEW6432 est défini si un processus 32-bit tourne sur Windows 64-bit
        return arch_w6432 in ("amd64", "x86_64") or arch in ("amd64", "x86_64")
    #
    # Detects if the host machine is a 32-bit x86 architecture (i686/i386/x86) on Windows.
    # Returns True only for a pure 32-bit process, not a 32-bit process emulated on 64-bit Windows.
    #
    @staticmethod
    def is_host_i686():
        arch = os.environ.get("PROCESSOR_ARCHITECTURE", "").lower()
        arch_w6432 = os.environ.get("PROCESSOR_ARCHITEW6432", "").lower()
        # Si le host est 32-bit pur ou un processus 32-bit sur 64-bit
        return arch in ("x86", "i386", "i686") and arch_w6432 == ""

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
    
    

