#####################################################################
# CompilerInfoLoader represent a yaml file that contains compilers to load
#####################################################################
from pathlib import Path
import console
from project import ProjectType
from yaml_file.line_loader import YamlObject
from toolchain.compiler.compiler_info import CXXLinkerFlagList, CompilerInfoRegistry, CompilerInfo, CompilerInfoList, Feature, FeatureList, FeatureRuleIncompatibleWith, FeatureRuleList, FeatureRuleOnlyOne, ProfileInfo, ProfileInfoList, ProjectSpecific

class CompilerInfoLoader:
    def __init__(self, file: Path):
        self.file = file
        self.compilers = CompilerInfoList()
    
    def _read_project_specific(self, project_type: ProjectType, yaml_object: YamlObject) -> ProjectSpecific | None:
        project_specific = ProjectSpecific(project_type)
        for item, yaml_object in yaml_object.value.items():
            match item:
                case "cxx-compiler-flags":
                    # Check that 'cxx-compiler-flags' is a list of string
                    if not isinstance(yaml_object.value, list) or not all(isinstance(x, str) for x in yaml_object.value):
                        console.print_error(f"❌ Line {yaml_object.key_line} : 'cxx-compiler-flags' must contains list of feature name in'{self.file}'")
                        return None
                    project_specific.cxx_compiler_flags.extend(yaml_object.value)
                case "cxx-linker-flags":
                    # Check that 'cxx-linker-flags' is a list of string
                    if not isinstance(yaml_object.value, list) or not all(isinstance(x, str) for x in yaml_object.value):
                        console.print_error(f"❌ Line {yaml_object.key_line} : 'cxx-linker-flags' must contains list of feature name in'{self.file}'")
                        return None
                    
                    project_specific.cxx_linker_flags.extend(yaml_object.value)
                case "enable-features":
                    # Check that 'enable-features' is a list of string
                    if not isinstance(yaml_object.value, list) or not all(isinstance(x, str) for x in yaml_object.value):
                        console.print_error(f"❌ Line {yaml_object.key_line} : 'enable-features' must contains list of feature name in'{self.file}'")
                        return None
                    project_specific.enable_features.feature_names.extend(yaml_object.value)
                case _:
                    console.print_error(f"❌ Line {yaml_object.key_line} : Unknown key '{item}' in'{self.file}'")
                    continue
        return project_specific
    
    def _read_profiles(self, yaml_object: YamlObject) -> ProfileInfoList | None:
        profiles = ProfileInfoList()
        for profile_name, yaml_object_profile in yaml_object.value.items():
            profile = ProfileInfo(profile_name)
            for item, yaml_object in yaml_object_profile.value.items():
                match item:
                    case "is_abstract":
                        # Check that 'is_abstract' is a boolean
                        if not isinstance(yaml_object.value, bool):
                            console.print_error(f"❌ Line {yaml_object.key_line} : 'is_abstract' must be a boolean value (true|false) in '{self.file}'")
                            return None
                        profile.is_abstract = yaml_object.value
                    case "enable-features":
                        # Check that 'enable-features' is a list of string
                        if not isinstance(yaml_object.value, list) or not all(isinstance(x, str) for x in yaml_object.value):
                            console.print_error(f"❌ Line {yaml_object.key_line} : 'enable-features' must contains list of feature name in'{self.file}'")
                            return None
                        profile.enable_features.feature_names.extend(yaml_object.value)
                    case "cxx-compiler-flags":
                        # Check that 'cxx-compiler-flags' is a list of string
                        if not isinstance(yaml_object.value, list) or not all(isinstance(x, str) for x in yaml_object.value):
                            console.print_error(f"❌ Line {yaml_object.key_line} : 'cxx-compiler-flags' must contains list of feature name in'{self.file}'")
                            return None
                        profile.cxx_compiler_flags.extend(yaml_object.value)
                    case "cxx-linker-flags":
                        # Check that 'cxx-linker-flags' is a list of string
                        if not isinstance(yaml_object.value, list) or not all(isinstance(x, str) for x in yaml_object.value):
                            console.print_error(f"❌ Line {yaml_object.key_line} : 'cxx-linker-flags' must contains list of feature name in'{self.file}'")
                            return None
                        profile.cxx_linker_flags.extend(yaml_object.value)
                    case "extends":
                        # Check that 'extends' is a string
                        if not isinstance(yaml_object.value, str):
                            console.print_error(f"❌ Line {yaml_object.key_line} : 'extends' must be a profile name in'{self.file}'")
                            return None
                        profile.extends = yaml_object.value
                    case _:
                        if ProjectType.is_valid_str(item):
                            # Check that 'bin|lib`|dyn' appears only one time
                            if item in profile.project_specifics:
                                console.print_error(f"❌ Line {yaml_object.key_line} : 'item' already exist in profile '{profile.name}' in'{self.file}'")
                                return None
                            project_specific = self._read_project_specific(ProjectType(item), yaml_object)
                            if project_specific is None:
                                return None
                            profile.project_specifics.add(project_specific)
                        else:
                            console.print_error(f"❌ Line {yaml_object.key_line} : Unknown key '{item}' in '{self.file}'")
                            continue
            profiles.add(profile)
        return profiles
    
    def _read_compiler_features(self, yaml_object: YamlObject) -> FeatureList | None:
        feature_list = FeatureList()
        for yaml_object_feature in yaml_object.value:
            # Read the name as it is required
            feature_name = yaml_object_feature.get("name")
            if not feature_name:
                console.print_error(f"❌ Line {yaml_object.key_line} : Feature 'name' is required for a feature in '{self.file}'")
                return None
            if feature_name in feature_list:
                console.print_error(f"❌ Line {yaml_object.key_line} : Feature '{feature_name}' already exist in '{self.file}'")
                return None
            
            # Read the feature
            feature = Feature(feature_name)
            for item, yaml_object in yaml_object_feature.items():
                match item:
                    case "name":
                        continue
                    case "description":
                        # Check that 'extends' is a string
                        if not isinstance(yaml_object.value, str):
                            console.print_error(f"❌ Line {yaml_object.key_line} : 'description' must be a string in'{self.file}'")
                            return None
                        feature.description = yaml_object.value
                    case "enable-features":
                        # Check that 'enable-features' is a list of string
                        if not isinstance(yaml_object.value, list) or not all(isinstance(x, str) for x in yaml_object.value):
                            console.print_error(f"❌ Line {yaml_object.key_line} : 'enable-features' must contains list of feature name in'{self.file}'")
                            return None
                        feature.enable_features.feature_names.extend(yaml_object.value)
                    case "cxx-compiler-flags":
                        # Check that 'cxx-compiler-flags' is a list of string
                        if not isinstance(yaml_object.value, list) or not all(isinstance(x, str) for x in yaml_object.value):
                            console.print_error(f"❌ Line {yaml_object.key_line} : 'cxx-compiler-flags' must contains list of feature name in'{self.file}'")
                            return None
                        feature.cxx_compiler_flags.extend(yaml_object.value)
                    case "cxx-linker-flags":
                        # Check that 'cxx-linker-flags' is a list of string
                        if not isinstance(yaml_object.value, list) or not all(isinstance(x, str) for x in yaml_object.value):
                            console.print_error(f"❌ Line {yaml_object.key_line} : 'cxx-linker-flags' must contains list of feature name in'{self.file}'")
                            return None
                        feature.cxx_linker_flags.extend(yaml_object.value)
                    case "profiles":
                        if not isinstance(yaml_object.value, dict):
                            console.print_error(f"❌ Line {yaml_object.key_line} : 'profiles' must contains profiles'{self.file}'")
                            return None
                        profiles = self._read_profiles(yaml_object)
                        if profiles is None:
                            return None
                        feature.profiles = profiles
                    case _:
                        console.print_error(f"❌ Line {yaml_object.key_line} : Unknown key '{item}' in'{self.file}'")
                        continue
            feature_list.add(feature)
        return feature_list
    
    def _read_compiler_feature_rules(self, yaml_object: YamlObject) -> FeatureRuleList | None:
        feature_rules_list = FeatureRuleList()
        for  yaml_object_feature_rule in yaml_object.value:
            # Read only-one feature rule
            feature_only_one_name = yaml_object_feature_rule.get("only-one")
            if feature_only_one_name:
                if not isinstance(feature_only_one_name.value, str):
                    console.print_error(f"❌ Line {feature_only_one_name.key_line} : 'only-one' must be a feature-rule name in'{self.file}'")
                    return None
                feature_only_one = FeatureRuleOnlyOne(feature_only_one_name.value)
                features = yaml_object_feature_rule.get("features")
                if not isinstance(features.value, list) or not all(isinstance(x, str) for x in features.value):
                    console.print_error(f"❌ Line {yaml_object.key_line} : 'features' must contains list of feature name in'{self.file}'")
                    return None
                feature_only_one.feature_list = features.value
                feature_rules_list.add(feature_only_one)
                continue
            # Read incompatible feature rule
            feature_incompatible_name = yaml_object_feature_rule.get("incompatible")
            if feature_incompatible_name:
                if not isinstance(feature_incompatible_name.value, str):
                    console.print_error(f"❌ Line {feature_incompatible_name.key_line} : 'only-one' must be a feature-rule name in'{self.file}'")
                    return None
                feature_incompatible = FeatureRuleIncompatibleWith(feature_incompatible_name.value)
                feature = yaml_object_feature_rule.get("feature")
                if not isinstance(feature.value, str):
                    console.print_error(f"❌ Line {feature_incompatible.key_line} : 'feature' must be a feature-rule name in'{self.file}'")
                    return None
                feature_incompatible.feature_name = feature.value
                with_list = yaml_object_feature_rule.get("with")
                if not isinstance(with_list.value, list) or not all(isinstance(x, str) for x in with_list.value):
                    console.print_error(f"❌ Line {yaml_object.key_line} : 'with' must contains list of feature name in'{self.file}'")
                    return None
                feature_incompatible.incompatible_with_feature_name_list = with_list
                feature_rules_list.add(feature_incompatible)
                continue
           
            console.print_error(f"❌ Line {yaml_object.key_line} : Unkown feature rule '{next(iter(yaml_object_feature_rule))}' in '{self.file}'")
            return None
        return feature_rules_list

    def _read_compiler_node(self, compiler_name: str, yaml_compiler : YamlObject) -> CompilerInfo | None:
       
        compiler : CompilerInfo = CompilerInfo(compiler_name)

        # If the compiler is empty, ignore it
        if not yaml_compiler.value:
            console.print_warning(f"⚠️  Line {yaml_compiler.key_line} : compiler '{compiler_name}' is empty in '{self.file}'")
            return None

        # Read compiler elements
        for item, yaml_object in yaml_compiler.value.items():
            match item:
                case "is_abstract":
                    if not isinstance(yaml_object.value, bool):
                        console.print_error(f"❌ Line {yaml_object.key_line} : 'is_abstract' must be a boolean value (true|false) in '{self.file}'")
                        return None
                    compiler.is_abstract = yaml_object.value
                case "extends":
                    # Check that 'extends' is a string
                    if not isinstance(yaml_object.value, str):
                        console.print_error(f"❌ Line {yaml_object.key_line} : 'extends' in must be a compiler name in'{self.file}'")
                        return None
                    compiler.extends = yaml_object.value
                case "profiles":
                    if not isinstance(yaml_object.value, dict):
                        console.print_error(f"❌ Line {yaml_object.key_line} : 'profiles' must contains profiles'{self.file}'")
                        return None
                    profiles = self._read_profiles(yaml_object)
                    if profiles is None:
                        return None
                    compiler.profiles = profiles
                case "features":
                    if not isinstance(yaml_object.value, list):
                        console.print_error(f"❌ Line {yaml_object.key_line} : 'features' must contains list of features in'{self.file}'")
                        return None
                    features = self._read_compiler_features(yaml_object)
                    if features is None:
                        return None
                    compiler.features = features
                case "feature-rules":
                    if not isinstance(yaml_object.value, list):
                        console.print_error(f"❌ Line {yaml_object.key_line} : 'feature-rules' must contains list of feature rules in'{self.file}'")
                        return None
                    feature_rules = self._read_compiler_feature_rules(yaml_object)
                    if feature_rules is None:
                        return None
                    compiler.feature_rules = feature_rules
                case _:
                    console.print_error(f"❌ Line {yaml_object.key_line} : Unknown key '{item}' in'{self.file}'")
                    continue

        return compiler 


    def read_yaml_compilers(self, item_yaml_object):
        for compiler_name, compiler_yaml_object in item_yaml_object.value.items():
            # Ignore if we already have a compiler name
            existing_compiler: CompilerInfo = self.compilers.get(compiler_name)
            if existing_compiler:
                console.print_error(f"❌ Line {compiler_yaml_object.key_line} : CompilerInfo '{existing_compiler}' already exist in '{existing_compiler.file}' when loading '{self.file}'")
                continue
            
            # Load the compiler
            compiler = self._read_compiler_node(compiler_name, compiler_yaml_object)
            if compiler is None:
                console.print_error(f"⚠️ Line {compiler_yaml_object.key_line} : CompilerInfo '{compiler_name}' in '{self.file}' will not be available")
                continue
            compiler.file = self.file

            # Add it to the available compiler list
            CompilerInfoRegistry.register_compiler(compiler)
            self.compilers.add(compiler)