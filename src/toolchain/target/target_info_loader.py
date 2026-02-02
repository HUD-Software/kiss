#####################################################################
# TargetInfoLoader represent a yaml file that contains compilers to load
#####################################################################
from pathlib import Path
import console
from toolchain.target.target_info import TargetInfo, TargetInfoList, TargetInfoRegistry
from yaml_file.line_loader import YamlObject

class TargetInfoLoader:
    def __init__(self, file: Path):
        self.file = file
        self.targets = TargetInfoList()
    
    def _read_target_node(self, target_name: str, yaml_target : YamlObject) -> TargetInfo | None:
        # Read the target name
        parts = target_name.split('-')
        if len(parts) != 4:
            console.print_error(f"❌ Line {yaml_target.key_line} : Invalid target name '{target_name}' in '{self.file}'")
            console.print_error(f"  💡 Expected 'arch-vendor-os-env' separated by '-'")
            return None
        arch = parts[0]
        vendor = parts[1]
        os = parts[2]
        env = parts[3]
        target_file : TargetInfo = TargetInfo(target_name,arch,vendor, os, env)

        # If the target is empty, ignore it
        if not yaml_target.value:
            console.print_warning(f"⚠️  Line {yaml_target.key_line} : target '{target_name}' is empty in '{self.file}'")
            return 
        
        for item, yaml_object in yaml_target.value.items():
            match item:
                case "arch":
                    # Check that 'arch' is a string
                    if not isinstance(yaml_object.value, str):
                        console.print_error(f"❌ Line {yaml_object.key_line} : 'arch' must be an arch name ( x86_64, i686, aarch64, arm ) in'{self.file}'")
                        return None
                    target_file.arch = yaml_object.value
                case "vendor":
                    # Check that 'vendor' is a string
                    if not isinstance(yaml_object.value, str):
                        console.print_error(f"❌ Line {yaml_object.key_line} : 'vendor' must be a vendor ( pc, unknown ) name in'{self.file}'")
                        return None
                    target_file.vendor = yaml_object.value
                case "os":
                    # Check that 'vendor' is a string
                    if not isinstance(yaml_object.value, str):
                        console.print_error(f"❌ Line {yaml_object.key_line} : 'os' must be an os name ( windows, linux, macos, none ) in'{self.file}'")
                        return None
                    target_file.os = yaml_object.value
                case "env":
                    # Check that 'env' is a string
                    if not isinstance(yaml_object.value, str):
                        console.print_error(f"❌ Line {yaml_object.key_line} : 'env' must be a environnement name ( msvc, gnu, musl, none ) in'{self.file}'")
                        return None
                    target_file.env = yaml_object.value
                case "pointer-width":
                    # Check that 'env' is a string
                    if not isinstance(yaml_object.value, int):
                        console.print_error(f"❌ Line {yaml_object.key_line} : 'pointer-width' must be a integer in'{self.file}'")
                        return None
                    target_file.pointer_width = yaml_object.value
                case "endianness":
                    # Check that 'env' is a string
                    if not isinstance(yaml_object.value, str):
                        console.print_error(f"❌ Line {yaml_object.key_line} : 'endianness' must be 'big' or 'little' in'{self.file}'")
                        return None
                    if yaml_object.value != "little" and yaml_object.value != "big":
                        console.print_error(f"❌ Line {yaml_object.key_line} : 'endianness' must be 'big' or 'little' in'{self.file}'")
                        return None
                    target_file.endianness = yaml_object.value
                case "supported-compilers":
                    # Check that 'supported-compilers' is a list of string
                    if not isinstance(yaml_object.value, list) or not all(isinstance(x, str) for x in yaml_object.value):
                        console.print_error(f"❌ Line {yaml_object.key_line} : 'supported-compilers' must contains list of feature name in'{self.file}'")
                        return None
                    target_file.suppported_compilers = yaml_object.value

        return target_file
        
        
    def read_targets(self, item_yaml_object) -> bool:
        for target_name, target_yaml_object in item_yaml_object.value.items():
            # Ignore if we already have a target name
            existing_target: TargetInfo = self.targets.get(target_name)
            if existing_target:
                console.print_error(f"❌ Line {target_yaml_object.key_line} : TargetInfo '{existing_target}' already exist in '{existing_target.file}' when loading '{self.file}'")
                continue
            
            # Load the target
            target_file = self._read_target_node(target_name, target_yaml_object)
            if target_file is None:
                console.print_error(f"⚠️ Line {target_yaml_object.key_line} : TargetInfo '{target_name}' in '{self.file}' will not be available")
                continue
            target_file.file = self.file
            # Add it to the available target list
            TargetInfoRegistry.register_compiler(target_file)
            self.targets.add(target_file)