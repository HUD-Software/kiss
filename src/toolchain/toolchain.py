

from json import tool
import os
from pathlib import Path
from typing import Self
import console
from toolchain.compiler import Compiler
from toolchain.compiler.compiler_registry import Profile
from toolchain.target import Target
from toolchain.target.target_registry import TargetRegistry
from toolchain.toolchain_yaml_loader import ToolchainYamlFile
from toolchain.toolset import Toolset


class Toolchain:
    def __init__(self, 
                 target: Target, 
                 toolset : Toolset):
        self.target = target
        self.toolset = toolset
    
    @property
    def compiler(self) -> Compiler:
        return self.toolset.compiler
    
    def get_profile(self, profile_name: str) -> Profile | None:
        return self.toolset.compiler.get_profile(profile_name)
    
    def is_profile_exist(self, profile_name: str) -> bool:
        return self.toolset.compiler.is_profile_exist(profile_name)
    
    def profile_name_list(self) -> list[str] : 
        return self.toolset.compiler.profile_name_list()
    
    def _build_repr(self) -> str:
        lines = [f"Toolchain:",
                f"  target:",
                f"    {self.target},\n",
                f"  toolset:",
                f"    {self.toolset}\n"]
        return "\n".join(lines)

    def __repr__(self) -> str:
        return self._build_repr()

    def __str__(self) -> str:
        return self._build_repr()
    
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
    def create(compiler_name: str, target_name: str)-> Self | None:
        # Find the target
        target = TargetRegistry.get(target_name)
        if not target:
            console.print_error(f"Target '{target_name}' not found  : {{{', '.join(TargetRegistry.target_name_list())}}}")
            return None
        
        # Create the toolset
        toolset = Toolset.create(compiler_name=compiler_name, 
                                 target=target)

        return Toolchain(target=target,
                         toolset=toolset)

    @staticmethod
    def load_all_toolchains_in_directory(directory: Path) -> bool :
        # Load the yaml file in this directory
        for file in directory.glob("**/*.yaml",):
            toolchain_file = ToolchainYamlFile(file)
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

            cls._default_toolchain = Toolchain.create(compiler_name=Toolchain.default_compiler_name(),
                                                     target_name=Toolchain.default_target_name())
                                                     
        return cls._default_toolchain
    
    

