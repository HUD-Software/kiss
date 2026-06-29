import yaml
from toolchain.nodes.compiler_nodes import CompilerFeatureNode, CompilerNode, CompilersOverrideNode, CompilerSpecificOverrideNode
from toolchain.nodes.feature_node import FeatureNodeList, FeatureRuleNodeList
from toolchain.nodes.linker_nodes import LinkersOverrideNode
from toolchain.nodes.property import PropertyDict
from toolchain.parsers.feature_parser import yaml_parse_feature, yaml_parse_feature_rule
from toolchain.parsers.linker_parser import yaml_parse_linkers_overrides
from toolchain.parsers.parse_utils import parse_property

def yaml_parse_compilers_overrides(data: dict) -> CompilersOverrideNode:
    """Parse the 'compilers:' block inside a compiler feature.

    compilers:
      enable-features: []
      gcc:
        enable-features: [OPT_LEVEL_0]
      clang:
        enable-features: [OPT_LEVEL_0]
    """
    node = CompilersOverrideNode()
    for key, value in data.items():
        prop = parse_property(key, value)
        if prop:
            node.add_property(prop)
        elif isinstance(value, dict):
            override = CompilerSpecificOverrideNode(key)
            for override_key, override_value in value.items():
                prop = parse_property(override_key, override_value)
                if prop:
                    override.add_property(prop)
            node.add_property(override)
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
                feature_list = FeatureNodeList()
                for f in value:
                    feature_list.add_feature(yaml_parse_compiler_feature(f))
                if feature_list.features:
                    node.feature_list = feature_list    
            case FeatureRuleNodeList.NAME:
                feature_rules = FeatureRuleNodeList()
                for fr in value:
                    feature_rules.add_feature_rule(yaml_parse_feature_rule(fr))
                if feature_rules.feature_rules:
                    node.add_property(feature_rules)
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
