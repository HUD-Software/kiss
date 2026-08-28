import yaml
from toolchain.nodes.compiler_nodes import CompilerFeatureNode, CompilerFeatureNodeList, CompilerNode, CompilersOverrideNode, CompilerSpecificOverrideNode
from toolchain.nodes.feature_node import FeatureNodeList, FeatureRuleNodeList
from toolchain.nodes.linker_nodes import LinkersOverrideNode
from toolchain.parsers.feature_parser import yaml_parse_feature, yaml_parse_feature_args, yaml_parse_feature_rule_list
from toolchain.parsers.linker_parser import yaml_parse_linkers_overrides
from toolchain.parsers.parse_utils import parse_property, try_parse_list_modifier

def _check_compilers_overrides_key(key): 
    if key == LinkersOverrideNode.NAME:
            raise ValueError(f"""'{LinkersOverrideNode.NAME}' found under '{CompilersOverrideNode.NAME}' but must be under specific compiler name like 'clang', 'cl' or 'gcc'
                             
-> If you want to modify the linker for all compilers, add '{LinkersOverrideNode.NAME}' next to '{CompilersOverrideNode.NAME}':
     example:
       {CompilersOverrideNode.NAME}:
         gcc:
           ...
       {LinkersOverrideNode.NAME}:
         # Here you modify the linker for all compilers

-> If you want to modify the linker for a specific compiler, add '{LinkersOverrideNode.NAME}' under the specific compiler name:
     example:
       {CompilersOverrideNode.NAME}:
         gcc:
           {LinkersOverrideNode.NAME}:
           # Here you modify the linker for 'gcc' compiler
""")
    
def yaml_parse_compilers_overrides(data: dict) -> CompilersOverrideNode:
    """Parse the 'compilers:' block inside a compiler feature.

    compilers: # CompilersOverrideNode
      enable-features: []
      gcc: # CompilerSpecificOverrideNode
        enable-features: [OPT_LEVEL_0]
      clang:
        enable-features: [OPT_LEVEL_0]
      cl:
        linkers: # LinkersOverrideNode
          lld-link:
            enable-features: []
          link :
            enable-features: []
        
    """
    node = CompilersOverrideNode()
    for key, value in data.items():
        _check_compilers_overrides_key(key)
        prop = parse_property(key, value)
        if prop:
            node.add_property(prop)
        elif isinstance(value, dict):
            compiler_specific= CompilerSpecificOverrideNode(key)
            for override_key, override_value in value.items():
                match override_key:
                    case LinkersOverrideNode.NAME:
                        compiler_specific.linkers = yaml_parse_linkers_overrides(override_value)
                    case FeatureNodeList.NAME:
                        compiler_specific.feature_list = yaml_parse_compiler_feature_list(override_value)
                    case FeatureRuleNodeList.NAME:
                        compiler_specific.feature_rule_list = yaml_parse_feature_rule_list(override_value)
                    case _:
                        prop = parse_property(override_key, override_value)
                        if prop:
                            compiler_specific.add_property(prop)
            node.add_compiler(compiler_specific)
    return node

def yaml_parse_compiler_feature(data: dict) -> CompilerFeatureNode:
    """Parse a single compiler feature entry.

    - name: OPT_LEVEL_0
      description: No optimization
      flags: [/Od]
      enable-features: [DEBUG_INFO]
      add-flags: [...]         # optional
      remove-flags: [...]         # optional
      linkers:
        enable-features: []
        link:
          enable-features: [OPT_LEVEL_0]
    """
    # Feature need 'name'
    name = data.get("name")
    if not name or not isinstance(name, str):
        raise ValueError("Missing 'name' for feature as string")

    # optional description
    description = data.get("description", "")
    if description and not isinstance(description, str):
        raise ValueError("'description' for feature must be a string")

    
    # Create the feature and load informations
    node = CompilerFeatureNode(name)
    for key, value in data.items():
        match key:
            case "name":
                pass
            case "description":
                if not isinstance(value, str):
                    raise ValueError(f"'description' must be a string value ({name})")
                node.description = value
            case "args":
                if not isinstance(value, dict):
                    raise ValueError(f"'args' must be a composed values -> {value} in ({name})")
                node.args = yaml_parse_feature_args(value, name)
            case "linkers":
                if not isinstance(value, dict):
                    raise ValueError(f"'linkers' must be a composed values -> {value} in ({name})")
                node.linkers = yaml_parse_linkers_overrides(value)
            case _:
                if try_parse_list_modifier("flags", node.flags, key, value):
                    continue
                elif try_parse_list_modifier("features", node.features.str_list, key, value):
                    continue
                else:    
                    raise ValueError(f"'{key}:{value}' is not a valid key ({name})")
    return node

def yaml_parse_compiler_feature_list(data: dict) -> CompilerFeatureNodeList:
    feature_list = CompilerFeatureNodeList()
    for f in data:
        feature_list.add_feature(yaml_parse_compiler_feature(f))
    return feature_list


def yaml_parse_compiler(data: dict) -> CompilerNode:
    """Parse a single compiler entry."""
    # Compiler need 'name'
    name = data.get("name")
    if not name or not isinstance(name, str):
        raise ValueError("Missing 'name' for compiler as string")
    
    # Create the compiler and load informations
    node = CompilerNode(name)
    for key, value in data.items():
        match key:
            case "name":
                pass
            case "features":
                node.feature_list = yaml_parse_compiler_feature_list(value)
            # case FeatureNodeList.NAME:
            #     feature_list = yaml_parse_compiler_feature_list(value)
            #     if feature_list.features:
            #         node.feature_list = feature_list    
            case "feature-rules":
                feature_rule_list = yaml_parse_feature_rule_list(value)
                node.feature_rule_list = feature_rule_list
            case "is_abstract":
                if not isinstance(value, bool):
                    raise ValueError(f"'is_abstract' must be a boolean value -> {value} in ({name})")
                node.is_abstract = value
            case "extends":
                if not isinstance(value, str):
                    raise ValueError(f"'extends' must be a string value -> {value} in ({name})")
                node.extends = value
            case "supported-linkers":
                if not isinstance(value, list) or any(not isinstance(sl, str) for sl in value):
                    raise ValueError(f"'supported-linkers' must be a list of string -> {value} in ({name})")
                node.supported_linkers = value
            case "default-linker":
                if not isinstance(value, str):
                    raise ValueError(f"'default-linker' must be a string value -> {value} in ({name})")
                node.default_linker = value
            case _:
                raise ValueError(f"'{key}:{value}' is not a valid key ({name})")
    return node


def load_compilers(path: str) -> dict[str, CompilerNode]:
    with open(path, encoding="utf-8") as f:
        data = yaml.safe_load(f)
    compilers = {}
    if data:
        for c in data.get("compilers", []):
            compiler = yaml_parse_compiler(c)
            compilers[compiler.name] = compiler
    return compilers
