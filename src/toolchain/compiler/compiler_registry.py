import platform
from typing import Self
import console
from project import ProjectType
from toolchain.compiler.compiler_info import CompilerNodeRegistry

class Flags:
    def __init__(self): 
        self.cxx_compiler_flags : list[str] = []
        self.cxx_linker_flags : list[str] = []
        self.enabled_features : list[str] = []
        
class Profile:
    def __init__(self, name: str):
        # The profile name
        self.name = name
        self.per_project_type_flags : dict[ProjectType, Flags] = {}

    def __hash__(self) -> int:
        return hash(self.name)

    def __eq__(self, other) -> bool:
        if not isinstance(other, Profile):
            return NotImplemented
        return self.name == other.name
    
    def flags_for_project_type(self, project_type: ProjectType) -> list[str]:
         return self.per_project_type_flags.get(project_type, [])
    
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

class Compiler:
    def __init__(self, name: str):
        # The compiler name
        self.name = name
        # List of profiles
        self.profiles = ProfileList()
    
    def _build_repr(self) -> str:
        lines = [
            f"Compiler : {self.name}",
        ]
        for profile in self.profiles:
            lines.append(f"  - {profile.name}")
            for project_type, flags in profile.per_project_type_flags.items():
                lines.append(f"    - {project_type}:")
                lines.append(f"      cxx_compiler_flags: {flags.cxx_compiler_flags}")
                lines.append(f"      cxx_linker_flags: {flags.cxx_linker_flags}")
                lines.append(f"      enable_features: {flags.enabled_features}")
        return "\n".join(lines)

    def __repr__(self) -> str:
        return self._build_repr()

    def __str__(self) -> str:
        return self._build_repr()
    
    @staticmethod
    def create(name :str) -> Self | None:
        if (root_compiler_info := CompilerNodeRegistry.get(name)) is None:
            console.print_error(f"Compiler {name} not found")
            return None
        
        if(compiler_node := root_compiler_info.extend_self()) is None:
            return None
        
        new_compiler = Compiler(compiler_node.name)
        for profile in compiler_node.profiles:
            if not profile.is_abstract:
                assert profile.is_extended, f"Profile {profile.name} must be extended"
                new_profile = Profile(profile.name)
                for bin_lib_dyn in profile.bin_lib_dyn_list:
                    flags = Flags()
                    flags.cxx_compiler_flags.extend(bin_lib_dyn.cxx_compiler_flags)
                    flags.cxx_linker_flags.extend(bin_lib_dyn.cxx_linker_flags)
                    flags.enabled_features.extend(bin_lib_dyn.enable_features)
                    # Add flags of features
                    for feature_name in bin_lib_dyn.enable_features:
                        if (feature_node := compiler_node.get_feature(feature_name)) is None:
                            console.print_error(f"Feature {feature_name} not found for profile {profile.name} in compiler {new_compiler.name}")
                            return None
                        flags.cxx_compiler_flags.extend(feature_node.cxx_compiler_flags)
                        flags.cxx_linker_flags.extend(feature_node.cxx_linker_flags)
                        
                    new_profile.per_project_type_flags[bin_lib_dyn.project_type] = flags
                new_compiler.profiles.add(new_profile)

        return new_compiler
    
    @classmethod
    def default_compiler_name(cls) -> Self:
        if not hasattr(cls, "_default_compiler_name"):
            system = platform.system()
            if system == "Windows":
                supported_compilers = ["cl", "clangcl"]
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