import yaml
from toolchain.nodes.compiler_nodes import CompilerFeatureNode, CompilerNode, CompilersOverrideNode, CompilerSpecificOverrideNode
from toolchain.nodes.feature_node import FeatureNodeList, FeatureRuleNodeList
from toolchain.nodes.linker_nodes import LinkersOverrideNode
from toolchain.parsers.feature_parser import yaml_parse_feature, yaml_parse_feature_rule_list
from toolchain.parsers.linker_parser import yaml_parse_linkers_overrides
from toolchain.parsers.parse_utils import parse_property

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
    node = yaml_parse_feature(data, CompilerFeatureNode)
    linkers_value = data.get(LinkersOverrideNode.NAME)
    if linkers_value:
        node.linkers = yaml_parse_linkers_overrides(linkers_value)
    return node

def yaml_parse_compiler_feature_list(data: dict) -> FeatureNodeList:
    feature_list = FeatureNodeList()
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
            case FeatureNodeList.NAME:
                feature_list = yaml_parse_compiler_feature_list(value)
                if feature_list.features:
                    node.feature_list = feature_list    
            case FeatureRuleNodeList.NAME:
                feature_rule_list = yaml_parse_feature_rule_list(value)
                if feature_rule_list.feature_rules:
                    node.feature_rule_list = feature_rule_list
            case _:
                prop = parse_property(key, value)
                if prop:
                    node.add_property(prop)
    return node


def load_compilers(path: str) -> dict[str, CompilerNode]:
    with open(path, encoding="utf-8") as f:
        data = yaml.safe_load(f)
    compilers = {}
    for c in data.get("compilers", []):
        compiler = yaml_parse_compiler(c)
        compilers[compiler.name] = compiler
    return compilers
