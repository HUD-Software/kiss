
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
    def __init__(self, name: str, features : set[FeatureName]):
        super().__init__(name=name)
        self.features=features

    def is_satisfied(self, enabled_features: set[FeatureName]) -> set[FeatureName]:
        common = self.features.intersection(enabled_features)
        if len(common) > 1:
            return common
        return set()
    
    @staticmethod
    def from_yaml(target_name: str, yaml : dict) -> Optional[Self]:
        name = yaml.get(FeatureOnlyOneRuleNode.KEY)
        if not name:
            return None
        features = yaml.get("features")
        if not features:
            console.print_error(f"❌ Line {name.line} : 'features' list is required in feature-rule '{name}' in '{target_name}' target")
            return None
        return FeatureOnlyOneRuleNode(name, set(features.value))


# The 'feature' is incompatible with all feature in 'with'
class FeatureIncompatibleRuleNode(TargetFeatureRuleNode):
    KEY = "incompatible"
    def __init__(self, name: str, feature_name: FeatureName, incompatible_with:set[FeatureName]):
        super().__init__(name=name)
        self.feature_name=feature_name
        self.incompatible_with=incompatible_with
    
    def is_satisfied(self, enabled_features: set[FeatureName]) -> set[FeatureName]:
        if self.feature_name.value in enabled_features:
            incompatible_features = self.incompatible_with.intersection(enabled_features)
            if incompatible_features:
                return incompatible_features
        return set()

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

        return FeatureIncompatibleRuleNode(name, feature, set(incompatible_with.value))
    

class TargetFeatureNode:
    def __init__(self, name: str):
        self._name = name
        self.description : str = ""
        self.cxx_compiler = TargetCXXCompilerNode()
        self.cxx_linker = TargetCXXLinkerNode()
        self.enable_feature : set[FeatureName] = set()

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
            console.print_error(f"❌ Line {next(iter(yaml.values())).line} : Feature 'name' in 'features' is missing in '{target_name}' target. Feature is '{next(iter(yaml))}'")
            return None
        feature_node = TargetFeatureNode(name)
        description = yaml.get("description") or str()
        feature_node.description = description
        cxx_compiler = yaml.get("cxx-compiler")
        if cxx_compiler:
            cxx_compiler = TargetCXXCompilerNode.from_yaml(target_name=target_name, yaml=cxx_compiler)
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

        enable_feature = yaml.get("enable-feature")
        if enable_feature:
            feature_node.enable_feature.update(enable_feature.value)
        return feature_node



class TargetCXXCompilerNode:
    def __init__(self):
        self._flags : dict[ConfigName, list[CompilerFlag]] = {}
    
    @property
    def flags(self) -> dict[ConfigName, list[CompilerFlag]]:
        return self._flags
    
    def merge_with(self, other : Self):
        for conf, list in other.flags.items():
            self.flags.setdefault(conf, []).extend(list)

    def get_flags_for_config(self, config: ConfigName) -> list[str]:
        l : list[CompilerFlag] = self.flags.get("all", []).copy()
        l.extend(self.flags.get(config, []))
        return l
    
    @staticmethod
    def from_yaml(target_name: str, yaml : dict) -> Optional[Self]:
        cxx_compiler_node = TargetCXXCompilerNode()
        for item, yaml_object in yaml.value.items():
            parts = item.split('-')
            if len(parts) != 2:
                console.print_error(f"❌ Line {yaml_object.line} : Invalid '{item}' in '{target_name}' target")
                return None
            config_name = parts[0]
            if parts[1] == "flags":
                if not isinstance(yaml_object.value, list) or not all(isinstance(x, str) for x in yaml_object.value):
                    console.print_error(f"❌ Line {yaml_object.line}: In target '{target_name}', 'flags' must be a list of strings, but got: {yaml_object.value}")
                    exit(1)
                cxx_compiler_node.flags.setdefault(config_name,[]).extend(yaml_object.value)
            else:
                console.print_error(f"❌ Line {yaml_object.line} : In target '{target_name}', invalid '{parts[1]}' in '{item}' item")
                return None
        return cxx_compiler_node


class TargetCXXLinkerNode:
    def __init__(self):
        self._flags : dict[ConfigName, list[LinkerFlag]] = {}
        
    @property
    def flags(self) -> dict[ConfigName, list[LinkerFlag]]:
        return self._flags

    def merge_with(self, other : Self):
        for conf, list in other.flags.items():
            self.flags.setdefault(conf, []).extend(list)
    
    def get_flags_for_config(self, config: ConfigName) -> list[str]:
        l : list[CompilerFlag] = self.flags.get("all", []).copy()
        l.extend(self.flags.get(config, []))
        return l
    
    @staticmethod
    def from_yaml(node_name: str, yaml : dict) -> Optional[Self]:
        cxx_linker_node = TargetCXXLinkerNode()
        for item, yaml_object in yaml.value.items():
            parts = item.split('-')
            if len(parts) != 2:
                console.print_error(f"❌ Line {yaml_object.line} : Invalid '{item}' in '{node_name}' target")
                return None
            config_name = parts[0]
            if parts[1] == "flags":
                cxx_linker_node.flags.setdefault(config_name,[]).extend(yaml_object.value)
            else:
                console.print_error(f"❌ Line {yaml_object.line} : Invalid '{parts[1]}' in '{item}' item in '{node_name}' target")
                return None
        return cxx_linker_node       
    
class TargetProjectTypeNode:
    def __init__(self):
        self.cxx_compiler= TargetCXXCompilerNode()
        self.cxx_linker= TargetCXXLinkerNode()
    
    def merge_with(self, other : Self):
        self.cxx_compiler.merge_with(other.cxx_compiler)
        self.cxx_linker.merge_with(other.cxx_linker)

    @staticmethod
    def from_yaml(node_name: TargetName, yaml : dict) -> Optional[Self]:
        project_type_node = TargetProjectTypeNode()
        cxx_compiler : Optional[TargetCXXCompilerNode] = None
        cxx_linker : Optional[TargetCXXLinkerNode] = None
        for item, yaml_object in yaml.value.items():
            match item:
                case "cxx-compiler":
                    if cxx_compiler:
                        console.print_error(f"❌ Line {yaml_object.line} : Multiple cxx-compiler in '{node_name}' is not supported")
                        return None
                    cxx_compiler = TargetCXXCompilerNode.from_yaml(node_name==node_name, yaml=yaml_object)
                case "cxx-linker":
                    if cxx_linker:
                        console.print_error(f"❌ Line {yaml_object.line} : Multiple cxx-linker in '{node_name}' is not supported")
                        return None
                    cxx_linker = TargetCXXLinkerNode.from_yaml(node_name=node_name, yaml=yaml_object)

        if cxx_compiler:
            project_type_node.cxx_compiler = cxx_compiler
        else:
            project_type_node.cxx_compiler = TargetCXXCompilerNode()
            
        if cxx_linker:
            project_type_node.cxx_linker = cxx_linker
        else:
            project_type_node.cxx_linker =  TargetCXXLinkerNode()
        
        return project_type_node  

class Target:
    def __init__(self, name: TargetName, arch: str, os :str, env:str, vendor:str, compiler_name:str):
        self._name = name
        self._arch = arch
        self._os = os
        self._env = env
        self._vendor = vendor
        self._compiler_name = compiler_name
        self.is_abstract = False
        self.default_features : dict[ConfigName, set[FeatureName]] = {}
        self.cxx_compiler = TargetCXXCompilerNode ()
        self.cxx_linker = TargetCXXLinkerNode()
        self.project_type : dict[ProjectType, TargetProjectTypeNode] = {}
        self.features : dict[FeatureName, TargetFeatureNode] = {}
        self.feature_rules : dict[FeatureRuleName, TargetFeatureRuleNode] = {}
        self.include : TargetName = ""
    
    def __hash__(self) -> int:
        return hash(self._name)

    def __eq__(self, other) -> bool:
        if not isinstance(other, TargetName):
            return NotImplemented
        return self._name == other
    
    @property
    def name(self) -> str:
        return self._name

    def merge_with(self, other: Self):
        self.cxx_compiler.merge_with(other.cxx_compiler)
        self.cxx_linker.merge_with(other.cxx_linker)
        for conf, s in other.default_features.items():
            self.default_features.setdefault(conf, set()).update(s)
        self.features.update(other.features)
        self.feature_rules.update(other.feature_rules)
        for project_type, project_type_node in other.project_type.items():
            self.project_type.setdefault(project_type, TargetProjectTypeNode()).merge_with(project_type_node)

    def get_cxx_compiler_flags(self, config: ConfigName, project_type: ProjectType, feature_name_list: set[FeatureName]) -> list[str]:
        # Retrieves all flags from features, cxx-compiler and per type project flags
        cxx_flags : list[CompilerFlag] = []
        cxx_flags.extend(self.cxx_compiler.get_flags_for_config(config))
        cxx_flags.extend(self.get_project_flags(config, project_type))
        for feature_name in feature_name_list:
            cxx_flags.extend(self.get_feature_flags(config,feature_name))
        return cxx_flags

    def get_feature_flags(self, config: ConfigName, feature: FeatureName) -> list[str]:
        cxx_flags : list[CompilerFlag] = []
        feature_node : TargetFeatureNode = self.features.get(feature)
        if feature_node:
            cxx_flags.extend(feature_node.cxx_compiler.get_flags_for_config(config))
        return cxx_flags

    def get_project_flags(self, config: ConfigName, project_type: ProjectType) -> list[str]:
        cxx_flags : list[CompilerFlag] = []
        project_type_node = self.project_type.get(project_type)
        if project_type_node:
            cxx_flags.extend(project_type_node.cxx_compiler.get_flags_for_config(config))
        return cxx_flags
    
    def get_default_feature_for_config(self, config: ConfigName):
        l : set[FeatureName] = self.default_features.get("all", set()).copy()
        l.update(self.default_features.get(config, set()))
        return l

    def validate_features(self, config: ConfigName, feature_list: set[FeatureName]) -> bool:
        all_valid = True
        for feature_rule in self.feature_rules.values():
            match feature_rule:
                case FeatureOnlyOneRuleNode() as only_one_rule:
                    list_invalid = only_one_rule.is_satisfied(feature_list)
                    if list_invalid:
                        console.print_error(f"❌ Feature rule '{FeatureOnlyOneRuleNode.KEY}' not satisfied in target '{self.name}'")
                        console.print_error(f"In '{config}' configuration features {', '.join(list_invalid)} are both enabled")
                        all_valid = False
                case FeatureIncompatibleRuleNode() as incompatible_rule:
                    list_of_incompatible_feature =  incompatible_rule.is_satisfied(feature_list)
                    if list_of_incompatible_feature:
                        console.print_error(f"❌ Feature rule '{FeatureIncompatibleRuleNode.KEY}' not satisfied in target '{self.name}'")
                        console.print_error(f"In '{config}' configuration features {', '.join(list_of_incompatible_feature)} are incompatible with {incompatible_rule.feature_name.value}")
                        all_valid = False
        return all_valid
   
    def _read_feature_rules_node(self, yaml_feature_rules_node :YamlObject):
        if self.feature_rules:
            console.print_error(f"Multiple 'feature-rules' in '{self.name}' is not supported")
        self.feature_rules : dict[FeatureRuleName, TargetFeatureRuleNode] = {}
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
    
    def _read_target_node(self, target_name: TargetName, yaml_target : dict) -> Target:
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
        target_node : Target = Target(name=target_name, arch=arch, os=os, env=env, vendor=vendor, compiler_name=compiler_name)

        if not yaml_target.value:
            console.print_warning(f"⚠️  Line {yaml_target.line} : target '{target_name}' in '{self._file}' is empty")
        else:
            cxx_compiler : Optional[TargetCXXCompilerNode] = None
            cxx_linker : Optional[TargetCXXLinkerNode] = None
            features : Optional[dict[FeatureName, TargetFeatureNode]] = None
            default_features : Optional[dict[ConfigName, set[FeatureName]]] = None
            feature_rules : Optional[dict[FeatureRuleName, TargetFeatureRuleNode]] = None

            for item, yaml_object in yaml_target.value.items():
                match item:
                    case "is_abstract":
                        target_node.is_abstract = yaml_object.value
                    case "default-features":
                        if default_features:
                            console.print_error(f"❌ Line {yaml_object.line} : Multiple 'default-features' in '{target_name}' is not supported")
                            exit(1)
                        default_features : dict[ConfigName, set[FeatureName]] = {}
                        for config_name, yaml_object in yaml_object.value.items():
                            default_features.setdefault(config_name, set()).update(yaml_object.value)
                    case "cxx-compiler":
                        if cxx_compiler:
                            console.print_error(f"❌ Line {yaml_object.line} : Multiple 'cxx-compiler' in '{target_name}' is not supported")
                            exit(1)
                        cxx_compiler = TargetCXXCompilerNode.from_yaml(target_name=target_name, yaml=yaml_object)
                    case "cxx-linker":
                        if cxx_linker:
                            console.print_error(f"❌ Line {yaml_object.line} : Multiple 'cxx-linker' in '{target_name}' is not supported")
                            exit(1)
                        cxx_linker = TargetCXXLinkerNode.from_yaml(node_name=target_name, yaml=yaml_object)
                    case "features":
                        if features:
                            console.print_error(f"❌ Line {yaml_object.line} : Multiple 'features' in '{target_name}' is not supported")
                            exit(1)
                        features : dict[FeatureName, TargetFeatureNode] = {}
                        for item in yaml_object.value:
                            feature_node:Optional[TargetFeatureNode] = TargetFeatureNode.from_yaml(target_name=target_name, yaml=item)
                            if feature_node in features:
                                console.print_error(f"❌ Line {yaml_object.line} : Feature with name '{feature_node.name}' already in '{target_name}'")
                                exit(1)
                            if feature_node:
                                features[feature_node.name.value] = feature_node
                    case "feature-rules":
                        if feature_rules:
                            console.print_error(f"❌ Line {yaml_object.line} : Multiple 'feature_rules' in '{target_name}' is not supported")
                            exit(1)
                        feature_rules : dict[FeatureRuleName, TargetFeatureRuleNode] = {}
                        for item in yaml_object.value:
                            only_one_rule_node = FeatureOnlyOneRuleNode.from_yaml(target_name=target_name, yaml=item)
                            if only_one_rule_node:
                                feature_rules[only_one_rule_node.name.value] = only_one_rule_node
                                continue
                            incompatible_rule_node =  FeatureIncompatibleRuleNode.from_yaml(target_name=target_name, yaml=item)
                            if incompatible_rule_node:
                                feature_rules[incompatible_rule_node.name.value] = incompatible_rule_node
                                continue
                            console.print_error(f"❌ Line {next(iter(item.values())).line} : Unknown 'feature-rules' '{next(iter(item))}' in '{target_name}' target")
                    case "include":
                        target_node.include = yaml_object.value
                    case _:
                        if item == ProjectType.bin or item == ProjectType.dyn or item == ProjectType.lib:
                            if item in target_node.project_type:
                                console.print_error(f"❌ Line {yaml_object.line} :Multiple 'project-type' in '{target_name}' is not supported")
                                exit(1)
                            target_node.project_type[item] = TargetProjectTypeNode.from_yaml(node_name=target_name, yaml=yaml_object)

        # Add cxx_compiler if any
        if cxx_compiler: 
            target_node.cxx_compiler = cxx_compiler
        else:
            target_node.cxx_compiler = TargetCXXCompilerNode()
        
        # Add cxx_linker if any
        if cxx_linker:
            target_node.cxx_linker = cxx_linker
        else:
            target_node.cxx_linker = TargetCXXLinkerNode()

        # Add features if any
        if features:
            target_node.features = features
        else:
            default : dict[FeatureName, TargetFeatureNode] = {}
            target_node.features = default

        # Add default_features if any
        if default_features:
            target_node.default_features = default_features
        else:
            default : dict[ConfigName, set[FeatureName]] = {}
            target_node.default_features  = default

        # Add feature_rules if any
        if feature_rules:
            target_node.feature_rules = feature_rules
        else:
            default : dict[FeatureRuleName, TargetFeatureRuleNode] = {}
            target_node.feature_rules = default
        return target_node

    def resolve_includes_target(self, target_dict : dict[TargetName, Target]):
        resolved_target_dict :  dict[TargetName, Target] = {}

        # Resolve all targets
        for root_target in target_dict.values():
            # Resolve it only once
            if root_target in resolved_target_dict:
                continue
            
            # Flattening the targets establishes a dependency order,
            # allowing safe iteration where all included targets are
            # resolved before the including target.
            # if A includes B, then B appears before A.
            flatten_includes_targets = YamlTargetFile._flatten_includes_targets(root_target, target_dict)
            console.print_tips(f"{root_target.name} : {' -> '.join([p.name for p in flatten_includes_targets])}")

            # Resoluve inclusions
            for target in flatten_includes_targets:
                # Resolve it only once
                if target in resolved_target_dict:
                    continue
                resolved_target_dict[target.name] = target

                # Merge included target into this target
                if target.include:
                    # Find the included target and resolve it
                    included :Target = resolved_target_dict.get(target.include)
                    if not included:
                        console.print_error(f"{target.name} include an unknown target {target.include}")
                        exit(1)
                    target.merge_with(included)
                
                # Validate the features
                empty_feature_list : list[FeatureName] = []
                all_feature_set = target.default_features.get("all") or empty_feature_list
                for config, feature_name_list in target.default_features.items():

                    # Skip 'all'
                    if config == "all":
                        continue

                    # Add config + all features
                    feature_list = set[FeatureName](feature_name_list)
                    feature_list.update(all_feature_set)

                    # Validate the config + all features list
                    target.validate_features(config, feature_list)

                # Add this target to the list of resolved target
                resolved_target_dict[target.name] = target

    def load_yaml(self) -> set[Target] :
        try:
            target_dict : dict[TargetName, Target] = {}

            # Load the file
            with self._file.open() as f:
                self._yaml = yaml.load(f,Loader=LineLoader)
                for item, target_yaml_object in self._yaml.items():
                    target = self._read_target_node(item, target_yaml_object)
                    if not target:
                        console.print_error(f"⚠️  Target '{item}' in '{self._file}' will not be available")
                        continue
                    target_dict[target.name] = target

            # Resolve includes
            self.resolve_includes_target(target_dict)
            return target_dict
          
        except (OSError, yaml.YAMLError) as e:
            console.print_error(f"Error: When loading '{self._file}' file: {e}")
            return list()


    @staticmethod
    def _flatten_includes_targets(target_node : Target, target_dict : dict[TargetName, Target]) -> list[Target]:
        # 1. Collecte du sous-graphe (DFS)
        all_targets: list[Target] = list()
        visiting_stack: list[Target] = []
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
        def collect(current_node : Target, parent_node: Target):
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
        self._targets: dict[str, Target] = {}
    
    def __contains__(self, name: str) -> bool:
        return name in self._targets

    def __iter__(self):
        return iter(self._targets.items())
    
    def items(self):
        return self._targets.items()
    
    def register_target(self, target: Target):
        existing_target = self._targets.get(target.name)
        if existing_target:
            console.print_error(f"⚠️  Warning: Project already registered: {existing_target.name} in {str(existing_target.file)}")
            exit(1)
        self._targets[target.name] = target
    
    def load_and_register_all_target_in_directory(self, directory: Path):
          for file in directory.glob("*.yaml"):
            yaml_target_file = YamlTargetFile(file)
            target_dict = yaml_target_file.load_yaml()
            for target in target_dict.values():
                target : Target = target
                if not target.is_abstract:
                    console.print_step(f"{target.name}:")
                    console.print_step(f" - CXX flags: ")
                    flags : list[str] = target.get_cxx_compiler_flags("debug", ProjectType.dyn, target.get_default_feature_for_config("debug"))
                    console.print_step(f"    └ Debug: {' '.join(flags)}")
                    flags : list[str] = target.get_cxx_compiler_flags("release", ProjectType.dyn, target.get_default_feature_for_config("release"))
                    console.print_step(f"    └ Release: {' '.join(flags)}")

TargetRegistry = TargetRegistry()