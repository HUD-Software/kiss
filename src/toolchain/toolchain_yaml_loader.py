from pathlib import Path
import yaml
import console
from toolchain.compiler import CompilerInfoLoader
from toolchain.target import TargetInfoLoader
from yaml_file.line_loader import LineLoader


class ToolchainYamlFile:
    def __init__(self, file: Path):
        self.file = file

    # Load all compilers in the file
    def load_yaml(self) -> bool :
        try:
            # Load the file
            with self.file.open() as f:
                self._yaml = yaml.load(f, Loader=LineLoader)
                for item_name, item_yaml_object in self._yaml.items():
                    match item_name:
                        case "compilers":
                            compiler_info_loader = CompilerInfoLoader(self.file)
                            compiler_info_loader.read_yaml_compilers(item_yaml_object)
                        case "targets":
                            target_info_loader = TargetInfoLoader(self.file)
                            target_info_loader.read_targets(item_yaml_object)
            return True
        
        except (OSError, yaml.YAMLError) as e:
            console.print_error(f"Error: When loading '{self.file}' file: {e}")
            return False


