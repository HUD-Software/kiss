from pathlib import Path
import platform
from typing import Self
import console
from project import ProjectType
from toolchain.compiler.compiler_info import CompilerNode, CompilerNodeRegistry

class Profile:
    def __init__(self, name: str):
        # The profile name
        self.name = name
        # Per project type flags and features
        self.per_project_type_linker_flags : dict[ProjectType, list[str]] = {}
        self.per_project_type_compiler_flags : dict[ProjectType, list[str]] = {}
        self.per_project_type_feature_names : dict[ProjectType, list[str]] = {}

    def __hash__(self) -> int:
        return hash(self.name)

    def __eq__(self, other) -> bool:
        if not isinstance(other, Profile):
            return NotImplemented
        return self.name == other.name
    
    def linker_flags_for_project_type(self, project_type: ProjectType) -> list[str]:
         return self.per_project_type_linker_flags.get(project_type, [])
    
    def compiler_flags_for_project_type(self, project_type: ProjectType) -> list[str]:
         return self.per_project_type_compiler_flags.get(project_type, [])

    def is_feature_enabled(self, project_type: ProjectType, feature_name: str) -> bool:
        if( list := self.per_project_type_feature_names.get(project_type,[])) is None:
            return False
        return feature_name in list
    
class ProfileList:
    def __init__(self):
        self.profiles: set[Profile] = set()
    
    def __iter__(self):
        return iter(self.profiles)
    
    def __len__(self):
        return len(self.profiles)
    
    def __contains__(self, profile: Profile) -> bool:
        return profile in self.profiles
    
    def __contains__(self, item) -> bool:
        if isinstance(item, Profile):
            return item in self.profiles
        if isinstance(item, str):
            return any(p.name == item for p in self.profiles)
        return False
    
    def add(self, profile:Profile):
        self.profiles.add(profile)

    def get(self, name: str) -> Profile | None:
        for p in self.profiles:
            if p.name == name:
                return p
        return None 

    def profile_name_list(self) -> list[str] : 
        return [p.name for p in self.profiles]

class Compiler:
    def __init__(self, name: str, cxx_path: Path, c_path: Path, compiler_info: CompilerNode):
        # The compiler name
        self.name = name
        # List of profiles
        self.profiles = ProfileList()
        # Path of the C++ compiler
        self.cxx_path = cxx_path
        # Path of the C compiler
        self.c_path = c_path
        # The extended compiler info used to create this compiler
        assert compiler_info.is_extended, f"Compiler info '{compiler_info.name}' must be extended to create a compiler"
        self._compiler_info = compiler_info
    
    def is_derived_from(self, compiler_name: Self) -> bool:
        return  self._compiler_info.is_derived_from(compiler_name)

    def is_cl_based(self) -> bool:
        return  self._compiler_info.is_derived_from("cl")
    
    def is_clangcl_based(self) -> bool:
        return  self._compiler_info.is_derived_from("clangcl")
    
    def get_profile(self, profile_name: str) -> Profile | None:
        return self.profiles.get(profile_name)
    
    def is_profile_exist(self, profile_name: str) -> bool:
        return profile_name in self.profiles

    def profile_name_list(self) -> list[str] : 
        return self.profiles.profile_name_list()
    
    def linker_flags_list(self, profile_name: str, project_type: ProjectType) -> list[str]:
        if( profile := self.get_profile(profile_name)) is None:
            console.print_warning(f"Profile {profile_name} not found in {self.name}")
            return []
        return profile.linker_flags_for_project_type(project_type)
    
    def compiler_flags_list(self, profile_name: str, project_type: ProjectType) -> list[str]: 
        if( profile := self.get_profile(profile_name)) is None:
            console.print_warning(f"Profile {profile_name} not found in {self.name}")
            return []
        return profile.compiler_flags_for_project_type(project_type)
    
    def is_feature_enabled(self, profile_name: str, project_type: ProjectType) -> bool:
        if( profile := self.get_profile(profile_name)) is None:
            console.print_warning(f"Profile {profile_name} not found in {self.name}")
            return []
        return profile.compiler_flags_for_project_type(project_type)

    @staticmethod
    def create(name :str) -> Self | None:
        if (root_compiler_info := CompilerNodeRegistry.get(name)) is None:
            console.print_error(f"Compiler {name} not found")
            return None
        
        if(compiler_node := root_compiler_info.extend_self()) is None:
            return None
        
        new_compiler = Compiler(name=compiler_node.name,
                                cxx_path=compiler_node.cxx_path,
                                c_path=compiler_node.c_path,
                                compiler_info=compiler_node)
        
        for profile in compiler_node.profiles:
            if not profile.is_abstract:
                assert profile.is_extended, f"Profile {profile.name} must be extended"
                new_profile = Profile(profile.name)
                for bin_lib_dyn in profile.bin_lib_dyn_list:
                    cxx_compiler_flags = list()
                    cxx_linker_flags = list()
                    cxx_feature_flags = list()
                    cxx_compiler_flags.extend(bin_lib_dyn.cxx_compiler_flags)
                    cxx_linker_flags.extend(bin_lib_dyn.cxx_linker_flags)
                    cxx_feature_flags.extend(bin_lib_dyn.enable_features)
                    # Add flags of features
                    for feature_name in bin_lib_dyn.enable_features:
                        if (feature_node := compiler_node.get_feature(feature_name)) is None:
                            console.print_error(f"Feature {feature_name} not found for profile {profile.name} in compiler {new_compiler.name}")
                            return None
                        cxx_compiler_flags.extend(feature_node.cxx_compiler_flags)
                        cxx_linker_flags.extend(feature_node.cxx_linker_flags)
                        cxx_feature_flags.extend(feature_node.enable_features)

                    new_profile.per_project_type_compiler_flags[bin_lib_dyn.project_type] = cxx_compiler_flags
                    new_profile.per_project_type_linker_flags[bin_lib_dyn.project_type] = cxx_linker_flags
                    new_profile.per_project_type_feature_names[bin_lib_dyn.project_type] = cxx_feature_flags
                    
                new_compiler.profiles.add(new_profile)

        return new_compiler
    
    @classmethod
    def default_compiler_name(cls) -> Self:
        if not hasattr(cls, "_default_compiler_name"):
            system = platform.system()
            if system == "Windows":
                supported_compilers = ["clangcl", "cl"]
            elif system == "Linux":
                supported_compilers = ["gcc", "clang"]
            elif system == "Darwin":
                supported_compilers = ["clang", "gcc"]
                
            for compiler_name in supported_compilers:
                if compiler_name in CompilerNodeRegistry:
                    cls._default_compiler_name = compiler_name
                    return cls._default_compiler_name
            console.print_warning("⚠️  Warning: Default compiler not found")
            return ""
        return cls._default_compiler_name
    def _build_repr(self) -> str:
        lines = [
            f"Compiler: {self.name}",
            f"  -  cxx_path: {self.cxx_path}",
            f"  -  c_path: {self.c_path}"
        ]
        for profile in self.profiles:
            lines.append(f"  - {profile.name}")
            for project_type, compiler_flags in profile.per_project_type_compiler_flags.items():
                lines.append(f"    - {project_type}:")
                lines.append(f"      cxx_compiler_flags: {compiler_flags}")
            for project_type, linker_flags in profile.per_project_type_linker_flags.items():
                lines.append(f"    - {project_type}:")
                lines.append(f"      cxx_linker_flags: {linker_flags}")
            for project_type, features in profile.per_project_type_feature_names.items():
                lines.append(f"    - {project_type}:")
                lines.append(f"      features: {features}")
        return "\n".join(lines)

    def __repr__(self) -> str:
        return self._build_repr()

    def __str__(self) -> str:
        return self._build_repr()
    
    
    
class CompilerList:
    def __init__(self):
        self.compilers : set[Compiler] = set()

    def __iter__(self):
        return iter(self.compilers)
    
    def __len__(self):
        return len(self.compilers)
    
    def __contains__(self, item) -> bool:
        if isinstance(item, Compiler):
            return item in self.compilers
        if isinstance(item, str):
            return any(t.name == item for t in self.compilers)
        return False

    def add(self, compiler:Compiler):
        self.compilers.add(compiler)

    def get(self, name: str) -> Compiler | None:
        for t in self.compilers:
            if t.name == name:
                return t
        return None
