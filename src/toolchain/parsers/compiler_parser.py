import yaml
from toolchain.nodes.compiler_nodes import CompilerFeatureNode, CompilerFeatureNodeList, CompilerNode, CompilersOverrideNode, CompilerSpecificOverrideNode
from toolchain.nodes.feature_node import FeatureNodeList, FeatureRuleNodeList
from toolchain.nodes.linker_nodes import LinkersOverrideNode
from toolchain.parsers.feature_parser import yaml_parse_feature, yaml_parse_feature_args, yaml_parse_feature_rule_list
from toolchain.parsers.linker_parser import yaml_parse_linkers_overrides
from toolchain.parsers.parse_utils import parse_property, try_parse_list_modifier

def yaml_parse_compiler_specific_overrides(name: str, data: dict) -> CompilerSpecificOverrideNode:
    compiler = CompilerSpecificOverrideNode(name)
    for key, value in data.items():
        if isinstance(value, dict):
            assert not compiler.linkers
            compiler.linkers = yaml_parse_linkers_overrides(value)
        else:
            if try_parse_list_modifier("flags", compiler.flags, key, value):
                continue
            elif try_parse_list_modifier("defines", compiler.defines, key, value):
                continue
            elif try_parse_list_modifier("features", compiler.features.str_list, key, value):
                continue
            else:    
                raise ValueError(f"'{key}:{value}' is not a valid key ({name})")
    return compiler


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
        if isinstance(value, dict):
            compiler = yaml_parse_compiler_specific_overrides(key, value)
            node.compilers.add(compiler)
        else:
            if try_parse_list_modifier("flags", node.common_compiler.flags, key, value):
                continue
            elif try_parse_list_modifier("defines", node.common_compiler.defines, key, value):
                continue
            elif try_parse_list_modifier("features", node.common_compiler.features.str_list, key, value):
                continue
            else:    
                raise ValueError(f"'{key}:{value}' is not a valid key")
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
