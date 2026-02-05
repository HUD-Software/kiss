
from pathlib import Path
from typing import Self
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
    
    def extend_with_list(self, flags: list[str]):
        for f in flags:
            self.add(f)

    def get_extended_with(self, base : Self) -> Self:
        # Flags are just merge, duplicate are removed
        extended = FlagList()
        extended.flags = self.flags.union(base.flags)
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

    def get_extended_with(self, base : Self) -> Self:
        # Flags are just merge, duplicate are removed
        extended = FeatureNameList()
        extended.feature_names = self.feature_names.union(base.feature_names)
        return extended

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

    def get_extended(self) -> Self:
        extended = FeatureNode(self.name)
        extended.cxx_linker_flags = self.cxx_linker_flags
        extended.cxx_compiler_flags = self.cxx_compiler_flags
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

    def get_extended_with(self, base : Self) -> Self:
        extended = CXXCompilerFlagList()
        extended.flags = self.flags.get_extended_with(base.flags)
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

    def get_extended_with(self, base : Self) -> Self:
        extended = CXXLinkerFlagList()
        extended.flags = self.flags.get_extended_with(base.flags)
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
        return f"""{self.project_type}:
    cxx_linker_flags : {self.cxx_linker_flags}
    cxx_compiler_flags : {self.cxx_compiler_flags}
    enable_features : {self.enable_features}"""
    
    def __str__(self) -> str:
        return str(self.flags)  
    
    def get_extended_with(self, base : Self) -> Self :
        if self.project_type != base.project_type:
            console.print_error(f"❌ Extend project specific {self.project_type} with different type is impossible {self.project_type} extended with {base.project_type}")
            exit(1)
        extended = BinLibDynNode(self.project_type)
        extended.cxx_compiler_flags = self.cxx_compiler_flags.get_extended_with(base.cxx_compiler_flags)
        extended.cxx_linker_flags = self.cxx_linker_flags.get_extended_with(base.cxx_linker_flags)
        extended.enable_features = self.enable_features.get_extended_with(base.enable_features)
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
        self.bin_lib_dyn: set[BinLibDynNode] = set()
    
    def __iter__(self):
        return iter(self.bin_lib_dyn)
    
    def __len__(self):
        return len(self.bin_lib_dyn)
    
    def __contains__(self, project_specific: BinLibDynNode) -> bool:
        return project_specific in self.bin_lib_dyn
    
    def __contains__(self, item) -> bool:
        if isinstance(item, BinLibDynNode):
            return item in self.bin_lib_dyn
        if isinstance(item, ProjectType):
            return any(p.project_type == item for p in self.bin_lib_dyn)
        return False

    def add(self, profile:BinLibDynNode):
        self.bin_lib_dyn.add(profile)

    def get(self, project_type: ProjectType) -> BinLibDynNode | None:
        for p in self.bin_lib_dyn:
            if p.project_type == project_type:
                return p
        return None 
    
    def get_extended_with(self, base : Self) -> BinLibDynNode :
        extended = BinLibDynNodeList()
        # Get elements in self AND base
        commons : set[BinLibDynNode] = self.bin_lib_dyn.intersection(base.bin_lib_dyn)
        # Get elements not in self and base
        non_commons : set[BinLibDynNode] = self.bin_lib_dyn.symmetric_difference(base.bin_lib_dyn)
        # Extends the commons and add non common
        for common in commons:
            extended.bin_lib_dyn.add(common.get_extended_with(base.get(common.project_type)))
        extended.bin_lib_dyn.update(non_commons)
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
        self.bin_lib_dyn = BinLibDynNodeList()

    def __hash__(self) -> int:
        return hash(self.name)

    def __eq__(self, other) -> bool:
        if not isinstance(other, ProfileNode):
            return NotImplemented
        return self.name == other.name

    def get_extended_with(self, base: Self) -> Self :
        extended = ProfileNode(self.name)
        extended.cxx_compiler_flags = self.cxx_compiler_flags.get_extended_with(base.cxx_compiler_flags)
        extended.cxx_linker_flags = self.cxx_linker_flags.get_extended_with(base.cxx_linker_flags)
        extended.enable_features = self.enable_features.get_extended_with(base.enable_features)
        extended.bin_lib_dyn = self.bin_lib_dyn.get_extended_with(base.bin_lib_dyn)
        return extended
    
    def get_enabled_features_list_for_project_type(self, project_type: ProjectType)-> FeatureNameList:
        feature_name_list = FeatureNameList()
        # Add common features
        feature_name_list.extend_with_list(self.enable_features)
        # Add project type specific features
        project_specific = self.bin_lib_dyn.get(project_type)
        if project_specific:
            feature_name_list.extend_with_list(project_specific.enable_features)
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
    def get_extended(self) -> Self:
        extended = ProfileNodeList()
        already_extended = set[ProfileNode]()
        for profile in self.profiles:
            if profile in already_extended:
                continue
            # Flattens the profile extension chain.
            # This detects extension cycles and orders the list so that
            # base profiles come before the profiles that extend them.
            flatten_profiles = self.flatten_extends_profile(profile)
            # Now we can iterate over the flattened profiles.
            # Because each node can only extend a single profile,
            # we are guaranteed that the base profile (at index i-1)
            # appears immediately before the current profile (at index i).
            for i, extend_profile in enumerate(flatten_profiles):
                # If the profile extends another one, extend it;
                # otherwise, just add it as is.
                if extend_profile.extends:
                    extended.add(extend_profile.get_extended_with(flatten_profiles[i-1]))
                else:
                    extended.add(extend_profile)
                already_extended.add(extend_profile)
        return extended


    def get_extended_with(self, base : Self) -> Self :
        extended = ProfileNodeList()
        # Get elements in self AND base
        commons : set[ProfileNode] = self.profiles.intersection(base.profiles)
        # Get elements not in self and base
        non_commons : set[ProfileNode] = self.profiles.symmetric_difference(base.profiles)

        # Extends the commons and add the non common
        for common in commons:
            extended.profiles.add(common.get_extended_with(base.get(common.name)))
        extended.profiles.update(non_commons)
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
    
    def get_extended(self) -> Self:
        extended = FeatureNodeList()
        for feature in self.features:
            extended.add(feature.get_extended())
        return extended

    def get_extended_with(self, base : Self) -> Self | None :
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
        
        # Extend feature
        extended = extended.get_extended()
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

    def __init__(self, name: str):
        super().__init__(name)
        self.feature_list = FeatureNameList()

    def is_satisfied(self, feature_list: FeatureNodeList) -> FeatureNodeList:
        common = self.feature_list.feature_names.intersection(feature_list)
        if len(common) > 1:
            return common
        return set()
    
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
                    list_invalid = only_one_rule.is_satisfied(feature_list)
                    if list_invalid:
                        console.print_error(f"❌ Feature rule '{FeatureRuleNodeOnlyOne.KEY}' not satisfied. [ {', '.join(list_invalid)} ] are enabled but only one in allowed.")
                        return False
                case FeatureRuleNodeIncompatibleWith() as incompatible_rule:
                    list_of_incompatible_feature =  incompatible_rule.is_satisfied(feature_list)
                    if list_of_incompatible_feature:
                        console.print_error(f"❌ Feature rule '{FeatureRuleNodeIncompatibleWith.KEY}' not satisfied. [ {', '.join(list_of_incompatible_feature)} ] are incompatible with '{incompatible_rule.feature_name}' ")
                        return False
        return True
    
######################################################
# CompilerNode
#
# Yaml:
#   <root>
#     compilers:     <== 'CompilerNodeList'
#       clang:       <== 'CompilerNode'
######################################################
class CompilerNode:
    def __init__(self, name: str):
        # The compiler name
        self.name = name
        # If this compiler is abstract ( Not usable by the user )
        self.is_abstract = False
        # The compiler used extends this one
        self.extends : str = None
        # List of profiles
        self.profiles = ProfileNodeList()
        # List of features
        self.features = FeatureNodeList()
        # List of feature rules
        self.feature_rules = FeatureRuleNodeList()
        # The file where the compiler was loaded
        self.file = Path()

    def __hash__(self) -> int:
        return hash(self.name)

    def __eq__(self, other) -> bool:
        if not isinstance(other, CompilerNode):
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
            lines.append(f"      bin_lib_dyn:")
            for ps in profile.bin_lib_dyn:
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
            if current_node.extends:
                extends_node = CompilerNodeRegistry.get(current_node.extends)
                if not extends_node:
                    console.print_error(f"❌ '{current_node.name}' profile extends unknown compiler '{current_node.extends}'")
                    exit(1)
                collect(extends_node, current_node)
            
            # Remove visited project
            visiting_stack.pop()
            all_profiles.append(current_node)
        collect(self, None)
        return all_profiles
    
    def get_extended_with(self, base: Self) -> Self :
        extended = CompilerNode(self.name)
        extended.file = self.file
        extended.profiles = self.profiles.get_extended().get_extended_with(base.profiles.get_extended())
        extended.features = self.features.get_extended().get_extended_with(base.features)
        extended.feature_rules = self.feature_rules.get_extended_with(base.feature_rules)
        return extended
    
    def get_profile_names(self) -> set[str]:
        profiles = set[str]()
        profiles.update(self.profiles.get_profile_names())
        profiles.update(self.features.get_profile_names())
        return profiles

    def get_extended(self) -> Self | None:
        # Flattening the compiler hierarchy establishes a dependency order.
        # This ensures safe iteration where all included compilers are
        # resolved before the compiler that extends them.
        # In other words, if compiler A extends B, then B appears before A.
        flatten_extends_compilers = self.flatten_extends_compilers()
        console.print_tips(f"{self.name} : [ {' -> '.join([p.name for p in flatten_extends_compilers])} ]")

        # Start by extending the top-most base compiler and validate features
        # at each level until we reach the target compiler.
        base: CompilerNode = CompilerNodeRegistry.get(flatten_extends_compilers[0].name)
        extended: CompilerNode = CompilerNodeRegistry.get(flatten_extends_compilers[1].name)

        def extend_with_and_validate_features(base: CompilerNode, extended: CompilerNode):
            result = None
            if extended:
                result = extended.get_extended_with(base)
            else:
                result = base.get_extended()
            if not result.validate_features():
                if result.extends:
                    console.print_error(f"   Failed to validate feature rules after extending '{result.name}' with '{result.extends}'.")
                else:
                    console.print_error(f"   Failed to validate feature rules on target {result.name}.")
                return None
            return result
    
        # If there is no compiler to extend from the base, return the extended base directly
        if not extended:
           return extend_with_and_validate_features(base, None)
        
        
        
        # If there is an extended compiler, combine it with the base.
        # The result becomes the new base for the next compiler in the extension chain.
        base = extend_with_and_validate_features(base, extended)
        
        # Extend the base with all subsequent compilers in the list.
        # This is analogous to: ((((A + B) + C) + D) + E)
        # where each intermediate result becomes the new 'base' for the next extension.
        for extended in flatten_extends_compilers[2:]:
            base = extend_with_and_validate_features(base, extended)

        return base
    
    def get_extended_with(self, other_compiler_node: Self):
        extended = CompilerNode(self.name)
        extended.file = self.file
        extended.extends = self.extends
        if self.extends:
            if not other_compiler_node:
                console.print_error(f"❌ '{self.name}' extends an unknown target '{self.extends}'")
                return None
            if self.extends != other_compiler_node.name:
                console.print_error(f"Incoherent target extends: Try to extend '{self.name}' with '{other_compiler_node.name}' but '{self.name}' extends '{self.extends}' ")
                exit(1)
            extended.profiles = self.profiles.get_extended().get_extended_with(other_compiler_node.profiles.get_extended())
            extended.features = self.features.get_extended().get_extended_with(other_compiler_node.features)
            if not extended.features:
                console.print_error(f"❌ Fail to extend '{self.name}' with base '{self.extends}'")
                return None
            extended.feature_rules = self.feature_rules.get_extended_with(other_compiler_node.feature_rules)
            if not extended.feature_rules:
                console.print_error(f"❌ Fail to extend '{self.name}' with base '{self.extends}'")
                return None
        else:
            extended.file = self.file
            extended.profiles = self.profiles.get_extended()
            extended.features = self.features.get_extended()
            extended.feature_rules = copy.deepcopy(self.feature_rules)
        return extended

    def validate_features(self) -> bool:
        # Retrieves feature list for each profile and project type
        # [debug, bin], [release, bin], [debug, lib], [custom, lib] etc...
        # Then for all thoses pairs, validate enabled features
        all_profile_names : set[str] = self.get_profile_names()
        for profile_name in all_profile_names:
            for project_type  in ProjectType:
                feature_list : FeatureNodeList = self.profiles.get_enabled_features_list_for_profile_and_project_type(profile_name, project_type)
                if not self.feature_rules.is_feature_list_validate_rules(feature_list):
                    console.print_error(f"   When validating rules for '{project_type}' project with '{profile_name}' profile.")
                    return False
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