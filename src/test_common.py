from toolchain.nodes.feature_node import FeatureRuleNodeOnlyOne
from toolchain.nodes.linker_nodes import LinkerSpecificOverrideNode, LinkersOverrideNode
from toolchain.nodes.property import StrList


def create_str_list(values, add_modifiers: list[str], remove_modifiers: list[str]) -> StrList:
    str_list = StrList()
    if isinstance(values, bool):
        str_list.override = values
    else:
        for value in values:
            str_list.override = True
            str_list.add_value(value)
    for modifier in add_modifiers:
        str_list.add_value(modifier)
    for modifier in remove_modifiers:
        str_list.add_modifier_remove(modifier)
    return str_list

def create_specific_linker_node(name: str, flags: StrList) -> LinkerSpecificOverrideNode:
    linker_node = LinkerSpecificOverrideNode(name)
    linker_node.flags = flags
    return linker_node

def create_test_linker_node(common_flag: StrList, specificflags: LinkerSpecificOverrideNode) -> LinkersOverrideNode:
    linker_node = LinkersOverrideNode()
    if common_flag:
        linker_node.common_linker.flags = common_flag
    if specificflags:
        linker_node.linker_overrides[specificflags.name] = specificflags
    return linker_node
