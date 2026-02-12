#####################################################################
# TargetInfoLoader represent a yaml file that contains compilers to load
#####################################################################
from pathlib import Path
import console
from toolchain.target.target_info import TargetInfo
from toolchain.target.target_registry import TargetRegistry, Target
from yaml_file.line_loader import YamlObject

class TargetInfoLoader:
    def __init__(self, file: Path):
        self.file = file
    
    def _read_target_node(self, target_name: str, yaml_target : YamlObject) -> TargetInfo | None:
        # Read the target name
        parts = target_name.split('-')
        if len(parts) != 4:
            console.print_error(f"Line {yaml_target.key_line} : Invalid target name '{target_name}' in '{self.file}'")
            console.print_error(f"  💡 Expected 'arch-vendor-os-abi' separated by '-'")
            return None
        arch = parts[0]
        vendor = parts[1]
        os = parts[2]
        abi = parts[3]
        target_file : TargetInfo = TargetInfo(target_name,arch,vendor, os, abi)

        # If the target is empty, ignore it
        if not yaml_target.value:
            console.print_warning(f"⚠️  Line {yaml_target.key_line} : target '{target_name}' is empty in '{self.file}'")
            return 
        
        for item, yaml_object in yaml_target.value.items():
            match item:
                case "arch":
                    # Check that 'arch' is a string
                    if not isinstance(yaml_object.value, str):
                        console.print_error(f"Line {yaml_object.key_line} : 'arch' must be an arch name ( x86_64, i686, aarch64, arm ) in'{self.file}'")
                        return None
                    target_file.arch = yaml_object.value
                case "vendor":
                    # Check that 'vendor' is a string
                    if not isinstance(yaml_object.value, str):
                        console.print_error(f"Line {yaml_object.key_line} : 'vendor' must be a vendor ( pc, unknown ) name in'{self.file}'")
                        return None
                    target_file.vendor = yaml_object.value
                case "os":
                    # Check that 'vendor' is a string
                    if not isinstance(yaml_object.value, str):
                        console.print_error(f"Line {yaml_object.key_line} : 'os' must be an os name ( windows, linux, macos, none ) in'{self.file}'")
                        return None
                    target_file.os = yaml_object.value
                case "abi":
                    # Check that 'abi' is a string
                    if not isinstance(yaml_object.value, str):
                        console.print_error(f"Line {yaml_object.key_line} : 'abi' must be a abi name ( msvc, gnu, musl, none ) in'{self.file}'")
                        return None
                    target_file.abi = yaml_object.value
                case "pointer-width":
                    # Check that 'pointer-width' is a string
                    if not isinstance(yaml_object.value, int):
                        console.print_error(f"Line {yaml_object.key_line} : 'pointer-width' must be a integer in'{self.file}'")
                        return None
                    target_file.pointer_width = yaml_object.value
                case "endianness":
                    # Check that 'endianness' is a string
                    if not isinstance(yaml_object.value, str):
                        console.print_error(f"Line {yaml_object.key_line} : 'endianness' must be 'big' or 'little' in'{self.file}'")
                        return None
                    if yaml_object.value != "little" and yaml_object.value != "big":
                        console.print_error(f"Line {yaml_object.key_line} : 'endianness' must be 'big' or 'little' in'{self.file}'")
                        return None
                    target_file.endianness = yaml_object.value
        return target_file
        
        
    def read_targets(self, item_yaml_object) -> bool:
        for target_name, target_yaml_object in item_yaml_object.value.items():
            # Ignore if we already have a target name
            if target_name in TargetRegistry:
                console.print_error(f"Line {target_yaml_object.key_line} : TargetInfo '{target_name}' already exist when loading '{self.file}'")
                continue
            
            # Load the target
            target_file = self._read_target_node(target_name, target_yaml_object)
            if target_file is None:
                console.print_error(f"Line {target_yaml_object.key_line} : TargetInfo '{target_name}' in '{self.file}' will not be available")
                continue

            # Add it to the available target list
            target = Target(name=target_file.name, 
                            arch=target_file.arch,
                            vendor=target_file.vendor,
                            os=target_file.os,
                            abi=target_file.abi)
            target.endianness = target_file.endianness
            target.pointer_width = target_file.pointer_width
            TargetRegistry.register_compiler(target=target)