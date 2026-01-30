
from pathlib import Path
from typing import Self
import console
from project import ProjectType



#####################################################################
# FlagList represent a list of flags used by the compiler or linker
# 
# Yaml:
#  cxx-compiler-flags|cxx-linker-flags : []
#
#####################################################################
class FlagList:
    def __init__(self):
        self.flags : list[str] = []

    def __iter__(self):
        return iter(self.flags)
    
    def __len__(self):
        return len(self.flags)
    
    def __contains__(self, flag: str) -> bool:
        return flag in self.flags
    
    
    def add(self, flag:str):
        self.flags.append(flag)

    def get(self, name: str) -> str | None:
        for f in self.flags:
            if f == name:
                return f
        return None  
    
    

##############################################################
# FeatureNameList are list of feature names
# 
# Yaml:
#   features: []
#
##############################################################
class FeatureNameList:
    def __init__(self):
        self.feature_names : list[str] = []

    def __iter__(self):
        return iter(self.feature_names)
    
    def __len__(self):
        return len(self.feature_names)
    
    def __contains__(self, feature_name: str) -> bool:
        return feature_name in self.feature_names
        
    def add(self, feature_name:str):
        self.feature_names.append(feature_name)

    def get(self, name: str) -> str | None:
        for f in self.feature_names:
            if f == name:
                return f
        return None  
    

##############################################################
# FeatureRule are base of all feature rule
##############################################################
class FeatureRule:
    def __init__(self, name: str):
        self.name = name


##################################################################################
# FeatureRuleOnlyOne ensures that only one feature can be enabled from a feature list.
#
# Enabling more than one feature in the same target raises an error.
# Enabling a feature in a derived target overrides the feature enabled in the base target.
# 
# Yaml :
#  - only-one: warning       <== 'FeatureRuleOnlyOne'
#    features: [WARNING_LEVEL_BASE, WARNING_LEVEL_STRICT, WARNING_ALL, NO_WARNING]
#
# Example:
#  - If target 'common' enables both 'WARNING_LEVEL_BASE' and 'WARNING_LEVEL_STRICT',
#    an error is raised.
#
#  - If target 'common' enables 'WARNING_LEVEL_BASE' and a target 'msvc' extending
#    'common' enables 'WARNING_LEVEL_STRICT', the only enabled feature will be
#    'WARNING_LEVEL_STRICT'.
#
#    Note: if target 'msvc' enables both 'WARNING_LEVEL_STRICT' and
#    'WARNING_LEVEL_BASE', an error is raised.
#
##################################################################################
class FeatureRuleOnlyOne(FeatureRule):
    def __init__(self, name: str):
        super().__init__(name)
        self.feature_list = FeatureNameList()

##################################################################################
# FeatureRuleIncompatibleWith
#
# Defines a feature that is incompatible with one or more other features.
# If the feature and at least one incompatible feature are enabled in any target,
# an error is raised.
#
# YAML:
#  - incompatible: no_opt      <== 'FeatureRuleIncompatibleWith'
#    feature: OPT_LEVEL_0
#    with: [LTCG, LTO, OMIT_FRAME_POINTER]
#
# Example:
#  - If the feature 'OPT_LEVEL_0' is enabled in any target and at least one feature
#    from the 'with' list is also enabled (in any target), an error is raised.
#
##################################################################################
class FeatureRuleIncompatibleWith(FeatureRule):
    def __init__(self, name: str):
        super().__init__(name)
        self.feature_name = ""
        self.incompatible_with_feature_name_list = FeatureNameList() 

#############################################################
# FeatureProfile add flags and features to enable for a feature.
# It also add project specific flags and features for the feature
#
# Yaml :
#   <root>
#     target:
#       features:
#         - name:                      <== 'Feature'
#           debug|release:             <== 'FeatureProfile'
#             cxx-compiler-flags: []   <== 'CXXCompilerFlagList'
#             cxx-linker-flags: []     <== 'CXXLinkerFlagList'
#             enable-features: []      <== 'FeatureNameList'
#             dyn|bin|lib:             <== set of 'ProjectSpecific'
# 
#############################################################
# class FeatureProfile:
#     def __init__(self, name: str):
#         # Name of the profile
#         self.name = name
#         # Flags pass to the linker
#         self.cxx_linker_flags = CXXLinkerFlagList()
#         # Flags pass to the compiler
#         self.cxx_compiler_flags = CXXCompilerFlagList()
#         # List of features to enable with this feature
#         self.enable_features = FeatureNameList()
#         # List of project specific flags and features with this feature
#         self.project_specifics : set[ProjectSpecific] = set()

#     def __hash__(self) -> int:
#         return hash(self.name)

#     def __eq__(self, other) -> bool:
#         if not isinstance(other, FeatureProfile):
#             return NotImplemented
#         return self.name == other.name

###############################################################
# Feature with a unique name
# It add flags and features for all profiles
# It also add project specific flags and features
#
# Yaml : 
#   <root>
#     target:
#       features:
#         - name:                      <== 'Feature'
#           description:
#           cxx-compiler-flags: []     <== 'CXXCompilerFlagList'
#           cxx-linker-flags: []       <== 'CXXLinkerFlagList'
#           enable-features: []        <== 'FeatureNameList'
#           profiles:
#             debug|release:           <== set of 'FeatureProfile'
#
##############################################################
class Feature:
    def __init__(self, name: str):
        self.name = name
        self.description: str = ""
        self.cxx_linker_flags = CXXLinkerFlagList()
        self.cxx_compiler_flags = CXXCompilerFlagList()
        self.enable_features = FeatureNameList()
        self.profiles = ProfileList()

    def __hash__(self) -> int:
        return hash(self.name)

    def __eq__(self, other) -> bool:
        if not isinstance(other, Feature):
            return NotImplemented
        return self.name == other.name



###############################################################
# CXXCompilerFlagList are flags pass to the compiler
# 
# Yaml :
#   cxx-compiler-flags: []
#
##############################################################
class CXXCompilerFlagList:
    def __init__(self):
        self.flags = FlagList()
    
    def __iter__(self):
        return iter(self.flags)
    
    def __len__(self):
        return len(self.flags)
    
    def __contains__(self, flag: str) -> bool:
        return flag in self.flags
    
    def add(self, flag:str):
        self.flags.append(flag)

    def get(self, name: str) -> str | None:
        return self.flags.get(name)
    
###############################################################
# CXXLinkerFlagList are flags pass to the linker
# 
# Yaml :
#   cxx-linker-flags: []
#
##############################################################
class CXXLinkerFlagList:
    def __init__(self):
        self.flags = FlagList()

    def __iter__(self):
        return iter(self.flags)
    
    def __len__(self):
        return len(self.flags)
    
    def __contains__(self, flag: str) -> bool:
        return flag in self.flags
    
    def add(self, flag:str):
        self.flags.append(flag)
        
    def get(self, name: str) -> str | None:
        return self.flags.get(name)
    
###############################################################
# ProjectSpecific add flags and features by project
# 
# Yaml :
#   dyn|bin|lib:                   <== 'ProjectSpecific'
#     cxx-compiler-flags: []       <== 'CXXCompilerFlagList'
#     cxx-linker-flags: []         <== 'CXXLinkerFlagList'
#     enable-features: []          <== 'FeatureNameList'
#
##############################################################
class ProjectSpecific:
    def __init__(self, project_type: ProjectType):
        self.project_type = project_type
        self.cxx_linker_flags = CXXLinkerFlagList()
        self.cxx_compiler_flags = CXXCompilerFlagList()
        self.enable_features = FeatureNameList()    
    
    def __hash__(self) -> int:
        return hash(self.project_type)

    def __eq__(self, other) -> bool:
        if not isinstance(other, ProjectSpecific):
            return NotImplemented
        return self.project_type == other.project_type

    
#############################################################
# Profile add flags and features by profile.
# It also add project specific flags and features for the profile
# Extending it with 'extends' merge all flags and features of the extended into this one
#
# Yaml :
#   <root>
#     target:
#       profiles:
#         debug|release:                <== 'Profile'
#           extends: common             <== 'Profile'
#           is_abstract: false
#           enable-features: []         <== 'FeatureNameList'
#           cxx-compiler-flags: []      <== 'CXXCompilerFlagList'
#           cxx-linker-flags: []        <== 'CXXLinkerFlagList'
#           dyn|bin|lib:                <== set of 'ProjectSpecific'
# 
#############################################################
class Profile:
    def __init__(self, name: str):
        # The profile name
        self.name = name
        # The profile used extends this one
        self.extends : Profile = None
        # If this profile specific is abstract ( Not usable by the user )
        self.is_abstract = False
        # Flags pass to the linker
        self.cxx_linker_flags = CXXLinkerFlagList()
        # Flags pass to the compiler
        self.cxx_compiler_flags = CXXCompilerFlagList()
        # List of features to enable with this profile
        self.enable_features = FeatureNameList()
        # List of project specific flags and features with this profile
        self.project_specifics : set[ProjectSpecific] = set()

    def __hash__(self) -> int:
        return hash(self.name)

    def __eq__(self, other) -> bool:
        if not isinstance(other, Profile):
            return NotImplemented
        return self.name == other.name


class ProfileCyclicError(Exception):
    def __init__(self, current_node : Profile, parent_node: Profile, visiting_stack: list[Profile]):
        super().__init__()
        self.current_node = current_node
        self.parent_node = parent_node
        self.visiting_stack = visiting_stack

    def __str__(self) -> str:
        parent_name = self.parent_node.name if self.parent_node else "<root>"
        stack = ProfileCyclicError._format_stack([p.name for p in self.visiting_stack] + [self.current_node.name])
        return f"Error: Cyclic dependency between '{self.current_node.name}' and '{parent_name}'\n{stack}" 
    
    @staticmethod
    def _format_stack(names: list[str]) -> str:
        lines = []
        for i, name in enumerate(names):
            indent = " " * (4 * max(i-1, 0))
            if i == 0:
                lines.append(name)
            elif i == len(names) - 1:
                lines.append(f"{indent}└ ⟲ loop {name}")
            else:
                lines.append(f"{indent}└ extends: {name}")
        return "\n".join(lines)


######################################################
# ProfileList list profile
#
# Yaml:
#   <root>
#     target:
#       profiles:       <== 'ProfileList', set of 'Profile'
#
######################################################
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
    
    def add(self, profile:Feature):
        self.profiles.add(profile)

    def get(self, name: str) -> Profile | None:
        for p in self.profiles:
            if p.name == name:
                return p
        return None 
    
    def flatten_extends_profile(self, profile : Profile) -> list[Profile]:
        # 1. Collecte du sous-graphe (DFS)
        all_profiles: list[Profile] = list()
        visiting_stack: list[Profile] = []
       
        def collect(current_node : Profile, parent_node: Profile):
            # Detect cyclic dependency
            if current_node in visiting_stack:
                raise ProfileCyclicError(current_node, parent_node, visiting_stack)

            # Visit the project only once
            if current_node in all_profiles:
                return
            visiting_stack.append(current_node)
 
            # Visit extends
            if current_node.extends:
                extends_node = self.get(current_node.extends)
                if not extends_node:
                    console.print_error(f"❌ '{current_node.name}' profile extends unknown target '{current_node.extends}'")
                    exit(1)
                collect(extends_node, current_node)
            
            # Remove visited project
            visiting_stack.pop()
            all_profiles.append(current_node)
        collect(profile, None)
        return all_profiles
    
######################################################
# FeatureList list features
#
# Yaml:
#   <root>
#     target:
#       features:       <== 'FeatureList', set of 'Feature'
#
######################################################
class FeatureList:
    def __init__(self):
        self.features : set[Feature] = set()

    def __iter__(self):
        return iter(self.features)
    
    def __len__(self):
        return len(self.features)
        
    def __contains__(self, item) -> bool:
        if isinstance(item, Feature):
            return item in self.features
        if isinstance(item, str):
            return any(f.name == item for f in self.features)
        return False
    
    def add(self, feature:Feature):
        self.features.add(feature)

    def get(self, name: str) -> FeatureRule | None:
        for f in self.features:
            if f.name == name:
                return f
        return None  
    
###############################################################
# FeatureRuleList is list of FeatureRule
#
# Yaml:
#   <root>
#     target:
#       feature-rules:      <== 'FeatureRuleList', set of 'FeatureRule'
#
###############################################################
class FeatureRuleList:
    def __init__(self):
        self.feature_rules : set[FeatureRule] = set()
    
    def __iter__(self):
        return iter(self.feature_rules)
    
    def __len__(self):
        return len(self.feature_rules)
    
    def __contains__(self, item) -> bool:
        if isinstance(item, FeatureRule):
            return item in self.feature_rules
        if isinstance(item, str):
            return any(t.name == item for t in self.feature_rules)
        return False
    
    def add(self, feature_rule:FeatureRule):
        self.feature_rules.add(feature_rule)
        
    def get(self, name: str) -> FeatureRule | None:
        for f in self.feature_rules:
            if f.name == name:
                return f
        return None 
    
######################################################
# Target
#
# Yaml:
#   <root>
#     target:
######################################################
class Target:
    def __init__(self, name: str, arch:str, vendor:str, os:str, env:str, compiler_name:str):
        # The target name
        self.name = name
        # The arch of the target
        self.arch = arch
        # The vendor of the target
        self.vendor = vendor
        # The os of the target
        self.os = os
        # The env of the target
        self.env = env
        # The compiler name of the target
        self.compiler_name = compiler_name
        # If this target is abstract ( Not usable by the user )
        self.is_abstract = False
        # The target used extends this one
        self.extends : Target = None
        # List of profiles
        self.profiles = ProfileList()
        # List of features
        self.features = FeatureList()
        # List of feature rules
        self.feature_rules = FeatureRuleList()
        # The file where the target was loaded
        self.file = Path()

    def __hash__(self) -> int:
        return hash(self.name)

    def __eq__(self, other) -> bool:
        if not isinstance(other, Target):
            return NotImplemented
        return self.name == other.name



################################################
# List of targets
################################################
class TargetList:
    def __init__(self):
        self.targets : set[Target] = set()

    def __iter__(self):
        return iter(self.targets)
    
    def __len__(self):
        return len(self.targets)
    
    def __contains__(self, item) -> bool:
        if isinstance(item, Target):
            return item in self.targets
        if isinstance(item, str):
            return any(t.name == item for t in self.targets)
        return False

    def add(self, target:Target):
        self.targets.add(target)

    def get(self, name: str) -> Target | None:
        for t in self.targets:
            if t.name == name:
                return t
        return None


