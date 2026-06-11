import yaml
from toolchain.nodes.property import PropertyDict
from toolchain.nodes.linker_nodes import LinkerNode
from toolchain.parsers.feature_parser import yaml_parse_feature, yaml_parse_feature_rule
from toolchain.parsers.parse_utils import parse_property


def yaml_parse_linker(data: dict) -> LinkerNode:
    node = LinkerNode(data["name"])
    for key, value in data.items():
        if key == "name":
            continue
        if key == "features" and isinstance(value, list):
            features = PropertyDict(key)
            for f in value:
                features.add_property(yaml_parse_feature(f))
            if features.properties:
                node.add_property(features)
            continue
        if key == "feature-rules" and isinstance(value, list):
            feature_rules = PropertyDict("feature-rules")
            for fr in value:
                feature_rules.add_property(yaml_parse_feature_rule(fr))
            if feature_rules.properties:
                node.add_property(feature_rules)
            continue
        
        prop = parse_property(key, value)
        if prop:
            node.add_property(prop)
    return node


def load_linkers(path: str) -> dict[str, LinkerNode]:
    with open(path, encoding="utf-8") as f:
        data = yaml.safe_load(f)

    linkers = {}
    for l in data.get("linkers", []):
        linker = yaml_parse_linker(l)
        linkers[linker.name] = linker
    return linkers
''