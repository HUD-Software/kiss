#####################################################################
# CompilerInfoLoader represent a yaml file that contains compilers to load
#####################################################################
from pathlib import Path
from typing import Optional
import console
from project import ProjectType
from yaml_file.line_loader import YamlObject
from toolchain.compiler.compiler_info import CompilerNodeRegistry, ProjectTypeNodeList, CompilerNode, CompilerNodeList, FeatureNode, FeatureNodeList, FeatureRuleNodeIncompatibleWith, FeatureRuleNodeList, FeatureRuleNodeOnlyOne, ProfileNode, ProfileNodeList, ProjectTypeNode, Commons

class CompilerInfoLoader:
    def __init__(self, file: Path):
        self.file = file
        self.compilers = CompilerNodeList()
    
    def _read_yaml_enable_feature(self, yaml_object: YamlObject) -> Optional[list[str]]:
        # Check that 'enable-features' is a list of string
        if not isinstance(yaml_object.value, list) or not all(isinstance(x, str) for x in yaml_object.value):
            console.print_error(f"Line {yaml_object.key_line} : 'enable-features' must contains list of feature name in '{self.file}'")
            return None
        return yaml_object.value
    
    def _read_yaml_cxx_linker_flags(self, yaml_object: YamlObject) -> Optional[list[str]]:
        # Check that 'cxx-linker-flags' is a list of string
        if not isinstance(yaml_object.value, list) or not all(isinstance(x, str) for x in yaml_object.value):
            console.print_error(f"Line {yaml_object.key_line} : 'cxx-linker-flags' must contains list of feature name in '{self.file}'")
            return None
        return yaml_object.value
    
    def _read_yaml_cxx_compiler_flags(self, yaml_object: YamlObject) -> Optional[list[str]]:
        # Check that 'cxx-compiler-flags' is a list of string
        if not isinstance(yaml_object.value, list) or not all(isinstance(x, str) for x in yaml_object.value):
            console.print_error(f"Line {yaml_object.key_line} : 'cxx-compiler-flags' must contains list of feature name in '{self.file}'")
            return None
        return yaml_object.value
    
    def is_yaml_name_commons(self, yaml_object: YamlObject) -> bool:
        pass 

    def read_commmons(self, yaml_object: YamlObject) -> Optional[Commons]:
        commons = Commons()
        for item, yaml_object in yaml_object.value.items():
            match item:
                case "cxx-compiler-flags":
                    if(cxx_compiler_flags := self._read_yaml_cxx_compiler_flags(yaml_object)) is None:
                        return None
                    commons.cxx_compiler_flags.add_list(cxx_compiler_flags)
                case "cxx-linker-flags":
                    if(cxx_linker_flags := self._read_yaml_cxx_linker_flags(yaml_object)) is None:
                        return None
                    commons.cxx_linker_flags.add_list(cxx_linker_flags)
                case "enable-features":
                    if(feature_name_list := self._read_yaml_enable_feature(yaml_object)) is None:
                        return None
                    commons.enable_features.add_list(feature_name_list)
                case _:
                    console.print_error(f"Line {yaml_object.key_line} : Unknown key '{item}' in'{self.file}'")
                    continue
        return commons
    def _read_yaml_project_type(self, project_type_name: str, yaml_object: YamlObject) -> Optional[ProjectTypeNode]:
        project_type_node = ProjectTypeNode(project_type_name)        
        return project_type_node

    def _read_bin_lib_dyn(self, project_type: ProjectType, yaml_object: YamlObject) -> ProjectTypeNode | None:
        project_specific = ProjectTypeNode(project_type)
        for item, yaml_object in yaml_object.value.items():
            match item:
                case "cxx-compiler-flags":
                    if(cxx_compiler_flags := self._read_yaml_cxx_compiler_flags(yaml_object)) is None:
                        return None
                    project_specific.cxx_compiler_flags.add_list(cxx_compiler_flags)
                case "cxx-linker-flags":
                    if(cxx_linker_flags := self._read_yaml_cxx_linker_flags(yaml_object)) is None:
                        return None
                    project_specific.cxx_linker_flags.add_list(cxx_linker_flags)
                case "enable-features":
                    if(feature_name_list := self._read_yaml_enable_feature(yaml_object)) is None:
                        return None
                    project_specific.enable_features.add_list(feature_name_list)
                case _:
                    console.print_error(f"Line {yaml_object.key_line} : Unknown key '{item}' in'{self.file}'")
                    continue
        return project_specific
    
    def _read_project_list(self, yaml_object: YamlObject) -> Optional[ProjectTypeNodeList]:
        project_type_list = ProjectTypeNodeList()
        for project_type_name, yaml_object in yaml_object.value.items():
            project_type_node = ProjectTypeNode(project_type_name)
            for item, yaml_object in yaml_object.value.items():
                match item:
                    case "cxx-compiler-flags":
                        if(cxx_compiler_flags := self._read_yaml_cxx_compiler_flags(yaml_object)) is None:
                            return None
                        project_type_node.commons.cxx_compiler_flags.add_list(cxx_compiler_flags)
                    case "cxx-linker-flags":
                        if(cxx_linker_flags := self._read_yaml_cxx_linker_flags(yaml_object)) is None:
                            return None
                        project_type_node.commons.cxx_linker_flags.add_list(cxx_linker_flags)
                    case "enable-features":
                        if(feature_name_list := self._read_yaml_enable_feature(yaml_object)) is None:
                            return None
                        project_type_node.commons.enable_features_list.add_list(feature_name_list)
                    case _:
                        console.print_error(f"Line {yaml_object.key_line} : Unknown key '{item}' in'{self.file}'")
                        continue
            project_type_list.add(project_type_node)
        return project_type_list
    
    def _read_profile_list(self, yaml_object: YamlObject) -> ProfileNodeList | None:
        profiles = ProfileNodeList()
        for profile_or_project_type_name, yaml_object_profile_or_project_type in yaml_object.value.items():
            if ProjectType.is_valid_str(profile_or_project_type_name):
                project_type_name = profile_or_project_type_name
                if project_type_name in profiles.common_bin_lib_dyn_set:
                    console.print_error(f"Line {yaml_object.key_line} : '{project_type_name}' already exist in 'profiles' in '{self.file}'")
                    return None
                yaml_project_type = yaml_object_profile_or_project_type
                project_specific = self._read_bin_lib_dyn(ProjectType(project_type_name), yaml_project_type)
                if project_specific is None:
                    return None
                profiles.common_bin_lib_dyn_set.add(project_specific)
            else:
                profile_name = profile_or_project_type_name
                profile = ProfileNode(profile_name)
                yaml_object_profile = yaml_object_profile_or_project_type
                if not yaml_object_profile.value:
                    console.print_warning(f"⚠️ Line {yaml_object_profile.key_line} : Profile 'profile_name' is empty in '{self.file}'")
                else:
                    for item, yaml_object in yaml_object_profile.value.items():
                        match item:
                            case "is_abstract":
                                # Check that 'is_abstract' is a boolean
                                if not isinstance(yaml_object.value, bool):
                                    console.print_error(f"Line {yaml_object.key_line} : 'is_abstract' must be a boolean value (true|false) in '{self.file}'")
                                    return None
                                profile.is_abstract = yaml_object.value
                            case "enable-features":
                                # Check that 'enable-features' is a list of string
                                if not isinstance(yaml_object.value, list) or not all(isinstance(x, str) for x in yaml_object.value):
                                    console.print_error(f"Line {yaml_object.key_line} : 'enable-features' must contains list of feature name in '{self.file}'")
                                    return None
                                profile.bin_lib_dyn_list.common_enable_features.add_list(yaml_object.value)
                            case "cxx-compiler-flags":
                                # Check that 'cxx-compiler-flags' is a list of string
                                if not isinstance(yaml_object.value, list) or not all(isinstance(x, str) for x in yaml_object.value):
                                    console.print_error(f"Line {yaml_object.key_line} : 'cxx-compiler-flags' must contains list of feature name in '{self.file}'")
                                    return None
                                profile.bin_lib_dyn_list.common_cxx_compiler.add_list(yaml_object.value)
                            case "cxx-linker-flags":
                                # Check that 'cxx-linker-flags' is a list of string
                                if not isinstance(yaml_object.value, list) or not all(isinstance(x, str) for x in yaml_object.value):
                                    console.print_error(f"Line {yaml_object.key_line} : 'cxx-linker-flags' must contains list of feature name in '{self.file}'")
                                    return None
                                profile.bin_lib_dyn_list.common_cxx_linker.add_list(yaml_object.value)
                            case "extends":
                                # Check that 'extends' is a string
                                if not isinstance(yaml_object.value, str):
                                    console.print_error(f"Line {yaml_object.key_line} : 'extends' must be a profile name in '{self.file}'")
                                    return None
                                profile.extends_name = yaml_object.value
                            case _:
                                if ProjectType.is_valid_str(item):
                                    # Check that 'bin|lib`|dyn' appears only one time
                                    if item in profile.bin_lib_dyn_list:
                                        console.print_error(f"Line {yaml_object.key_line} : '{item}' already exist in profile '{profile.name}' in '{self.file}'")
                                        return None
                                    project_specific = self._read_bin_lib_dyn(ProjectType(item), yaml_object)
                                    if project_specific is None:
                                        return None
                                    profile.bin_lib_dyn_list.add(project_specific)
                                else:
                                    console.print_error(f"Line {yaml_object.key_line} : Unknown key '{item}' in '{self.file}'")
                                    continue
                profiles.add(profile)
        return profiles
    
    def _read_compiler_features(self, yaml_object: YamlObject) -> FeatureNodeList | None:
        feature_list = FeatureNodeList()
        for yaml_object_feature in yaml_object.value:
            # Read the name as it is required
            feature_name = yaml_object_feature.get("name")
            if not feature_name:
                console.print_error(f"Line {yaml_object.key_line} : FeatureNode 'name' is required for a feature in '{self.file}'")
                return None
            if feature_name in feature_list:
                console.print_error(f"Line {yaml_object.key_line} : FeatureNode '{feature_name.value}' already exist in '{self.file}'")
                return None
            
            # Read the feature
            feature = FeatureNode(feature_name.value)
            for item, yaml_object in yaml_object_feature.items():
                match item:
                    case "name":
                        continue
                    case "description":
                        # Check that 'extends' is a string
                        if not isinstance(yaml_object.value, str):
                            console.print_error(f"Line {yaml_object.key_line} : 'description' must be a string in '{self.file}'")
                            return None
                        feature.description = yaml_object.value
                    case "enable-features":
                        # Check that 'enable-features' is a list of string
                        if not isinstance(yaml_object.value, list) or not all(isinstance(x, str) for x in yaml_object.value):
                            console.print_error(f"Line {yaml_object.key_line} : 'enable-features' must contains list of feature name in '{self.file}'")
                            return None
                        feature.enable_features.add_list(yaml_object.value)
                    case "cxx-compiler-flags":
                        # Check that 'cxx-compiler-flags' is a list of string
                        if not isinstance(yaml_object.value, list) or not all(isinstance(x, str) for x in yaml_object.value):
                            console.print_error(f"Line {yaml_object.key_line} : 'cxx-compiler-flags' must contains list of feature name in '{self.file}'")
                            return None
                        feature.cxx_compiler_flags.add_list(yaml_object.value)
                    case "cxx-linker-flags":
                        # Check that 'cxx-linker-flags' is a list of string
                        if not isinstance(yaml_object.value, list) or not all(isinstance(x, str) for x in yaml_object.value):
                            console.print_error(f"Line {yaml_object.key_line} : 'cxx-linker-flags' must contains list of feature name in '{self.file}'")
                            return None
                        feature.cxx_linker_flags.add_list(yaml_object.value)
                    case "profiles":
                        if not isinstance(yaml_object.value, dict):
                            console.print_error(f"Line {yaml_object.key_line} : 'profiles' must contains profiles '{self.file}'")
                            return None
                        profiles = self._read_profile_list(yaml_object)
                        if profiles is None:
                            return None
                        feature.profiles = profiles
                    case _:
                        if ProjectType.is_valid_str(item):
                            # Check that 'bin|lib`|dyn' appears only one time
                            if item in feature.common_bin_lib_dyn_list:
                                console.print_error(f"Line {yaml_object.key_line} : '{item}' already exist in feature '{feature.name}' in '{self.file}'")
                                return None
                            project_specific = self._read_bin_lib_dyn(ProjectType(item), yaml_object)
                            if project_specific is None:
                                return None
                            feature.common_bin_lib_dyn_list.add(project_specific)
                        else:
                            console.print_error(f"Line {yaml_object.key_line} : Unknown key '{item}' in '{self.file}'")
                            continue
            feature_list.add(feature)
        return feature_list
    
    def _read_compiler_feature_list(self, yaml_object: YamlObject) -> FeatureRuleNodeList | None:
        feature_rules_list = FeatureRuleNodeList()
        for  yaml_object_feature_rule in yaml_object.value:
            # Read only-one feature rule
            feature_only_one_name = yaml_object_feature_rule.get(FeatureRuleNodeOnlyOne.KEY)
            if feature_only_one_name:
                if not isinstance(feature_only_one_name.value, str):
                    console.print_error(f"Line {feature_only_one_name.key_line} : '{FeatureRuleNodeOnlyOne.KEY}' must be a feature-rule name in '{self.file}'")
                    return None
                feature_only_one = FeatureRuleNodeOnlyOne(feature_only_one_name.value)
                features = yaml_object_feature_rule.get("features")
                if not isinstance(features.value, list) or not all(isinstance(x, str) for x in features.value):
                    console.print_error(f"Line {yaml_object.key_line} : 'features' must contains list of feature name in '{self.file}'")
                    return None
                feature_only_one.feature_list.add_list(features.value)
                feature_rules_list.add(feature_only_one)
                continue
            # Read incompatible feature rule
            feature_incompatible_name = yaml_object_feature_rule.get(FeatureRuleNodeIncompatibleWith.KEY)
            if feature_incompatible_name:
                if not isinstance(feature_incompatible_name.value, str):
                    console.print_error(f"Line {feature_incompatible_name.key_line} : '{FeatureRuleNodeIncompatibleWith.KEY}' must be a feature-rule name in '{self.file}'")
                    return None
                feature_incompatible = FeatureRuleNodeIncompatibleWith(feature_incompatible_name.value)
                feature = yaml_object_feature_rule.get("feature")
                if not isinstance(feature.value, str):
                    console.print_error(f"Line {feature_incompatible.key_line} : 'feature' must be a feature-rule name in '{self.file}'")
                    return None
                feature_incompatible.feature_name = feature.value
                with_list = yaml_object_feature_rule.get("with")
                if not isinstance(with_list.value, list) or not all(isinstance(x, str) for x in with_list.value):
                    console.print_error(f"Line {yaml_object.key_line} : 'with' must contains list of feature name in '{self.file}'")
                    return None
                feature_incompatible.incompatible_with.add_list(with_list.value)
                feature_rules_list.add(feature_incompatible)
                continue
           
            console.print_error(f"Line {yaml_object.key_line} : Unkown feature rule '{next(iter(yaml_object_feature_rule))}' in '{self.file}'")
            return None
        return feature_rules_list

    def _read_compiler_node(self, compiler_name: str, yaml_compiler : YamlObject) -> CompilerNode | None:
        compiler_node : CompilerNode = CompilerNode(compiler_name)

        # If the compiler is empty, ignore it
        if not yaml_compiler.value:
            console.print_warning(f"⚠️  Line {yaml_compiler.key_line} : compiler '{compiler_name}' is empty in '{self.file}'")
            return None

        # Read compiler elements
        for item, yaml_object in yaml_compiler.value.items():
            match item:
                case "is_abstract":
                    if not isinstance(yaml_object.value, bool):
                        console.print_error(f"Line {yaml_object.key_line} : 'is_abstract' must be a boolean value (true|false) in '{self.file}'")
                        return None
                    compiler_node.is_abstract = yaml_object.value
                case "extends":
                    # Check that 'extends' is a string
                    if not isinstance(yaml_object.value, str):
                        console.print_error(f"Line {yaml_object.key_line} : 'extends' in must be a compiler name in '{self.file}'")
                        return None
                    compiler_node.extends_name = yaml_object.value
                case "profiles":
                    if not isinstance(yaml_object.value, dict):
                        console.print_error(f"Line {yaml_object.key_line} : 'profiles' must contains profiles '{self.file}'")
                        return None
                    profiles = self._read_profile_list(yaml_object)
                    if profiles is None:
                        return None
                    compiler_node.profiles = profiles
                case "features":
                    if not isinstance(yaml_object.value, list):
                        console.print_error(f"Line {yaml_object.key_line} : 'features' must contains list of features in '{self.file}'")
                        return None
                    features = self._read_compiler_features(yaml_object)
                    if features is None:
                        return None
                    compiler_node.features = features
                case "feature-rules":
                    if not isinstance(yaml_object.value, list):
                        console.print_error(f"Line {yaml_object.key_line} : 'feature-rules' must contains list of feature rules in '{self.file}'")
                        return None
                    feature_rules = self._read_compiler_feature_list(yaml_object)
                    if feature_rules is None:
                        return None
                    compiler_node.feature_rules = feature_rules
                case "cxx_path":
                    if not isinstance(yaml_object.value, str):
                        console.print_error(f"Line {yaml_object.key_line} : 'cxx_path' in must be a compiler path in '{self.file}'")
                        return None
                    compiler_node.cxx_path = Path(yaml_object.value)
                case "c_path":
                    if not isinstance(yaml_object.value, str):
                        console.print_error(f"Line {yaml_object.key_line} : 'c_path' in must be a compiler path in '{self.file}'")
                        return None
                    compiler_node.c_path = Path(yaml_object.value)
                case _:
                    console.print_error(f"Line {yaml_object.key_line} : Unknown key '{item}' in '{self.file}'")
                    continue

        return compiler_node 


    def read_yaml_compilers(self, item_yaml_object):
        compiler_list = CompilerNodeList()
        for node_name, yaml_object in item_yaml_object.value.items():
            match node_name:
                case "cxx-compiler-flags":
                    if(cxx_compiler_flags := self._read_yaml_cxx_compiler_flags(yaml_object)) is None:
                        return None
                    CompilerNodeRegistry.compiler_list.commons.cxx_compiler_flags.add_list(cxx_compiler_flags)
                case "cxx-linker-flags":
                    if(cxx_linker_flags := self._read_yaml_cxx_linker_flags(yaml_object)) is None:
                        return None
                    CompilerNodeRegistry.compiler_list.commons.cxx_linker_flags.add_list(cxx_linker_flags)
                case "enable-features":
                    if(feature_name_list := self._read_yaml_enable_feature(yaml_object)) is None:
                        return None
                    CompilerNodeRegistry.compiler_list.commons.enable_features_list.add_list(feature_name_list)
                case "projects":
                    if(project_list := self._read_project_list(yaml_object)) is None:
                        return None
                    CompilerNodeRegistry.compiler_list.project_list = project_list
                case "profiles":
                    if(profile_list := self._read_profile_list(yaml_object)) is None:
                        return None
                case _:
                    # Ignore if we already have a compiler name
                    existing_compiler: CompilerNode = CompilerNodeRegistry.get(node_name)
                    if existing_compiler:
                        console.print_warning(f"⚠️ Line {yaml_object.key_line} : CompilerNode '{existing_compiler}' already exist in '{existing_compiler.file}' when loading '{self.file}'")
                        continue
                    
                    # Load the compiler
                    compiler = self._read_compiler_node(node_name, yaml_object)
                    if compiler is None:
                        console.print_warning(f"⚠️ Line {yaml_object.key_line} : CompilerNode '{node_name}' in '{self.file}' will not be available")
                        continue
                    compiler.file = self.file

                    # Add it to the available compiler list
                    CompilerNodeRegistry.register_compiler(compiler)
                    self.compilers.add(compiler)

                    
           


