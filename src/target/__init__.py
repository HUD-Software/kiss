
from pathlib import Path
from typing import Optional, Self
import yaml
import console

class TargetFeature:
    def __init__(self):
        pass
    
    @staticmethod
    def from_yaml(yaml : dict) -> Self:
        name = yaml.get("name")
        if not name:
            #console.print_error(f"⚠️  Error: Project name is missing in {self.file} under '{project_type_key}'")
            exit(1)


class TargetCXXCompiler:
    def __init__(self):
        self._all_config_default_feature_names : list[str]= []
        self._config_feature_names : dict[str, list[str]] = dict[str, list[str]]()
        
    @property
    def all_config_feature_names(self):
        return self._all_config_default_feature_names
    
    def config_feature_names(self, config: str) -> list[str]:
        return self._config_feature_names.setdefault(config, [])
    
    
    

class TargetCXXLinker:
    def __init__(self):
        pass
    

class Target:
    def __init__(self, file: Path, name: str):
        self._file = file
        self._name = name
        
    @property
    def file(self):
        return self._file

    @property
    def name(self):
        return self._name


class YamlTargetFile:
    def __init__(self, file: Path):
        self._file = file
    
    def _load_cxx_compiler(self, yaml_cxx_compiler : dict) -> TargetCXXCompiler:
        cxx_compiler = TargetCXXCompiler()
        for item, yaml_object in yaml_cxx_compiler.items():
            if item == "default-features":
                for config_name, yaml_object in yaml_object.items():
                    if config_name == "all":
                        cxx_compiler.all_config_feature_names.extend(yaml_object)
                    else:
                        cxx_compiler.config_feature_names(config_name).extend(yaml_object)

        return cxx_compiler
    def _load_target(self, name: str, yaml_target : dict) -> Target:
        # Read the target name
        parts = name.split('-')
        if len(parts) != 5:
            console.print_error(f"Invalid target name in {self._file}:\t\n'{name}'. Expected 'arch-vendor-os-env-compiler' separated by '-'")
            return None
        # Common compiler target (name, Target)
        all_compiler_target : dict[str, Target] = None

        for item, yaml_object in yaml_target.items():
            if item == "cxx-compiler":
                cxx_compiler : TargetCXXCompiler = self._load_cxx_compiler(yaml_cxx_compiler=yaml_object)
                pass
        # arch = parts[0]
        # vendor = parts[1]
        # os = parts[2]
        # env = parts[3]
        compiler = parts[4]
        if compiler == "all":
            pass

    def load_yaml(self) -> list[Target] :
        try:
            with self._file.open() as f:
                self._yaml = yaml.safe_load(f)
                for item, object in self._yaml.items():
                    target = self._load_target(item, object)
                    if not target:
                        console.print_error("target {item} will not be available")

            return True
        except (OSError, yaml.YAMLError) as e:
            console.print_error(f"Error: When loading {self._file} file: {e}")
            return False
        

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
            yaml_target_file.load_yaml()


TargetRegistry = TargetRegistry()