from pathlib import Path
import platform
from typing import Optional, Self
import console
import toolchain
from toolchain.compiler.compiler_info import CompilerNode, CompilerNodeRegistry, FeatureNode, ProfileNode
from toolchain.target.target_registry import Target


class ProjectType:
    def __init__(
        self,
        name: str,
        cxx_linker_flags: set[str],
        cxx_compiler_flags: set[str],
        enabled_feature_list: set[str],
    ):
        self.name = name
        self.cxx_linker_flags = cxx_linker_flags
        self.cxx_compiler_flags = cxx_compiler_flags
        self.enabled_feature_list = enabled_feature_list

    def __hash__(self) -> int:
        return hash(self.name)

    def __eq__(self, other : str | Self) -> bool:
        if isinstance(other, ProjectType):
            return self.name == other.name
        elif isinstance(other, str):
            return self.name == other
        return NotImplemented
    
    def is_feature_enabled(self, feature_name : str) -> bool:
        return feature_name in self.enabled_feature_list

class ProjectList:
    def __init__(self):
        self.project_type_list: set[ProjectType] = set()
    
    def __iter__(self):
        return iter(self.project_type_list)
    
    def __len__(self):
        return len(self.project_type_list)
    
    def __contains__(self, project: ProjectType) -> bool:
        return project in self.project_type_list
    
    def __contains__(self, item : str | ProjectType) -> bool:
        return item in self.project_type_list
    
    def add(self, project: ProjectType):
        self.project_type_list.add(project)

    def get(self, item: str | ProjectType) -> Optional[ProjectType]:
        for p in self.project_type_list:
            if p.name == item:
                return p
        return None 

    def project_name_list(self) -> list[str] : 
        return [p.name for p in self.project_type_list]
    
class Profile:
    def __init__(self, name: str):
        self.name = name
        # Project type specific flags and features
        self.project_type_list = ProjectList()

        # Default flags and features that is not specific to a project type
        self.cxx_linker_flags = set[str]()
        self.cxx_compiler_flags = set[str]()
        self.enabled_feature_list = set[str]()

    def __hash__(self) -> int:
        return hash(self.name)

    def __eq__(self, other: str | Self) -> bool:
        if isinstance(other, Profile):
            return self.name == other.name
        elif isinstance(other, str):
            return self.name == other
        return NotImplemented

    def get(self, project_type_name: str) -> Optional[ProjectType]:
        return self.project_type_list.get(item=project_type_name)

    def linker_flags_for_project_type(self, project_type_name: str) -> list[str]:
        if(project_type := self.get(project_type_name=project_type_name)) is None:
            return self.cxx_linker_flags
        return project_type.cxx_linker_flags

    def compiler_flags_for_project_type(self, project_type_name: str) -> list[str]:
        if (project_type := self.get(project_type_name=project_type_name)) is None:
            return self.cxx_compiler_flags
        return project_type.cxx_compiler_flags

    def is_feature_enabled(self, project_type_name: str, feature_name: str) -> bool:
        if (project_type := self.get(project_type_name=project_type_name)) is None:
            return self.enabled_feature_list
        return project_type.is_feature_enabled(feature_name=feature_name)
    
class ProfileList:
    def __init__(self):
        self.profiles: set[Profile] = set()
    
    def __iter__(self):
        return iter(self.profiles)
    
    def __len__(self):
        return len(self.profiles)
    
    def __contains__(self, profile: Profile) -> bool:
        return profile in self.profiles
    
    def __contains__(self, item : str | Profile) -> bool:
        return item in self.profiles
    
    def add(self, profile:Profile):
        self.profiles.add(profile)

    def get(self, name: str) -> Optional[Profile]:
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
        # The compiler info node from which the compiler is created
        self._compiler_info = compiler_info
    
    def is_based_on(self, compiler_name: Self) -> bool:
        return  self._compiler_info.is_based_on(compiler_name)

    def is_cl_based(self) -> bool:
        return  self._compiler_info.is_based_on("cl")
    
    def is_clangcl_based(self) -> bool:
        return  self._compiler_info.is_based_on("clangcl")
    
    def get_profile(self, profile_name: str) -> Optional[Profile]:
        # Check if we already create the profile
        if(profile := self.profiles.get(profile_name)):
            return profile

        # Load the profile from the compiler info node describes in file
        if( profile := self._compiler_info.profile_list.get(profile_name)):
            profile = Profile(profile_name)

            self.profiles.add(profile)
            return profile
        
        # Else we need to create the profile with all 'commons' info
    
    def is_profile_exist(self, profile_name: str) -> bool:
        return profile_name in self.profiles

    def profile_name_list(self) -> list[str] : 
        return self.profiles.profile_name_list()
    
    def get_linker_flags_list(self, profile_name: str, project_type_name: str) -> list[str]:
        if( profile := self.get_profile(profile_name)) is None:
            console.print_warning(f"Profile {profile_name} not found in {self.name}")
            return []
        return profile.linker_flags_for_project_type(project_type_name=project_type_name)
    
    def get_compiler_flags_list(self, profile_name: str, project_type_name: str) -> list[str]: 
        if( profile := self.get_profile(profile_name)) is None:
            console.print_warning(f"Profile {profile_name} not found in {self.name}")
            return []
        return profile.compiler_flags_for_project_type(project_type_name=project_type_name)
    
    def is_feature_enabled(self, profile_name: str, project_type_name: str) -> bool:
        if( profile := self.get_profile(profile_name)) is None:
            console.print_warning(f"Profile {profile_name} not found in {self.name}")
            return []
        return profile.compiler_flags_for_project_type(project_type_name=project_type_name)

    @staticmethod
    def create(name :str, target: Target) -> Optional[Self]:
        if(compiler_node := CompilerNodeRegistry.get_extended(name)) is None:
            return None
        compiler_node : CompilerNode = compiler_node

        
        new_compiler = Compiler(name=compiler_node.name,
                                cxx_path=compiler_node.cxx_path,
                                c_path=compiler_node.c_path,
                                compiler_info=compiler_node)
        for profile in compiler_node.profile_list:
            profile : ProfileNode = profile
            if not profile.is_abstract:
                new_profile = Profile(profile.name)
                # Each profile contains a per project flags and commons to all project flags
                for project_type in profile.project_type_list:
                    cxx_compiler_flags = set()
                    cxx_linker_flags = set()
                    enabled_feature_list = set()
                    cxx_compiler_flags.update(project_type.commons.cxx_compiler_flags)
                    cxx_linker_flags.update(project_type.commons.cxx_linker_flags)
                    enabled_feature_list.update(project_type.commons.enable_features_list)

                    # Add all features enabled by features
                    for feature_name in project_type.commons.enable_features_list:
                        if (feature_node := compiler_node.get_feature(feature_name)) is None:
                            console.print_error(f"Feature {feature_name} not found for profile {profile.name} in compiler {new_compiler.name}")
                            return None
                        feature_node : FeatureNode = feature_node
                        if (profile_node := feature_node.profile_list.get(profile.name)):
                            if( project_type_node := profile_node.project_type_list.get(project_type.name)):
                                cxx_compiler_flags.update(project_type_node.commons.cxx_compiler_flags)
                                cxx_linker_flags.update(project_type_node.commons.cxx_linker_flags)
                        cxx_linker_flags.update(feature_node.commons.cxx_linker_flags)
                        enabled_feature_list.update(feature_node.commons.enable_features_list)

                    new_profile.project_type_list.add(ProjectType(name=project_type.project_type_name,
                                                     cxx_linker_flags=cxx_linker_flags,
                                                     cxx_compiler_flags=cxx_compiler_flags,
                                                     enabled_feature_list=enabled_feature_list))
                new_compiler.profiles.add(new_profile)

        if target.is_windows_os():
            from visual_studio import get_windows_latest_toolset
            if( toolset := get_windows_latest_toolset(new_compiler)) is None:
                return None
            year = toolset.product_year
            if toolset.major_version == 18:
                year = 2026
            if not year:
                year = int(toolset.product_line_version)
                pass
            # return CMakeGeneratorName(f"{toolset.product_name} {toolset.major_version} {year}", 
            #                           vstoolset=toolset)
        elif target.is_linux_os():
            pass
            #return CMakeGeneratorName("Unix Makefiles")
        else:
            console.print_error(f"Unsupported target platform: {target.platform}")
            return None
        return new_compiler
    
    @classmethod
    def default_compiler_name(cls) -> Optional[Self]:
        if not hasattr(cls, "_default_compiler_name"):
            system = platform.system()
            if system == "Windows":
                supported_compilers = ["cl", "clangcl"]
            elif system == "Linux":
                supported_compilers = ["gcc", "clang"]
            elif system == "Darwin":
                supported_compilers = ["clang", "gcc"]
                
            for compiler_name in supported_compilers:
                for compiler_list in CompilerNodeRegistry.file_compiler_list:
                    if compiler_name in compiler_list:
                        cls._default_compiler_name = compiler_name
                        return cls._default_compiler_name
            return None
        return cls._default_compiler_name
    def _build_repr(self) -> str:
        lines = [
            f"{self.name}",
            f"  -  cxx_path: {self.cxx_path}",
            f"  -  c_path: {self.c_path}"
        ]
        for profile in self.profiles:
            lines.append(f"  - {profile.name}")
            for project_type in profile.project_type_list:
                lines.append(f"    - {project_type.name}:")
                lines.append(f"      cxx_compiler_flags:{project_type.cxx_compiler_flags}:")
                lines.append(f"      cxx_linker_flags:{project_type.cxx_linker_flags}:")
                lines.append(f"      enabled_feature_list:{project_type.enabled_feature_list}:")
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
