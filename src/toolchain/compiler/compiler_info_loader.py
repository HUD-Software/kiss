#####################################################################
# CompilerInfoLoader represent a yaml file that contains compilers to load
#####################################################################
from pathlib import Path
from typing import Optional
import console
from yaml_file.line_loader import YamlObject
from toolchain.compiler.compiler_info import CompilerNodeRegistry, ProjectNodeList, CompilerNode, CompilerNodeList, FeatureNode, FeatureNodeList, FeatureRuleNodeIncompatibleWith, FeatureRuleNodeList, FeatureRuleNodeOnlyOne, ProfileNode, ProfileNodeList, ProjectTypeNode, Commons

class CompilerInfoLoader:
    def __init__(self, file: Path):
        self.file = file
    
    def _read_yaml_enable_feature(self, yaml_object: YamlObject) -> Optional[list[str]]:
        # Check that 'enable-features' is a list of string
        if not yaml_object.value:
            console.print_warning(f"'enable-features' is empty in '{self.file}({yaml_object.key_line})'")
        elif not isinstance(yaml_object.value, list) or not all(isinstance(x, str) for x in yaml_object.value):
            console.print_error(f"'enable-features' must contains list of feature name in '{self.file}({yaml_object.key_line})'")
            return None
        return yaml_object.value
    
    def _read_yaml_cxx_linker_flags(self, yaml_object: YamlObject) -> Optional[list[str]]:
        # Check that 'cxx-linker-flags' is a list of string
        if not yaml_object.value:
            console.print_warning(f"'cxx-linker-flags' is empty in '{self.file}({yaml_object.key_line})'")
        elif not isinstance(yaml_object.value, list) or not all(isinstance(x, str) for x in yaml_object.value):
            console.print_error(f"'cxx-linker-flags' must contains list of feature name in '{self.file}({yaml_object.key_line})'")
            return None
        return yaml_object.value
    
    def _read_yaml_cxx_compiler_flags(self, yaml_object: YamlObject) -> Optional[list[str]]:
        # Check that 'cxx-compiler-flags' is a list of string
        if not yaml_object.value:
            console.print_warning(f"'cxx-compiler-flags' is empty in '{self.file}({yaml_object.key_line})'")
        elif not isinstance(yaml_object.value, list) or not all(isinstance(x, str) for x in yaml_object.value):
            console.print_error(f"'cxx-compiler-flags' must contains list of feature name in '{self.file}({yaml_object.key_line})'")
            return None
        return yaml_object.value
    
    def _read_project_list(self, yaml_object: YamlObject) -> Optional[ProjectNodeList]:
        project_type_list = ProjectNodeList()
        for project_type_name, yaml_object in yaml_object.value.items():
            project_type_node = ProjectTypeNode(project_type_name)
            if not isinstance(yaml_object.value, dict):
                console.print_error(f"'projects' must contains projects type '{self.file}({yaml_object.key_line})'")
                return None
            elif not yaml_object.value:
                console.print_warning(f"Project type '{project_type_node}' is empty in '{self.file}({yaml_object.key_line})'")
            else:
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
                            console.print_error(f"Unknown key '{item}' in'{self.file}({yaml_object.key_line})'")
                            continue
            project_type_list.add(project_type_node)
        return project_type_list
    
    def _read_profile_list(self, yaml_object: YamlObject) -> Optional[ProfileNodeList]:
        profile_list = ProfileNodeList()

        for profile_name, yaml_object in yaml_object.value.items():
            profile = ProfileNode(profile_name)
            if not yaml_object.value:
                console.print_warning(f"Profile '{profile_name}' is empty in '{self.file}({yaml_object.key_line})'")
            else:
                for item, yaml_object in yaml_object.value.items():
                    match item:
                        case "cxx-compiler-flags":
                            if(cxx_compiler_flags := self._read_yaml_cxx_compiler_flags(yaml_object)) is None:
                                return None
                            profile.commons.cxx_compiler_flags.add_list(cxx_compiler_flags)
                        case "cxx-linker-flags":
                            if(cxx_linker_flags := self._read_yaml_cxx_linker_flags(yaml_object)) is None:
                                return None
                            profile.commons.cxx_linker_flags.add_list(cxx_linker_flags)
                        case "enable-features":
                            if(feature_name_list := self._read_yaml_enable_feature(yaml_object)) is None:
                                return None
                            profile.commons.enable_features_list.add_list(feature_name_list)
                        case "projects":
                            if(project_list := self._read_project_list(yaml_object)) is None:
                                return None
                            profile.projects.project_type_set.update(project_list.project_type_set)
                        case "is_abstract":
                            # Check that 'is_abstract' is a boolean
                            if not yaml_object.value:
                                console.print_warning(f"'is_abstract' in profile '{profile_name}' is empty in '{self.file}({yaml_object.key_line})'")
                            elif not isinstance(yaml_object.value, bool):
                                console.print_error(f"'is_abstract' must be a boolean value (true|false) in '{self.file}({yaml_object.key_line})'")
                                return None
                            else:
                                profile.is_abstract = yaml_object.value
                        case "extends":
                            # Check that 'extends' is a string
                            if not yaml_object.value:
                                console.print_warning(f"'extends' in profile '{profile_name}' is empty in '{self.file}({yaml_object.key_line})'")
                            elif not isinstance(yaml_object.value, str):
                                console.print_error(f"'extends' must be a profile name in '{self.file}({yaml_object.key_line})'")
                                return None
                            else:
                                profile.extends_name = yaml_object.value
                        case _:
                            console.print_error(f"Unknown key '{item}' in'{self.file}({yaml_object.key_line})'")
                            continue
            profile_list.add(profile)
        return profile_list
    
    def _read_compiler_features(self, yaml_object: YamlObject) -> FeatureNodeList | None:
        feature_list = FeatureNodeList()
        for yaml_object_feature in yaml_object.value:
            # Read the name as it is required
            feature_name = yaml_object_feature.get("name")
            if not feature_name:
                console.print_error(f"'name' is required for a feature in '{self.file}({yaml_object.key_line})'")
                return None
            if feature_name in feature_list:
                console.print_error(f"'{feature_name.value}' feature already exist in '{self.file}({yaml_object.key_line})'")
                return None
            
            # Read the feature
            feature = FeatureNode(feature_name.value)
            for item, yaml_object in yaml_object_feature.items():
                match item:
                    case "name":
                        continue
                    case "description":
                        # Check that 'description' is a string
                        if not yaml_object.value:
                            console.print_warning(f"'description' in feature '{feature_name.value}' is empty in '{self.file}({yaml_object.key_line})'")
                        elif not isinstance(yaml_object.value, str):
                            console.print_error(f"'description' must be a string in '{self.file}({yaml_object.key_line})'")
                            return None
                        else:
                            feature.description = yaml_object.value
                    case "enable-features":
                        # Check that 'enable-features' is a list of string
                        if not yaml_object.value:
                            console.print_warning(f"'enable-features' in feature '{feature_name.value}' is empty in '{self.file}({yaml_object.key_line})'")
                        elif not isinstance(yaml_object.value, list) or not all(isinstance(x, str) for x in yaml_object.value):
                            console.print_error(f"'enable-features' must contains list of feature name in '{self.file}({yaml_object.key_line})'")
                            return None
                        else:
                            feature.commons.enable_features_list.add_list(yaml_object.value)
                    case "cxx-compiler-flags":
                        # Check that 'cxx-compiler-flags' is a list of string
                        if not yaml_object.value:
                            console.print_warning(f"'cxx-compiler-flags' in feature '{feature_name.value}' is empty in '{self.file}({yaml_object.key_line})'")
                        elif not isinstance(yaml_object.value, list) or not all(isinstance(x, str) for x in yaml_object.value):
                            console.print_error(f"'cxx-compiler-flags' must contains list of feature name in '{self.file}({yaml_object.key_line})'")
                            return None
                        else:
                            feature.commons.cxx_compiler_flags.add_list(yaml_object.value)
                    case "cxx-linker-flags":
                        # Check that 'cxx-linker-flags' is a list of string
                        if not yaml_object.value:
                            console.print_warning(f"'cxx-linker-flags' in feature '{feature_name.value}' is empty in '{self.file}({yaml_object.key_line})'")
                        elif not isinstance(yaml_object.value, list) or not all(isinstance(x, str) for x in yaml_object.value):
                            console.print_error(f"'cxx-linker-flags' must contains list of feature name in '{self.file}({yaml_object.key_line})'")
                            return None
                        else:
                            feature.commons.cxx_linker_flags.add_list(yaml_object.value)
                    case "profiles":
                        if not yaml_object.value:
                            console.print_warning(f"'profiles' in feature '{feature_name.value}' is empty in '{self.file}({yaml_object.key_line})'")
                        elif not isinstance(yaml_object.value, dict):
                            console.print_error(f"'profiles' must contains profiles '{self.file}({yaml_object.key_line})'")
                            return None
                        elif( profiles := self._read_profile_list(yaml_object)) is None:
                            return None
                        feature.profile_list = profiles
                    case "projects":
                        if not yaml_object.value:
                            console.print_warning(f"'projects' in feature '{feature_name.value}' is empty in '{self.file}({yaml_object.key_line})'")
                        elif not isinstance(yaml_object.value, dict):
                            console.print_error(f"'projects' must contains projects '{self.file}({yaml_object.key_line})'")
                            return None
                        elif(project_list := self._read_project_list(yaml_object)) is None:
                            return None
                        feature.project_list = project_list
                    case _:
                        console.print_error(f"Unknown key '{item}' in '{self.file}({yaml_object.key_line})'")
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
                    console.print_error(f"'{FeatureRuleNodeOnlyOne.KEY}' must be a feature-rule name in '{self.file}({feature_only_one_name.key_line})'")
                    return None
                feature_only_one = FeatureRuleNodeOnlyOne(feature_only_one_name.value)
                features = yaml_object_feature_rule.get("features")
                if not isinstance(features.value, list) or not all(isinstance(x, str) for x in features.value):
                    console.print_error(f"features' must contains list of feature name in '{self.file}({yaml_object.key_line})'")
                    return None
                feature_only_one.feature_list.add_list(features.value)
                feature_rules_list.add(feature_only_one)
                continue
            # Read incompatible feature rule
            feature_incompatible_name = yaml_object_feature_rule.get(FeatureRuleNodeIncompatibleWith.KEY)
            if feature_incompatible_name:
                if not isinstance(feature_incompatible_name.value, str):
                    console.print_error(f"'{FeatureRuleNodeIncompatibleWith.KEY}' must be a feature-rule name in '{self.file}({feature_incompatible_name.key_line})'")
                    return None
                feature_incompatible = FeatureRuleNodeIncompatibleWith(feature_incompatible_name.value)
                feature = yaml_object_feature_rule.get("feature")
                if not isinstance(feature.value, str):
                    console.print_error(f"'feature' must be a feature-rule name in '{self.file}({feature_incompatible.key_line})'")
                    return None
                feature_incompatible.feature_name = feature.value
                with_list = yaml_object_feature_rule.get("with")
                if not isinstance(with_list.value, list) or not all(isinstance(x, str) for x in with_list.value):
                    console.print_error(f"'with' must contains list of feature name in '{self.file}({yaml_object.key_line})'")
                    return None
                feature_incompatible.incompatible_with.add_list(with_list.value)
                feature_rules_list.add(feature_incompatible)
                continue
           
            console.print_error(f"Unkown feature rule '{next(iter(yaml_object_feature_rule))}' in '{self.file}({yaml_object.key_line})'")
            return None
        return feature_rules_list

    def _read_compiler_node(self, compiler_name: str, yaml_compiler : YamlObject) -> CompilerNode | None:
        compiler_node : CompilerNode = CompilerNode(compiler_name)

        # If the compiler is empty, ignore it
        if not yaml_compiler.value:
            console.print_warning(f"'{compiler_name}' compiler is empty in '{self.file}({yaml_compiler.key_line})'")
            return None

        # Read compiler elements
        for item, yaml_object in yaml_compiler.value.items():
            match item:
                case "is_abstract":
                    if not yaml_object.value:
                        console.print_warning(f"'is_abstract' in compiler '{compiler_name}' is empty in '{self.file}({yaml_compiler.key_line})'")
                    elif not isinstance(yaml_object.value, bool):
                        console.print_error(f"'is_abstract' must be a boolean value (true|false) in '{self.file}({yaml_compiler.key_line})'")
                        return None
                    else:
                        compiler_node.is_abstract = yaml_object.value
                case "extends":
                    # Check that 'extends' is a string
                    if not yaml_object.value:
                        console.print_warning(f"'extends' in compiler '{compiler_name}' is empty in '{self.file}({yaml_compiler.key_line})'")
                    elif not isinstance(yaml_object.value, str):
                        console.print_error(f"'extends' in must be a compiler name in '{self.file}({yaml_compiler.key_line})'")
                        return None
                    else:
                        compiler_node.extends_name = yaml_object.value
                case "profiles":
                    if not yaml_object.value:
                        console.print_warning(f"'profiles' in compiler '{compiler_name}' is empty in '{self.file}({yaml_compiler.key_line})'")
                    elif not isinstance(yaml_object.value, dict):
                        console.print_error(f"'profiles' must contains profiles '{self.file}({yaml_compiler.key_line})'")
                        return None
                    elif( profiles := self._read_profile_list(yaml_object)) is None:
                        return None
                    else:
                        compiler_node.profile_list = profiles
                case "projects":
                    if not yaml_object.value:
                        console.print_warning(f"'projects' in compiler '{compiler_name}' is empty in '{self.file}({yaml_compiler.key_line})'")
                    elif not isinstance(yaml_object.value, dict):
                        console.print_error(f"'projects' must contains projects '{self.file}({yaml_compiler.key_line})'")
                        return None
                    elif( projects := self._read_project_list(yaml_object)) is None:
                        return None
                    else:
                        compiler_node.project_list = projects
                case "features":
                    if not yaml_object.value:
                        console.print_warning(f"'features' in compiler '{compiler_name}' is empty in '{self.file}({yaml_compiler.key_line})'")
                    elif not isinstance(yaml_object.value, list):
                        console.print_error(f"'features' must contains list of features in '{self.file}({yaml_compiler.key_line})'")
                        return None
                    elif( features := self._read_compiler_features(yaml_object)) is None:
                        return None
                    else:
                        compiler_node.features = features
                case "feature-rules":
                    if not yaml_object.value:
                        console.print_warning(f"'feature-rules' in compiler '{compiler_name}' is empty in '{self.file}({yaml_compiler.key_line})'")
                    elif not isinstance(yaml_object.value, list):
                        console.print_error(f"'feature-rules' must contains list of feature rules in '{self.file}({yaml_compiler.key_line})'")
                        return None
                    elif( feature_rules := self._read_compiler_feature_list(yaml_object)) is None:
                        return None
                    else:
                        compiler_node.feature_rules = feature_rules
                case "cxx-compiler-flags":
                    if(cxx_compiler_flags := self._read_yaml_cxx_compiler_flags(yaml_object)) is None:
                        return None
                    compiler_node.commons.cxx_compiler_flags.add_list(cxx_compiler_flags)
                case "cxx-linker-flags":
                    if(cxx_linker_flags := self._read_yaml_cxx_linker_flags(yaml_object)) is None:
                        return None
                    compiler_node.commons.cxx_linker_flags.add_list(cxx_linker_flags)
                case "enable-features":
                    if(feature_name_list := self._read_yaml_enable_feature(yaml_object)) is None:
                        return None
                    compiler_node.commons.enable_features_list.add_list(feature_name_list)
                case "cxx_path":
                    if not yaml_object.value:
                        console.print_warning(f"'cxx_path' in compiler '{compiler_name}' is empty in '{self.file}({yaml_compiler.key_line})'")
                    elif not isinstance(yaml_object.value, str):
                        console.print_error(f"'cxx_path' must contains C++ compiler path. '{self.file}({yaml_compiler.key_line})'")
                        return None
                    else:
                        compiler_node.cxx_path = yaml_object.value
                case "c_path":
                    if not yaml_object.value:
                        console.print_warning(f"'c_path' in compiler '{compiler_name}' is empty in '{self.file}({yaml_compiler.key_line})'")
                    elif not isinstance(yaml_object.value, str):
                        console.print_error(f"'c_path' must contains C++ compiler path. '{self.file}({yaml_compiler.key_line})'")
                        return None
                    else:
                        compiler_node.c_path = yaml_object.value
                case _:
                    console.print_error(f"Unknown key '{item}' in '{self.file}({yaml_compiler.key_line})'")
                    continue

        return compiler_node 


    def read_yaml_compilers(self, item_yaml_object):
        compiler_list = CompilerNodeList()
        for node_name, yaml_object in item_yaml_object.value.items():
            match node_name:
                case "cxx-compiler-flags":
                    if(cxx_compiler_flags := self._read_yaml_cxx_compiler_flags(yaml_object)) is None:
                        return None
                    compiler_list.commons.cxx_compiler_flags.add_list(cxx_compiler_flags)
                case "cxx-linker-flags":
                    if(cxx_linker_flags := self._read_yaml_cxx_linker_flags(yaml_object)) is None:
                        return None
                    compiler_list.commons.cxx_linker_flags.add_list(cxx_linker_flags)
                case "enable-features":
                    if(feature_name_list := self._read_yaml_enable_feature(yaml_object)) is None:
                        return None
                    compiler_list.commons.enable_features_list.add_list(feature_name_list)
                case "projects":
                    if(project_list := self._read_project_list(yaml_object)) is None:
                        return None
                    compiler_list.project_list = project_list
                case "profiles":
                    if(profile_list := self._read_profile_list(yaml_object)) is None:
                        return None
                    compiler_list.profile_list = profile_list
                case _:
                    # Ignore if we already have a compiler name
                    existing_compiler: CompilerNode = CompilerNodeRegistry.get(node_name)
                    if existing_compiler:
                        console.print_warning(f"'{existing_compiler}' compiler already exist in '{existing_compiler.file}' when loading '{self.file}({yaml_object.key_line})'")
                        continue
                    
                    # Load the compiler
                    if( compiler := self._read_compiler_node(node_name, yaml_object)) is None:
                        console.print_warning(f"'{node_name}' compiler in '{self.file}({yaml_object.key_line})' will not be available")
                        continue
                    compiler.file = self.file

                    # Add it to the available compiler list
                    compiler_list.add(compiler)
        
        # Register all compilers we just load
        for compiler in compiler_list:
            CompilerNodeRegistry.register_compiler(compiler)
        
                    
           


