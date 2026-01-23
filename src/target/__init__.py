
from pathlib import Path
from typing import Optional, Self
import yaml
import console
from project import ProjectType

class LineLoader(yaml.SafeLoader):
    pass

class YamlObject:
    def __init__(self, value, line):
        self.value = value
        self.line = line
        
def construct_mapping(loader, node, deep=False):
    mapping = {}
    for key_node, value_node in node.value:
        key = loader.construct_object(key_node)
        value = loader.construct_object(value_node)

        mapping[key] = YamlObject(
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

class FeatureRuleNode:
    def __init__(self, name: str):
        self._name = name
    
    @property
    def name(self) -> FeatureName:
        return self._name
    
    @name.setter
    def name(self, value: FeatureName):
         self._name = value
         
# Only 1 rules is allowed in 'features'
class FeatureOnlyOneRuleNode(FeatureRuleNode):
    def __init__(self, name: str, features : list[FeatureName]):
        super().__init__(name=name)
        self.features=features

    @staticmethod
    def from_yaml(target_name: str, yaml : dict) -> Optional[Self]:
        name = yaml.get("only-one")
        if not name:
            return None
        features = yaml.get("features")
        if not features:
            console.print_error(f"❌ Line {name.line} : 'features' list is required in feature-rule '{name}' in '{target_name}' target")
            return None
        return FeatureOnlyOneRuleNode(name, features)


# The 'feature' is incompatible with all feature in 'with'
class FeatureIncompatibleRuleNode(FeatureRuleNode):
    def __init__(self, name: str, feature: FeatureName, incompatible_with:list[FeatureName]):
        super().__init__(name=name)
        self.feature=feature
        self.incompatible_with=incompatible_with
            
    @staticmethod
    def from_yaml(target_name: str, yaml : dict) -> Optional[Self]:
        name = yaml.get("incompatible")
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
        self.enable_feature = list[FeatureName]()

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
            console.print_error(f"⚠️  Error: Feature 'name' in 'features' is missing in '{target_name}' target. Feature is '{next(iter(yaml))}'")
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

        enable_feature = yaml.get("enable-feature")
        if enable_feature:
            feature_node.enable_feature.extend(enable_feature.value)
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
        self._cxx_compiler: Optional[TargetCXXCompilerNode] = None
        self._cxx_linker: Optional[TargetCXXLinkerNode] = None
    
    @property
    def name(self):
        return self._name
    
    @property
    def cxx_compiler(self):
        return self._cxx_compiler
   
    @cxx_compiler.setter
    def cxx_compiler(self, value: TargetCXXCompilerNode):
        self._cxx_compiler = value

    @property
    def cxx_linker(self):
        return self._cxx_linker
   
    @cxx_linker.setter
    def cxx_linker(self, value: TargetCXXCompilerNode):
        self._cxx_linker = value

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
        self._cxx_compiler: Optional[TargetCXXCompilerNode] = None
        self._cxx_linker: Optional[TargetCXXLinkerNode] = None
        self._project_type: Optional[TargetProjectTypeNode] = None
        self._features : Optional[set[TargetFeatureNode]] = None
        self._feature_rules : Optional[set[FeatureRuleNode]] = None
        self.include = TargetName()

    @property
    def name(self):
        return self._name
    
    @property
    def cxx_compiler(self) -> TargetCXXCompilerNode:
        return self._cxx_compiler
   
    @cxx_compiler.setter
    def cxx_compiler(self, value: TargetCXXCompilerNode):
        self._cxx_compiler = value

    @property
    def cxx_linker(self) -> TargetCXXCompilerNode:
        return self._cxx_linker
   
    @cxx_linker.setter
    def cxx_linker(self, value: TargetCXXCompilerNode):
        self._cxx_linker = value

    @property
    def project_type(self) -> TargetProjectTypeNode:
        return self._project_type
   
    @project_type.setter
    def project_type(self, value: TargetProjectTypeNode):
        self._project_type = value

    @property
    def features(self) -> set[TargetFeatureNode]:
        return self._features
   
    @features.setter
    def features(self, value: set[TargetFeatureNode]):
        self._features = value

    @property
    def feature_rules(self) -> set[TargetFeatureNode]:
        return self._feature_rules
   
    @feature_rules.setter
    def feature_rules(self, value: set[TargetFeatureNode]):
        self._feature_rules = value

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
        self.features = set[TargetFeatureNode]()
        for item in yaml_features_node.value:
            feature_node:Optional[TargetFeatureNode] = TargetFeatureNode.from_yaml(target_name=self.name, yaml=item)
            if feature_node in self.features:
                console.print_error(f"❌ Line {yaml_features_node.line} : Feature with name '{feature_node.name}' already in '{self.name}'")
                continue
            if feature_node:
                self.features.add(feature_node)
    
    def _read_feature_rules_node(self, yaml_feature_rules_node :YamlObject):
        if self.feature_rules:
            console.print_error(f"Multiple 'feature-rules' in '{self.name}' is not supported")
        self.feature_rules = set[FeatureRuleNode]()
        for item in yaml_feature_rules_node.value:
            only_one_rule_node = FeatureOnlyOneRuleNode.from_yaml(target_name=self.name, yaml=item)
            if only_one_rule_node:
                self.feature_rules.add(only_one_rule_node)
                continue
            incompatible_rule_node =  FeatureIncompatibleRuleNode.from_yaml(target_name=self.name, yaml=item)
            if incompatible_rule_node:
                self.feature_rules.add(incompatible_rule_node)
                continue
            console.print_error(f"❌ Line {next(iter(item.values())).line} : Unknown 'feature-rules' '{next(iter(item))}' in '{self.name}' target")



class YamlTargetFile:
    

    def __init__(self, file: Path):
        self._file = file
    
    def _read_target_node(self, target_name: TargetName, yaml_target : dict) -> TargetNode:
        # Read the target name
        parts = target_name.split('-')
        if len(parts) != 5:
            console.print_error(f"Invalid target name in '{self._file}':\t\n'{target_name}'. Expected 'arch-vendor-os-env-compiler' separated by '-'")
            return None
        arch = parts[0]
        vendor = parts[1]
        os = parts[2]
        env = parts[3]
        compiler_name = parts[4]
        target_node : TargetNode = TargetNode(name=target_name, arch=arch, os=os, env=env, vendor=vendor, compiler_name=compiler_name)

        for item, yaml_object in yaml_target.value.items():
            match item:
                case "cxx-compiler":
                    target_node._read_cxx_compiler_node(yaml_cxx_compiler=yaml_object)
                case "cxx-linker":
                    target_node._read_cxx_linker_node(yaml_cxx_linker=yaml_object)
                case "features":
                    target_node._read_features_node(yaml_features_node=yaml_object)
                case "feature-rules":
                    target_node._read_feature_rules_node(yaml_feature_rules_node=yaml_object)
                case "include":
                    target_node.include = yaml_object
                case _:
                    if item == ProjectType.bin or item == ProjectType.dyn or item == ProjectType.lib:
                        target_node._read_project_type_node(target_name=item, yaml_project_type=yaml_object)

        return target_node
            

    def load_yaml(self) -> list[TargetNode] :
        try:
            target_list = list[TargetNode]()

            # Load the file
            with self._file.open() as f:
                self._yaml = yaml.load(f,Loader=LineLoader)
                for item, object in self._yaml.items():
                    target = self._read_target_node(item, object)
                    if not target:
                        console.print_error(f"target '{item}' in '{self._file}' will not be available")
                        continue
                    target_list.append(target)

            # Resolve includes
            return target_list
        except (OSError, yaml.YAMLError) as e:
            console.print_error(f"Error: When loading '{self._file}' file: {e}")
            return list()
        
        

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