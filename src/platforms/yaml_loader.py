import yaml

############################################################
# LineLoader used to keep track of line when parsing YAML
############################################################
class LineLoader(yaml.SafeLoader):
    pass

class YamlObject:
    def __init__(self, key_line, value, line):
        self.key_line = key_line
        self.value = value
        self.line = line
        
def construct_mapping(loader, node, deep=False):
    mapping = {}
    for key_node, value_node in node.value:
        key = loader.construct_object(key_node)
        value = loader.construct_object(value_node)

        mapping[key] = YamlObject(
            key_line=key_node.start_mark.line + 1,
            value=value,
            line=value_node.start_mark.line + 1
        )

    return mapping

LineLoader.add_constructor(
    yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG,
    construct_mapping,
)
