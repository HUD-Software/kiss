
from pathlib import Path
from typing import Optional, Self, Union
import console
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
    def merge_with_other(self, other : Self) -> Self:
        merged = FlagList()
        merged.flags = self.flags.union(other.flags)
        return merged
    

##############################################################
# FeatureNameList are list of feature names
##############################################################
class FeatureNameList:
    def __init__(self):
        self.feature_names = set[str]()
     #   self.is_self_extended = False
        
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

    # Merge this feature list with another feature list
    # Check that the merge of the 2 feature list validate feature rules
    # Do not add features enabled by features in the other list, only features in self and other are merged
    def merge_with_other(self, other: Self, compiler_feature_rules) -> Optional[Self]:
        merged = FeatureNameList()

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
                    result = FeatureRuleNodeOnlyOne.ResultOnlyOne = only_one_rule.evaluate(merged)
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
        merged.feature_names = cleaned_list_base.feature_names.union(self.feature_names)
        # Check that merge feature_names validate feature-rules before merging
        if not compiler_feature_rules.is_feature_list_validate_rules(merged.feature_names):
            console.print_error(f"Rule invalidate feature list '{', '.join(list(merged.feature_names))}' ")
            return None
        return merged
    
    
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

    def merge_with_other(self, other_commons: Self, compiler_feature_rules) -> Optional[Self]:
        extended = Commons()
        extended.cxx_compiler_flags = self.cxx_compiler_flags.merge_with_other(other=other_commons.cxx_compiler_flags)
        extended.cxx_linker_flags = self.cxx_linker_flags.merge_with_other(other=other_commons.cxx_linker_flags)
        if(enable_feature := self.enable_features_list.merge_with_other(other=other_commons.enable_features_list,
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
        self.project_list = ProjectTypeNodeList()
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

    def merge_with_other(self, other : Self) -> Self:
        merged = CXXCompilerFlagList()
        merged.flags = self.flags.merge_with_other(other.flags)
        return merged
    
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

    def merge_with_other(self, other : Self) -> Self:
        merged = CXXLinkerFlagList()
        merged.flags = self.flags.merge_with_other(other.flags)
        return merged
    
###############################################################
# ProjectTypeNode add flags and features by project type
##############################################################
class ProjectTypeNode:
    def __init__(self, project_type_name: str):
        self.project_type_name = project_type_name
        self.commons = Commons()

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
    
    def merge_with_commons(self, 
                           commons: Commons, 
                           compiler_feature_rules:'FeatureRuleNodeList') -> Optional[Self]:
        merged = ProjectTypeNode(project_type_name=self.project_type_name)
        if( merged_commons := self.commons.merge_with_other(other_commons=commons,
                                                            compiler_feature_rules=compiler_feature_rules)) is None:
            return None
        merged.commons = merged_commons
        return merged
    
    def merge_with_other(self, 
                         other: Self, 
                         compiler_feature_rules:'FeatureRuleNodeList') -> Optional[Self]:
        return self.merge_with_commons(commons=other.commons, 
                                       compiler_feature_rules=compiler_feature_rules)

###############################################################
# ProjectTypeNodeList are list of ProjectTypeNode
##############################################################
class ProjectTypeNodeList:
    def __init__(self):
        self.project_type_set: set[ProjectTypeNode] = set()
    #    self.is_self_extended = False

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
    def get(self, project_type_node: ProjectTypeNode) -> Optional[ProjectTypeNode]:
        for p in self.project_type_set:
            if p.project_type_name == project_type_node.project_type_name:
                return p
        return None 
       
    def merge_with_commons(self, 
                           commons: Commons, 
                           compiler_feature_rules : 'FeatureRuleNodeList') -> Optional[Self]:
        merged = ProjectTypeNodeList()
        for project_type in self.project_type_set:
            if( merged_project_type := project_type.merge_with_commons(commons=commons,
                                                                       compiler_feature_rules=compiler_feature_rules)) is None:
                return None
            merged.add(merged_project_type)
        return merged
        
    def merge_with_other(self, 
                         other_project_node_list: Self, 
                         compiler_feature_rules : 'FeatureRuleNodeList') -> Optional[Self]:
        merged = ProjectTypeNodeList()
        for project_type in other_project_node_list.project_type_set:
            # If the project type is not in self, we add it to the extended
            if (existing_project_type := self.get(project_type)) is None:
                merged.project_type_set.add(project_type)
            # If the project type is in self, we extend it with the project type of other
            else:
                if(extended_existing_project_type := existing_project_type.merge_with_other(project_type, 
                                                                                            compiler_feature_rules)) is None:
                    return None
                merged.project_type_set.add(extended_existing_project_type)
        return merged
                
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
        self.project_type_list = ProjectTypeNodeList()
        # True if this node is extended with self
       # self.is_self_extended = False

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
        if len(self.project_type_list) > 0:
            lines.append(f" projects:")
            for project_type in self.project_type_list:
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
    

    def merge_with_commons_and_project_list(self, 
                                            commons: Commons, 
                                            project_type_list: ProjectTypeNodeList,
                                            compiler_feature_rules: 'FeatureRuleNodeList') -> Optional[Self]:
        merged = ProfileNode(self.name)
        merged.extends_name = self.extends_name
        merged.is_abstract = self.is_abstract
        
        # Merge global common in profile common
        if( merged_commons := self.commons.merge_with_other(other_commons=commons,
                                                            compiler_feature_rules=compiler_feature_rules)) is None:
            return None
        merged.commons = merged_commons

        # Merge global common in profile project list
        if( merged_project_list := self.project_type_list.merge_with_commons(commons=commons,
                                                                        compiler_feature_rules=compiler_feature_rules)) is None:
            return None
        
        # Merge global project list in profile project list
        if( merged_project_list := merged_project_list.merge_with_other(other_project_node_list=project_type_list,
                                                                        compiler_feature_rules=compiler_feature_rules)) is None:
            return None
        merged.project_type_list = merged_project_list
        return merged
           
    def merge_with_commons(self, 
                           commons: Commons,
                           compiler_feature_rules : 'FeatureRuleNodeList') -> Optional[Self]:
        merged = ProfileNode(self.name)
        merged.extends_name = self.extends_name
        merged.is_abstract = self.is_abstract

        if( merged_commons := self.commons.merge_with_other(other_commons=commons,
                                                            compiler_feature_rules=compiler_feature_rules)) is None:
            return None
        merged.commons = merged_commons

        if( merged_project_list := self.project_type_list.merge_with_commons(commons=commons,
                                                                               compiler_feature_rules=compiler_feature_rules)) is None:
            return None
        merged.project_type_list = merged_project_list

        return merged
   
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
#     compilers:        <== 'FileCompilerNodeList'
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

    def get(self, name: str) -> Optional[ProfileNode]:
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
    
    def merge_with_commons_and_project_list(self, 
                                            commons: Commons, 
                                            project_type_list: ProjectTypeNodeList,
                                            compiler_feature_rules: 'FeatureRuleNodeList') -> Optional[Self]:
        merged = ProfileNodeList()
        profiles_to_extend = self.profiles.copy()
        while profiles_to_extend:
            to_process_profile = profiles_to_extend.pop()
            if(extended_profile := to_process_profile.merge_with_commons_and_project_list(commons=commons,
                                                                                          project_type_list=project_type_list,
                                                                                          compiler_feature_rules=compiler_feature_rules)) is None:
                console.print_error(f"When extending '{to_process_profile.name}' profile with commons and project list.")
                return None
            merged.add(extended_profile)
        return merged
    

    def merge_with_other(self,
                         other_profile_list: Self,
                         compiler_feature_rules: 'FeatureRuleNodeList') -> Optional[Self]:
        merged = ProfileNodeList()
        for profile in other_profile_list.profiles:
            existing_profile = self.get(profile.name)
            # If the profile is not in other_profile_list, we add it to the merged
            if not existing_profile:
                merged.profiles.add(profile)
            # If the profile is in other_profile_list, we merge it with the profile of other_profile_list
            else:
                if(merged_profile := profile.merge_with_commons_and_project_list(commons=existing_profile.commons,
                                                                                 project_type_list=existing_profile.project_type_list,
                                                                                 compiler_feature_rules=compiler_feature_rules)) is None:
                    console.print_error(f"When merging '{profile.name}' profile with '{existing_profile.name}' profile.")
                    return None
                merged.profiles.add(merged_profile)
        return merged
    
    
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
#     compilers:          <== 'FileCompilerNodeList'
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

    def get(self, item: str | FeatureNode) -> Optional[FeatureNode]:
        if isinstance(item, FeatureNode):
            return item if item in self.features else None
        if isinstance(item, str):
            for f in self.features:
                if f.name == item:
                    return f
        return None
    
    def merge_with_other(self, other_features_list : Self) -> Optional[Self]:
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
        # Feature that are in both, we keep self feature
        for common_feature in common_features:
            extended.features.add(self.get(common_feature))
        # Add feature that are not common
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
#     compilers:              <== 'FileCompilerNodeList'
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
        
    def get(self, item: str | FeatureRuleNode) -> Optional[FeatureRuleNode]:
        if isinstance(item, FeatureRuleNode):
            return item if item in self.feature_rules else None
        if isinstance(item, str):
            for f in self.feature_rules:
                if f.name == item:
                    return f
        return None 
    
    def merge_with_other(self, other_feature_rule_list : Self) -> Optional[Self]:
        extended = FeatureRuleNodeList()
        # Get elements in self AND other_feature_rule_list
        common_feature_rules : set[FeatureNode] = self.feature_rules.intersection(other_feature_rule_list.feature_rules)
        # Get elements not in self and other_feature_rule_list
        non_commons_feature_rules : set[FeatureNode] = self.feature_rules.symmetric_difference(other_feature_rule_list.feature_rules)
        # Extends the common_feature_nodes and add the non common feature rules
        if common_feature_rules:
             console.print_error(f"Feature rule with same name both target [{', '.join(f.name for f in common_feature_rules)}]")
             return None
        # Feature rule that are in both, we keep self feature
        for common_feature_rule in common_feature_rules:
            extended.feature_rules.add(self.get(common_feature_rule))
        # Add feature rule that are not common
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
#     compilers:     <== 'FileCompilerNodeList'
#       clang:       <== 'CompilerNode'
######################################################
class CompilerNode:
    def __init__(self, name: str, file_path: Path):
        # The compiler name
        self.name = name
        # The file path where the compiler is defined, this is used for error reporting
        self.file_path = file_path
        # If this compiler is abstract ( Not usable by the user )
        self.is_abstract = False
        # The compiler used extends this one
        self.extends_name : str = None
        # List of flags and features that apply to all project types and all profiles
        self.commons = Commons()
        # List of project type specific flags and features with this compiler
        self.project_type_list = ProjectTypeNodeList()
        # List of profiles specific flags and features with this compiler
        self.profile_list = ProfileNodeList()
        # List of features
        self.features = FeatureNodeList()
        # List of feature rules that are common to all profiles
        self.feature_rules = FeatureRuleNodeList()
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
                extends_node = CompilerNodeRegistry.get_compiler_node(current_node.extends_name)
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

    # Merge this compiler commons, project list and profiles list inner parts.
    # This will check that the merge of commons, project list and profile list validate feature rules.
    # This do not extend features enabled by other features
    def merge_inner(self) -> Optional[Self]:
        merged = CompilerNode(self.name, self.file_path)
        merged.extends_name = self.extends_name
        merged.is_abstract = self.is_abstract
        merged.cxx_path = self.cxx_path
        merged.c_path = self.c_path
        merged.features = copy.deepcopy(self.features)
        merged.feature_rules = copy.deepcopy(self.feature_rules)
        merged.extends_ordered_list = self.extends_ordered_list.copy()

        if(extended_project_list := self.project_type_list.merge_with_commons(commons=self.commons,
                                                                         compiler_feature_rules=self.feature_rules)) is None:
            console.print_error(f"Error merging project list for compiler '{self.name}'")
            return None
        merged.project_type_list = extended_project_list

        if(extended_profile_list := self.profile_list.merge_with_commons_and_project_list(commons=self.commons,
                                                                                          project_type_list=extended_project_list,
                                                                                          compiler_feature_rules=self.feature_rules)) is None:
            console.print_error(f"Error merging profile list for compiler '{self.name}'")
            return None
        merged.profile_list = extended_profile_list
        return merged
    
    # Extends this compiler with the other compiler, 
    # this will merge commons, project list and profile list of the other compiler into this one.
    def extend_with_other(self, other_compiler_node: Self) -> Optional[Self]:
        extended = CompilerNode(self.name, self.file_path)
        extended.extends_name = self.extends_name
        extended.is_abstract = self.is_abstract
        extended.cxx_path = self.cxx_path or other_compiler_node.cxx_path
        extended.c_path = self.c_path or other_compiler_node.c_path
        extended.extends_ordered_list.append(other_compiler_node)

        # Extend feature rules
        if(extended_feature_rules := self.feature_rules.merge_with_other(other_feature_rule_list=other_compiler_node.feature_rules)) is None:
            console.print_error(f"Error extending feature rules for compiler '{self.name}' with '{other_compiler_node.name}'")
            return None
        extended.feature_rules = extended_feature_rules

        # Extend features
        if(extended_features := self.features.merge_with_other(other_features_list=other_compiler_node.features)) is None:
            console.print_error(f"Error extending features for compiler '{self.name}' with '{other_compiler_node.name}'")
            return None
        extended.features = extended_features

        # Extends commons
        if (extended_commons := self.commons.merge_with_other(other_commons=other_compiler_node.commons,
                                                              compiler_feature_rules=extended_feature_rules)) is None:
            console.print_error(f"Error extending commons for compiler '{self.name}' with '{other_compiler_node.name}'")
            return None
        extended.commons = extended_commons

        # Extends project list
        if( extended_project_list := self.project_type_list.merge_with_other(other_project_node_list=other_compiler_node.project_type_list,
                                                                        compiler_feature_rules=extended_feature_rules)) is None:
            console.print_error(f"Error extending project list for compiler '{self.name}' with '{other_compiler_node.name}'")
            return None
        if( extended_project_list := extended_project_list.merge_with_commons(commons=extended_commons,
                                                                              compiler_feature_rules=extended_feature_rules)) is None:
            console.print_error(f"Error extending project list with commons for compiler '{self.name}' with '{other_compiler_node.name}'")
            return None
        extended.project_type_list = extended_project_list

        # Extends profile list
        if( extended_profile_list := self.profile_list.merge_with_other(other_profile_list=other_compiler_node.profile_list,
                                                                        compiler_feature_rules=extended_feature_rules)) is None:
            console.print_error(f"Error extending profile list for compiler '{self.name}' with '{other_compiler_node.name}'")
            return None
        if( extended_profile_list := extended_profile_list.merge_with_commons_and_project_list(commons=extended_commons,
                                                                                               project_type_list=extended_project_list,
                                                                                               compiler_feature_rules=extended_feature_rules)) is None:
            console.print_error(f"Error extending profile list with commons for compiler '{self.name}' with '{other_compiler_node.name}'")
            return None
        extended.profile_list = extended_profile_list                                                   
        return extended

    # Extend this compiler by adding features enabled by features, this will add features enabled by features to the compiler features. 
    def extend_features(self) -> Optional[Self]:
        extended = CompilerNode(self.name, self.file_path)
        extended.extends_name = self.extends_name
        extended.is_abstract = self.is_abstract
        extended.cxx_path = self.cxx_path
        extended.c_path = self.c_path
        extended.extends_ordered_list =self.extends_ordered_list.copy()
        extended.feature_rules = copy.deepcopy(self.feature_rules)
        for feature in self.features:
            pass
        return extended

    def get_feature(self, feature_name: str) -> Optional[FeatureNode]:
        return self.features.get(feature_name)
    
################################################
# List of compilers defined in file
#
# Yaml:
#   <root>
#     compilers: <== 'FileCompilerNodeList'
################################################
class FileCompilerNodeList:
    def __init__(self, file_path: Path):
        self.file_path = file_path
        self.compilers : set[CompilerNode] = set()
        self.common_compiler = CompilerNode(name=str(file_path), file_path=file_path)

    def __hash__(self):
        return hash(self.file_path)

    def __eq__(self, other):
        if not isinstance(other, FileCompilerNodeList):
            return NotImplemented
        return self.file_path == other.file_path

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
        
        # 1. Merge common compiler
        if( merged_common := self.common_compiler.merge_inner()) is None:
            console.print_error(f"Error merging common for compiler {compiler_name} in file {str(self.file_path)}")
            return None
        extended_compiler = merged_common

        # Extends compiler one by one 
        flatten_extends = compiler_node._flatten_extends_compilers()
        # The first one should not have extends_name because it's the top-most base compiler, 
        # but if it does not have extends_name we set it with compiler common compiler name for better error reporting in the merge and extend process
        if flatten_extends and not flatten_extends[0].extends_name:
            flatten_extends[0].extends_name = extended_compiler.name

        # Extends all compiler one by one
        for compiler in flatten_extends:
            # 1. Merge inner part of the compiler
            if( merged_compiler := compiler.merge_inner()) is None:
                console.print_error(f"Error merging inner part of compiler {compiler_name} in file {str(self.file_path)}")
                return None
            
            # 2. Merge common compiler with compiler extend (base)
            if(extended_compiler := merged_compiler.extend_with_other(other_compiler_node=extended_compiler)) is None:
                console.print_error(f"Error merging common compiler with compiler {compiler_name} in file {str(self.file_path)}")
                return None

        # Extends features enabled by features
        # if(extended_features_compiler := extended_compiler.extend_features()) is None:
        #     console.print_error(f"Error extending features enabled by features for compiler {compiler_name} in file {str(self.file_path)}")
        #     return None
        # extended_compiler.features = extended_features_compiler

        return extended_compiler
        

################################################
# List of all 'FileCompilerNodeList' loaded
# They are non extended compilers infos
################################################
class CompilerNodeRegistry:
    def __init__(self):
        self.file_compiler_list = set[FileCompilerNodeList]()
    
    def __contains__(self, compiler_name: str) -> bool:
        return compiler_name in self.file_compiler_list

    def __iter__(self):
        return iter(self.file_compiler_list)
    
    def __len__(self):
        return len(self.file_compiler_list)
    
    def __contains__(self, compiler_name: str) -> bool:
        return compiler_name in self.file_compiler_list
    
    def get_compiler_node(self, compiler_name: str) -> Optional[CompilerNode]:
        for compiler_list in self.file_compiler_list:
            if (compiler := compiler_list.get(compiler_name)):
                 return compiler
        return None
    
    def get_compiler_list_with_compiler(self, compiler_name: str) -> Optional[FileCompilerNodeList]:
        for compiler_list in self.file_compiler_list:
            if compiler_name in compiler_list:
                return compiler_list
        return None
    
    def get_extended(self, compiler_name : str) -> Optional[CompilerNode] :
        if(compiler_node_list := self.get_compiler_list_with_compiler(compiler_name)) is None:
            console.print_error(f"Compiler {compiler_name} not found")
            return None
        return compiler_node_list.get_extended(compiler_name=compiler_name)
    
    def register_file_compiler_list(self, file_compiler_list: FileCompilerNodeList):
        if file_compiler_list in self.file_compiler_list:
            console.print_error(f"Error: Compiler file already registered: {str(file_compiler_list.file_path)}")
            exit(1)
        self.file_compiler_list.add(file_compiler_list)



CompilerNodeRegistry = CompilerNodeRegistry()
