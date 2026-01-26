
from pathlib import Path
from typing import Optional, Self
import yaml
import console
from project import ProjectType

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

TargetName = str
FeatureName = str
ConfigName = str
CompilerFlag = str
LinkerFlag = str
FeatureRuleName = str

class TargetFeatureRuleNode:
    def __init__(self, name: str):
        self._name = name
    
    @property
    def name(self) -> FeatureName:
        return self._name
         
# Only 1 rules is allowed in 'features'
class FeatureOnlyOneRuleNode(TargetFeatureRuleNode):
    KEY = "only-one"
    def __init__(self, name: str, features : list[FeatureName]):
        super().__init__(name=name)
        self.features=features

    def is_satisfied(self, enabled_features) -> list[FeatureName]:
        all_enabled = set[FeatureName]()
        enabled_feature_node : Optional[TargetFeatureNode] = None
        for feature_name in self.features.value:
            for feature_node in enabled_features:
                if feature_node.name.value == feature_name:
                    if enabled_feature_node:
                        all_enabled.add(enabled_feature_node.name.value)
                        all_enabled.add(feature_name)
                    enabled_feature_node = feature_node
        return list(all_enabled)
    
    @staticmethod
    def from_yaml(target_name: str, yaml : dict) -> Optional[Self]:
        name = yaml.get(FeatureOnlyOneRuleNode.KEY)
        if not name:
            return None
        features = yaml.get("features")
        if not features:
            console.print_error(f"❌ Line {name.line} : 'features' list is required in feature-rule '{name}' in '{target_name}' target")
            return None
        return FeatureOnlyOneRuleNode(name, features)


# The 'feature' is incompatible with all feature in 'with'
class FeatureIncompatibleRuleNode(TargetFeatureRuleNode):
    KEY = "incompatible"
    def __init__(self, name: str, feature_name: FeatureName, incompatible_with:list[FeatureName]):
        super().__init__(name=name)
        self.feature_name=feature_name
        self.incompatible_with=incompatible_with
    
    def is_satisfied(self, enabled_features) -> list[FeatureName]:
        list_of_incompatible_feature_in_enabled_features = list[FeatureName]()
        # Check if the feature that is incompatible is present
        is_feature_in_list = False
        for feature in enabled_features:
            if feature.name.value == self.feature_name.value:
                is_feature_in_list = True
                break

        # If the incompatible feature is present
        if is_feature_in_list:
            for incompatible_feature_name in self.incompatible_with.value:
                for feature in enabled_features:
                    if incompatible_feature_name == feature.name.value:
                        list_of_incompatible_feature_in_enabled_features.append(incompatible_feature_name)
       
        return list_of_incompatible_feature_in_enabled_features

    @staticmethod
    def from_yaml(target_name: str, yaml : dict) -> Optional[Self]:
        name = yaml.get(FeatureIncompatibleRuleNode.KEY)
        if not name:
            return None

        feature = yaml.get("feature")
        if not feature:
            console.print_error(f"❌ Line {name.line} : 'feature' is required in feature-rule '{name}' in '{target_name}' target")
            return None

        incompatible_with = yaml.get("with")
        if not incompatible_with:
            console.print_error(f"❌ Line {name.line} : 'with' is required in feature-rule '{name}' in '{target_name}' target")
            return None

        return FeatureIncompatibleRuleNode(name, feature, incompatible_with)
    

class TargetFeatureNode:
    def __init__(self, name: str):
        self._name = name
        self.description = str()
        self.cxx_compiler = TargetCXXCompilerNode()
        self.cxx_linker = TargetCXXLinkerNode()
        self.enable_feature_names = list[FeatureName]()

    def __hash__(self) -> int:
        return hash(self._name)

    def __eq__(self, other) -> bool:
        if not isinstance(other, TargetFeatureNode):
            return NotImplemented
        return self._name == other._name

    @property
    def name(self) -> FeatureName:
        return self._name

    @staticmethod
    def from_yaml(target_name: str, yaml : dict) -> Optional[Self]:
        name = yaml.get("name")
        if not name:
            console.print_error(f"❌ Line {next(iter(yaml.values())).line} :: Feature 'name' in 'features' is missing in '{target_name}' target. Feature is '{next(iter(yaml))}'")
            return None
        feature_node = TargetFeatureNode(name)
        description = yaml.get("description") or str()
        feature_node.description = description
        cxx_compiler = yaml.get("cxx-compiler")
        if cxx_compiler:
            cxx_compiler = TargetCXXCompilerNode.from_yaml(node_name=target_name, yaml=cxx_compiler)
            if not cxx_compiler:
                console.print_error(f"Failed to load feature '{name}' in {target_name}")
                return None
            feature_node.cxx_compiler = cxx_compiler
                
        cxx_linker = yaml.get("cxx-linker")
        if cxx_linker:
            cxx_linker = TargetCXXLinkerNode.from_yaml(node_name=target_name, yaml=cxx_linker)
            if not cxx_linker:
                console.print_error(f"Failed to load feature '{name}' in {target_name}")
                return None
            feature_node.cxx_linker = cxx_linker

        enable_feature_names = yaml.get("enable-feature")
        if enable_feature_names:
            feature_node.enable_feature_names.extend(enable_feature_names.value)
        return feature_node



class TargetCXXCompilerNode:
    def __init__(self):
        self._default_features : dict[ConfigName, list[FeatureName]] = dict[ConfigName, list[FeatureName]]()
        self._flags : dict[ConfigName, list[CompilerFlag]] = dict[ConfigName, list[CompilerFlag]]()
        
    @property
    def default_features(self) -> dict[ConfigName, list[FeatureName]]:
        return self._default_features
    
    @property
    def flags(self) -> dict[ConfigName, list[CompilerFlag]]:
        return self._flags
    
    @staticmethod
    def from_yaml(node_name: str, yaml : dict) -> Optional[Self]:
        cxx_compiler_node = TargetCXXCompilerNode()
        for item, yaml_object in yaml.value.items():
            match item:
                case  "default-features":
                    for config_name, yaml_object in yaml_object.value.items():
                            cxx_compiler_node.default_features.setdefault(config_name, []).extend(yaml_object.value)
                case _:
                    parts = item.split('-')
                    if len(parts) != 2:
                        console.print_error(f"❌ Line {yaml_object.line} : Invalid '{item}' in '{node_name}' target")
                        return None
                    config_name = parts[0]
                    if parts[1] == "flags":
                        cxx_compiler_node.flags.setdefault(config_name,[]).extend(yaml_object.value)
                    else:
                        console.print_error(f"❌ Line {yaml_object.line} : Invalid '{parts[1]}' in '{item}' item in '{node_name}' target")
        return cxx_compiler_node

class TargetCXXLinkerNode:
    def __init__(self):
        self._default_features : dict[ConfigName, list[FeatureName]] = dict[ConfigName, list[FeatureName]]()
        self._flags : dict[ConfigName, list[LinkerFlag]] = dict[ConfigName, list[LinkerFlag]]()
        
    @property
    def default_features(self) -> dict[ConfigName, list[FeatureName]]:
        return self._default_features
    
    @property
    def flags(self) -> dict[ConfigName, list[LinkerFlag]]:
        return self._flags

    @staticmethod
    def from_yaml(node_name: str, yaml : dict) -> Optional[Self]:
        cxx_linker_node = TargetCXXLinkerNode()
        for item, yaml_object in yaml.value.items():
            match item:
                case  "default-features":
                    for config_name, yaml_object in yaml_object.value.items():
                            cxx_linker_node.default_features.setdefault(config_name, []).extend(yaml_object.value)
                case _:
                    parts = item.split('-')
                    if len(parts) != 2:
                        console.print_error(f"❌ Line {yaml_object.line} : Invalid '{item}' in '{node_name}' target")
                        return None
                    config_name = parts[0]
                    if parts[1] == "flags":
                        cxx_linker_node.flags.setdefault(config_name,[]).extend(yaml_object.value)
                    else:
                        console.print_error(f"❌ Line {yaml_object.line} : Invalid '{parts[1]}' in '{item}' item in '{node_name}' target")
        return cxx_linker_node       
    
class TargetProjectTypeNode:
    def __init__(self, name:str):
        self._name = name
        self.cxx_compiler: Optional[TargetCXXCompilerNode] = None
        self.cxx_linker: Optional[TargetCXXLinkerNode] = None
    
    @property
    def name(self):
        return self._name

    @staticmethod
    def from_yaml(node_name: TargetName, yaml : dict) -> Optional[Self]:
        project_type_node = TargetProjectTypeNode(node_name)
        for item, yaml_object in yaml.value.items():
            match item:
                case "cxx-compiler":
                    if project_type_node.cxx_compiler:
                        console.print_error(f"❌ Line {yaml_object.line} : Multiple cxx-compiler in '{node_name}' is not supported")
                    project_type_node.cxx_compiler= TargetCXXCompilerNode.from_yaml(node_name==node_name, yaml=yaml_object)
                case "cxx-linker":
                    if project_type_node.cxx_linker:
                        console.print_error(f"❌ Line {yaml_object.line} : Multiple cxx-linker in '{node_name}' is not supported")
                    project_type_node.cxx_linker = TargetCXXLinkerNode.from_yaml(node_name=node_name, yaml=yaml_object)
        return project_type_node  
    
class TargetNode:
    def __init__(self, name: TargetName, arch: str, os :str, env:str, vendor:str, compiler_name:str):
        self._name = name
        self._arch = arch
        self._os = os
        self._env = env
        self._vendor = vendor
        self._compiler_name = compiler_name
        self.abstract = False
        self.cxx_compiler : Optional[TargetCXXCompilerNode] = None
        self.cxx_linker : Optional[TargetCXXLinkerNode] = None
        self.project_type : Optional[TargetProjectTypeNode] = None
        self.features = dict[FeatureName, TargetFeatureNode]()
        self.feature_rules = dict[FeatureRuleName, TargetFeatureRuleNode]()
        self.include = TargetName()
    
    def __hash__(self) -> int:
        return hash(self._name)

    def __eq__(self, other) -> bool:
        if not isinstance(other, TargetName):
            return NotImplemented
        return self._name == other._name
    
    @property
    def name(self) -> str:
        return self._name

    def _read_cxx_compiler_node(self, yaml_cxx_compiler : YamlObject):
        if self.cxx_compiler:
            console.print_error(f"❌ Line {yaml_cxx_compiler.line} : Multiple cxx-compiler in '{self.name}' is not supported")
        self.cxx_compiler = TargetCXXCompilerNode.from_yaml(node_name=self.name, yaml=yaml_cxx_compiler)
    
    def _read_cxx_linker_node(self, yaml_cxx_linker : YamlObject):
        if self.cxx_linker:
            console.print_error(f"❌ Line {yaml_cxx_linker.line} :Multiple cxx-linker in '{self.name}' is not supported")
        self.cxx_linker = TargetCXXLinkerNode.from_yaml(node_name=self.name, yaml=yaml_cxx_linker)
   
    def _read_project_type_node(self, target_name:TargetName, yaml_project_type :YamlObject):
        if self.project_type:
            console.print_error(f"❌ Line {yaml_project_type.line} :Multiple 'project-type' in '{self.name}' is not supported")
        self.project_type = TargetProjectTypeNode.from_yaml(node_name=target_name, yaml=yaml_project_type)
    
    def _read_features_node(self, yaml_features_node :YamlObject):
        if self.features:
            console.print_error(f"❌ Line {yaml_features_node.line} :Multiple 'features' in '{self.name}' is not supported")
        self.features = dict[FeatureName, TargetFeatureNode]()
        for item in yaml_features_node.value:
            feature_node:Optional[TargetFeatureNode] = TargetFeatureNode.from_yaml(target_name=self.name, yaml=item)
            if feature_node in self.features:
                console.print_error(f"❌ Line {yaml_features_node.line} : Feature with name '{feature_node.name}' already in '{self.name}'")
                continue
            if feature_node:
                self.features[feature_node.name.value] = feature_node
    
    def _read_feature_rules_node(self, yaml_feature_rules_node :YamlObject):
        if self.feature_rules:
            console.print_error(f"Multiple 'feature-rules' in '{self.name}' is not supported")
        self.feature_rules = dict[FeatureRuleName, TargetFeatureRuleNode]()
        for item in yaml_feature_rules_node.value:
            only_one_rule_node = FeatureOnlyOneRuleNode.from_yaml(target_name=self.name, yaml=item)
            if only_one_rule_node:
                self.feature_rules[only_one_rule_node.name.value] = only_one_rule_node
                continue
            incompatible_rule_node =  FeatureIncompatibleRuleNode.from_yaml(target_name=self.name, yaml=item)
            if incompatible_rule_node:
                self.feature_rules[incompatible_rule_node.name.value] = incompatible_rule_node
                continue
            console.print_error(f"❌ Line {next(iter(item.values())).line} : Unknown 'feature-rules' '{next(iter(item))}' in '{self.name}' target")

    
class YamlTargetFile:
    def __init__(self, file: Path):
        self._file = file
    
    def _read_target_node(self, target_name: TargetName, yaml_target : dict) -> TargetNode:
        # Read the target name
        parts = target_name.split('-')
        if len(parts) != 5:
            console.print_error(f"❌ Line {yaml_target.key_line} : Invalid target name '{target_name}' in '{self._file}'")
            console.print_error(f"  💡 Expected 'arch-vendor-os-env-compiler' separated by '-'")
            return None
        arch = parts[0]
        vendor = parts[1]
        os = parts[2]
        env = parts[3]
        compiler_name = parts[4]
        target_node : TargetNode = TargetNode(name=target_name, arch=arch, os=os, env=env, vendor=vendor, compiler_name=compiler_name)

        if not yaml_target.value:
            console.print_warning(f"⚠️  Line {yaml_target.line} : target '{target_name}' in '{self._file}' is empty")
        else:
            for item, yaml_object in yaml_target.value.items():
                match item:
                    case "abstract":
                        target_node.abstract = yaml_object.value
                    case "cxx-compiler":
                        target_node._read_cxx_compiler_node(yaml_cxx_compiler=yaml_object)
                    case "cxx-linker":
                        target_node._read_cxx_linker_node(yaml_cxx_linker=yaml_object)
                    case "features":
                        target_node._read_features_node(yaml_features_node=yaml_object)
                    case "feature-rules":
                        target_node._read_feature_rules_node(yaml_feature_rules_node=yaml_object)
                    case "include":
                        target_node.include = yaml_object.value
                    case _:
                        if item == ProjectType.bin or item == ProjectType.dyn or item == ProjectType.lib:
                            target_node._read_project_type_node(target_name=item, yaml_project_type=yaml_object)

        return target_node

    @staticmethod    
    def _find_feature_from_name(feature_name : str, target_list: list[TargetNode]):
        for target in target_list:
            pass

    def load_yaml(self) -> set[TargetNode] :
        try:
            target_dict = dict[TargetName, TargetNode]()

            # Load the file
            with self._file.open() as f:
                self._yaml = yaml.load(f,Loader=LineLoader)
                for item, target_yaml_object in self._yaml.items():
                    target = self._read_target_node(item, target_yaml_object)
                    if not target:
                        console.print_error(f"⚠️  Target '{item}' in '{self._file}' will not be available")
                        continue
                    target_dict[target.name] = target

            # Flatten non abstract targets and detect cyclic dependency
            flatten_includes_targets = list[TargetNode]()
            for root_target in target_dict.values():
                if not root_target.abstract:    
                    # return a flatten list of targets inclusion order list where if A include B B is before A in the list
                    flatten_includes_targets = YamlTargetFile._flatten_includes_targets(root_target, target_dict)
                    console.print_tips(f"{root_target.name} : {' -> '.join([p.name for p in flatten_includes_targets])}")

                    # This list contains all feature that are declared
                    # This is used to merge all feature declared in included target
                    # Also, it is use to detect that enable-feature only enable feature that are already declared
                    # thank to the _flatten_includes_targets that return a inclusion order list where 
                    # if A include B B is before A in the list
                    all_feature_list = dict[FeatureName, TargetFeatureNode]()
                    all_config_features = dict[ConfigName, dict[FeatureName, TargetFeatureNode]]()

                    for target in flatten_includes_targets:
                        # Add features that are enabled by the feature
                        all_feature_list.update(target.features)

                        # Check all features that are enable by 'enable-feature' exist in current or included target
                        for feature in target.features.values():
                            for enabled_feature_name in feature.enable_feature_names:
                               if not enabled_feature_name in all_feature_list:
                                    console.print_warning(f"Feature '{feature.name}' in target '{target.name}' enable a feature named {enabled_feature_name} that is not in the target or in the included target")
                        
                        # Resolve defaut features
                        # For each configuration we add default feature that are enabled
                        if target.cxx_compiler:
                            def add_feature(target_feature_name : FeatureName) -> list[FeatureName]:
                                # Check that feature exists
                                default_feature = all_feature_list.get(target_feature_name)
                                if not default_feature:
                                    console.print_error(f"cxx-compiler default-features '{target_feature_name}' in target '{target.name}' is not found")
                                    exit(1)

                                # Add the feature for this config
                                config_feature = all_config_features.setdefault(config_name, dict[FeatureName, TargetFeatureNode]())
                                config_feature[default_feature.name] = default_feature

                                # Return features that must be enable by this one
                                return default_feature.enable_feature_names

                            for config_name, default_feature_names in target.cxx_compiler.default_features.items():
                                to_enable_list = list[FeatureName]()
                                to_enable_list.extend(default_feature_names)
                                while to_enable_list:
                                    to_enable_list.extend(add_feature(to_enable_list.pop()))

                        # Merge 'all' config features in other configurations
                        all_features = all_config_features.pop("all", {})
                        for features in all_config_features.values():
                            features.update(all_features)

                        # Check feature rules
                        for feature_rule in target.feature_rules.values():
                            match feature_rule:
                                case FeatureOnlyOneRuleNode() as only_one_rule:
                                    for config, config_features in all_config_features.items():
                                        list_invalid = only_one_rule.is_satisfied(config_features.values())
                                        if list_invalid:
                                            console.print_error(f"❌ Feature rule '{FeatureOnlyOneRuleNode.KEY}' not satisfied in target '{target.name}'")
                                            console.print_error(f"In '{config}' configuration features {", ".join(list_invalid)} are both enabled")
                                            exit(1)
                                case FeatureIncompatibleRuleNode() as incompatible_rule:
                                    for config, config_features in all_config_features.items():
                                        list_of_incompatible_feature =  incompatible_rule.is_satisfied(config_features.values())
                                        if list_of_incompatible_feature:
                                            console.print_error(f"❌ Feature rule '{FeatureIncompatibleRuleNode.KEY}' not satisfied in target '{target.name}'")
                                            console.print_error(f"In '{config}' configuration features {", ".join(list_of_incompatible_feature)} are incompatible with {incompatible_rule.feature_name.value}")
                                            exit(1)
                        
            
            return target_dict
        except (OSError, yaml.YAMLError) as e:
            console.print_error(f"Error: When loading '{self._file}' file: {e}")
            return list()


    @staticmethod
    def _flatten_includes_targets(target_node : TargetNode, target_dict : dict[TargetName, TargetNode]) -> list[TargetNode]:
        # 1. Collecte du sous-graphe (DFS)
        all_targets: list[TargetNode] = list()
        visiting_stack: list[TargetNode] = []
        def format_stack(names: list[str]) -> str:
            lines = []
            for i, name in enumerate(names):
                indent = " " * (4 * max(i-1, 0))
                if i == 0:
                    lines.append(name)
                elif i == len(names) - 1:
                    lines.append(f"{indent}└ ⟲ loop {name}")
                else:
                    lines.append(f"{indent}└ includes {name}")
            return "\n".join(lines)
        def collect(current_node : TargetNode, parent_node: TargetNode):
            # Detect cyclic dependency
            if current_node in visiting_stack:
                parent_name = parent_node.name if parent_node else "<root>"
                console.print_error(f"❌ Error: Cyclic dependency between '{current_node.name}' and '{parent_name}'")
                console.print_error(format_stack([p.name for p in visiting_stack] + [current_node.name]))
                exit(1)

            # Visit the project only once
            if current_node in all_targets:
                return
            visiting_stack.append(current_node)
 
            # Visit include
            if current_node.include:
                include_node = target_dict.get(current_node.include)
                if not include_node:
                    console.print_error(f"❌ '{current_node.name}' target include unknown target '{current_node.include}'")
                    exit(1)
                collect(include_node, current_node)
            
            # Remove visited project
            visiting_stack.pop()
            all_targets.append(current_node)
        collect(target_node, None)
        return all_targets
    



class TargetRegistry:
    def __init__(self):
        self._targets: dict[str, TargetNode] = {}
    
    def __contains__(self, name: str) -> bool:
        return name in self._targets

    def __iter__(self):
        return iter(self._targets.items())
    
    def items(self):
        return self._targets.items()
    
    def register_target(self, target: TargetNode):
        existing_target = self._targets.get(target.name)
        if existing_target:
            console.print_error(f"⚠️  Warning: Project already registered: {existing_target.name} in {str(existing_target.file)}")
            exit(1)
        self._targets[target.name] = target
    
    def load_and_register_all_target_in_directory(self, directory: Path):
          for file in directory.glob("*.yaml"):
            yaml_target_file = YamlTargetFile(file)
            yaml_target_file.load_yaml()

TargetRegistry = TargetRegistry()