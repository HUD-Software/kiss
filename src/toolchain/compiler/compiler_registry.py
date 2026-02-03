import console
from project import ProjectType
from toolchain.compiler.compiler_info import CompilerInfo, CompilerInfoRegistry, FeatureList

class Flags:
    def __init__(self):
        self.compiler_flags : list[str] = []
        self.linker_flags : list[str] = []

class Profile:
    def __init__(self, name: str):
        # The profile name
        self.name = name
        self.flags = Flags()
        self.per_project_type_flags : dict[ProjectType, Flags]

    def __hash__(self) -> int:
        return hash(self.name)

    def __eq__(self, other) -> bool:
        if not isinstance(other, Profile):
            return NotImplemented
        return self.name == other.name
    
    def flags_for_project_type(self, project_type: ProjectType) -> list[str]:
         return [*self.flags,*self.per_project_type_flags.get(project_type, [])]
    
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
    
    @staticmethod
    def create(name :str) -> Profile | None:
        root_compiler_info: CompilerInfo = CompilerInfoRegistry.get(name)
        if not root_compiler_info:
            console.print_error(f"❌  Warning: Compiler {name} not found")
            return None
        
        # Flattening the compilers establishes a dependency order,
        # allowing safe iteration where all included compilers are
        # resolved before the including compiler.
        # if A extends B, then B appears before A.
        flatten_extends_compilers = root_compiler_info.flatten_extends_compilers()
        console.print_tips(f"{root_compiler_info.name} : {' -> '.join([p.name for p in flatten_extends_compilers])}")

        # Resoluve inclusions
        for target in flatten_extends_compilers:

            # compiler_info: CompilerInfo = CompilerInfoRegistry.get(name)
            # extended_compiler_info = compiler_info.get_extended_with()
            # pass
            # Merge included target into this target
            if target.extends:
                # Find the included target and resolve it
                extended_compiler_info: CompilerInfo = CompilerInfoRegistry.get(target.extends)
                if not extended_compiler_info:
                    console.print_error(f"{target.name} extends an unknown target {target.extends}")
                    return None
                extended : CompilerInfo= target.get_extended_with(extended_compiler_info)
                console.print_tips(extended)

                # Validate the features rules
                empty_feature_list : list[str] = []

                # Retrieves feature list for each profile and project type
                # [debug, bin], [release, bin], [debug, lib], [custom, lib] etc...
                # Then for all thoses paris, validate enabled features
                all_profile_names : set[str] = extended.available_profile_names()
                for profile_name in all_profile_names:
                    for project_type  in ProjectType:
                        feature_list : FeatureList = extended.feature_list_for_profile_and_project_type(profile_name, project_type)
                        extended.validate_features(profile_name, project_type, feature_list)

            else:
                console.print_tips(target)
            # Validate the features
            #empty_feature_list : list[str] = []
            # all_feature_set = target.default_features.get("all") or empty_feature_list
            # for config, feature_name_list in target.default_features.items():

            #     # Skip 'all'
            #     if config == "all":
            #         continue

            #     # Add config + all features
            #     feature_list = set[FeatureName](feature_name_list)
            #     feature_list.update(all_feature_set)

            #     # Validate the config + all features list
            #     target.validate_features(config, feature_list)

            # # Add this target to the list of resolved target
            # resolved_target_dict[target.name] = target

        

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