
from typing import Optional, Self
import console
from toolchain.target.target_registry import Target
from toolchain.toolchain import Toolchain
from toolchain.toolset import GNUToolset, VSToolset

class CMakeGeneratorName:
    def __init__(self, name: str): 
        self.name = name

    def is_visual_studio(self) -> bool:
        return self.name.startswith("Visual Studio")
    
    def is_xcode(self) -> bool: 
        return "Xcode" in self.name
    
    def is_ninja(self) -> bool:
        return self.name == "Ninja"
    
    def is_ninja_multi_config(self) -> bool:
        return self.name == "Ninja Multi-Config"
    
    def is_unix_makefiles(self) -> bool:
        return self.name == "Unix Makefiles"
    
    def is_mingw_makefiles(self) -> bool:
        return self.name == "MinGW Makefiles"

    def is_nmakefiles(self) -> bool:
        return self.name == "NMake Makefiles"
    
    def is_nmakefiles_jom(self) -> bool:
        return self.name == "NMake Makefiles JOM"
    
    def is_single_profile(self) -> bool:
        return any([
            self.is_mingw_makefiles(),
            self.is_nmakefiles(),
            self.is_nmakefiles_jom(),
            self.is_unix_makefiles(),
            self.is_ninja(),
        ])

    
    def is_multi_profile(self) -> bool:
        return any([
            self.is_visual_studio(),
            self.is_xcode(),
            self.is_ninja_multi_config(),
        ])

    @classmethod
    def available_generator_for_platform_target(cls, target: Target) -> list[str]: 
        if target.is_windows_os():
            if target.is_msvc_abi():
                return [
                    "Visual Studio 17 2022",
                    "Ninja",
                    "Ninja Multi-Config",
                    "NMake Makefiles",
                    "NMake Makefiles JOM",
                ]
            elif target.is_gnu_abi():
                return [
                    "MinGW Makefiles",
                    "Ninja",
                ]
        elif target.is_linux_os():
            return [
                "Ninja",
                "Unix Makefiles",
                "Ninja Multi-Config",
            ]
        elif target.is_macos():
            return [
                "Xcode",
                "Ninja",
                "Unix Makefiles",
            ]
        else:
            console.print_error(f"Unsupported target platform: {target.platform}")
            return []
        
    @staticmethod
    def create(toolchain: Toolchain) -> Optional[Self]:
        if isinstance(toolchain.toolset, VSToolset):
            year = toolchain.toolset.product_year
            if toolchain.toolset.major_version == 18:
                year = 2026
            if not year:
                year = int(toolchain.toolset.product_line_version)
            return CMakeGeneratorName(f"{toolchain.toolset.product_name} {toolchain.toolset.major_version} {year}")
        elif isinstance(toolchain.toolset, GNUToolset):
           return CMakeGeneratorName("Unix Makefiles")
        else:
            console.print_error(f"Unsupported toolset: {toolchain.toolset.__class__.__name__}")
            return None
        
