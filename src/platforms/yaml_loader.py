from pathlib import Path
import yaml
import console
from platforms.platforms import Feature, FeatureList, FeatureNameList, FeatureRuleIncompatibleWith, FeatureRuleList, FeatureRuleOnlyOne, Profile, ProfileList, ProjectSpecific, Target, TargetList
from project import ProjectType

############################################################
# LineLoader used to keep track of line when parsing YAML
############################################################
class LineLoader(yaml.SafeLoader):
    pass

class YamlObject:
    def __init__(self, key_line, value, line):
        self.key_line = key_line
        self.value = value
        self.line = line
        
def construct_mapping(loader, node, deep=False):
    mapping = {}
    for key_node, value_node in node.value:
        key = loader.construct_object(key_node)
        value = loader.construct_object(value_node)

        mapping[key] = YamlObject(
            key_line=key_node.start_mark.line + 1,
            value=value,
            line=value_node.start_mark.line + 1
        )

    return mapping

LineLoader.add_constructor(
    yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG,
    construct_mapping,
)

#####################################################################
# YamlTargetFile represent a yaml file that contains targets to load
#####################################################################
class YamlTargetFile:
    def __init__(self, file: Path):
        self.file = file
        self.targets = TargetList()
    
    def _read_project_specific(self, project_type: ProjectType, yaml_object: YamlObject) -> ProjectSpecific | None:
        project_specific = ProjectSpecific(project_type)
        for item, yaml_object in yaml_object.value.items():
            match item:
                case "cxx-compiler-flags":
                    # Check that 'cxx-compiler-flags' is a list of string
                    if not isinstance(yaml_object.value, list) or not all(isinstance(x, str) for x in yaml_object.value):
                        console.print_error(f"❌ Line {yaml_object.key_line} : 'cxx-compiler-flags' must contains list of feature name in'{self.file}'")
                        return None
                    project_specific.cxx_compiler_flags = yaml_object.value
                case "cxx-linker-flags":
                    # Check that 'cxx-linker-flags' is a list of string
                    if not isinstance(yaml_object.value, list) or not all(isinstance(x, str) for x in yaml_object.value):
                        console.print_error(f"❌ Line {yaml_object.key_line} : 'cxx-linker-flags' must contains list of feature name in'{self.file}'")
                        return None
                    project_specific.cxx_linker_flags = yaml_object.value
                case "enable-features":
                    # Check that 'enable-features' is a list of string
                    if not isinstance(yaml_object.value, list) or not all(isinstance(x, str) for x in yaml_object.value):
                        console.print_error(f"❌ Line {yaml_object.key_line} : 'enable-features' must contains list of feature name in'{self.file}'")
                        return None
                    project_specific.enable_features.feature_names = yaml_object.value
                case _:
                    console.print_error(f"❌ Line {yaml_object.key_line} : Unknown key '{item}' in'{self.file}'")
                    continue
        return project_specific
    
    def _read_profiles(self, yaml_object: YamlObject) -> ProfileList | None:
        profiles = ProfileList()
        for profile_name, yaml_object_profile in yaml_object.value.items():
            profile = Profile(profile_name)
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
                        profile.enable_features.feature_names = yaml_object.value
                    case "cxx-compiler-flags":
                        # Check that 'cxx-compiler-flags' is a list of string
                        if not isinstance(yaml_object.value, list) or not all(isinstance(x, str) for x in yaml_object.value):
                            console.print_error(f"❌ Line {yaml_object.key_line} : 'cxx-compiler-flags' must contains list of feature name in'{self.file}'")
                            return None
                        profile.cxx_compiler_flags = yaml_object.value
                    case "cxx-linker-flags":
                        # Check that 'cxx-linker-flags' is a list of string
                        if not isinstance(yaml_object.value, list) or not all(isinstance(x, str) for x in yaml_object.value):
                            console.print_error(f"❌ Line {yaml_object.key_line} : 'cxx-linker-flags' must contains list of feature name in'{self.file}'")
                            return None
                        profile.cxx_linker_flags = yaml_object.value
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
        return profiles
    
    def _read_target_features(self, yaml_object: YamlObject) -> FeatureList | None:
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
                        feature.enable_features.feature_names = yaml_object.value
                    case "cxx-compiler-flags":
                        # Check that 'cxx-compiler-flags' is a list of string
                        if not isinstance(yaml_object.value, list) or not all(isinstance(x, str) for x in yaml_object.value):
                            console.print_error(f"❌ Line {yaml_object.key_line} : 'cxx-compiler-flags' must contains list of feature name in'{self.file}'")
                            return None
                        feature.cxx_compiler_flags = yaml_object.value
                    case "cxx-linker-flags":
                        # Check that 'cxx-linker-flags' is a list of string
                        if not isinstance(yaml_object.value, list) or not all(isinstance(x, str) for x in yaml_object.value):
                            console.print_error(f"❌ Line {yaml_object.key_line} : 'cxx-linker-flags' must contains list of feature name in'{self.file}'")
                            return None
                        feature.cxx_linker_flags = yaml_object.value
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
    
    def _read_target_feature_rules(self, yaml_object: YamlObject) -> FeatureRuleList | None:
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

    def _read_target_node(self, target_name: str, yaml_target : YamlObject) -> Target | None:
        # Read the target name
        parts = target_name.split('-')
        if len(parts) != 5:
            console.print_error(f"❌ Line {yaml_target.key_line} : Invalid target name '{target_name}' in '{self.file}'")
            console.print_error(f"  💡 Expected 'arch-vendor-os-env-compiler' separated by '-'")
            return None
        arch = parts[0]
        vendor = parts[1]
        os = parts[2]
        env = parts[3]
        compiler_name = parts[4]
        target : Target = Target(target_name,arch,vendor, os, env, compiler_name)

        # If the target is empty, ignore it
        if not yaml_target.value:
            console.print_warning(f"⚠️  Line {yaml_target.key_line} : target '{target_name}' is empty in '{self.file}'")
            return None

        # Read target elements
        for item, yaml_object in yaml_target.value.items():
            match item:
                case "is_abstract":
                    if not isinstance(yaml_object.value, bool):
                        console.print_error(f"❌ Line {yaml_object.key_line} : 'is_abstract' must be a boolean value (true|false) in '{self.file}'")
                        return None
                    target.is_abstract = yaml_object.value
                case "extends":
                    # Check that 'extends' is a string
                    if not isinstance(yaml_object.value, str):
                        console.print_error(f"❌ Line {yaml_object.key_line} : 'extends' in must be a target name in'{self.file}'")
                        return None
                    target.extends = yaml_object.value
                case "profiles":
                    if not isinstance(yaml_object.value, dict):
                        console.print_error(f"❌ Line {yaml_object.key_line} : 'profiles' must contains profiles'{self.file}'")
                        return None
                    profiles = self._read_profiles(yaml_object)
                    if profiles is None:
                        return None
                    target.profiles = profiles
                case "features":
                    if not isinstance(yaml_object.value, list):
                        console.print_error(f"❌ Line {yaml_object.key_line} : 'features' must contains list of features in'{self.file}'")
                        return None
                    features = self._read_target_features(yaml_object)
                    if features is None:
                        return None
                    target.features = features
                case "feature-rules":
                    if not isinstance(yaml_object.value, list):
                        console.print_error(f"❌ Line {yaml_object.key_line} : 'feature-rules' must contains list of feature rules in'{self.file}'")
                        return None
                    feature_rules = self._read_target_feature_rules(yaml_object)
                    if feature_rules is None:
                        return None
                    target.feature_rules = feature_rules
                case _:
                    console.print_error(f"❌ Line {yaml_object.key_line} : Unknown key '{item}' in'{self.file}'")
                    continue

        return target 

    # Load all targets in the file
    def load_yaml(self) -> bool :
        try:
            # Load the file
            with self.file.open() as f:
                self._yaml = yaml.load(f, Loader=LineLoader)
                for target_name, target_yaml_object in self._yaml.items():

                    # Validate the target name in form 'arch-vendor-os-env-compiler'
                    parts = target_name.split('-')
                    if not len(parts) == 5:
                        console.print_error(f"❌ Line {target_yaml_object.key_line} : Invalid target name '{target_name}' in '{self.file}'")
                        console.print_error(f"  💡 Expected 'arch-vendor-os-env-compiler' separated by '-'")
                        continue
                    
                    # Ignore if we already have a target name
                    existing_target: Target = self.targets.get(target_name)
                    if existing_target:
                        console.print_error(f"❌ Line {target_yaml_object.key_line} : Target '{existing_target}' already exist in '{existing_target.file}' when loading '{self.file}'")
                        continue
                    
                    # Load the target
                    target = self._read_target_node(target_name, target_yaml_object)
                    if target is None:
                        console.print_error(f"⚠️ Line {target_yaml_object.key_line} : Target '{target_name}' in '{self.file}' will not be available")
                        continue

                    # Add it to the available target list
                    self.targets.add(target)

            # Resolve includes
             #self.resolve_includes_target(targets)
            return True
        
        except (OSError, yaml.YAMLError) as e:
            console.print_error(f"Error: When loading '{self.file}' file: {e}")
            return False


###################################################################################
# Target registry contains all resolved target available including abstract target
###################################################################################
class TargetRegistry:
    def __init__(self):
        self.targets= TargetList()
    
    def __contains__(self, name: str) -> bool:
        return name in self.targets

    def __iter__(self):
        return iter(self.targets.items())
    
    def items(self):
        return self.targets.items()
    
    # def register_target(self, target: Target):
    #     existing_target = self.targets.get(target.name)
    #     if existing_target:
    #         console.print_error(f"⚠️  Warning: Target already registered: {existing_target.name} in {str(existing_target.file)}")
    #         exit(1)
    #     self._targets[target.name] = target
    
    def load_and_register_all_target_in_directory(self, directory: Path):
          for file in directory.glob("*.yaml"):
            yaml_target_file = YamlTargetFile(file)
            yaml_target_file.load_yaml()
            for target in yaml_target_file.targets:
                console.print_tips(
f"""--> {target.name} ({'abstract' if target.is_abstract else 'usable' })
 """)
                pass

TargetRegistry = TargetRegistry()