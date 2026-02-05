import console
from project import ProjectType
from toolchain.compiler.compiler_info import CompilerNode, CompilerNodeRegistry, FeatureNodeList

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
        root_compiler_info: CompilerNode = CompilerNodeRegistry.get(name)
        if not root_compiler_info:
            console.print_error(f"❌ Compiler {name} not found")
            return None
        
        return root_compiler_info.get_extended()
        # # Flattening the compilers establishes a dependency order,
        # # allowing safe iteration where all included compilers are
        # # resolved before the including compiler.
        # # if A extends B, then B appears before A.
        # flatten_extends_compilers = root_compiler_info.flatten_extends_compilers()
        # console.print_tips(f"{root_compiler_info.name} : [ {' -> '.join([p.name for p in flatten_extends_compilers])} ]")

        # extended_compiler_node = 
        # # Resoluve inclusions
        # for target in flatten_extends_compilers:
        #     extended_target: CompilerNode = target.get_extended()
        #     if not extended_target:
        #         console.print_error(f"   Target '{target.name}' could not be extended with '{target.extends}' and will not be available.")
        #         return None
        #     if not extended_target.validate_features():
        #         if extended_target.extends:
        #             console.print_error(f"   Failed to validate feature rules after extending '{extended_target.name}' with '{extended_target.extends}'.")
        #         else:
        #             console.print_error(f"   Failed to validate feature rules on target {extended_target.name}.")
        #         return None
        #     console.print_tips(extended_target)

        # return flatten_extends_compilers[-1]
        

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