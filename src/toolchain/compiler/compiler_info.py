
from pathlib import Path
from typing import Optional, Self, Union
import console
from project import ProjectType
import copy

#####################################################################
# FlagList represent a list of flags used by the compiler or linker
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
    def extend_with_other(self, other : Self) -> Self:
        extended = FlagList()
        extended.flags = self.flags.union(other.flags)
        return extended
    

##############################################################
# FeatureNameList are list of feature names
##############################################################
class FeatureNameList:
    def __init__(self):
        self.feature_names = set[str]()
        self.is_self_extended = False
        
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
    def extend_self(self, compiler_features, compiler_feature_rules) -> Optional[Self]:
        if self.is_self_extended:
            return self
        extended = FeatureNameList()
        extended.feature_names = copy.deepcopy(self.feature_names)
        to_process = copy.deepcopy(self.feature_names)
        while to_process:
            # Find the feature to enable
            feature_name = to_process.pop()
            if (feature := compiler_features.get(feature_name)) is None:
                console.print_error(f"Feature {feature_name} not found")
                return None
            feature : FeatureNode = feature
            
            # Add all features that are enable by the feature
            for new_feature in feature.commons.enable_features_list:
                if new_feature not in extended.feature_names:  # Add it only once
                    if new_feature not in compiler_features:
                        console.print_error(f"Feature {new_feature} not found")
                        return None
                    extended.feature_names.add(new_feature)
                    to_process.add(new_feature)
        if not compiler_feature_rules.is_feature_list_validate_rules(extended.feature_names):
            console.print_error(f"Rule invalidate feature list '{', '.join(list(extended.feature_names))}' ")
            return None
        extended.is_self_extended = True
        return extended
    
    # Extend this feature name list with another feature name list.
    # This is a merge but with some rules:
    #  - If the list is not extended, we add all features enabled by the features in this list
    #    e.g. If we have feature A that enable feature B, and we add B in this list ( A is already in the list).
    #  - We check that the merge of the two list validate the feature rules, if not we return None
    #  - For the rule 'only-one', if we have a feature name in self and a feature name in other that are in the same 'only-one' rule, we keep the one in self
    def extend_with_other(self, other: Self, compiler_features, compiler_feature_rules) -> Optional[Self]:
        assert other.is_self_extended, "should be call with an extended feature name list"
        # Extend self, adding feature enable by each feature
        if(extended := self.extend_self(compiler_features, compiler_feature_rules)) is None:
            return None
        extended:Self = extended

        # Merge 2 features name list
        # - If 'base' and 'self' contains feature name that exists in a 'only-one' rule
        #   We don't add 'base' but 'self'. 
        #   Error when 'base' contains more that 1 elements on 'only-one', same for 'self'
        # - If 'base' and 'self' contains feature name that exists in a 'incompatible' rule
        #   Error
        only_one_rules = [
            rule
            for rule in compiler_feature_rules
            if isinstance(rule, FeatureRuleNodeOnlyOne)
        ]
        cleaned_list_base:Self= copy.deepcopy(other)
        for only_one_rule in only_one_rules:
            result = FeatureRuleNodeOnlyOne.ResultOnlyOne = only_one_rule.evaluate(other)
            match result:
                # One feature name is present in base that is also present in 'only-one' rule
                case str() as base_feature_name:
                    # We have a feature name in base that is concerned by this rule,
                    # Check if the rule also concern self
                    result = FeatureRuleNodeOnlyOne.ResultOnlyOne = only_one_rule.evaluate(extended)
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
        extended.feature_names = cleaned_list_base.feature_names.union(extended.feature_names)
        # Check that merge feature_names validate feature-rules before merging
        if not compiler_feature_rules.is_feature_list_validate_rules(extended.feature_names):
            console.print_error(f"Rule invalidate feature list '{', '.join(list(extended.feature_names))}' ")
            return None
        return extended
    
    
##############################################################
# FeatureRuleNode are base of all feature rule
##############################################################
class FeatureRuleNode:
    def __init__(self, name: str):
        self.name = name


class Commons:
    def __init__(self):
        self.cxx_linker_flags = CXXLinkerFlagList()
        self.cxx_compiler_flags = CXXCompilerFlagList()
        self.enable_features_list = FeatureNameList()
        self.is_self_extended = False

    # def merge_with_other(self, other: Self) -> Self:
    #     merged = Commons()
    #     merged.cxx_compiler_flags = self.cxx_compiler_flags.extend_with_other(other.cxx_compiler_flags)
    #     merged.cxx_linker_flags = self.cxx_linker_flags.extend_with_other(other.cxx_linker_flags)
    #     merged.enable_features_list = self.enable_features_list.add_list(other.enable_features_list)
    #     return merged
    
    def extend_self(self, compiler_features, compiler_feature_rules) -> Optional[Self]:
        if self.is_self_extended:
            return self
        extended = Commons()
        extended.cxx_linker_flags = copy.deepcopy(self.cxx_linker_flags)
        extended.cxx_compiler_flags = copy.deepcopy(self.cxx_compiler_flags)
        if(extended_enable_features_list := self.enable_features_list.extend_self(compiler_features=compiler_features, 
                                                                                  compiler_feature_rules=compiler_feature_rules)) is None:
            return None
        extended.enable_features_list = extended_enable_features_list
        extended.is_self_extended = True
        return extended

    def extends_with_other(self, other_commons: Self, compiler_features, compiler_feature_rules) -> Optional[Self]:
        if( extended := self.extend_self(compiler_features=compiler_features, compiler_feature_rules=compiler_feature_rules)) is None:
            return None
        extended.cxx_compiler_flags = extended.cxx_compiler_flags.extend_with_other(other=other_commons.cxx_compiler_flags)
        extended.cxx_linker_flags = extended.cxx_linker_flags.extend_with_other(other=other_commons.cxx_linker_flags)

        # Extends 
        if(enable_feature := extended.enable_features_list.extend_with_other(other=other_commons.enable_features_list,
                                                                             compiler_features=compiler_features,
                                                                             compiler_feature_rules=compiler_feature_rules)) is None:
            return None
        extended.enable_features_list = enable_feature
        return extended
    
###############################################################
# FeatureNode with a unique name
# It add flags and features for all profiles
# It also add project specific flags and features
##############################################################
class FeatureNode:
    def __init__(self, name: str):
        self.name = name
        self.description: str = ""
        self.commons = Commons()
        self.common_project_list = ProjectNodeList()
        self.profile_list = ProfileNodeList()

    def __hash__(self) -> int:
        return hash(self.name)

    def __eq__(self, other) -> bool:
        if not isinstance(other, FeatureNode):
            return NotImplemented
        return self.name == other.name
    
    # Retrieves all profile names of the profiles that are in this feature
    def get_profile_names(self) -> set[str]:
        return self.profile_list.get_profile_names()

    # Extend this feature node.
    # This will extends all profiles in this feature by dispatching common flags and features into all profiles and check that the result validate feature rules
    def extend_self(self, compiler_features, compiler_feature_rules) -> Optional[Self]:
        extended = FeatureNode(self.name)
        extended.description = self.description

        # First extends common part of the feature, this will check that the common enable features validate feature rules
        if( extended_common := self.commons.extend_self(compiler_features=compiler_features, 
                                                        compiler_feature_rules=compiler_feature_rules)) is None:
            return None
        extended.commons = extended_common

        # Then extends project with common part, this will check that the merge of common and project specific validate feature rules
        if(extended_project_list := self.common_project_list.extend_with_commons(commons=extended.commons,
                                                                                 compiler_features=compiler_features,
                                                                                 compiler_feature_rules=compiler_feature_rules)) is None:
            return None
        extended.common_project_list = extended_project_list

        # Then extends profile with project part, this will check that the merge of common and profile specific validate feature rules
        if(extended_profile_list := self.profile_list.extend_with_commons(commons=extended.commons,
                                                                                 compiler_features=compiler_features,
                                                                                 compiler_feature_rules=compiler_feature_rules)) is None:
            return None
        if(extended_profile_list := extended_profile_list.extend_with_project_list(project_node_list=extended.common_project_list,
                                                                                   compiler_features=compiler_features,
                                                                                   compiler_feature_rules=compiler_feature_rules)) is None:
            return None
        extended.profile_list = extended_profile_list
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
        self.flags.add(flag)

    def get(self, name: str) -> str | None:
        return self.flags.get(name)
    
    def add_list(self, flags: list[str]):
        self.flags.add_list(flags)

    def extend_with_other(self, other : Self) -> Self:
        extended = CXXCompilerFlagList()
        extended.flags = self.flags.extend_with_other(other.flags)
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
        self.flags.add(flag)
        
    def get(self, name: str) -> str | None:
        return self.flags.get(name)
 
    def add_list(self, flags: list[str]):
        self.flags.add_list(flags)

    def extend_with_other(self, other : Self) -> Self:
        extended = CXXLinkerFlagList()
        extended.flags = self.flags.extend_with_other(other.flags)
        return extended
    
###############################################################
# ProjectTypeNode add flags and features by project type
##############################################################
class ProjectTypeNode:
    def __init__(self, project_type_name: str):
        self.project_type_name = project_type_name
        self.commons = Commons()
        self.is_self_extended = False

    def __hash__(self) -> int:
        return hash(self.project_type_name)

    def __eq__(self, other) -> bool:
        if not isinstance(other, str):
            return NotImplemented
        if isinstance(other, ProjectTypeNode):
            return self.project_type_name == other.project_type_name
        return NotImplemented
    
    def _build_repr(self) -> str:
        return f""" ProjectTypeNode : {self.project_type_name}:
    cxx_linker_flags : {self.commons.cxx_linker_flags}
    cxx_compiler_flags : {self.commons.cxx_compiler_flags}
    enable_features : {self.commons.enable_features_list}"""

    def __repr__(self) -> str:
        return self._build_repr()
    
    def __str__(self) -> str:
        return self._build_repr()
    
    def extend_self(self, compiler_features, compiler_feature_rules) -> Optional[Self]:
        if self.is_self_extended:
            return self
        extended = ProjectTypeNode(self.project_type_name)
        if( extended_commons := self.commons.extend_self(compiler_features=compiler_features,
                                                         compiler_feature_rules=compiler_feature_rules)) is None:
            return None
        extended.commons = extended_commons
        extended.is_self_extended = True
        return extended
    
    def extend_with_commons(self, commons: Commons, compiler_features, compiler_feature_rules) -> Optional[Self]:
        if (extended := self.extend_self(compiler_features=compiler_features, 
                                         compiler_feature_rules=compiler_feature_rules)) is None:
            return None

        if( extended_commons := extended.commons.extends_with_other(other_commons=commons,
                                                                    compiler_features=compiler_features,
                                                                    compiler_feature_rules=compiler_feature_rules)) is None:
            return None
        extended.commons = extended_commons
        return extended
    
    def extend_with_other(self, other: Self, compiler_features, compiler_feature_rules) -> Optional[Self]:
        return self.extend_with_commons(commons=other.commons, 
                                        compiler_features=compiler_features, 
                                        compiler_feature_rules=compiler_feature_rules)

###############################################################
# ProjectNodeList are list of ProjectTypeNode
##############################################################
class ProjectNodeList:
    def __init__(self):
        self.project_type_set: set[ProjectTypeNode] = set()
        self.is_self_extended = False

    def __iter__(self):
        return iter(self.project_type_set)
    
    def __len__(self):
        return len(self.project_type_set)
    
    def __contains__(self, project_type_node: ProjectTypeNode) -> bool:
        return project_type_node in self.project_type_set
    
    def __contains__(self, item) -> bool:
        if isinstance(item, ProjectTypeNode):
            return item in self.project_type_set
        if isinstance(item, str):
            return any(p.project_type_name == item for p in self.project_type_set)
        return False
    
    def _build_repr(self) -> str:
        lines = [
            f"projects :",
        ]
        for ps in self.project_type_set:
            lines.append(f"  {ps.project_type_name}:")
            lines.append(f"    cxx_compiler_flags: {ps.commons.cxx_compiler_flags}")
            lines.append(f"    cxx_linker_flags: {ps.commons.cxx_linker_flags}")
            lines.append(f"    features: {ps.commons.enable_features_list}")
        return "\n".join(lines)

    def __repr__(self) -> str:
        return self._build_repr()

    def __str__(self) -> str:
        return self._build_repr()
    
    def add(self, project_type_node:ProjectTypeNode):
        self.project_type_set.add(project_type_node)
    
    # Retrieves the project specific with the given project type, if not found return None
    def get(self, project_type_name: str) -> Optional[ProjectTypeNode]:
        for p in self.project_type_set:
            if p.project_type_name == project_type_name:
                return p
        return None 
       
    def extend_self(self, compiler_features, compiler_feature_rules) -> Optional[Self]:
        if self.is_self_extended:
            return self
        extended = ProjectNodeList()
        for project_type_node in self.project_type_set:
            if( extended_project_type_node := project_type_node.extend_self(compiler_features=compiler_features,
                                                                            compiler_feature_rules=compiler_feature_rules)) is None:
                return None
            extended.add(extended_project_type_node)
        extended.is_self_extended = True
        return extended
    
    def extend_with_commons(self, commons: Commons, compiler_features, compiler_feature_rules) -> Optional[Self]:
        if (extended := self.extend_self(compiler_features=compiler_features, 
                                         compiler_feature_rules=compiler_feature_rules)) is None:
            return None
        
        extended_project_type_set = set[ProjectTypeNode]()
        for project_type in extended.project_type_set:
            if( extended_project_type := project_type.extend_with_commons(commons=commons,
                                                                          compiler_features=compiler_features,
                                                                          compiler_feature_rules=compiler_feature_rules)) is None:
                return None
            extended_project_type_set.add(extended_project_type)
        extended.project_type_set = extended_project_type_set
        return extended
        
    def extend_with_other(self, other_project_node_list: Self, compiler_features, compiler_feature_rules) -> Optional[Self]:
        assert other_project_node_list.is_self_extended, "should be call with an extended project list"

        if (extended := self.extend_self(compiler_features=compiler_features, 
                                         compiler_feature_rules=compiler_feature_rules)) is None:
            return None
        
        extended_project_type_set = set[ProjectTypeNode]()
        for project_type in other_project_node_list.project_type_set:
            # If the project type is not in self, we add it to the extended
            if (existing_project_type := extended.get(project_type)) is None:
                extended_project_type_set.add(project_type)
            # If the project type is in self, we extend it with the project type of other
            else:
                if(extended_existing_project_type := existing_project_type.extend_with_other(project_type)) is None:
                    return None
                extended_project_type_set.add(extended_existing_project_type)
        extended.project_type_set = extended_project_type_set
        return extended
                
                
        


    # Extends the ProjectNodeList with common flags and features.
    # This will merge compiler and linker flags and extends features and validate feature rules.
    # def extends_with_other(self, other: Self, compiler_features, compiler_feature_rules) -> Self | None :
    #     extended = ProjectNodeList()

    #     # Get elements in self AND profiles_of_base
    #     common_bin_dyn_lib = self.project_type_set.intersection(other)
        
    #     # Get elements not in self and profiles_of_base
    #     non_common_bin_dyn_lib = self.project_type_set.symmetric_difference(other)

    #     # Extend common
    #     for bin_dyn_lib in common_bin_dyn_lib:
    #         self_bin_dyn_lib = self.get(bin_dyn_lib.project_type_name)
    #         other_bin_dyn_lib = other.get(bin_dyn_lib.project_type_name)
    #         extended_bin_lib_dyn = self_bin_dyn_lib.extends_with_other(other=other_bin_dyn_lib,
    #                                                                    compiler_features=compiler_features,
    #                                                                    compiler_feature_rules=compiler_feature_rules)
    #         extended.add(extended_bin_lib_dyn)
        
    #     # Add non common
    #     extended.project_type_set.update(non_common_bin_dyn_lib)
      
    #     return extended

###############################################################
# PerProfileBinLibDynNodeList are list of ProjectTypeNode
##############################################################
# class PerProfileBinLibDynNodeList:
#     def __init__(self):
#         self.bin_lib_dyn_list = ProjectNodeList()
#         self.flag_and_feature = Commons()
    
#     def __iter__(self):
#         return iter(self.bin_lib_dyn_list)
    
#     def __len__(self):
#         return len(self.bin_lib_dyn_list)
    
#     def __contains__(self, binlibdyn_node: ProjectTypeNode) -> bool:
#         return binlibdyn_node in self.bin_lib_dyn_list
    
#     def __contains__(self, item) -> bool:
#         return item in self.bin_lib_dyn_list
    
#     def _build_repr(self) -> str:
#         lines = [
#             f"PerProfileBinLibDynNodeList :",
#         ]
#         lines.append(f"        cxx_compiler_flags: {self.flag_and_feature.cxx_compiler_flags}")
#         lines.append(f"        cxx_linker_flags: {self.flag_and_feature.cxx_linker_flags}")
#         lines.append(f"        features: {self.flag_and_feature.enable_features}")
#         lines.append(f"        bin_lib_dyn:")
#         for ps in self.bin_lib_dyn_list.bin_lib_dyn_set:
#             lines.append(f"          {ps.project_type}:")
#             lines.append(f"            cxx_compiler_flags: {ps.flag_and_feature.cxx_compiler_flags}")
#             lines.append(f"            cxx_linker_flags: {ps.flag_and_feature.cxx_linker_flags}")
#             lines.append(f"            features: {ps.flag_and_feature.enable_features}")
#         return "\n".join(lines)

#     def __repr__(self) -> str:
#         return self._build_repr()

#     def __str__(self) -> str:
#         return self._build_repr()
    
#     def add(self, profile:ProjectTypeNode):
#         self.bin_lib_dyn_list.add(profile)
    
#     # Retrieves the project specific with the given project type, if not found return None
#     def get(self, project_type: ProjectType) -> ProjectTypeNode | None:
#         return self.bin_lib_dyn_list.get(project_type)
    
#     def extend_self(self, compiler_features, compiler_feature_rules, common_bin_lib_dyn_set: Optional[ProjectNodeList]) -> Self:
#         # Extends common part under
#         # debug|release :
#         #  cxx-compiler-flags:
#         #  cxx-linker-flags:
#         #  enable-features:
#         extended = PerProfileBinLibDynNodeList()
#         extended.common_cxx_compiler = copy.deepcopy(self.common_cxx_compiler)
#         extended.common_cxx_linker = copy.deepcopy(self.common_cxx_linker)
#         # Extends the feature name list
#         # If enable-features contains a feature that enables other features, we extend enable-features with those additional features.
#         # Return None if the feature rule is not respected
#         if (extended_common_enable_features := self.common_enable_features.extend_self(compiler_features=compiler_features, 
#                                                                                        compiler_feature_rules=compiler_feature_rules)) is None:
#             return None
#         extended.common_enable_features = extended_common_enable_features


#         # For each feature that are enable
#         # Dispatch each enable-feature per project type
#         # Eg:
#         # asan profile enable-feature is ASAN
#         # ASAN feature enable DYNAMIC_LIBRARY_RELEASE for dyn project type
#         # We merge DYNAMIC_LIBRARY_RELEASE to the common bin_lib_dyn_list['dyn'].enable_features
#         # Note: Flags are merge later when we create the compiler because we don't have to check compatiblity like feature rules
#         extended_bin_lib_dyn_list : ProjectNodeList = copy.deepcopy(self.bin_lib_dyn_list)
#         for feature in extended_common_enable_features:
#             compiler_feature = compiler_features.get(feature)
#             extended_bin_lib_dyn_list = extended_bin_lib_dyn_list.extends_with_common(compiler_feature.common_bin_lib_dyn_list, 
#                                                                                       compiler_features=compiler_feature,
#                                                                                       compiler_feature_rules=compiler_feature_rules)

#         # Add project type that does not exists in the project to extends first
#         for project_type in ProjectType:
#             if not project_type in self:
#                 self.add(ProjectTypeNode(project_type))

#         # Merge common per project first
#         # profiles:
#         #   bin|dyn|lib:
#         # merge into
#         # profiles:
#         #  debug|release:
#         #   bin|dyn|lib:
#         #     cxx-compiler-flags:
#         #     cxx-linker-flags:
#         #     enable-features:
#         if common_bin_lib_dyn_set:
#             extended_bin_lib_dyn = ProjectNodeList()
#             for bin_lib_dyn in common_bin_lib_dyn_set:
#                 if project_type in self:
#                     if( a := self.get(bin_lib_dyn.project_type)) is None:
#                         continue
#                     extended_bin_lib_dyn.add(a.extend_with_commons(common_cxx_compiler=bin_lib_dyn.cxx_compiler_flags,
#                                                                     common_cxx_linker=bin_lib_dyn.cxx_linker_flags,
#                                                                     common_enable_features=bin_lib_dyn.enable_features,
#                                                                     compiler_features=compiler_features, 
#                                                                     compiler_feature_rules=compiler_feature_rules))
#                 else:
#                     extended_bin_lib_dyn.add(bin_lib_dyn)
#         else:
#             extended_bin_lib_dyn = extended_bin_lib_dyn_list
    
#         # Extends per project part under
#         # debug|release:
#         #   bin|dyn|lib:
#         #     cxx-compiler-flags:
#         #     cxx-linker-flags:
#         #     enable-features:
#         for bin_lib_dyn in extended_bin_lib_dyn:
#             # The merge per project 
#             extended.add(bin_lib_dyn.extend_with_commons(common_cxx_compiler=extended.common_cxx_compiler, 
#                                                           common_cxx_linker=extended.common_cxx_linker, 
#                                                           common_enable_features=extended.common_enable_features, 
#                                                           compiler_features=compiler_features, 
#                                                           compiler_feature_rules=compiler_feature_rules))
#         return extended

#     def extend_with_base_profile(self, bin_lib_dyn_of_base : Self, compiler_features, compiler_feature_rules) -> Self :
#         if( self_extended := self.extend_self( compiler_features=compiler_features,
#                                                compiler_feature_rules=compiler_feature_rules,
#                                                common_bin_lib_dyn_set=None)) is None:
#             return None
        
#         extended = PerProfileBinLibDynNodeList()
#         # Get elements in self_extended AND other
#         same_name_nodes : set[ProjectTypeNode] = self_extended.bin_lib_dyn_list.bin_lib_dyn_set.intersection(bin_lib_dyn_of_base.bin_lib_dyn_list.bin_lib_dyn_set)
#         # Get elements not in self_extended and other
#         non_commons : set[ProjectTypeNode] = self_extended.bin_lib_dyn_list.bin_lib_dyn_set.symmetric_difference(bin_lib_dyn_of_base.bin_lib_dyn_list.bin_lib_dyn_set)

#         # Extends the commons and add non common
#         for same_name_node in same_name_nodes:
#             self_same_name_node = self_extended.get(same_name_node.project_type)
#             base_same_name_node = bin_lib_dyn_of_base.get(same_name_node.project_type)
#             if (extended_self_same_name_node := self_same_name_node.extend_with_commons(common_cxx_compiler=base_same_name_node.cxx_compiler_flags, 
#                                                                                          common_cxx_linker=base_same_name_node.cxx_linker_flags,
#                                                                                          common_enable_features=base_same_name_node.enable_features, 
#                                                                                          compiler_features=compiler_features,
#                                                                                          compiler_feature_rules=compiler_feature_rules)) is None:
#                 console.print_error(f"When extending '{self_same_name_node.project_type}' with profile commons")
#                 return None
#             extended.bin_lib_dyn_list.add(extended_self_same_name_node)
#         extended.bin_lib_dyn_list.bin_lib_dyn_set.update(non_commons)
#         return extended
    
#############################################################
# ProfileNode add flags and features by profile.
# It also add project specific flags and features for the profile
# Extending it with 'extends' merge all flags and features of the extended into this one
#############################################################
class ProfileNode:
    def __init__(self, name: str):
        # The profile name
        self.name = name
        # The profile used to extends this one
        self.extends_name : str = None
        # If this profile specific is abstract ( Not usable by the user )
        self.is_abstract = False
        # List of flags and features that apply to all project types of this profile
        self.commons = Commons()
        # List of project type specific flags and features with this profile
        self.common_project_list = ProjectNodeList()
        # True if this node is extended with self
        self.is_self_extended = False

    def __hash__(self) -> int:
        return hash(self.name)

    def __eq__(self, other) -> bool:
        if not isinstance(other, ProfileNode):
            return NotImplemented
        return self.name == other.name

    def _build_repr(self) -> str:
        lines = [
            f"{self.name} : (abstract:{self.is_abstract}, extends: {self.extends_name})",
            f" cxx_compiler_flags: {self.commons.cxx_compiler_flags}",
            f" cxx_linker_flags: {self.commons.cxx_linker_flags}",
            f" enable_features: {self.commons.enable_features_list}",
        ]
        if len(self.common_project_list) > 0:
            lines.append(f" projects:")
            for project_type in self.common_project_list:
                lines.append(f"    {project_type.project_type_name}:")
                lines.append(f"      cxx_compiler_flags : {project_type.commons.cxx_compiler_flags}")
                lines.append(f"      cxx_linker_flags : {project_type.commons.cxx_linker_flags}")
                lines.append(f"      enable_features : {project_type.commons.enable_features_list}")
        else:
            lines.append(f" projects: None")
        return "\n".join(lines)

    def __repr__(self) -> str:
        return self._build_repr()

    def __str__(self) -> str:
        return self._build_repr()
    
    def extend_with_commons(self, commons: Commons, compiler_features, compiler_feature_rules) -> Optional[Self]:
        if (extended := self.extend_self(compiler_features=compiler_features, 
                                         compiler_feature_rules=compiler_feature_rules)) is None:
            return None

        if( extended_commons := extended.commons.extends_with_other(other_commons=commons,
                                                                    compiler_features=compiler_features,
                                                                    compiler_feature_rules=compiler_feature_rules)) is None:
            return None
        extended.commons = extended_commons

        if( extended_project_list := extended.common_project_list.extend_with_commons(commons=commons, 
                                                                                      compiler_features=compiler_features, 
                                                                                      compiler_feature_rules=compiler_feature_rules)) is None:
            return None
        extended.common_project_list = extended_project_list

        return extended
    
    def extend_self(self, compiler_features, compiler_feature_rules) -> Optional[Self]:
        if self.is_self_extended:
            return self
        
        extended = ProfileNode(self.name)
        extended.extends_name = self.extends_name
        extended.is_abstract = self.is_abstract
        # First, extends common part of the profile, this will check that the common enable features validate feature rules
        if(extended_commons := self.commons.extend_self(compiler_features=compiler_features, 
                                                        compiler_feature_rules=compiler_feature_rules)) is None:
            return None
        extended.commons = extended_commons
        # Then, extends project with common part, this will check that the merge of common and project specific validate feature rules
        if(extended_project_list := self.common_project_list.extend_with_commons(commons=extended.commons, 
                                                                                  compiler_features=compiler_features, 
                                                                                  compiler_feature_rules=compiler_feature_rules)) is None:
            return None
        extended.common_project_list = extended_project_list
        extended.is_self_extended = True
        return extended
    
    def extend_with_project_list(self, project_node_list: ProjectNodeList, compiler_features, compiler_feature_rules) -> Optional[Self]:
        assert project_node_list.is_self_extended, "Project list must be extended before extending profile with it"
        if(extended := self.extend_self(compiler_features=compiler_features, 
                                        compiler_feature_rules=compiler_feature_rules)) is None:
            return None

        extended.extends_name = self.extends_name
        extended.is_abstract = self.is_abstract
       
        # Then extends profile with project part, this will check that the merge of common and profile specific validate feature rules
        if(extended_project_list := extended.common_project_list.extend_with_other(other_project_node_list=project_node_list,
                                                                                   compiler_features=compiler_features,
                                                                                   compiler_feature_rules=compiler_feature_rules)) is None:
            return None
        extended.common_project_list = extended_project_list
        return extended
    
    def extend_with_other(self, other: Self, compiler_features, compiler_feature_rules) -> Optional[Self]:
        assert other.is_self_extended, "Base profile must be extended before extending profile with it"

        if(extended := self.extend_self(compiler_features=compiler_features, 
                                        compiler_feature_rules=compiler_feature_rules)) is None:
            return None
        
        # 1. extends commons with base.commons
        if (extended_common := extended.commons.extends_with_other(other_commons=other.commons, 
                                                                   compiler_features=compiler_features, 
                                                                   compiler_feature_rules=compiler_feature_rules)) is None:
            return None
        extended.commons = extended_common
        # 2. extends project list with base project list
        if( extended_project_list := extended.common_project_list.extend_with_other(other_project_node_list=other.common_project_list,
                                                                                    compiler_features=compiler_features,
                                                                                    compiler_feature_rules=compiler_feature_rules)) is None:
            return None 
        extended.common_project_list = extended_project_list
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
        self.is_self_extended = False

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
    
    def _build_repr(self) -> str:
        lines = []
        for profile in self.profiles:
            lines.append(str(profile))
        return "\n".join(lines)

    def __repr__(self) -> str:
        return self._build_repr()

    def __str__(self) -> str:
        return self._build_repr()
    
    def extend_with_commons(self, commons: Commons, compiler_features, compiler_feature_rules) -> Optional[Self]:
        assert commons.is_self_extended, "Commons must be extended before extending profile list with it"
        if (extended := self.extend_self(compiler_features=compiler_features, 
                                         compiler_feature_rules=compiler_feature_rules)) is None:
            return None
        
        extended_profiles = set[ProfileNode]()
        for to_process_profile in extended.profiles:
            # Then extends profile with common part, this will check that the merge of common and profile specific validate feature rules
            if(extended_profile := to_process_profile.extend_with_commons(commons=commons, 
                                                                          compiler_features=compiler_features, 
                                                                          compiler_feature_rules=compiler_feature_rules)) is None:
                console.print_error(f"When extending '{to_process_profile.name}' profile with commons.")
                return None
            extended_profiles.add(extended_profile)
        extended.profiles = extended_profiles
        return extended
    
    def extend_with_project_list(self, project_node_list: ProjectNodeList, compiler_features, compiler_feature_rules) -> Optional[Self]:
        assert project_node_list.is_self_extended, "Project list must be extended before extending profile list with it"
        if( extended := self.extend_self(compiler_features=compiler_features,
                                         compiler_feature_rules=compiler_feature_rules)) is None:
            return None
        
        extended_profiles = set[ProfileNode]()
        while extended.profiles:
            to_process_profile = extended.profiles.pop()
            # Then extends profile with project part, this will check that the merge of common and profile specific validate feature rules
            if(extended_profile := to_process_profile.extend_with_project_list( project_node_list=project_node_list, 
                                                                                compiler_features=compiler_features, 
                                                                                compiler_feature_rules=compiler_feature_rules)) is None:
                console.print_error(f"When extending '{to_process_profile.name}' profile with project list.")
                return None
            extended_profiles.add(extended_profile)
        assert len(extended.profiles) == 0, "All profiles should have been processed"
        extended.profiles = extended_profiles

        return extended

    # Retrieves an extended version of this ProfileNode list.
    # Any ProfileNode that extends another ProfileNode inherits the features and flags
    # of the ProfileNode it extends.
    # For example, if we have two ProfileNodes A and B, where B extends A,
    # the returned list will contain A and B (with B including A's features).
    # Cyclic extensions are also detected.
    def extend_self(self, compiler_features:'FeatureNodeList', compiler_feature_rules: 'FeatureRuleNodeList') -> Self | None:
        if self.is_self_extended:
            return self
        
        extended = ProfileNodeList()
        already_extended = ProfileNodeList()
        
        # Then we extends all profiles in self
        for profile in self.profiles:
            if profile in already_extended:
                continue
            # Flattens the profile extension chain.
            # This detects extension cycles and orders the list so that
            # base profiles come before the profiles that extend them.
            flatten_profiles: list[ProfileNode] = self.flatten_extends_profile(profile)

            # Get the base profile that as no 'extends'
            # This is the first profile in the flatten profiles list
            base_profile = already_extended.get(flatten_profiles[0].name) 
            if not base_profile:
                if( base_profile := flatten_profiles[0].extend_self(compiler_features=compiler_features, 
                                                                    compiler_feature_rules=compiler_feature_rules)) is None:
                    console.print_error(f"When extending '{flatten_profiles[0].name}' profile.")
                    return None
                extended.add(base_profile)
                already_extended.add(base_profile)
            # Extends the rest of profiles
            for profile in flatten_profiles[1:]:
                # Extend the profile only once
                extended_p = already_extended.get(profile.name) 
                if not extended_p:
                    if( extended_p := profile.extend_with_other(other=base_profile,
                                                                compiler_features=compiler_features,
                                                                compiler_feature_rules=compiler_feature_rules)) is None:
                        console.print_error(f"When extending '{profile.name}' profile with '{base_profile.name}' base profile.")
                        return None
                    #  if not extended_p.is_feature_rules_valid(compiler_feature_rules):
                    #     console.print_error(f"When validating rules for '{profile.name}' profile.")
                    #     return None
                    extended.add(extended_p)
                    already_extended.add(extended_p)
                base_profile = extended_p
        
        extended.is_self_extended = True
        return extended
    
    def extend_with_other(self, other_profile_list : Self, compiler_features, compiler_feature_rules) -> Optional[Self] :
        assert other_profile_list.is_self_extended, "Other profile list must be extended before extending profile list with it"

        # We don't want to modify the original profile list, we create a copy of it and extend the copy with the other profile list
        extended = copy.deepcopy(self)

        # If profile in other_profile_list in not present in self, we add it the self profile list
        for profile_of_base in other_profile_list:
            if not profile_of_base in self.profiles:
                extended.add(copy.deepcopy(profile_of_base))

        # Ensure self if extended
        if( extended := extended.extend_self(compiler_features=compiler_features,
                                             compiler_feature_rules=compiler_feature_rules)) is None:
            return None
        
        # Get elements in self AND other_profile_list
        common_profiles : set[ProfileNode] = extended.profiles.intersection(other_profile_list.profiles)
        # Get elements not in self and other_profile_list
        non_common_profiles : set[ProfileNode] = extended.profiles.symmetric_difference(other_profile_list.profiles)

        # Extends the common profiles with the base profiles first
        for common_profile in common_profiles:
            self_common_profile = extended.get(common_profile.name)
            other_profile = other_profile_list.get(self_common_profile.name)
            if (extended_profile := self_common_profile.extend_with_other(other=other_profile,
                                                                          compiler_features=compiler_features, 
                                                                          compiler_feature_rules=compiler_feature_rules)) is None:
                console.print_error(f"When extending '{self_common_profile.name}' profile with '{other_profile.name}' base profile.")
                return None
            extended.profiles.remove(self_common_profile)
            extended.profiles.add(extended_profile)

        # If the profile is in self but not in base
        for non_common_profile in non_common_profiles:
            self_non_common_profile = extended.get(non_common_profile.name)
            if(other_profile := extended.get(non_common_profile.extends_name)) is None:
                if(other_profile := other_profile_list.get(self_common_profile.name)) is None:
                    console.print_error(f"Base profile '{self_common_profile.extends_name}' not found '{self_common_profile.name}'")
                    return None
            # At this point, profile is only extends with itself, mark it a not extended to extends with a base after
            self_non_common_profile.is_self_extended = False
            if (extended_profile := self_non_common_profile.extend_with_other(other=other_profile,
                                                                              compiler_features=compiler_features,
                                                                              compiler_feature_rules=compiler_feature_rules)) is None:
                console.print_error(f"When extending '{self_non_common_profile.name}' profile with '{other_profile.name}' base profile.")
                return None
            extended.profiles.remove(self_non_common_profile)
            extended.profiles.add(extended_profile)
        return extended
        # If profile in other_profile_list in not present in self, we add it the self profile list
        # for profile_of_base in other_profile_list:
        #     if not profile_of_base in self.profiles:
        #         extended.add(copy.deepcopy(profile_of_base))



        # Extends the common profiles with the base profiles first


        # # If profile in base in not present in self, we add it the self profile list
        # # This will allow other profile that extends this one to also extends with profile at the top
        # # Copy it, we don't want to modify the base profile
        # self_profiles_of_base : Self = ProfileNodeList()
        # self_profiles_of_base.profiles.update(self.profiles)
        # # for profile_of_base in profiles_of_base:
        # #     if not profile_of_base in self.profiles:
        # #         self.add(copy.deepcopy(profile_of_base))

        # if(self_extended := self.extend_self(compiler_features=compiler_features,
        #                                      compiler_feature_rules=compiler_feature_rules,
        #                                      profiles_of_base=self_profiles_of_base)) is None:
        #     return None
        
        # extended = ProfileNodeList()
        
        # # Get elements in self AND profiles_of_base
        # common_profiles : set[ProfileNode] = self_extended.profiles.intersection(other_profile_list.profiles)
        # # Get elements not in self and profiles_of_base
        # non_common_profiles : set[ProfileNode] = self_extended.profiles.symmetric_difference(other_profile_list.profiles)

        # # Extends the common profiles with the base profiles first
        # for common_profile in common_profiles:
        #     self_common_profile = self_extended.get(common_profile.name)
        #     base_profile = other_profile_list.get(self_common_profile.name)
        #     # At this point, profile is only extends with itself, mark it a not extended to extends with a base after
        #     self_common_profile.is_self_extended = False
        #     if (extended_profile := self_common_profile.extend(base_profile=base_profile, 
        #                                                     compiler_features=compiler_features, 
        #                                                     compiler_feature_rules=compiler_feature_rules)) is None:
        #         console.print_error(f"When extending '{self_common_profile.name}' profile with '{base_profile.name}' base profile.")
        #         return None
        #     extended.profiles.add(extended_profile)

        # # If the profile is in self but not in base
        # for non_common_profile in non_common_profiles:
        #     self_non_common_profile = self_extended.get(non_common_profile.name)
        #     if(base_profile := extended.get(non_common_profile.extends_name)) is None:
        #         if(base_profile := other_profile_list.get(self_common_profile.name)) is None:
        #             console.print_error(f"Base profile '{self_common_profile.extends_name}' not found '{self_common_profile.name}'")
        #             return None
        #     # At this point, profile is only extends with itself, mark it a not extended to extends with a base after
        #     self_non_common_profile.is_self_extended = False
        #     if (extended_profile := self_non_common_profile.extend(base_profile=base_profile, 
        #                                                     compiler_features=compiler_features, 
        #                                                     compiler_feature_rules=compiler_feature_rules)) is None:
        #         console.print_error(f"When extending '{self_non_common_profile.name}' profile with '{base_profile.name}' base profile.")
        #         return None
        #     extended.profiles.add(extended_profile)

        #return extended

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
                    console.print_error(f"'{current_node.name}' profile extends unknown profile '{current_node.extends_name}'")
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
    
    def extend_self(self, compiler_feature_rules) -> Optional[Self]:
        extended = FeatureNodeList()
        for feature in self.features:
            if(extended_feature := feature.extend_self(compiler_features=self,
                                                       compiler_feature_rules=compiler_feature_rules)) is None:
                return None
            extended.add(extended_feature)
        return extended

    def extend_with_other(self, other_features_list : Self, compiler_feature_rules) -> Self | None :
        
        extended = FeatureNodeList()
        # Get elements in self AND features_of_base
        common_features : set[FeatureNode] = self.features.intersection(other_features_list.features)
        # Get elements not in self and other_features_list
        non_commons_features : set[FeatureNode] = self.features.symmetric_difference(other_features_list.features)
        # We don't have extension on feature
        # We don't allow multiple same name
        if common_features:
            console.print_error(f"Feature with same name both target [{', '.join(f.name for f in common_features)}]")
            return None
        extended.features.update(common_features)
        extended.features.update(non_commons_features)
        
        if(extended_self := extended.extend_self(compiler_feature_rules)) is None:
            return None
    
        return extended_self
    
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
    
    def extend_self(self) -> Self:
        return copy.deepcopy(self)
    
    def extends_with_other(self, other_feature_rule_list : Self) -> Self | None:
        extended = FeatureRuleNodeList()
        # Get elements in self AND other_feature_rule_list
        common_feature_rules : set[FeatureNode] = self.feature_rules.intersection(other_feature_rule_list.feature_rules)
        # Get elements not in self and other_feature_rule_list
        non_commons_feature_rules : set[FeatureNode] = self.feature_rules.symmetric_difference(other_feature_rule_list.feature_rules)
        # Extends the common_feature_nodes and add the non common feature rules
        if common_feature_rules:
             console.print_error(f"Feature rule with same name both target [{', '.join(f.name for f in common_feature_rules)}]")
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
                            console.print_error(f"Feature rule '{FeatureRuleNodeOnlyOne.KEY}' not satisfied. [{', '.join(list(mutliple_feature))}] are enabled but only one in allowed.")
                            return False
                case FeatureRuleNodeIncompatibleWith() as incompatible_rule:
                    list_of_incompatible_feature =  incompatible_rule.is_satisfied(feature_list)
                    if list_of_incompatible_feature:
                        console.print_error(f"Feature rule '{FeatureRuleNodeIncompatibleWith.KEY}' not satisfied. [{', '.join(list_of_incompatible_feature)}] are incompatible with '{incompatible_rule.feature_name}' ")
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
        self.extends_name : str = None
        # List of flags and features that apply to all project types and all profiles
        self.commons = Commons()
        # List of profiles specific flags and features with this compiler
        self.profile_list = ProfileNodeList()
        # List of project type specific flags and features with this compiler
        self.common_project_list = ProjectNodeList()
        # List of features
        self.features = FeatureNodeList()
        # List of feature rules that are common to all profiles
        self.feature_rules = FeatureRuleNodeList()
        # The file where the compiler was loaded
        self.file = Path()
        # True if this node is extended
        self.is_self_extended = False
        # Compiler extends names
        self.extends_ordered_list = list[Self]()
        # C++ compiler path
        self.cxx_path : Optional[Path] = None
        # C compiler path
        self.c_path : Optional[Path] = None

    def is_derived_from(self, compiler_name: Self) -> bool:
        for extends in self.extends_ordered_list:
            if extends.name == compiler_name: return True
        return False

    def __hash__(self) -> int:
        return hash(self.name)

    def __eq__(self, other) -> bool:
        if not isinstance(other, CompilerNode):
            return NotImplemented
        return self.name == other.name
    
    def _build_repr(self) -> str:
        lines = [
            f"CompilerNode : {self.name} (abstract:{self.is_abstract}, extends: {self.extends_name})",
            "  Profiles : TDB",
        ]
        return "\n".join(lines)

    def __repr__(self) -> str:
        return self._build_repr()

    def __str__(self) -> str:
        return self._build_repr()
    
    def _flatten_extends_compilers(self) -> list[Self]:
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
                    console.print_error(f"'{current_node.name}' profile extends unknown compiler '{current_node.extends_name}'")
                    exit(1)
                collect(extends_node, current_node)
            
            # Remove visited project
            visiting_stack.pop()
            all_profiles.append(current_node)
        collect(self, None)
        return all_profiles
    
    def get_profile_names(self) -> set[str]:
        profiles = set[str]()
        profiles.update(self.get_profile_names())
        profiles.update(self.features.get_profile_names())
        return profiles

    @staticmethod
    def _extend_no_base_then_validate_features(to_extend_compiler_node: Self, 
                                               commons: Commons, 
                                               common_project_list : ProjectNodeList, 
                                               profile_list : ProfileNodeList) -> Self | None:
        to_extend_compiler_node : CompilerNode = to_extend_compiler_node
        assert not to_extend_compiler_node.is_self_extended, f"'{to_extend_compiler_node.name}' Already extended"

        if(extended_compiler := ExtendedCompilerNodeRegistry.get(to_extend_compiler_node.name)) is None:
            extended_compiler = CompilerNode(to_extend_compiler_node.name)
      
            extended_compiler.file = to_extend_compiler_node.file
            extended_compiler.cxx_path = to_extend_compiler_node.cxx_path
            extended_compiler.c_path = to_extend_compiler_node.c_path
            extended_compiler.extends_name = to_extend_compiler_node.extends_name
            # 1; Extends feature rules
            extended_compiler.feature_rules = to_extend_compiler_node.feature_rules.extend_self()

            # 2. Extends features, this will check that the features validate feature rules
            if(extended_features := to_extend_compiler_node.features.extend_self(compiler_feature_rules=extended_compiler.feature_rules)) is None:
                console.print_error(f"When extending '{to_extend_compiler_node.name}' compiler")
                return None
            extended_compiler.features = extended_features

            # 2. Self extends all compilers commons
            # Extend 'compilers:' 
            #           'enable-features:'
            #           'cxx-linker-flags:'
            #           'cxx-compiler-flags:'
            if(global_extended_commons := commons.extend_self(compiler_features=extended_compiler.features, 
                                                              compiler_feature_rules=extended_compiler.feature_rules)) is None:
                console.print_error(f"When extending '{to_extend_compiler_node.name}' compiler")
                return None
            
            # Extend 'compilers:' 
            #           'projects:' 
            # with extended 'compilers:'
            #                 'enable-features:'
            #                 'cxx-linker-flags:'
            #                 'cxx-compiler-flags:'
            if(global_extended_project_list := common_project_list.extend_self(compiler_features=extended_compiler.features,
                                                                               compiler_feature_rules=extended_compiler.feature_rules)) is None:
                console.print_error(f"When extending '{to_extend_compiler_node.name}' compiler")
                return None
            if(global_extended_project_list := global_extended_project_list.extend_with_commons(commons=global_extended_commons,
                                                                                       compiler_features=extended_compiler.features,
                                                                                       compiler_feature_rules=extended_compiler.feature_rules)) is None:
                console.print_error(f"When extending '{to_extend_compiler_node.name}' compiler")
                return None

         
            # Extend 'compilers:' :
            #           'profiles:'
            # with extended 'compilers:'
            #                      'projects:'
            # We don't need to extends with commons because it was already extends with projects
            if(global_extended_profile_list := profile_list.extend_self(compiler_features=extended_compiler.features,
                                                                               compiler_feature_rules=extended_compiler.feature_rules)) is None:
                console.print_error(f"When extending '{to_extend_compiler_node.name}' compiler")
                return None
            if(global_extended_profile_list := global_extended_profile_list.extend_with_commons(commons=global_extended_commons,
                                                                                                compiler_features=extended_compiler.features,
                                                                                                compiler_feature_rules=extended_compiler.feature_rules)) is None:
                console.print_error(f"When extending '{to_extend_compiler_node.name}' compiler")
                return None
            if(global_extended_profile_list := global_extended_profile_list.extend_with_project_list(project_node_list=global_extended_project_list,
                                                                                                     compiler_features=extended_compiler.features,
                                                                                                     compiler_feature_rules=extended_compiler.feature_rules)) is None:
                console.print_error(f"When extending '{to_extend_compiler_node.name}' compiler")
                return None
            
          
          
            
            
            # 3. Extends 'compilers:'
            #               'compiler_name:' 
            #                  'enable-features:'
            #                  'cxx-linker-flags:'
            #                  'cxx-compiler-flags:'
            # with global extended compiler 'compilers:' 
            #                                 'enable-features:'
            #                                 'cxx-linker-flags:'
            #                                 'cxx-compiler-flags:
            if(extended_compiler_common := to_extend_compiler_node.commons.extends_with_other(other_commons=global_extended_commons,
                                                                                              compiler_features=extended_compiler.features,
                                                                                              compiler_feature_rules=extended_compiler.feature_rules)) is None:
                console.print_error(f"When extending '{to_extend_compiler_node.name}' compiler")
                return None
            extended_compiler.commons = extended_compiler_common

            # 4. Extends 'compilers:' 
            #               'compiler_name:' 
            #                  'projects:'
            # with global extended compiler 'compiler:'
            #                                  'projects:'
            # then with compiler extended compiler 'compilers:' 
            #                                        'compiler_name:' 
            #                                          'enable-features:'
            #                                          'cxx-linker-flags:'
            #                                          'cxx-compiler-flags:
            if(extended_compiler_common_project_list := to_extend_compiler_node.common_project_list.extend_with_other(other_project_node_list=global_extended_project_list,
                                                                                                                      compiler_features=extended_compiler.features,
                                                                                                                      compiler_feature_rules=extended_compiler.feature_rules)) is None:
                console.print_error(f"When extending '{to_extend_compiler_node.name}' compiler")
                return None
            if(extended_compiler_common_project_list := extended_compiler_common_project_list.extend_with_commons(commons=extended_compiler_common,
                                                                                                                  compiler_features=extended_compiler.features,
                                                                                                                  compiler_feature_rules=extended_compiler.feature_rules)) is None:
                console.print_error(f"When extending '{to_extend_compiler_node.name}' compiler")
                return None
         
            extended_compiler.common_project_list = extended_compiler_common_project_list

            # 5. Extends 'compilers:' 
            #               'compiler_name:' 
            #                  'profiles:'
            # with global extended compiler 'compilers:' 
            #                                 'profiles:'
            # then with compiler extended compiler 'compilers:' 
            #                                        'compiler_name:' 
            #                                          'projects:'
            if(extended_compiler_profile_list := to_extend_compiler_node.profile_list.extend_with_other(other_profile_list=global_extended_profile_list,
                                                                                                                      compiler_features=extended_compiler.features,
                                                                                                                      compiler_feature_rules=extended_compiler.feature_rules)) is None:
                console.print_error(f"When extending '{to_extend_compiler_node.name}' compiler")
                return None
            if(extended_compiler_profile_list := to_extend_compiler_node.profile_list.extend_with_project_list(project_node_list=extended_compiler_common_project_list,
                                                                                                                             compiler_features=extended_compiler.features,
                                                                                                                             compiler_feature_rules=extended_compiler.feature_rules)) is None:
                console.print_error(f"When extending '{to_extend_compiler_node.name}' compiler")
                return None

            extended_compiler.profile_list = extended_compiler_profile_list
            extended_compiler.is_self_extended = True
            ExtendedCompilerNodeRegistry.register_extended_compiler(extended_compiler)
        assert extended_compiler.is_self_extended
        return extended_compiler
            
    @staticmethod
    def _extend_and_validate_features(base_compiler_node: Self, to_extend_compiler_node: Self) -> Self | None:
        base_compiler_node :CompilerNode = base_compiler_node
        to_extend_compiler_node: CompilerNode = to_extend_compiler_node
        assert base_compiler_node.is_self_extended, f"'Base {base_compiler_node.name}' must be extended"
        assert not to_extend_compiler_node.is_self_extended, f"'{to_extend_compiler_node.name}' Already extended"

        if(extended := ExtendedCompilerNodeRegistry.get(to_extend_compiler_node.name)) is None:
            # Check that the base compiler node match the 'extends' 
            if to_extend_compiler_node.extends_name != base_compiler_node.name:
                console.print_error(f"Incoherent target extends: Try to extend '{to_extend_compiler_node.name}' with '{base_compiler_node.name}' but '{to_extend_compiler_node.name}' extends '{to_extend_compiler_node.extends_name}' ")
                exit(1)

            extended = CompilerNode(to_extend_compiler_node.name)
            extended.is_self_extended = True
            extended.file = to_extend_compiler_node.file
            extended.extends_name = to_extend_compiler_node.extends_name
            if not to_extend_compiler_node.cxx_path or str(to_extend_compiler_node.cxx_path) == ".":
                extended.cxx_path = base_compiler_node.cxx_path
            else:
                extended.cxx_path = to_extend_compiler_node.cxx_path
            if not to_extend_compiler_node.c_path or str(to_extend_compiler_node.c_path) == ".":
                extended.c_path = base_compiler_node.c_path
            else:
                extended.c_path = to_extend_compiler_node.c_path

            # 1. Extends feature rules with base_compiler_node feature rules
            extended.feature_rules = to_extend_compiler_node.feature_rules.extends_with_other(other_feature_rule_list=base_compiler_node.feature_rules)

            # 2. Extends features with base_compiler_node features, this will check that the features validate feature rules
            extended.features = to_extend_compiler_node.features.extend_with_other(other_features_list=base_compiler_node.features,
                                                                                   compiler_feature_rules=extended.feature_rules)
            # 3. Extends common part of the feature with base_compiler_node common part, this will check that the common enable features validate feature rules
            extended.commons = to_extend_compiler_node.commons.extends_with_other(other_commons=base_compiler_node.commons,
                                                                                  compiler_features=extended.features,
                                                                                  compiler_feature_rules=extended.feature_rules)
            # 4. Extends project with common part, this will check that the merge of common and project specific validate feature rules
            extended.common_project_list = to_extend_compiler_node.common_project_list.extend_with_other(other_project_node_list=base_compiler_node.common_project_list,
                                                                                                         compiler_features=extended.features,
                                                                                                         compiler_feature_rules=extended.feature_rules)
            # 5. Extends profile with project part, this will check that the merge of common and profile specific validate feature rules
            extended.profile_list = to_extend_compiler_node.profile_list.extend_with_other(other_profile_list=base_compiler_node.profile_list,
                                                                                           compiler_features=extended.features,
                                                                                           compiler_feature_rules=extended.feature_rules)

            # Register for futur use
            ExtendedCompilerNodeRegistry.register_extended_compiler(extended)
        assert extended.is_self_extended
        return extended

    def extend_with_commons(self, commons: Commons, common_project_list : ProjectNodeList, profile_list : ProfileNodeList) -> Optional[Self]:
        
        # Flattening the compiler hierarchy establishes a dependency order.
        # This ensures safe iteration where all included compilers are
        # resolved before the compiler that extends them.
        # In other words, if compiler A extends B, then B appears before A.
        flatten_compiler_extends = self._flatten_extends_compilers()
        
        # Start by extending the top-most base compiler and validate features
        # at each level until we reach the target compiler.
        base_compiler_node: CompilerNode = CompilerNodeRegistry.get(flatten_compiler_extends[0].name)
        
        # Extend the base
        if (extended_base := CompilerNode._extend_no_base_then_validate_features(to_extend_compiler_node=base_compiler_node,
                                                                                 commons=commons,
                                                                                 common_project_list=common_project_list,
                                                                                 profile_list=profile_list)) is None:
            return None
        
        # If there is no compiler to extend from the base, return the extended_base directly
        if( to_extend_compiler_node := CompilerNodeRegistry.get(flatten_compiler_extends[1].name) if len(flatten_compiler_extends) > 1 else None) is None:
           return extended_base

        extends_ordered_list = list[CompilerNode]()
        # If there is an to_extend_compiler_node compiler, combine it with the base.
        # The result becomes the new base for the next compiler in the extension chain.
        if (extended_base := CompilerNode._extend_and_validate_features(extended_base, to_extend_compiler_node)) is None:
            return None
        extends_ordered_list.insert(0,extended_base)
        # Extend the base with all subsequent compilers in the list.
        # This is analogous to: ((((A + B) + C) + D) + E)
        # where each intermediate result becomes the new 'base' for the next extension.
        for to_extend_compiler_node in flatten_compiler_extends[2:]:
            new_extended_base = extended_base
            if (new_extended_base := CompilerNode._extend_and_validate_features(new_extended_base, to_extend_compiler_node)) is None:
                return None
            extends_ordered_list.insert(0,extended_base)

        # extended_base is the last node in the last taht match self.name in the flatten_compiler_extends list
        extended_base.extends_ordered_list = extends_ordered_list
        return extended_base
    
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
        self.commons = Commons()
        self.common_project_list = ProjectNodeList()
        self.profile_list = ProfileNodeList()

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

    def get_extended(self, compiler_name : str) -> Optional[Self] :
        if (compiler_node := self.get(compiler_name)) is None:
            console.print_error(f"Compiler {compiler_name} not found")
            return None
        return compiler_node.extend_with_commons(commons=self.commons,
                                                 common_project_list=self.common_project_list,
                                                 profile_list=self.profile_list)

################################################
# List of all 'CompilerNode' loaded by files
# They are non extended compilers infos
################################################
class CompilerNodeRegistry:
    def __init__(self):
        self.compiler_list = CompilerNodeList()
    
    def __contains__(self, name: str) -> bool:
        return name in self.compiler_list

    def __iter__(self):
        return iter(self.compiler_list)
    
    def get(self, name: str) -> Optional[CompilerNode]:
        return self.compiler_list.get(name)
    
    def commons(self) -> Commons:
        return self.compiler_list.commons
    
    def profile_list(self) -> ProfileNodeList:
        return self.compiler_list.profile_list
    
    def common_project_list(self) -> ProjectNodeList:
        return self.compiler_list.common_project_list
    
    def get_extended(self, compiler_name : str) -> Optional[CompilerNode] :
        return self.compiler_list.get_extended(compiler_name=compiler_name)
    
    def register_compiler(self, compiler: CompilerNode):
        existing_compiler = self.compiler_list.get(compiler.name)
        if existing_compiler:
            console.print_error(f"Error: Compiler node already registered: {existing_compiler.name} in {str(existing_compiler.file)}")
            exit(1)
        self.compiler_list.add(compiler)


CompilerNodeRegistry = CompilerNodeRegistry()


################################################
# List of 'CompilerNode' loaded by files
# The are extended compilers infos
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
        assert compiler.is_self_extended
        existing_compiler = self.compilers.get(compiler.name)
        if existing_compiler:
            console.print_error(f"Error: Extended compiler node already registered: {existing_compiler.name} in {str(existing_compiler.file)}")
            exit(1)
        self.compilers.add(compiler)


ExtendedCompilerNodeRegistry = ExtendedCompilerNodeRegistry()