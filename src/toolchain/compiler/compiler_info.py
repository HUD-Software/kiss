
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
        self.flags = set[str]()

    def __iter__(self):
        return iter(self.flags)
    
    def __len__(self):
        return len(self.flags)
    
    def __contains__(self, flag: str) -> bool:
        return flag in self.flags
    
    def __repr__(self) -> str:
        return repr(self.flags)
    
    def __str__(self) -> str:
        return str(self.flags)

    def add(self, flag:str):
        self.flags.add(flag)

    def get(self, name: str) -> str | None:
        for f in self.flags:
            if f == name:
                return f
        return None
    
    def extend_with_list(self, flags: list[str]):
        for f in flags:
            self.add(f)

    def get_extended_with(self, other : Self) -> Self:
        extended = FlagList()
        extended.flags = self.flags.union(other.flags)
        return extended
    
    

##############################################################
# FeatureNameList are list of feature names
# 
# Yaml:
#   features: []
#
##############################################################
class FeatureNameList:
    def __init__(self):
        self.feature_names = set[str]()

    def __iter__(self):
        return iter(self.feature_names)
    
    def __len__(self):
        return len(self.feature_names)
    
    def __contains__(self, feature_name: str) -> bool:
        return feature_name in self.feature_names
    
    def __repr__(self) -> str:
        return repr(self.feature_names)
    
    def __str__(self) -> str:
        return str(self.feature_names)  
      
    def add(self, feature_name:str):
        self.feature_names.add(feature_name)

    def get(self, name: str) -> str | None:
        for f in self.feature_names:
            if f == name:
                return f
        return None 
    
    def extend_with_list(self, flags: list[str]):
        for f in flags:
            self.add(f)

    def get_extended_with(self, other : Self) -> Self:
        extended = FeatureNameList()
        extended.feature_names = self.feature_names.union(other.feature_names)
        return extended

##############################################################
# FeatureRule are base of all feature rule
##############################################################
class FeatureRule:
    def __init__(self, name: str):
        self.name = name


###############################################################
# FeatureInfo with a unique name
# It add flags and features for all profiles
# It also add project specific flags and features
#
# Yaml : 
#   <root>
#     compiler:
#       features:
#         - name:                      <== 'FeatureInfo'
#           description:
#           cxx-compiler-flags: []     <== 'CXXCompilerFlagList'
#           cxx-linker-flags: []       <== 'CXXLinkerFlagList'
#           enable-features: []        <== 'FeatureNameList'
#           profiles:
#             debug|release:           <== set of 'FeatureProfile'
#
##############################################################
class FeatureInfo:
    def __init__(self, name: str):
        self.name = name
        self.description: str = ""
        self.cxx_linker_flags = CXXLinkerFlagList()
        self.cxx_compiler_flags = CXXCompilerFlagList()
        self.enable_features = FeatureNameList()
        self.profiles = ProfileInfoList()

    def __hash__(self) -> int:
        return hash(self.name)

    def __eq__(self, other) -> bool:
        if not isinstance(other, FeatureInfo):
            return NotImplemented
        return self.name == other.name
    
    def available_profile_names(self) -> set[str]:
        return self.profiles.available_profile_names()
    
    def get_extended(self) -> Self:
        extended = FeatureInfo(self.name)
        extended.cxx_compiler_flags = self.cxx_compiler_flags
        extended.cxx_linker_flags = self.cxx_linker_flags
        extended.enable_features = self.enable_features
        extended.profiles = self.profiles.get_extended()
        return extended

    
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
        
    def __repr__(self) -> str:
        return repr(self.flags)
    
    def __str__(self) -> str:
        return str(self.flags)  
      

    def add(self, flag:str):
        self.flags.append(flag)

    def get(self, name: str) -> str | None:
        return self.flags.get(name)
    
    def extend_with_list(self, flags: list[str]):
        self.flags.extend_with_list(flags)

    def get_extended_with(self, other : Self) -> Self:
        extended = CXXCompilerFlagList()
        extended.flags = self.flags.get_extended_with(other.flags)
        return extended
    
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
    
    def __repr__(self) -> str:
        return repr(self.flags)
    
    def __str__(self) -> str:
        return str(self.flags)  
    
    def add(self, flag:str):
        self.flags.append(flag)
        
    def get(self, name: str) -> str | None:
        return self.flags.get(name)
 
    def extend_with_list(self, flags: list[str]):
        self.flags.extend_with_list(flags)

    def get_extended_with(self, other : Self) -> Self:
        extended = CXXLinkerFlagList()
        extended.flags = self.flags.get_extended_with(other.flags)
        return extended
    
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
    
    def __repr__(self) -> str:
        return f"""{self.project_type}:
    cxx_linker_flags : {self.cxx_linker_flags}
    cxx_compiler_flags : {self.cxx_compiler_flags}
    enable_features : {self.enable_features}"""
    
    def __str__(self) -> str:
        return str(self.flags)  
    
    def get_extended_with(self, other : Self) -> Self :
        if self.project_type != other.project_type:
            console.print_error(f"❌ Extend project specific {self.project_type} with different type is impossible {self.project_type} extended with {other.project_type}")
            exit(1)
        extended = ProjectSpecific(self.project_type)
        extended.cxx_compiler_flags = self.cxx_compiler_flags.get_extended_with(other.cxx_compiler_flags)
        extended.cxx_linker_flags = self.cxx_linker_flags.get_extended_with(other.cxx_linker_flags)
        extended.enable_features = self.enable_features.get_extended_with(other.enable_features)
        return extended

###############################################################
# CXXLinkerFlagList are flags pass to the linker
# 
# Yaml :
#   cxx-linker-flags: []
#
##############################################################
class ProjectSpecificList:
    def __init__(self):
        self.project_specifics: set[ProjectSpecific] = set()
    
    def __iter__(self):
        return iter(self.project_specifics)
    
    def __len__(self):
        return len(self.project_specifics)
    
    def __contains__(self, project_specific: ProjectSpecific) -> bool:
        return project_specific in self.project_specifics
    
    def __contains__(self, item) -> bool:
        if isinstance(item, ProjectSpecific):
            return item in self.project_specifics
        if isinstance(item, ProjectType):
            return any(p.project_type == item for p in self.project_specifics)
        return False

    def add(self, profile:ProjectSpecific):
        self.project_specifics.add(profile)

    def get(self, project_type: ProjectType) -> ProjectSpecific | None:
        for p in self.project_specifics:
            if p.project_type == project_type:
                return p
        return None 
    
    def get_extended_with(self, other : Self) -> ProjectSpecific :
        extended = ProjectSpecificList()
        # Get elements in self AND other
        # Extends the commons
        commons : set[ProjectSpecific] = self.project_specifics.intersection(other.project_specifics)
        for common in commons:
            extended.project_specifics.add(common.get_extended_with(other.get(common.project_type)))
        # Get elements not in self and other
        # Add the non common
        non_commons : set[ProjectSpecific] = self.project_specifics.symmetric_difference(other.project_specifics)
        extended.project_specifics.update(non_commons)
        return extended
    
#############################################################
# ProfileInfo add flags and features by profile.
# It also add project specific flags and features for the profile
# Extending it with 'extends' merge all flags and features of the extended into this one
#
# Yaml :
#   <root>
#     compiler:
#       profiles:
#         debug|release:                <== 'ProfileInfo'
#           extends: common             <== 'ProfileInfo'
#           is_abstract: false
#           enable-features: []         <== 'FeatureNameList'
#           cxx-compiler-flags: []      <== 'CXXCompilerFlagList'
#           cxx-linker-flags: []        <== 'CXXLinkerFlagList'
#           dyn|bin|lib:                <== set of 'ProjectSpecific'
# 
#############################################################
class ProfileInfo:
    def __init__(self, name: str):
        # The profile name
        self.name = name
        # The profile used to extends this one
        self.extends : str = None
        # If this profile specific is abstract ( Not usable by the user )
        self.is_abstract = False
        # Flags pass to the linker
        self.cxx_linker_flags = CXXLinkerFlagList()
        # Flags pass to the compiler
        self.cxx_compiler_flags = CXXCompilerFlagList()
        # List of features to enable with this profile
        self.enable_features = FeatureNameList()
        # List of project specific flags and features with this profile
        self.project_specifics = ProjectSpecificList()

    def __hash__(self) -> int:
        return hash(self.name)

    def __eq__(self, other) -> bool:
        if not isinstance(other, ProfileInfo):
            return NotImplemented
        return self.name == other.name

    def get_extended_with(self, other: Self) -> Self :
        extended = ProfileInfo(self.name)
        extended.cxx_compiler_flags = self.cxx_compiler_flags.get_extended_with(other.cxx_compiler_flags)
        extended.cxx_linker_flags = self.cxx_linker_flags.get_extended_with(other.cxx_linker_flags)
        extended.enable_features = self.enable_features.get_extended_with(other.enable_features)
        extended.project_specifics = self.project_specifics.get_extended_with(other.project_specifics)
        return extended
    
    def enabled_feature_list_for_project_type(self, project_type: ProjectType)-> FeatureNameList:
        feature_name_list = FeatureNameList()
        feature_name_list.extend_with_list(self.enable_features)
        project_specific = self.project_specifics.get(project_type)
        if project_specific:
            feature_name_list.extend_with_list(project_specific.enable_features)
        return feature_name_list

    # def flatten_extends_profile(self, profile: Self, profile_list: ProfileInfoList) -> list[Self]:
    #     # 1. Collecte du sous-graphe (DFS)
    #     all_profiles: list[ProfileInfo] = list()
    #     visiting_stack: list[ProfileInfo] = []
       
    #     def collect(current_node : ProfileInfo, parent_node: ProfileInfo):
    #         # Detect cyclic dependency
    #         if current_node in visiting_stack:
    #             raise CyclicError(current_node, parent_node, visiting_stack)

    #         # Visit the project only once
    #         if current_node in all_profiles:
    #             return
    #         visiting_stack.append(current_node)
 
    #         # Visit extends
    #         if current_node.extends:
    #             extends_node = profile_list.get(current_node.extends)
    #             if not extends_node:
    #                 console.print_error(f"❌ '{current_node.name}' profile extends unknown compiler '{current_node.extends}'")
    #                 exit(1)
    #             collect(extends_node, current_node)
            
    #         # Remove visited project
    #         visiting_stack.pop()
    #         all_profiles.append(current_node)
    #     collect(profile, None)
    #     return all_profiles
    
class CyclicError(Exception):
    def __init__(self, current_node, parent_node, visiting_stack):
        super().__init__()
        self.current_node = current_node
        self.parent_node = parent_node
        self.visiting_stack = visiting_stack

    def __str__(self) -> str:
        parent_name = self.parent_node.name if self.parent_node else "<root>"
        stack = CyclicError._format_stack([p.name for p in self.visiting_stack] + [self.current_node.name])
        return f"Error: Cyclic dependency between '{self.current_node.name}' and '{parent_name}'\n{stack}" 
    
    def stack(self) -> list[ProfileInfo]:
        return self.visiting_stack
    
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
# ProfileInfoList list profile
#
# Yaml:
#   <root>
#     compiler:
#       profiles:       <== 'ProfileInfoList', set of 'ProfileInfo'
#
######################################################
class ProfileInfoList:
    def __init__(self):
        self.profiles: set[ProfileInfo] = set()
    
    def __iter__(self):
        return iter(self.profiles)
    
    def __len__(self):
        return len(self.profiles)
    
    def __contains__(self, profile: ProfileInfo) -> bool:
        return profile in self.profiles
    
    def __contains__(self, item) -> bool:
        if isinstance(item, ProfileInfo):
            return item in self.profiles
        if isinstance(item, str):
            return any(p.name == item for p in self.profiles)
        return False
    
    def add(self, profile:ProfileInfo):
        self.profiles.add(profile)

    def get(self, name: str) -> ProfileInfo | None:
        for p in self.profiles:
            if p.name == name:
                return p
        return None 
    
    # Retrieves an extended version of this list
    # All profile that extends another profile contains the features and flags of the extended profile
    # For exemple, we have 2 profile A and B, B extends A, we return the list A and B (Where B contains A)
    # We also detect cyclic extends
    def get_extended(self) -> Self:
        extended = ProfileInfoList()
        already_extended = set[ProfileInfo]()
        for profile in self.profiles:
            if profile in already_extended:
                continue
            flatten_profiles = self.flatten_extends_profile(profile)
            for i, extend_profile in enumerate(flatten_profiles):
                if extend_profile.extends:
                    extended.add(extend_profile.get_extended_with(flatten_profiles[i-1]))
                else:
                    extended.add(extend_profile)
                already_extended.add(extend_profile)
        return extended


    def get_extended_with(self, other : Self) -> Self :
        extended = ProfileInfoList()
        # Get elements in self AND other
        # Extends the commons
        commons : set[ProfileInfo] = self.profiles.intersection(other.profiles)
        for common in commons:
            extended.profiles.add(common.get_extended_with(other.get(common.name)))
        # Get elements not in self and other
        # Add the non common
        non_commons : set[ProfileInfo] = self.profiles.symmetric_difference(other.profiles)
        extended.profiles.update(non_commons)
        return extended

    def flatten_extends_profile(self, profile: ProfileInfo) -> list[ProfileInfo]:
        # 1. Collecte du sous-graphe (DFS)
        all_profiles: list[ProfileInfo] = list()
        visiting_stack: list[ProfileInfo] = []
       
        def collect(current_node : ProfileInfo, parent_node: ProfileInfo):
            # Detect cyclic dependency
            if current_node in visiting_stack:
                raise CyclicError(current_node, parent_node, visiting_stack)

            # Visit the project only once
            if current_node in all_profiles:
                return
            visiting_stack.append(current_node)
 
            # Visit extends
            if current_node.extends:
                extends_node = self.get(current_node.extends)
                if not extends_node:
                    console.print_error(f"❌ '{current_node.name}' profile extends unknown compiler '{current_node.extends}'")
                    exit(1)
                collect(extends_node, current_node)
            
            # Remove visited project
            visiting_stack.pop()
            all_profiles.append(current_node)
        collect(profile, None)
        return all_profiles
    
    def available_profile_names(self) -> set[str]:
        profiles = set[str]()
        for profile in self.profiles:
            profiles.add(profile.name)
        return profiles
    
    def enabled_feature_list_for_profile_and_project_type(self, profile_name: str, project_type: ProjectType)-> FeatureNameList:
        profile_info = self.get(profile_name)
        if profile_info:
            return profile_info.enabled_feature_list_for_project_type(project_type)
        return FeatureNameList()
    
######################################################
# FeatureInfoList list features
#
# Yaml:
#   <root>
#     compiler:
#       features:       <== 'FeatureInfoList', set of 'FeatureInfo'
#
######################################################
class FeatureInfoList:
    def __init__(self):
        self.features : set[FeatureInfo] = set()

    def __iter__(self):
        return iter(self.features)
    
    def __len__(self):
        return len(self.features)
        
    def __contains__(self, item) -> bool:
        if isinstance(item, FeatureInfo):
            return item in self.features
        if isinstance(item, str):
            return any(f.name == item for f in self.features)
        return False
    
    def add(self, feature:FeatureInfo):
        self.features.add(feature)

    def get(self, name: str) -> FeatureRule | None:
        for f in self.features:
            if f.name == name:
                return f
        return None
    
    def get_extended(self) -> Self:
        extended = FeatureInfoList()
        for feature in self.features:
            extended.add(feature.get_extended())
        return extended

    def get_extended_with(self, extended_feature_info_list : Self) -> Self :
        # Note: We must validate feature rule here and don't allow multiple only-one and incompatible feature here
        extended = FeatureInfoList()
        # Get elements in self AND other
        # Extends the commons
        commons : set[FeatureInfo] = self.features.intersection(extended_feature_info_list.features)
        for common in commons:
            extended.features.add(common.get_extended_with(extended_feature_info_list.get(common.name)))
        # Get elements not in self and other
        # Add the non common
        non_commons : set[FeatureInfo] = self.features.symmetric_difference(extended_feature_info_list.features)
        extended.features.update(non_commons)
        
        # Extend feature profiles
        extended = extended.get_extended()

        return extended
    
    def available_profile_names(self) -> set[str]:
        profiles = set[str]()
        for feature in self.features:
            profiles.update(feature.available_profile_names())
        return profiles
    
##################################################################################
# FeatureRuleOnlyOne ensures that only one feature can be enabled from a feature list.
#
# Enabling more than one feature in the same compiler raises an error.
# Enabling a feature in a derived compiler overrides the feature enabled in the base compiler.
# 
# Yaml :
#  - only-one: warning       <== 'FeatureRuleOnlyOne'
#    features: [WARNING_BASE, WARNING_STRICT, WARNING_ALL, NO_WARNING]
#
# Example:
#  - If compiler 'common' enables both 'WARNING_BASE' and 'WARNING_STRICT',
#    an error is raised.
#
#  - If compiler 'common' enables 'WARNING_BASE' and a compiler 'msvc' extending
#    'common' enables 'WARNING_STRICT', the only enabled feature will be
#    'WARNING_STRICT'.
#
#    Note: if compiler 'msvc' enables both 'WARNING_STRICT' and
#    'WARNING_BASE', an error is raised.
#
##################################################################################
class FeatureRuleOnlyOne(FeatureRule):
    KEY = "only-one"

    def __init__(self, name: str):
        super().__init__(name)
        self.feature_list = FeatureNameList()

    def is_satisfied(self, feature_list: FeatureInfoList) -> FeatureInfoList:
        common = self.feature_list.feature_names.intersection(feature_list)
        if len(common) > 1:
            return common
        return set()
    
##################################################################################
# FeatureRuleIncompatibleWith
#
# Defines a feature that is incompatible with one or more other features.
# If the feature and at least one incompatible feature are enabled in any compiler,
# an error is raised.
#
# YAML:
#  - incompatible: no_opt      <== 'FeatureRuleIncompatibleWith'
#    feature: OPT_LEVEL_0
#    with: [LTCG, LTO, OMIT_FRAME_POINTER]
#
# Example:
#  - If the feature 'OPT_LEVEL_0' is enabled in any compiler and at least one feature
#    from the 'with' list is also enabled (in any compiler), an error is raised.
#
##################################################################################
class FeatureRuleIncompatibleWith(FeatureRule):
    KEY = "incompatible"

    def __init__(self, name: str):
        super().__init__(name)
        self.feature_name = ""
        self.incompatible_with = FeatureNameList() 

    def is_satisfied(self, enabled_features: FeatureInfoList) -> FeatureInfoList:
        if self.feature_name in enabled_features:
            incompatible_features = self.incompatible_with.feature_names.intersection(enabled_features)
            if incompatible_features:
                return incompatible_features
        return set()


###############################################################
# FeatureRuleList is list of FeatureRule
#
# Yaml:
#   <root>
#     compiler:
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
    
    def get_extended_with(self, other : Self) -> Self :
        extended = FeatureRuleList()
        # Get elements in self AND other
        # Extends the commons
        commons : set[FeatureRule] = self.feature_rules.intersection(other.feature_rules)
        for common in commons:
            extended.feature_rules.add(common.get_extended_with(other.get(common.name)))
        # Get elements not in self and other
        # Add the non common
        non_commons : set[FeatureRule] = self.feature_rules.symmetric_difference(other.feature_rules)
        extended.feature_rules.update(non_commons)
        return extended
    
    def is_feature_list_validate_rules(self, feature_list: FeatureInfoList) -> bool:
        all_valid = True
        for feature_rule in self.feature_rules:
            match feature_rule:
                case FeatureRuleOnlyOne() as only_one_rule:
                    list_invalid = only_one_rule.is_satisfied(feature_list)
                    if list_invalid:
                        console.print_error(f"❌ Feature rule '{FeatureRuleOnlyOne.KEY}' not satisfied. {', '.join(list_invalid)} are both enabled")
                        all_valid = False
                case FeatureRuleIncompatibleWith() as incompatible_rule:
                    list_of_incompatible_feature =  incompatible_rule.is_satisfied(feature_list)
                    if list_of_incompatible_feature:
                        console.print_error(f"❌ Feature rule '{FeatureRuleIncompatibleWith.KEY}' not satisfied. {', '.join(list_of_incompatible_feature)} are incompatible with {incompatible_rule.feature_name}")
                        all_valid = False
        return all_valid
    
######################################################
# CompilerInfo
#
# Yaml:
#   <root>
#     compiler:
######################################################
class CompilerInfo:
    def __init__(self, name: str):
        # The compiler name
        self.name = name
        # If this compiler is abstract ( Not usable by the user )
        self.is_abstract = False
        # The compiler used extends this one
        self.extends : str = None
        # List of profiles
        self.profiles = ProfileInfoList()
        # List of features
        self.features = FeatureInfoList()
        # List of feature rules
        self.feature_rules = FeatureRuleList()
        # The file where the compiler was loaded
        self.file = Path()

    def __hash__(self) -> int:
        return hash(self.name)

    def __eq__(self, other) -> bool:
        if not isinstance(other, CompilerInfo):
            return NotImplemented
        return self.name == other.name
    
    def _build_repr(self) -> str:
        lines = [
            f"Compiler : {self.name} (abstract:{self.is_abstract}, extends: {self.extends})",
            "  Profiles :",
        ]
        for profile in self.profiles:
            lines.append(f"    {profile.name} (extends: {profile.extends})")
            lines.append(f"      cxx_compiler_flags: {profile.cxx_compiler_flags.flags}")
            lines.append(f"      cxx_linker_flags: {profile.cxx_linker_flags.flags}")
            lines.append(f"      features: {profile.enable_features.feature_names}")
            lines.append(f"      project_specifics:")
            for ps in profile.project_specifics:
                lines.append(f"        {ps.project_type}:")
                lines.append(f"          cxx_compiler_flags: {ps.cxx_compiler_flags}")
                lines.append(f"          cxx_linker_flags: {ps.cxx_linker_flags}")
                lines.append(f"          features: {ps.enable_features}")
        return "\n".join(lines)

    def __repr__(self) -> str:
        return self._build_repr()

    def __str__(self) -> str:
        return self._build_repr()
    
    def flatten_extends_compilers(self) -> list[Self]:
        # 1. Collecte du sous-graphe (DFS)
        all_profiles: list[Self] = list()
        visiting_stack: list[Self] = []
       
        def collect(current_node : Self, parent_node: Self):
            # Detect cyclic dependency
            if current_node in visiting_stack:
                raise CyclicError(current_node, parent_node, visiting_stack)

            # Visit the project only once
            if current_node in all_profiles:
                return
            visiting_stack.append(current_node)
 
            # Visit extends
            if current_node.extends:
                extends_node = CompilerInfoRegistry.get(current_node.extends)
                if not extends_node:
                    console.print_error(f"❌ '{current_node.name}' profile extends unknown compiler '{current_node.extends}'")
                    exit(1)
                collect(extends_node, current_node)
            
            # Remove visited project
            visiting_stack.pop()
            all_profiles.append(current_node)
        collect(self, None)
        return all_profiles
    
    def get_extended_with(self, other: Self) -> Self :
        extended = CompilerInfo(self.name)
        extended.file = self.file
        extended.profiles = self.profiles.get_extended().get_extended_with(other.profiles.get_extended())
        extended.features = self.features.get_extended().get_extended_with(other.features)
        extended.feature_rules = self.feature_rules.get_extended_with(other.feature_rules)
        return extended
    
    def available_profile_names(self) -> set[str]:
        profiles = set[str]()
        profiles.update(self.profiles.available_profile_names())
        profiles.update(self.features.available_profile_names())
        return profiles

    def get_extended(self) -> Self | None:
        extended = CompilerInfo(self.name)
        extended.file = self.file
        extended.extends = self.extends
        # Merge included target into this target
        if self.extends:
            # Find the included target and resolve it
            extended_compiler_info: CompilerInfo = CompilerInfoRegistry.get(self.extends)
            if not extended_compiler_info:
                console.print_error(f"'{self.name}' extends an unknown target '{self.extends}'")
                return None
            extended.profiles = self.profiles.get_extended().get_extended_with(extended_compiler_info.profiles.get_extended())
            extended.features = self.features.get_extended().get_extended_with(extended_compiler_info.features)
            extended.feature_rules = self.feature_rules.get_extended_with(extended_compiler_info.feature_rules)
        else:
            extended.file = self.file
            extended.profiles = self.profiles.get_extended()
            extended.features = self.features.get_extended()
            extended.feature_rules = self.feature_rules
        return extended
            
    def validate_features(self) -> bool:
        # Retrieves feature list for each profile and project type
        # [debug, bin], [release, bin], [debug, lib], [custom, lib] etc...
        # Then for all thoses pairs, validate enabled features
        all_valid = True
        all_profile_names : set[str] = self.available_profile_names()
        for profile_name in all_profile_names:
            for project_type  in ProjectType:
                feature_list : FeatureInfoList = self.profiles.enabled_feature_list_for_profile_and_project_type(profile_name, project_type)
                if not self.feature_rules.is_feature_list_validate_rules(feature_list):
                    console.print_error(f"   When evaluating rules for '{project_type}' project with '{profile_name}' profile.")
                    console.print_error(f"   Target '{self.name}' could not be extended with '{self.extends}' and will not be available.")
                    all_valid = False
        return all_valid
    
################################################
# List of compilers in file
################################################
class CompilerInfoList:
    def __init__(self):
        self.compilers : set[CompilerInfo] = set()

    def __iter__(self):
        return iter(self.compilers)
    
    def __len__(self):
        return len(self.compilers)
    
    def __contains__(self, item) -> bool:
        if isinstance(item, CompilerInfo):
            return item in self.compilers
        if isinstance(item, str):
            return any(t.name == item for t in self.compilers)
        return False

    def add(self, compiler:CompilerInfo):
        self.compilers.add(compiler)

    def get(self, name: str) -> CompilerInfo | None:
        for t in self.compilers:
            if t.name == name:
                return t
        return None

    def get_extended(self) -> Self :
        extended = CompilerInfoList()
        for compiler in self.compilers:
            extended.add(compiler.get_extended())
        return extended

################################################
# List of compilers loaded by files
################################################
class CompilerInfoRegistry:
    def __init__(self):
        self.compilers = CompilerInfoList()
    
    def __contains__(self, name: str) -> bool:
        return name in self.compilers

    def __iter__(self):
        return iter(self.compilers)
    
    def get(self, name: str) -> CompilerInfo | None:
        return self.compilers.get(name)

    def register_compiler(self, compiler: CompilerInfo):
        existing_compiler = self.compilers.get(compiler.name)
        if existing_compiler:
            console.print_error(f"⚠️  Warning: Compiler already registered: {existing_compiler.name} in {str(existing_compiler.file)}")
            exit(1)
        self.compilers.add(compiler)


CompilerInfoRegistry = CompilerInfoRegistry()