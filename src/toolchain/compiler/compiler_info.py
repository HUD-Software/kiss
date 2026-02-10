
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
    def __init__(self, is_extended = False):
        self.feature_names = set[str]()
        self.is_extended = is_extended
        
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
    
    # Extend this feature name list
    # This is similar to extend but we don't merge with a base, we just add enabled features by the features in this list
    # and check that the result validate feature rules
    def extend_self(self, compiler_features, compiler_feature_rules) -> Self | None:
        return self.extend(base_enable_features=FeatureNameList(is_extended=True), 
                           compiler_features=compiler_features, 
                           compiler_feature_rules=compiler_feature_rules)
    
    # Extend this feature name list with another feature name list.
    # This is a merge but with some rules:
    #  - If the list is not extended, we add all features enabled by the features in this lis
    #    e.g. If we have feature A that enable feature B, and we add B in this list ( A is already in the list).
    #  - We check that the merge of the two list validate the feature rules, if not we return None
    #  - For the rule 'only-one', if we have a feature name in self and a feature name in base_enable_features that are in the same 'only-one' rule, we keep the one in self
    def extend(self, base_enable_features: Self, compiler_features, compiler_feature_rules) -> Self | None:
        if not self.is_extended:
            # Add enabled feature that feature enables
            to_process = list(self)
            while to_process:
                feature_name = to_process.pop()

                if (feature := compiler_features.get(feature_name)) is None:
                    console.print_error(f"❌ Feature {feature_name} not found")
                    return None

                for new_feature in feature.enable_features:
                    if new_feature not in self:  # éviter doublons
                        if (feature2 := compiler_features.get(new_feature)) is None:
                            console.print_error(f"❌ Feature {new_feature} not found")
                            return None
                        self.add(new_feature)
                        to_process.append(new_feature)

        # Check that self validate feature-rules before merging
        # We check base after that
        # Merge 2 features name list
        # - If 'base' and 'self' contains feature name that exists in a 'only-one' rule
        #   We don't add 'base' but 'self'. 
        #   Error when 'base' contains more that 1 elements on 'only-one', same for 'self'
        # - If 'base' and 'self' contains feature name that exists in a 'incompatible' rule
        #   Error
        if not compiler_feature_rules.is_feature_list_validate_rules(self):
            console.print_error(f"Rule invalidate feature list '{', '.join(list(self.feature_names))}' ")
            return None

        only_one_rules = [
            rule
            for rule in compiler_feature_rules
            if isinstance(rule, FeatureRuleNodeOnlyOne)
        ]
        cleaned_list_base = copy.deepcopy(base_enable_features)
        for only_one_rule in only_one_rules:
            result = FeatureRuleNodeOnlyOne.ResultOnlyOne = only_one_rule.evaluate(base_enable_features)
            match result:
                # One feature name is present in base that is also present in 'only-one' rule
                case str() as base_feature_name:
                    # We have a feature name in base that is concerned by this rule,
                    # Check if the rule also concern self
                    result = FeatureRuleNodeOnlyOne.ResultOnlyOne = only_one_rule.evaluate(self)
                    match result:
                        # One feature name is present in self that is also present in base and 'only-one' rule
                        case str():
                            # We have one feature name in base and one in self
                            # We keep the one in self
                            cleaned_list_base.feature_names.remove(base_feature_name)
                # Multiple feature name is present in base that is also present in 'only-one' rule
                case FeatureNameList() as mutliple_feature:
                    console.print_error(f"Rule '{FeatureRuleNodeOnlyOne.KEY}' invalidate feature list '{', '.join(list(mutliple_feature.feature_names))}' ")
                # No feature name is present in base that is also present in 'only-one' rule
                case None:
                    pass

        # Merge cleaned_list_base and self    
        result = FeatureNameList(is_extended=True)
        result.feature_names = cleaned_list_base.feature_names.union(self.feature_names)
        # Check that merge feature_names validate feature-rules before merging
        if not compiler_feature_rules.is_feature_list_validate_rules(result.feature_names):
            console.print_error(f"Rule invalidate feature list '{', '.join(list(result.feature_names))}' ")
            return None
        return result
    
    
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
    
    # Retrieves all profile names of the profiles that are in this feature
    def get_profile_names(self) -> set[str]:
        return self.profiles.get_profile_names()

    # Extend this feature node.
    # This will basically extends all profiles in this feature and check that the result validate feature rules
    def extend_self(self, compiler_features, compiler_feature_rules) -> Self:
        extended = FeatureNode(self.name)
        extended.cxx_linker_flags = copy.deepcopy(self.cxx_linker_flags)
        extended.cxx_compiler_flags = copy.deepcopy(self.cxx_compiler_flags)
        extended.enable_features = copy.deepcopy(self.enable_features)
        extended.profiles = self.profiles.extend_self(compiler_features=compiler_features,
                                                      compiler_feature_rules=compiler_feature_rules, 
                                                      profiles_of_base=None)
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
    
    def _build_repr(self) -> str:
        return f""" BinLibDynNode : {self.project_type}:
    cxx_linker_flags : {self.cxx_linker_flags}
    cxx_compiler_flags : {self.cxx_compiler_flags}
    enable_features : {self.enable_features}"""

    def __repr__(self) -> str:
        return self._build_repr()
    
    def __str__(self) -> str:
        return self._build_repr()
    
    # Extends the BinLibDynNode with common flags and features of the profile.
    # This will merge compiler and linker flags and extends features and validate feature rules.
    def extends_with_profile_commons(self, common_cxx_compiler: CXXCompilerFlagList, common_cxx_linker : CXXLinkerFlagList, common_enable_features: FeatureNameList, compiler_features, compiler_feature_rules) -> Self | None :
        extended = BinLibDynNode(self.project_type)
        extended.cxx_compiler_flags = self.cxx_compiler_flags.merge(common_cxx_compiler)
        extended.cxx_linker_flags = self.cxx_linker_flags.merge(common_cxx_linker)
        if(enable_feature := self.enable_features.extend(base_enable_features=common_enable_features,
                                                         compiler_features=compiler_features, 
                                                         compiler_feature_rules=compiler_feature_rules)) is None:
            return None
        extended.enable_features = enable_feature
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
        self.common_cxx_compiler = CXXCompilerFlagList()
        self.common_cxx_linker = CXXLinkerFlagList()
        self.common_enable_features = FeatureNameList()
    
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
    def _build_repr(self) -> str:
        lines = [
            f"BinLibDynNodeList :",
        ]
        lines.append(f"        cxx_compiler_flags: {self.common_cxx_compiler.flags}")
        lines.append(f"        cxx_linker_flags: {self.common_cxx_linker.flags}")
        lines.append(f"        features: {self.common_enable_features.feature_names}")
        lines.append(f"        bin_lib_dyn:")
        for ps in self.bin_lib_dyn_set:
            lines.append(f"          {ps.project_type}:")
            lines.append(f"            cxx_compiler_flags: {ps.cxx_compiler_flags}")
            lines.append(f"            cxx_linker_flags: {ps.cxx_linker_flags}")
            lines.append(f"            features: {ps.enable_features}")
        return "\n".join(lines)

    def __repr__(self) -> str:
        return self._build_repr()

    def __str__(self) -> str:
        return self._build_repr()
    def add(self, profile:BinLibDynNode):
        self.bin_lib_dyn_set.add(profile)
    
    # Retrieves the project specific with the given project type, if not found return None
    def get(self, project_type: ProjectType) -> BinLibDynNode | None:
        for p in self.bin_lib_dyn_set:
            if p.project_type == project_type:
                return p
        return None 
    
    def extend_self(self, compiler_features, compiler_feature_rules) -> Self:
        extended = BinLibDynNodeList()
        extended.common_cxx_compiler = self.common_cxx_compiler
        extended.common_cxx_linker = self.common_cxx_linker
        
        if (extended_common_enable_features := self.common_enable_features.extend_self(compiler_features=compiler_features, compiler_feature_rules=compiler_feature_rules)) is None:
            return None
        extended.common_enable_features = extended_common_enable_features

         # Add project type that does not exists in the project to extends first
        for project_type in ProjectType:
            if not project_type in self:
                self.add(BinLibDynNode(project_type))
        for bin_lib_dyn in self.bin_lib_dyn_set:
            extended.add(bin_lib_dyn.extends_with_profile_commons(common_cxx_compiler=extended.common_cxx_compiler, 
                                                                  common_cxx_linker=extended.common_cxx_linker, 
                                                                  common_enable_features=extended.common_enable_features, 
                                                                  compiler_features=compiler_features, 
                                                                  compiler_feature_rules=compiler_feature_rules))
        return extended

    def extend(self, bin_lib_dyn_of_base : Self, compiler_features, compiler_feature_rules) -> Self :
        if( self_extended := self.extend_self( compiler_features=compiler_features,
                                               compiler_feature_rules=compiler_feature_rules)) is None:
            return None
        
        extended = BinLibDynNodeList()
        # Get elements in self_extended AND other
        same_name_nodes : set[BinLibDynNode] = self_extended.bin_lib_dyn_set.intersection(bin_lib_dyn_of_base.bin_lib_dyn_set)
        # Get elements not in self_extended and other
        non_commons : set[BinLibDynNode] = self_extended.bin_lib_dyn_set.symmetric_difference(bin_lib_dyn_of_base.bin_lib_dyn_set)

        # Extends the commons and add non common
        for same_name_node in same_name_nodes:
            self_same_name_node = self_extended.get(same_name_node.project_type)
            base_same_name_node = bin_lib_dyn_of_base.get(same_name_node.project_type)
            if (extended_self_same_name_node := self_same_name_node.extends_with_profile_commons(common_cxx_compiler=base_same_name_node.cxx_compiler_flags, 
                                                                                                 common_cxx_linker=base_same_name_node.cxx_linker_flags,
                                                                                                 common_enable_features=base_same_name_node.enable_features, 
                                                                                                 compiler_features=compiler_features,
                                                                                                 compiler_feature_rules=compiler_feature_rules)) is None:
                console.print_error(f"When extending '{self_same_name_node.project_type}' with profile commons")
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
            f" bin_lib_dyn: {self.bin_lib_dyn_list}"
        ]
        return "\n".join(lines)

    def __repr__(self) -> str:
        return self._build_repr()

    def __str__(self) -> str:
        return self._build_repr()
    
    def is_feature_rules_valid(self, compiler_feature_rules) -> bool:
        assert self.is_extended, f"'{self.name}' must be extended"
        return compiler_feature_rules.is_feature_list_validate_rules(self.bin_lib_dyn_list.common_enable_features)
        
    def extend_self(self, compiler_features, compiler_feature_rules) -> Self | None:
        if self.is_extended:
            return self
        extended = ProfileNode(self.name, True)
        extended.extends_name = self.extends_name
        extended.is_abstract = self.is_abstract
        if( extended_bin_lib_dyn_list := self.bin_lib_dyn_list.extend_self(compiler_features=compiler_features,
                                                                       compiler_feature_rules=compiler_feature_rules)) is None:
            return None
        
        extended.bin_lib_dyn_list = extended_bin_lib_dyn_list
        return extended
    
    def extend(self, base_profile: Self, compiler_features,compiler_feature_rules) -> Self  | None:
        assert base_profile.is_extended, f"Base '{base_profile.name}' must be extended"
        if self.is_extended:
            return self
        
        extended = ProfileNode(self.name, True)
        extended.extends_name = self.extends_name
        extended.is_abstract = self.is_abstract
       
        if(extended_bin_lib_dyn_list := self.bin_lib_dyn_list.extend(bin_lib_dyn_of_base=base_profile.bin_lib_dyn_list,
                                                                         compiler_features=compiler_features,
                                                                         compiler_feature_rules=compiler_feature_rules)) is None:
            return None
        extended.bin_lib_dyn_list = extended_bin_lib_dyn_list
        return extended
    
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
    def extend_self(self, compiler_features, compiler_feature_rules, profiles_of_base: Self) -> Self | None:
        extended = ProfileNodeList()
        already_extended = ProfileNodeList()

        # If profile in base in not present in self, we add it the self profile list
        # This will allow other profile that extends this one to also extends with profile at the top
        # Copy it, we don't want to modify the base profile
        if profiles_of_base:
            for profile_of_base in profiles_of_base:
                if not profile_of_base in self.profiles:
                    self.add(copy.deepcopy(profile_of_base))
        
        # Then we extends all profiles in self
        for profile in self.profiles:
            if profile in already_extended:
                continue
            # Flattens the profile extension chain.
            # This detects extension cycles and orders the list so that
            # base profiles come before the profiles that extend them.
            flatten_profiles: list[ProfileNode] = self.flatten_extends_profile(profile)

            # Get the base that as no 'extends'
            # This is the first profile in the flatten profiles list
            base_profile = already_extended.get(flatten_profiles[0].name) 
            if not base_profile:
                if( base_profile := flatten_profiles[0].extend_self(compiler_features=compiler_features, 
                                                            compiler_feature_rules=compiler_feature_rules)) is None:
                    console.print_error(f"When extending '{flatten_profiles[0].name}' profile.")
                    return None
                extended.add(base_profile)
                already_extended.add(base_profile)
            # Extends the rest
            for p in flatten_profiles[1:]:
                # Extend only once
                extended_p = already_extended.get(p.name) 
                if not extended_p:
                    if( extended_p := p.extend(base_profile=base_profile, 
                                               compiler_features=compiler_features,
                                               compiler_feature_rules=compiler_feature_rules)) is None:
                        console.print_error(f"When extending '{p.name}' profile with '{base_profile.name}' base profile.")
                        return None
                    if not extended_p.is_feature_rules_valid(compiler_feature_rules):
                        console.print_error(f"When validating rules for '{p.name}' profile.")
                        return None
                    extended.add(extended_p)
                    already_extended.add(extended_p)
                base_profile = extended_p
                
        return extended

    def get_extended_with_base(self, profiles_of_base : Self, compiler_features, compiler_feature_rules) -> Self | None :
        if(self_extended := self.extend_self(compiler_features=compiler_features,
                                             compiler_feature_rules=compiler_feature_rules,
                                             profiles_of_base=profiles_of_base)) is None:
            return None
        
        extended = ProfileNodeList()
        
        # Get elements in self AND profiles_of_base
        common_profiles : set[ProfileNode] = self_extended.profiles.intersection(profiles_of_base.profiles)
        # Get elements not in self and profiles_of_base
        non_common_profiles : set[ProfileNode] = self_extended.profiles.symmetric_difference(profiles_of_base.profiles)

        # Extends the common profiles with the base profiles first
        for common_profile in common_profiles:
            self_common_profile = self_extended.get(common_profile.name)
            base_profile = profiles_of_base.get(self_common_profile.name)
            # At this point, profile is only extends with itself, mark it a not extended to extends with a base after
            self_common_profile.is_extended = False
            if (extended_profile := self_common_profile.extend(base_profile=base_profile, 
                                                            compiler_features=compiler_features, 
                                                            compiler_feature_rules=compiler_feature_rules)) is None:
                console.print_error(f"When extending '{self_common_profile.name}' profile with '{base_profile.name}' base profile.")
                return None
            extended.profiles.add(extended_profile)

        # If the profile is in self but not in base
        for non_common_profile in non_common_profiles:
            self_non_common_profile = self_extended.get(non_common_profile.name)
            if(base_profile := extended.get(non_common_profile.extends_name)) is None:
                if(base_profile := profiles_of_base.get(self_common_profile.name)) is None:
                    console.print_error(f"❌ Base profile '{self_common_profile.extends_name}' not found '{self_common_profile.name}'")
                    return None
            # At this point, profile is only extends with itself, mark it a not extended to extends with a base after
            self_non_common_profile.is_extended = False
            if (extended_profile := self_non_common_profile.extend(base_profile=base_profile, 
                                                            compiler_features=compiler_features, 
                                                            compiler_feature_rules=compiler_feature_rules)) is None:
                console.print_error(f"When extending '{self_non_common_profile.name}' profile with '{base_profile.name}' base profile.")
                return None
            extended.profiles.add(extended_profile)

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

    def get(self, name: str) -> FeatureNode | None:
        for f in self.features:
            if f.name == name:
                return f
        return None
    
    def extend_self(self, compiler_feature_rules) -> Self:
        extended = FeatureNodeList()
        for feature in self.features:
            extended.add(feature.extend_self(self, compiler_feature_rules))
        return extended

    def get_extended_with_base(self, features_of_base : Self, compiler_feature_rules) -> Self | None :
        if(extended_self := self.extend_self(compiler_feature_rules)) is None:
            return None

        extended = FeatureNodeList()
        # Get elements in self AND features_of_base
        common_features : set[FeatureNode] = extended_self.features.intersection(features_of_base.features)
        # Get elements not in self and features_of_base
        non_commons_features : set[FeatureNode] = extended_self.features.symmetric_difference(features_of_base.features)
        # We don't have extension on feature
        # We don't allow multiple same name
        if common_features:
            console.print_error(f"❌ Feature with same name both target [{', '.join(f.name for f in common_features)}]")
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
             console.print_error(f"❌ Feature rule with same name both target [{', '.join(f.name for f in common_feature_rules)}]")
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
                            console.print_error(f"❌ Feature rule '{FeatureRuleNodeOnlyOne.KEY}' not satisfied. [{', '.join(list(mutliple_feature))}] are enabled but only one in allowed.")
                            return False
                case FeatureRuleNodeIncompatibleWith() as incompatible_rule:
                    list_of_incompatible_feature =  incompatible_rule.is_satisfied(feature_list)
                    if list_of_incompatible_feature:
                        console.print_error(f"❌ Feature rule '{FeatureRuleNodeIncompatibleWith.KEY}' not satisfied. [{', '.join(list_of_incompatible_feature)}] are incompatible with '{incompatible_rule.feature_name}' ")
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
            lines.append(f"      {profile.bin_lib_dyn_list}")
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
            extended.features = to_extend_compiler_node.features.extend_self(compiler_feature_rules=extended.feature_rules)
            if (extended_profiles := to_extend_compiler_node.profiles.extend_self(compiler_features=extended.features, 
                                                                                  compiler_feature_rules=extended.feature_rules,
                                                                                  profiles_of_base=None)) is None:
                console.print_error(f"When extending '{to_extend_compiler_node.name}' compiler")
                return None
            extended.profiles = extended_profiles
            ExtendedCompilerNodeRegistry.register_extended_compiler(extended)
        assert extended.is_extended
        console.print_tips(extended)
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
            extended.feature_rules = to_extend_compiler_node.feature_rules.get_extended_with(base=base_compiler_node.feature_rules)
            if not extended.feature_rules:
                console.print_error(f"❌ Fail to extend '{to_extend_compiler_node.name}' with base '{to_extend_compiler_node.extends_name}'")
                return None
            # Extend features
            extended.features = to_extend_compiler_node.features.get_extended_with_base(features_of_base=base_compiler_node.features, compiler_feature_rules=extended.feature_rules)
            if not extended.features:
                console.print_error(f"❌ Fail to extend '{to_extend_compiler_node.name}' with base '{to_extend_compiler_node.extends_name}'")
                return None
            # Extend profiles
            extended.profiles = to_extend_compiler_node.profiles.get_extended_with_base(profiles_of_base=base_compiler_node.profiles, compiler_features=extended.features, compiler_feature_rules=extended.feature_rules)
            if not extended.profiles:
                console.print_error(f"❌ Fail to extend '{to_extend_compiler_node.name}' with base '{to_extend_compiler_node.extends_name}'")
                return None
            
       
            
            # Register for futur use
            ExtendedCompilerNodeRegistry.register_extended_compiler(extended)
        assert extended.is_extended
        console.print_tips(extended)
        return extended

    def extend_self(self) -> Self | None:
        
        # Flattening the compiler hierarchy establishes a dependency order.
        # This ensures safe iteration where all included compilers are
        # resolved before the compiler that extends them.
        # In other words, if compiler A extends B, then B appears before A.
        flatten_compiler_extends = self.flatten_extends_compilers()

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
    
    def get_feature(self, feature_name: str) -> FeatureNode:
        return self.features.get(feature_name)
    
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