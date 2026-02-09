
from pathlib import Path
from typing import Self, Union
import console
from project import ProjectType
import copy

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
    
    def add_list(self, flags: list[str]):
        for f in flags:
            self.add(f)

    # Merge, duplicate are removed
    def merge(self, other : Self) -> Self:
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
    
    def add_list(self, flags: list[str]):
        for f in flags:
            self.add(f)

    def merge(self, base: Self, feature_rules) -> Self:
        return feature_rules.merge_feature_name_list(list_base=base.feature_names, list_extends=self.feature_names)
    
##############################################################
# FeatureRuleNode are base of all feature rule
##############################################################
class FeatureRuleNode:
    def __init__(self, name: str):
        self.name = name


###############################################################
# FeatureNode with a unique name
# It add flags and features for all profiles
# It also add project specific flags and features
#
# Yaml : 
#   <root>
#     compilers:          <== 'CompilerNodeList'
#       clang:            <== 'CompilerNode'
#         features:
#           - name:                      <== 'FeatureNode'
#             description:
#             cxx-compiler-flags: []     <== 'CXXCompilerFlagList'
#             cxx-linker-flags: []       <== 'CXXLinkerFlagList'
#             enable-features: []        <== 'FeatureNameList'
#             profiles:                  <== 'ProfileNodeList'
#
##############################################################
class FeatureNode:
    def __init__(self, name: str):
        self.name = name
        self.description: str = ""
        self.cxx_linker_flags = CXXLinkerFlagList()
        self.cxx_compiler_flags = CXXCompilerFlagList()
        self.enable_features = FeatureNameList()
        self.profiles = ProfileNodeList()

    def __hash__(self) -> int:
        return hash(self.name)

    def __eq__(self, other) -> bool:
        if not isinstance(other, FeatureNode):
            return NotImplemented
        return self.name == other.name
    
    def get_profile_names(self) -> set[str]:
        return self.profiles.get_profile_names()

    def extends_self(self, feature_rules) -> Self:
        extended = FeatureNode(self.name)
        extended.cxx_linker_flags = copy.deepcopy(self.cxx_linker_flags)
        extended.cxx_compiler_flags = copy.deepcopy(self.cxx_compiler_flags)
        extended.enable_features = copy.deepcopy(self.enable_features)
        extended.profiles = self.profiles.extends_self(feature_rules)
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
    
    def add_list(self, flags: list[str]):
        self.flags.add_list(flags)

    def merge(self, other : Self) -> Self:
        extended = CXXCompilerFlagList()
        extended.flags = self.flags.merge(other.flags)
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
 
    def add_list(self, flags: list[str]):
        self.flags.add_list(flags)

    def merge(self, other : Self) -> Self:
        extended = CXXLinkerFlagList()
        extended.flags = self.flags.merge(other.flags)
        return extended
    
###############################################################
# BinLibDynNode add flags and features by project
# 
# Yaml :
#   <root>
#     compilers|features:               <== 'CompilerNodeList'|'FeatureNodeList'
#       profiles:                       <== 'ProfileNodeList', set of 'ProfileNode'
#         debug|release:                <== 'ProfileNode'
#           dyn|bin|lib:                <== 'BinLibDynNodeList', set of 'BinLibDynNode'
#             cxx-compiler-flags: []       <== 'CXXCompilerFlagList'
#             cxx-linker-flags: []         <== 'CXXLinkerFlagList'
#             enable-features: []          <== 'FeatureNameList'
#
##############################################################
class BinLibDynNode:
    def __init__(self, project_type: ProjectType):
        self.project_type = project_type
        self.cxx_linker_flags = CXXLinkerFlagList()
        self.cxx_compiler_flags = CXXCompilerFlagList()
        self.enable_features = FeatureNameList()

    def __hash__(self) -> int:
        return hash(self.project_type)

    def __eq__(self, other) -> bool:
        if not isinstance(other, BinLibDynNode):
            return NotImplemented
        return self.project_type == other.project_type
    
    def __repr__(self) -> str:
        return f""" BinLibDynNode : {self.project_type}:
    cxx_linker_flags : {self.cxx_linker_flags}
    cxx_compiler_flags : {self.cxx_compiler_flags}
    enable_features : {self.enable_features}"""
    
    def __str__(self) -> str:
        return str(self.flags)  
    
    def merge(self, cxx_compiler: CXXCompilerFlagList, cxx_linker : CXXLinkerFlagList, features: FeatureNameList, feature_rules) -> Self :
        extended = BinLibDynNode(self.project_type)
        extended.cxx_compiler_flags = self.cxx_compiler_flags.merge(cxx_compiler)
        extended.cxx_linker_flags = self.cxx_linker_flags.merge(cxx_linker)
        extended.enable_features = self.enable_features.merge(base=features, feature_rules=feature_rules)
        return extended

###############################################################
# BinLibDynNodeList are list of BinLibDynNode
# 
# Yaml :
#   <root>
#     compilers|features:               <== 'CompilerNodeList'|'FeatureNodeList'
#       profiles:                       <== 'ProfileNodeList', set of 'ProfileNode'
#         debug|release:                <== 'ProfileNode'
#           dyn|bin|lib:                <== 'BinLibDynNodeList', set of 'BinLibDynNode'
#
##############################################################
class BinLibDynNodeList:
    def __init__(self):
        self.bin_lib_dyn_set: set[BinLibDynNode] = set()
    
    def __iter__(self):
        return iter(self.bin_lib_dyn_set)
    
    def __len__(self):
        return len(self.bin_lib_dyn_set)
    
    def __contains__(self, project_specific: BinLibDynNode) -> bool:
        return project_specific in self.bin_lib_dyn_set
    
    def __contains__(self, item) -> bool:
        if isinstance(item, BinLibDynNode):
            return item in self.bin_lib_dyn_set
        if isinstance(item, ProjectType):
            return any(p.project_type == item for p in self.bin_lib_dyn_set)
        return False

    def add(self, profile:BinLibDynNode):
        self.bin_lib_dyn_set.add(profile)

    def get(self, project_type: ProjectType) -> BinLibDynNode | None:
        for p in self.bin_lib_dyn_set:
            if p.project_type == project_type:
                return p
        return None 
    
    def get_project_type_name(self) -> set[ProjectType]:
        bin_lib_dyn_names = set[ProjectType]()
        for bin_lib_dyn in self.bin_lib_dyn_set:
            bin_lib_dyn_names.add(bin_lib_dyn.project_type)
        return bin_lib_dyn_names
    
    def merge_commons(self, cxx_compiler: CXXCompilerFlagList, cxx_linker : CXXLinkerFlagList, enable_features: FeatureNameList, feature_rules):
        extended = BinLibDynNodeList()
        for bin_lib_dyn in self.bin_lib_dyn_set:
            extended.add(bin_lib_dyn.merge(cxx_compiler, cxx_linker, enable_features, feature_rules))
        return extended

    def extends(self, bin_lib_dyn_of_base : Self, feature_rules) -> Self :
        extended = BinLibDynNodeList()
        # Get elements in self AND other
        same_name_nodes : set[BinLibDynNode] = self.bin_lib_dyn_set.intersection(bin_lib_dyn_of_base.bin_lib_dyn_set)
        # Get elements not in self and other
        non_commons : set[BinLibDynNode] = self.bin_lib_dyn_set.symmetric_difference(bin_lib_dyn_of_base.bin_lib_dyn_set)

        # Extends the commons and add non common
        for same_name_node in same_name_nodes:
            self_same_name_node = self.get(same_name_node.project_type)
            base_same_name_node = bin_lib_dyn_of_base.get(same_name_node.project_type)
            if (extended_self_same_name_node := self_same_name_node.merge(base_same_name_node.cxx_compiler_flags, base_same_name_node.cxx_linker_flags, base_same_name_node.enable_features, feature_rules)) is None:
                return None
            extended.bin_lib_dyn_set.add(extended_self_same_name_node)
        extended.bin_lib_dyn_set.update(non_commons)
        return extended
    
#############################################################
# ProfileNode add flags and features by profile.
# It also add project specific flags and features for the profile
# Extending it with 'extends' merge all flags and features of the extended into this one
#
# Yaml :
#   <root>
#     compilers|features:               <== 'CompilerNodeList'|'FeatureNodeList'
#       profiles:                       <== 'ProfileNodeList', set of 'ProfileNode'
#         debug|release:                <== 'ProfileNode'
#           extends: common
#           is_abstract: false
#           enable-features: []         <== 'FeatureNameList'
#           cxx-compiler-flags: []      <== 'CXXCompilerFlagList'
#           cxx-linker-flags: []        <== 'CXXLinkerFlagList'
#           dyn|bin|lib:                <== <== 'BinLibDynNodeList', set of 'BinLibDynNode'
# 
#############################################################
class ProfileNode:
    def __init__(self, name: str, is_extended = False):
        # The profile name
        self.name = name
        # The profile used to extends this one
        self.extends_name : str = None
        # If this profile specific is abstract ( Not usable by the user )
        self.is_abstract = False
        # Flags pass to the linker
        self.common_cxx_linker_flags = CXXLinkerFlagList()
        # Flags pass to the compiler
        self.common_cxx_compiler_flags = CXXCompilerFlagList()
        # List of features to enable with this profile
        self.common_enable_features = FeatureNameList()
        # List of project specific flags and features with this profile
        self.bin_lib_dyn_list = BinLibDynNodeList()
        # True if this node is extended
        self.is_extended = is_extended

    def __hash__(self) -> int:
        return hash(self.name)

    def __eq__(self, other) -> bool:
        if not isinstance(other, ProfileNode):
            return NotImplemented
        return self.name == other.name

    def _build_repr(self) -> str:
        lines = [
            f"ProfileNode : {self.name} (abstract:{self.is_abstract}, extends: {self.extends_name}, is_extended {self.is_extended})",
        ]
        lines.append(f"      cxx_compiler_flags: {self.common_cxx_compiler_flags.flags}")
        lines.append(f"      cxx_linker_flags: {self.common_cxx_linker_flags.flags}")
        lines.append(f"      features: {self.common_enable_features.feature_names}")
        lines.append(f"      bin_lib_dyn:")
        for ps in self.bin_lib_dyn_list:
            lines.append(f"        {ps.project_type}:")
            lines.append(f"          cxx_compiler_flags: {ps.cxx_compiler_flags}")
            lines.append(f"          cxx_linker_flags: {ps.cxx_linker_flags}")
            lines.append(f"          features: {ps.enable_features}")
        return "\n".join(lines)

    def __repr__(self) -> str:
        return self._build_repr()

    def __str__(self) -> str:
        return self._build_repr()
    
    def is_feature_rules_valid(self, feature_rules) -> bool:
        assert self.is_extended, f"'{self.name}' must be extended"
        return feature_rules.is_feature_list_validate_rules(self.common_enable_features)
        
    def extends_self(self, feature_rules) -> Self | None:
        assert not self.is_extended, f"'{self.name} is already extended'"
        extended = ProfileNode(self.name, True)
        extended.extends_name = self.extends_name
        extended.is_abstract = self.is_abstract
        extended.common_cxx_compiler_flags = copy.deepcopy(self.common_cxx_compiler_flags)
        extended.common_cxx_linker_flags = copy.deepcopy(self.common_cxx_linker_flags)
        if not feature_rules.is_feature_list_validate_rules(self.common_enable_features):
            return None
        extended.common_enable_features =  copy.deepcopy(self.common_enable_features)
        extended.bin_lib_dyn_list = self.bin_lib_dyn_list.merge_commons(extended.common_cxx_linker_flags,extended.common_cxx_compiler_flags, extended.common_enable_features, feature_rules)
        return extended
    
    def extends(self, base: Self, feature_rules) -> Self :
        assert base.is_extended, f"Base '{base.name}' must be extended"
        assert not self.is_extended, f"'{self.name} is already extended'"
        extended = ProfileNode(self.name, True)
        extended.extends_name = self.extends_name
        extended.is_abstract = self.is_abstract
        extended.common_cxx_compiler_flags = self.common_cxx_compiler_flags.merge(base.common_cxx_compiler_flags)
        extended.common_cxx_linker_flags = self.common_cxx_linker_flags.merge(base.common_cxx_linker_flags)
        extended.common_enable_features = self.common_enable_features.merge(base.common_enable_features, feature_rules)

        # Add project type that does not exists in the project to extends first
        # Merge commons in all project type specifics
        # Then Extends with the base
        # Keep this order, we want to first extends self before adding base, 
        # because we want to override feature in base with feature in self if only-one feature is concerned by this feature
        for project_type in base.bin_lib_dyn_list.get_project_type_name():
            if not project_type in self.bin_lib_dyn_list:
                self.bin_lib_dyn_list.add(BinLibDynNode(project_type))
        
        extended.bin_lib_dyn_list = self.bin_lib_dyn_list.merge_commons(extended.common_cxx_compiler_flags, extended.common_cxx_linker_flags, extended.common_enable_features, feature_rules)
        extended.bin_lib_dyn_list = extended.bin_lib_dyn_list.extends(bin_lib_dyn_of_base=base.bin_lib_dyn_list, feature_rules=feature_rules)
        return extended
    
    def get_enabled_features_list_for_project_type(self, project_type: ProjectType)-> FeatureNameList:
        feature_name_list = FeatureNameList()
        # Add common features
        feature_name_list.add_list(self.common_enable_features)
        # Add project type specific features
        project_specific = self.bin_lib_dyn_list.get(project_type)
        if project_specific:
            feature_name_list.add_list(project_specific.enable_features)
        return feature_name_list
    
##################################################################
# ExtendsCyclicError is raised when a extends cycle is detected
#
##################################################################
class ExtendsCyclicError(Exception):
    def __init__(self, current_node, parent_node, visiting_stack):
        super().__init__()
        self.current_node = current_node
        self.parent_node = parent_node
        self.visiting_stack = visiting_stack

    def __str__(self) -> str:
        parent_name = self.parent_node.name if self.parent_node else "<root>"
        stack = ExtendsCyclicError._format_stack([p.name for p in self.visiting_stack] + [self.current_node.name])
        return f"Error: Cyclic dependency between '{self.current_node.name}' and '{parent_name}'\n{stack}" 
    
    def stack(self) -> list[ProfileNode]:
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
# ProfileNodeList list profile
#
# Yaml:
#   <root>
#     compilers:        <== 'CompilerNodeList'
#       profiles:       <== 'ProfileNodeList', set of 'ProfileNode'
#
######################################################
class ProfileNodeList:
    def __init__(self):
        self.profiles: set[ProfileNode] = set()
    
    def __iter__(self):
        return iter(self.profiles)
    
    def __len__(self):
        return len(self.profiles)
    
    def __contains__(self, profile: ProfileNode) -> bool:
        return profile in self.profiles
    
    def __contains__(self, item) -> bool:
        if isinstance(item, ProfileNode):
            return item in self.profiles
        if isinstance(item, str):
            return any(p.name == item for p in self.profiles)
        return False
    
    def add(self, profile:ProfileNode):
        self.profiles.add(profile)

    def get(self, name: str) -> ProfileNode | None:
        for p in self.profiles:
            if p.name == name:
                return p
        return None 
    
    # Retrieves an extended version of this ProfileNode list.
    # Any ProfileNode that extends another ProfileNode inherits the features and flags
    # of the ProfileNode it extends.
    # For example, if we have two ProfileNodes A and B, where B extends A,
    # the returned list will contain A and B (with B including A's features).
    # Cyclic extensions are also detected.
    def extends_self(self, feature_rules) -> Self | None:
        extended = ProfileNodeList()
        already_extended = ProfileNodeList()
        for profile in self.profiles:
            if profile in already_extended:
                continue
            # Flattens the profile extension chain.
            # This detects extension cycles and orders the list so that
            # base profiles come before the profiles that extend them.
            flatten_profiles: list[ProfileNode] = self.flatten_extends_profile(profile)

            # Get the base that as no 'extends'
            # This is the first profile in the flatten profiles list
            base = already_extended.get(flatten_profiles[0].name) 
            if not base:
                base = flatten_profiles[0].extends_self(feature_rules)
                if not base:
                    console.print_error(f"   When validating rules for '{flatten_profiles[0].name}' profile.")
                    return None
                extended.add(base)
                already_extended.add(base)
            # Extends the rest
            for p in flatten_profiles[1:]:
                # Extend only once
                extended_p = already_extended.get(p.name) 
                if not extended_p:
                    extended_p = p.extends(base, feature_rules)
                    if not extended_p.is_feature_rules_valid(feature_rules):
                        console.print_error(f"   When validating rules for '{p.name}' profile.")
                        return None
                    extended.add(extended_p)
                    already_extended.add(extended_p)
                base = extended_p
                
        return extended

    def get_extended_with_base(self, profiles_of_base : Self, feature_rules) -> Self | None :
        if(self_extended := self.extends_self(feature_rules)) is None:
            return None
        
        extended = ProfileNodeList()
        # Get elements in self AND profiles_of_base
        common_profiles : set[ProfileNode] = self_extended.profiles.intersection(profiles_of_base.profiles)
        # Get elements not in self and profiles_of_base
        non_common_profiles : set[ProfileNode] = self_extended.profiles.symmetric_difference(profiles_of_base.profiles)

        # Extends the common profiles with the base profiles
        for common_profile in common_profiles:
            self_common_profile = self_extended.get(common_profile.name)
            base_profile = profiles_of_base.get(self_common_profile.name)
            # At this point, profile is only extends with itself, mark it a not extended to extends with a base after
            self_common_profile.is_extended = False
            if (extended_profile := self_common_profile.extends(base_profile, feature_rules)) is None:
                return None
            extended.profiles.add(extended_profile)

        # juste add non common profiles
        extended.profiles.update(non_common_profiles)

        return extended

    def flatten_extends_profile(self, profile: ProfileNode) -> list[ProfileNode]:
        # 1. Collecte du sous-graphe (DFS)
        all_profiles: list[ProfileNode] = list()
        visiting_stack: list[ProfileNode] = []
       
        def collect(current_node : ProfileNode, parent_node: ProfileNode):
            # Detect cyclic dependency
            if current_node in visiting_stack:
                raise ExtendsCyclicError(current_node, parent_node, visiting_stack)

            # Visit the project only once
            if current_node in all_profiles:
                return
            visiting_stack.append(current_node)
 
            # Visit extends
            if current_node.extends_name:
                extends_node = self.get(current_node.extends_name)
                if not extends_node:
                    console.print_error(f"❌ '{current_node.name}' profile extends unknown compiler '{current_node.extends_name}'")
                    exit(1)
                collect(extends_node, current_node)
            
            # Remove visited project
            visiting_stack.pop()
            all_profiles.append(current_node)
        collect(profile, None)
        return all_profiles
    
    def get_profile_names(self) -> set[str]:
        profiles = set[str]()
        for profile in self.profiles:
            profiles.add(profile.name)
        return profiles
    
    def get_enabled_features_list_for_profile_and_project_type(self, profile_name: str, project_type: ProjectType)-> FeatureNameList:
        profile_info = self.get(profile_name)
        if profile_info:
            return profile_info.get_enabled_features_list_for_project_type(project_type)
        return FeatureNameList()
    
######################################################
# FeatureNodeList list features
#
# Yaml:
#   <root>
#     compilers:          <== 'CompilerNodeList'
#       clang:            <== 'CompilerNode'
#         features:       <== 'FeatureNodeList'
#
######################################################
class FeatureNodeList:
    def __init__(self):
        self.features : set[FeatureNode] = set()

    def __iter__(self):
        return iter(self.features)
    
    def __len__(self):
        return len(self.features)
        
    def __contains__(self, item) -> bool:
        if isinstance(item, FeatureNode):
            return item in self.features
        if isinstance(item, str):
            return any(f.name == item for f in self.features)
        return False

    def add(self, feature:FeatureNode):
        self.features.add(feature)

    def get(self, name: str) -> FeatureRuleNode | None:
        for f in self.features:
            if f.name == name:
                return f
        return None
    
    def extends_self(self, compiler_node) -> Self:
        extended = FeatureNodeList()
        for feature in self.features:
            extended.add(feature.extends_self(compiler_node))
        return extended

    def get_extended_with_base(self, base : Self) -> Self | None :
        extended = FeatureNodeList()
        # Get elements in self AND base
        common_features : set[FeatureNode] = self.features.intersection(base.features)
        # Get elements not in self and base
        non_commons_features : set[FeatureNode] = self.features.symmetric_difference(base.features)
        # Extends the common_feature_nodes and add the non common features
        if common_features:
            console.print_error(f"❌ Feature with same name both target [ {', '.join(f.name for f in common_features)} ]")
            return None
        extended.features.update(common_features)
        extended.features.update(non_commons_features)
        
        return extended
    
    def get_profile_names(self) -> set[str]:
        profiles = set[str]()
        for feature in self.features:
            profiles.update(feature.get_profile_names())
        return profiles
    
##################################################################################
# FeatureRuleNodeOnlyOne ensures that only one feature can be enabled from a feature list.
#
# Enabling more than one feature in the same compiler raises an error.
# Enabling a feature in a derived compiler overrides the feature enabled in the base compiler.
# 
# Yaml :
#  - only-one: warning       <== 'FeatureRuleNodeOnlyOne'
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
class FeatureRuleNodeOnlyOne(FeatureRuleNode):
    KEY = "only-one"
    ResultOnlyOne = Union[str, FeatureNameList, None]

    def __init__(self, name: str):
        super().__init__(name)
        self.feature_list = FeatureNameList()

    def evaluate(self, feature_list: FeatureNodeList) -> ResultOnlyOne:
        common = self.feature_list.feature_names.intersection(feature_list)
        match len(common):
            case 0:
                return None
            case 1:
                return next(iter(common))
            case _:
                result = FeatureNameList()
                result.add_list(list(common))
                return result
    def is_satisfied(self, enabled_features: FeatureNodeList) -> bool:
        return self.evaluate(enabled_features) is str()
    
    def __contains__(self, feature_name: str) -> bool:
        return feature_name in self.feature_list
    
##################################################################################
# FeatureRuleNodeIncompatibleWith
#
# Defines a feature that is incompatible with one or more other features.
# If the feature and at least one incompatible feature are enabled in any compiler,
# an error is raised.
#
# YAML:
#  - incompatible: no_opt      <== 'FeatureRuleNodeIncompatibleWith'
#    feature: OPT_LEVEL_0
#    with: [LTCG, LTO, OMIT_FRAME_POINTER]
#
# Example:
#  - If the feature 'OPT_LEVEL_0' is enabled in any compiler and at least one feature
#    from the 'with' list is also enabled (in any compiler), an error is raised.
#
##################################################################################
class FeatureRuleNodeIncompatibleWith(FeatureRuleNode):
    KEY = "incompatible"

    def __init__(self, name: str):
        super().__init__(name)
        self.feature_name = ""
        self.incompatible_with = FeatureNameList() 

    def is_satisfied(self, enabled_features: FeatureNodeList) -> FeatureNodeList:
        if self.feature_name in enabled_features:
            incompatible_features = self.incompatible_with.feature_names.intersection(enabled_features)
            if incompatible_features:
                return incompatible_features
        return set()


###############################################################
# FeatureRuleNodeList is list of FeatureRuleNode
#
# Yaml:
#   <root>
#     compilers:              <== 'CompilerNodeList'
#       clang:                <== 'CompilerNode'
#         feature-rules:      <== 'FeatureRuleNodeList', set of 'FeatureRuleNode'
#
###############################################################
class FeatureRuleNodeList:
    def __init__(self):
        self.feature_rules : set[FeatureRuleNode] = set()
    
    def __iter__(self):
        return iter(self.feature_rules)
    
    def __len__(self):
        return len(self.feature_rules)
    
    def __contains__(self, item) -> bool:
        if isinstance(item, FeatureRuleNode):
            return item in self.feature_rules
        if isinstance(item, str):
            return any(t.name == item for t in self.feature_rules)
        return False
    
    def add(self, feature_rule:FeatureRuleNode):
        self.feature_rules.add(feature_rule)
        
    def get(self, name: str) -> FeatureRuleNode | None:
        for f in self.feature_rules:
            if f.name == name:
                return f
        return None 
    
    def get_extended_with(self, base : Self) -> Self | None:
        extended = FeatureRuleNodeList()
        # Get elements in self AND base
        common_feature_rules : set[FeatureNode] = self.feature_rules.intersection(base.feature_rules)
        # Get elements not in self and base
        non_commons_feature_rules : set[FeatureNode] = self.feature_rules.symmetric_difference(base.feature_rules)
        # Extends the common_feature_nodes and add the non common feature rules
        if common_feature_rules:
             console.print_error(f"❌ Feature rule with same name both target [ {', '.join(f.name for f in common_feature_rules)} ]")
             return None
        extended.feature_rules.update(common_feature_rules)
        extended.feature_rules.update(non_commons_feature_rules)
        return extended

    def is_feature_list_validate_rules(self, feature_list: FeatureNodeList) -> bool:
        for feature_rule in self.feature_rules:
            match feature_rule:
                case FeatureRuleNodeOnlyOne() as only_one_rule:
                    result = only_one_rule.evaluate(feature_list)
                    match result:
                        case FeatureNameList() as mutliple_feature:
                            console.print_error(f"❌ Feature rule '{FeatureRuleNodeOnlyOne.KEY}' not satisfied. [ {', '.join(list(mutliple_feature))} ] are enabled but only one in allowed.")
                            return False
                case FeatureRuleNodeIncompatibleWith() as incompatible_rule:
                    list_of_incompatible_feature =  incompatible_rule.is_satisfied(feature_list)
                    if list_of_incompatible_feature:
                        console.print_error(f"❌ Feature rule '{FeatureRuleNodeIncompatibleWith.KEY}' not satisfied. [ {', '.join(list_of_incompatible_feature)} ] are incompatible with '{incompatible_rule.feature_name}' ")
                        return False
        return True
    
    # Merge 2 features name list
    # - If 'list_base' and 'list_extends' contains feature name that exists in a 'only-one' rule
    #   We don't add 'list_base' but 'list_extends'. 
    #   Error when 'list_base' contains more that 1 elements on 'only-one', same for 'list_extends'
    # - If 'list_base' and 'list_extends' contains feature name that exists in a 'incompatible' rule
    #   Error
    def merge_feature_name_list(self, list_base: FeatureNameList, list_extends: FeatureNameList) -> FeatureNameList:
        # Check that list_extends validate feature-rules before merging
        # We check list_base after that
        if not self.is_feature_list_validate_rules(list_extends):
            console.print_error(f"Rule '{FeatureRuleNodeOnlyOne.KEY}' invalidate feature list '{' , '.join(list_extends.feature_names)}' ")
            return None
        
        only_one_rules = [
            rule
            for rule in self.feature_rules
            if isinstance(rule, FeatureRuleNodeOnlyOne)
        ]
        cleaned_list_base = copy.deepcopy(list_base)
        for only_one_rule in only_one_rules:
            result = FeatureRuleNodeOnlyOne.ResultOnlyOne = only_one_rule.evaluate(list_base)
            match result:
                # One feature name is present in list_base that is also present in 'only-one' rule
                case str() as base_feature_name:
                    # We have a feature name in list_base that is concerned by this rule,
                    # Check if the rule also concern list_extends
                    result = FeatureRuleNodeOnlyOne.ResultOnlyOne = only_one_rule.evaluate(list_extends)
                    match result:
                        # One feature name is present in list_extends that is also present in list_base and 'only-one' rule
                        case str() as extends_feature_name:
                            # We have one feature name in list_base and one in list_extends
                            # We keep the one in list_extends
                            cleaned_list_base.remove(base_feature_name)
                # Multiple feature name is present in list_base that is also present in 'only-one' rule
                case FeatureNameList() as mutliple_feature:
                    console.print_error(f"Rule '{FeatureRuleNodeOnlyOne.KEY}' invalidate feature list '{' , '.join(list(mutliple_feature.feature_names))}' ")
                # No feature name is present in list_base that is also present in 'only-one' rule
                case None:
                    pass

        # Merge cleaned_list_base and list_extends    
        result = FeatureNameList()
        result.feature_names = cleaned_list_base.union(list_extends)
        return result

######################################################
# CompilerNode
#
# Yaml:
#   <root>
#     compilers:     <== 'CompilerNodeList'
#       clang:       <== 'CompilerNode'
######################################################
class CompilerNode:
    def __init__(self, name: str, is_extended: bool = False):
        # The compiler name
        self.name = name
        # If this compiler is abstract ( Not usable by the user )
        self.is_abstract = False
        # The compiler used extends this one
        self.extends_name : str = None
        # List of profiles
        self.profiles = ProfileNodeList()
        # List of features
        self.features = FeatureNodeList()
        # List of feature rules that are common to all profiles
        self.feature_rules = FeatureRuleNodeList()
        # The file where the compiler was loaded
        self.file = Path()
        # True if this node is extended
        self.is_extended = is_extended

    def __hash__(self) -> int:
        return hash(self.name)

    def __eq__(self, other) -> bool:
        if not isinstance(other, CompilerNode):
            return NotImplemented
        return self.name == other.name
    
    def _build_repr(self) -> str:
        lines = [
            f"CompilerNode : {self.name} (abstract:{self.is_abstract}, extends: {self.extends_name}, is_extended {self.is_extended})",
            "  Profiles :",
        ]
        for profile in self.profiles:
            lines.append(f"   - {profile.name} (extends: {profile.extends_name})")
            lines.append(f"      cxx_compiler_flags: {profile.common_cxx_compiler_flags.flags}")
            lines.append(f"      cxx_linker_flags: {profile.common_cxx_linker_flags}")
            lines.append(f"      features: {profile.common_enable_features}")
            lines.append(f"      bin_lib_dyn:")
            for ps in profile.bin_lib_dyn_list:
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
                raise ExtendsCyclicError(current_node, parent_node, visiting_stack)

            # Visit the project only once
            if current_node in all_profiles:
                return
            visiting_stack.append(current_node)
 
            # Visit extends
            if current_node.extends_name:
                extends_node = CompilerNodeRegistry.get(current_node.extends_name)
                if not extends_node:
                    console.print_error(f"❌ '{current_node.name}' profile extends unknown compiler '{current_node.extends_name}'")
                    exit(1)
                collect(extends_node, current_node)
            
            # Remove visited project
            visiting_stack.pop()
            all_profiles.append(current_node)
        collect(self, None)
        return all_profiles
    
   
    def get_profile_names(self) -> set[str]:
        profiles = set[str]()
        profiles.update(self.profiles.get_profile_names())
        profiles.update(self.features.get_profile_names())
        return profiles

    @staticmethod
    def _extend_no_base_then_validate_features(to_extend_compiler_node: Self) -> Self | None:
        assert not to_extend_compiler_node.is_extended, f"'{to_extend_compiler_node.name}' Already extended"
        
        if(extended := ExtendedCompilerNodeRegistry.get(to_extend_compiler_node.name)) is None:
            extended = CompilerNode(to_extend_compiler_node.name, is_extended=True)
            extended.file = to_extend_compiler_node.file
            extended.extends_name = to_extend_compiler_node.extends_name
            extended.file = to_extend_compiler_node.file
            extended.feature_rules = copy.deepcopy(to_extend_compiler_node.feature_rules)
            extended.features = to_extend_compiler_node.features.extends_self(extended.feature_rules)
            if (extended_profiles := to_extend_compiler_node.profiles.extends_self(extended.feature_rules)) is None:
                console.print_error(f"   When extending '{to_extend_compiler_node.name}' compiler")
                return None
            extended.profiles = extended_profiles

            
            console.print_tips(extended)
            ExtendedCompilerNodeRegistry.register_extended_compiler(extended)
        assert extended.is_extended
        return extended
            
    @staticmethod
    def _extend_and_validate_features(base_compiler_node: Self, to_extend_compiler_node: Self) -> Self | None:
        assert base_compiler_node.is_extended, f"'Base {base_compiler_node.name}' must be extended"
        assert not to_extend_compiler_node.is_extended, f"'{to_extend_compiler_node.name}' Already extended"
        if(extended := ExtendedCompilerNodeRegistry.get(to_extend_compiler_node.name)) is None:
            extended = CompilerNode(to_extend_compiler_node.name, is_extended=True)
            extended.file = to_extend_compiler_node.file
            extended.extends_name = to_extend_compiler_node.extends_name
            # Check that the base compiler node match the 'extends' 
            if to_extend_compiler_node.extends_name != base_compiler_node.name:
                console.print_error(f"Incoherent target extends: Try to extend '{to_extend_compiler_node.name}' with '{base_compiler_node.name}' but '{to_extend_compiler_node.name}' extends '{to_extend_compiler_node.extends_name}' ")
                exit(1)

            # Extend feature rules
            extended.feature_rules = to_extend_compiler_node.feature_rules.get_extended_with(base_compiler_node.feature_rules)
            if not extended.feature_rules:
                console.print_error(f"❌ Fail to extend '{to_extend_compiler_node.name}' with base '{to_extend_compiler_node.extends_name}'")
                return None
            
            # Extend profiles
            ##extended_profile = to_extend_compiler_node.profiles.extends_self(extended.feature_rules)
            extended.profiles = to_extend_compiler_node.profiles.get_extended_with_base(base_compiler_node.profiles, extended.feature_rules)
            if not extended.profiles:
                console.print_error(f"❌ Fail to extend '{to_extend_compiler_node.name}' with base '{to_extend_compiler_node.extends_name}'")
                return None
            
            # Extend features
            extended_features = to_extend_compiler_node.features.extends_self(extended.feature_rules)
            extended.features = extended_features.get_extended_with_base(base_compiler_node.features)
            if not extended.features:
                console.print_error(f"❌ Fail to extend '{to_extend_compiler_node.name}' with base '{to_extend_compiler_node.extends_name}'")
                return None
            
            # Validate features
            console.print_tips(extended)
            if not extended.validate_features():
                if extended.extends_name:
                    console.print_error(f"   Failed to validate feature rules after extending '{extended.name}' with '{extended.extends_name}'.")
                else:
                    console.print_error(f"   Failed to validate feature rules on target {extended.name}.")
                return None
            
            # Register for futur use
            ExtendedCompilerNodeRegistry.register_extended_compiler(extended)
        assert extended.is_extended
        return extended

    def extends_self(self) -> Self | None:
        
        # Flattening the compiler hierarchy establishes a dependency order.
        # This ensures safe iteration where all included compilers are
        # resolved before the compiler that extends them.
        # In other words, if compiler A extends B, then B appears before A.
        flatten_compiler_extends = self.flatten_extends_compilers()
        console.print_tips(f"{self.name} : [ {' -> '.join([p.name for p in flatten_compiler_extends])} ]")

        # Start by extending the top-most base compiler and validate features
        # at each level until we reach the target compiler.
        base_compiler_node: CompilerNode = CompilerNodeRegistry.get(flatten_compiler_extends[0].name)
        to_extend_compiler_node: CompilerNode = CompilerNodeRegistry.get(flatten_compiler_extends[1].name) if len(flatten_compiler_extends) > 1 else None

        # Extend the base
        if (base_compiler_node := CompilerNode._extend_no_base_then_validate_features(base_compiler_node)) is None:
            return None
        # If there is no compiler to extend from the base, return the to_extend_compiler_node base directly
        if not to_extend_compiler_node:
           return base_compiler_node

        # If there is an to_extend_compiler_node compiler, combine it with the base.
        # The result becomes the new base for the next compiler in the extension chain.
        if (base_compiler_node := CompilerNode._extend_and_validate_features(base_compiler_node, to_extend_compiler_node)) is None:
            return None
        
        # Extend the base with all subsequent compilers in the list.
        # This is analogous to: ((((A + B) + C) + D) + E)
        # where each intermediate result becomes the new 'base' for the next extension.
        for to_extend_compiler_node in flatten_compiler_extends[2:]:
            if (base_compiler_node := CompilerNode._extend_and_validate_features(base_compiler_node, to_extend_compiler_node)) is None:
                return None
        return base_compiler_node
    
    def validate_features(self) -> bool:
        assert self.is_extended, f"'{self.name}' must be extended"

        # Order profiles to validate from base to bottom
        already_validated_profiles = set[ProfileNode]()
        for profile in self.profiles:
             for profile in self.profiles.flatten_extends_profile(profile):
                if not profile in already_validated_profiles:
                    if not profile.is_feature_rules_valid(self.feature_rules):
                        console.print_error(f"   When validating rules for '{profile.name}' profile in '{self.name}' compiler.")
                        return False
                    already_validated_profiles.add(profile)
        return True
    
################################################
# List of compilers in file
#
# Yaml:
#   <root>
#     compilers: <== 'CompilerNodeList'
################################################
class CompilerNodeList:
    def __init__(self):
        self.compilers : set[CompilerNode] = set()

    def __iter__(self):
        return iter(self.compilers)
    
    def __len__(self):
        return len(self.compilers)
    
    def __contains__(self, item) -> bool:
        if isinstance(item, CompilerNode):
            return item in self.compilers
        if isinstance(item, str):
            return any(t.name == item for t in self.compilers)
        return False

    def add(self, compiler:CompilerNode):
        self.compilers.add(compiler)

    def get(self, name: str) -> CompilerNode | None:
        for t in self.compilers:
            if t.name == name:
                return t
        return None

    def get_extended(self) -> Self :
        extended = CompilerNodeList()
        for compiler in self.compilers:
            extended.add(compiler.get_extended())
        return extended

################################################
# List of 'CompilerNode' loaded by files
################################################
class CompilerNodeRegistry:
    def __init__(self):
        self.compilers = CompilerNodeList()
    
    def __contains__(self, name: str) -> bool:
        return name in self.compilers

    def __iter__(self):
        return iter(self.compilers)
    
    def get(self, name: str) -> CompilerNode | None:
        return self.compilers.get(name)

    def register_compiler(self, compiler: CompilerNode):
        existing_compiler = self.compilers.get(compiler.name)
        if existing_compiler:
            console.print_error(f"⚠️  Warning: Compiler node already registered: {existing_compiler.name} in {str(existing_compiler.file)}")
            exit(1)
        self.compilers.add(compiler)


CompilerNodeRegistry = CompilerNodeRegistry()


################################################
# List of 'ExtendedCompilerNode' loaded by files
################################################
class ExtendedCompilerNodeRegistry:
    def __init__(self):
        self.compilers = CompilerNodeList()
    
    def __contains__(self, name: str) -> bool:
        return name in self.compilers

    def __iter__(self):
        return iter(self.compilers)
    
    def get(self, name: str) -> CompilerNode | None:
        return self.compilers.get(name)

    def register_extended_compiler(self, compiler: CompilerNode):
        assert compiler.is_extended
        existing_compiler = self.compilers.get(compiler.name)
        if existing_compiler:
            console.print_error(f"⚠️  Warning: Extended csompiler node already registered: {existing_compiler.name} in {str(existing_compiler.file)}")
            exit(1)
        self.compilers.add(compiler)


ExtendedCompilerNodeRegistry = ExtendedCompilerNodeRegistry()