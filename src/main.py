from modulefinder import test
import sys
import os

from toolchain.nodes.linker_nodes import LinkerSpecificOverrideNode, LinkersOverrideNode
from toolchain.nodes.property import PropertyDict, PropertyStrList, PropertyStrListModifier, StrList, StrListModifierOperation, resolve_extends_common_str_list, resolve_extends_str_list

sys.path.insert(0, os.path.dirname(__file__))

from cli.app import app


# def test_merge() :
#     #-----------------------------------------------------------------------
#     # Self        ----->    Parent     ----->    Result
#     # f:[0]                 f:[10]               f:[10]
#     # add-f:[1]             add-f:[11]           add-f:[11]
#     # add-r:[2]             add-r:[12]           add-r:[2, 12]
#     _self = PropertyDict()
#     _self.add_property(PropertyStrList("f", ["0"]))
#     _self.add_property(PropertyStrListModifier("f", ["1"], StrListModifierOperation.ADD ))
#     _self.add_property(PropertyStrListModifier("r", ["2"], StrListModifierOperation.ADD ))

#     _parent = PropertyDict()
#     _parent.add_property(PropertyStrList("f", ["10"]))
#     _parent.add_property(PropertyStrListModifier("f", ["11"], StrListModifierOperation.ADD ))
#     _parent.add_property(PropertyStrListModifier("r", ["12"], StrListModifierOperation.ADD ))

#     _result = _self.merge_with(_parent)

#     # Validate result
#     f_list = _result.get_property_as("f", PropertyStrList)
#     assert f_list.name == "f"
#     assert len(f_list.values) == 1
#     assert "0" in f_list.values

#     f_add = _result.get_property_as("add-f", PropertyStrListModifier)
#     assert f_add.name == "add-f"
#     assert f_add.list_name == "f" 
#     assert f_add.operation == StrListModifierOperation.ADD
#     assert len(f_add.values) == 1 
#     assert set(["1"]) == set(f_add.values)

#     r_add = _result.get_property_as("add-r", PropertyStrListModifier)
#     assert r_add.name == "add-r"
#     assert r_add.list_name == "r"
#     assert f_add.operation == StrListModifierOperation.ADD
#     assert len(r_add.values) == 2 
#     assert set(["12", "2"]) == set(r_add.values)

#     #-----------------------------------------------------------------------
#     # Self        ----->    Parent     ----->    Result
#     # f:[0]                                      f:[0]
#     # add-f:[1]             add-f:[11]           add-f:[1]
#     # add-r:[2]             add-r:[12]           add-r:[2, 12]
#     _self = PropertyDict()
#     _self.add_property(PropertyStrList("f", ["0"]))
#     _self.add_property(PropertyStrListModifier("f", ["1"], StrListModifierOperation.ADD ))
#     _self.add_property(PropertyStrListModifier("r", ["2"], StrListModifierOperation.ADD ))

#     _parent = PropertyDict()
#     _parent.add_property(PropertyStrListModifier("f", ["11"], StrListModifierOperation.ADD ))
#     _parent.add_property(PropertyStrListModifier("r", ["12"], StrListModifierOperation.ADD ))

#     _result = _self.merge_with(_parent)

#     # Validate result
#     f_list = _result.get_property_as("f", PropertyStrList)
#     assert f_list.name == "f"
#     assert len(f_list.values) == 1
#     assert "0" in f_list.values

#     f_add = _result.get_property_as("add-f", PropertyStrListModifier)
#     assert f_add.name == "add-f"
#     assert f_add.list_name == "f"
#     assert f_add.operation == StrListModifierOperation.ADD
#     assert len(f_add.values) == 1
#     assert set(["1"]) == set(f_add.values)

#     r_add = _result.get_property_as("add-r", PropertyStrListModifier)
#     assert r_add.name == "add-r"
#     assert r_add.list_name == "r"
#     assert f_add.operation == StrListModifierOperation.ADD
#     assert len(r_add.values) == 2 
#     assert set(["12", "2"]) == set(r_add.values)

#     #-----------------------------------------------------------------------
#     # Self        ----->    Parent     ----->    Result
#     #                       f:[10]               f:[10]
#     # add-f:[1]             add-f:[11]           add-f:[11, 1]
#     # add-r:[2]             add-r:[12]           add-r:[2, 12]
#     _self = PropertyDict()
#     _self.add_property(PropertyStrListModifier("f", ["1"], StrListModifierOperation.ADD ))
#     _self.add_property(PropertyStrListModifier("r", ["2"], StrListModifierOperation.ADD ))

#     _parent = PropertyDict()
#     _parent.add_property(PropertyStrList("f", ["10"]))
#     _parent.add_property(PropertyStrListModifier("f", ["11"], StrListModifierOperation.ADD ))
#     _parent.add_property(PropertyStrListModifier("r", ["12"], StrListModifierOperation.ADD ))
    
#     _result = _self.merge_with(_parent)

#     # Validate result
#     f_list = _result.get_property_as("f", PropertyStrList)
#     assert f_list.name == "f"
#     assert len(f_list.values) == 1
#     assert "10" in f_list.values

#     f_add = _result.get_property_as("add-f", PropertyStrListModifier)
#     assert f_add.name == "add-f"
#     assert f_add.list_name == "f"
#     assert f_add.operation == StrListModifierOperation.ADD
#     assert len(f_add.values) == 2
#     assert set(["1", "11"]) == set(f_add.values)

#     r_add = _result.get_property_as("add-r", PropertyStrListModifier)
#     assert r_add.name == "add-r"
#     assert r_add.list_name == "r"
#     assert f_add.operation == StrListModifierOperation.ADD
#     assert len(r_add.values) == 2 
#     assert set(["12", "2"]) == set(r_add.values)

#     #-----------------------------------------------------------------------
#     # Self        ----->    Parent     ----->    Result
#     # add-f:[1]             add-f:[11]           add-f:[1, 11]
#     # add-r:[2]             add-r:[12]           add-r:[2, 12]
#     _self = PropertyDict()
#     _self.add_property(PropertyStrListModifier("f", ["1"], StrListModifierOperation.ADD ))
#     _self.add_property(PropertyStrListModifier("r", ["2"], StrListModifierOperation.ADD ))

#     _parent = PropertyDict()
#     _parent.add_property(PropertyStrListModifier("f", ["11"], StrListModifierOperation.ADD ))
#     _parent.add_property(PropertyStrListModifier("r", ["12"], StrListModifierOperation.ADD ))

#     _result = _self.merge_with(_parent)

#     # Validate result
#     f_add = _result.get_property_as("add-f", PropertyStrListModifier)
#     assert f_add.name == "add-f"
#     assert f_add.list_name == "f"
#     assert f_add.operation == StrListModifierOperation.ADD
#     assert len(f_add.values) == 2
#     assert set(["1", "11"]) == set(f_add.values)

#     r_add = _result.get_property_as("add-r", PropertyStrListModifier)
#     assert r_add.name == "add-r"
#     assert r_add.list_name == "r"
#     assert f_add.operation == StrListModifierOperation.ADD
#     assert len(r_add.values) == 2 
#     assert set(["12", "2"]) == set(r_add.values)


# def test_dispatch() :
#     #-----------------------------------------------------------------------
#     # Top         ----->    Bottom     ----->    Result
#     # f:[0]                 f:[10]               f:[10]
#     # add-f:[1]             add-f:[11]           add-f:[11]
#     # add-r:[2]             add-r:[12]           add-r:[2, 12]
#     _top = PropertyDict()
#     _top.add_property(PropertyStrList("f", ["0"]))
#     _top.add_property(PropertyStrListModifier("f", ["1"], StrListModifierOperation.ADD ))
#     _top.add_property(PropertyStrListModifier("r", ["2"], StrListModifierOperation.ADD ))

#     _bottom = PropertyDict()
#     _bottom.add_property(PropertyStrList("f", ["10"]))
#     _bottom.add_property(PropertyStrListModifier("f", ["11"], StrListModifierOperation.ADD ))
#     _bottom.add_property(PropertyStrListModifier("r", ["12"], StrListModifierOperation.ADD ))

#     _result = _bottom.dispatch(_top)

#     # Validate result
#     f_list = _result.get_property_as("f", PropertyStrList)
#     assert f_list.name == "f"
#     assert len(f_list.values) == 1
#     assert "10" in f_list.values

#     f_add = _result.get_property_as("add-f", PropertyStrListModifier)
#     assert f_add.name == "add-f"
#     assert f_add.list_name == "f" 
#     assert f_add.operation == StrListModifierOperation.ADD
#     assert len(f_add.values) == 1 
#     assert set(["11"]) == set(f_add.values)

#     r_add = _result.get_property_as("add-r", PropertyStrListModifier)
#     assert r_add.name == "add-r"
#     assert r_add.list_name == "r"
#     assert f_add.operation == StrListModifierOperation.ADD
#     assert len(r_add.values) == 2 
#     assert set(["12", "2"]) == set(r_add.values)

#     #-----------------------------------------------------------------------
#     # Top         ----->    Bottom     ----->    Result
#     # f:[0]                                      f:[0]
#     # add-f:[1]             add-f:[11]           add-f:[1, 11]
#     # add-r:[2]             add-r:[12]           add-r:[2, 12]
#     _top = PropertyDict()
#     _top.add_property(PropertyStrList("f", ["0"]))
#     _top.add_property(PropertyStrListModifier("f", ["1"], StrListModifierOperation.ADD ))
#     _top.add_property(PropertyStrListModifier("r", ["2"], StrListModifierOperation.ADD ))

#     _bottom = PropertyDict()
#     _bottom.add_property(PropertyStrListModifier("f", ["11"], StrListModifierOperation.ADD ))
#     _bottom.add_property(PropertyStrListModifier("r", ["12"], StrListModifierOperation.ADD ))

#     _result = _bottom.dispatch(_top)

#     # Validate result
#     f_list = _result.get_property_as("f", PropertyStrList)
#     assert f_list.name == "f"
#     assert len(f_list.values) == 1
#     assert "0" in f_list.values

#     f_add = _result.get_property_as("add-f", PropertyStrListModifier)
#     assert f_add.name == "add-f"
#     assert f_add.list_name == "f"
#     assert f_add.operation == StrListModifierOperation.ADD
#     assert len(f_add.values) == 2
#     assert set(["1", "11"]) == set(f_add.values)

#     r_add = _result.get_property_as("add-r", PropertyStrListModifier)
#     assert r_add.name == "add-r"
#     assert r_add.list_name == "r"
#     assert f_add.operation == StrListModifierOperation.ADD
#     assert len(r_add.values) == 2 
#     assert set(["12", "2"]) == set(r_add.values)

#     #-----------------------------------------------------------------------
#     # Top         ----->    Bottom     ----->    Result
#     #                       f:[10]               f:[10]
#     # add-f:[1]             add-f:[11]           add-f:[11]
#     # add-r:[2]             add-r:[12]           add-r:[2, 12]
#     _top = PropertyDict()
#     _top.add_property(PropertyStrListModifier("f", ["1"], StrListModifierOperation.ADD ))
#     _top.add_property(PropertyStrListModifier("r", ["2"], StrListModifierOperation.ADD ))

#     _bottom = PropertyDict()
#     _bottom.add_property(PropertyStrList("f", ["10"]))
#     _bottom.add_property(PropertyStrListModifier("f", ["11"], StrListModifierOperation.ADD ))
#     _bottom.add_property(PropertyStrListModifier("r", ["12"], StrListModifierOperation.ADD ))
    
#     _result = _bottom.dispatch(_top)

#     # Validate result
#     f_list = _result.get_property_as("f", PropertyStrList)
#     assert f_list.name == "f"
#     assert len(f_list.values) == 1
#     assert "10" in f_list.values

#     f_add = _result.get_property_as("add-f", PropertyStrListModifier)
#     assert f_add.name == "add-f"
#     assert f_add.list_name == "f"
#     assert f_add.operation == StrListModifierOperation.ADD
#     assert len(f_add.values) == 1
#     assert set(["11"]) == set(f_add.values)

#     r_add = _result.get_property_as("add-r", PropertyStrListModifier)
#     assert r_add.name == "add-r"
#     assert r_add.list_name == "r"
#     assert f_add.operation == StrListModifierOperation.ADD
#     assert len(r_add.values) == 2 
#     assert set(["12", "2"]) == set(r_add.values)

#     #-----------------------------------------------------------------------
#     # Top         ----->    Bottom     ----->    Result
#     # add-f:[1]             add-f:[11]           add-f:[1, 11]
#     # add-r:[2]             add-r:[12]           add-r:[2, 12]
#     _top = PropertyDict()
#     _top.add_property(PropertyStrListModifier("f", ["1"], StrListModifierOperation.ADD ))
#     _top.add_property(PropertyStrListModifier("r", ["2"], StrListModifierOperation.ADD ))

#     _bottom = PropertyDict()
#     _bottom.add_property(PropertyStrListModifier("f", ["11"], StrListModifierOperation.ADD ))
#     _bottom.add_property(PropertyStrListModifier("r", ["12"], StrListModifierOperation.ADD ))

#     _result = _bottom.dispatch(_top)

#     # Validate result
#     f_add = _result.get_property_as("add-f", PropertyStrListModifier)
#     assert f_add.name == "add-f"
#     assert f_add.list_name == "f"
#     assert f_add.operation == StrListModifierOperation.ADD
#     assert len(f_add.values) == 2
#     assert set(["1", "11"]) == set(f_add.values)

#     r_add = _result.get_property_as("add-r", PropertyStrListModifier)
#     assert r_add.name == "add-r"
#     assert r_add.list_name == "r"
#     assert f_add.operation == StrListModifierOperation.ADD
#     assert len(r_add.values) == 2 
#     assert set(["12", "2"]) == set(r_add.values)

def create_specific_linker_node(name: str, flags: StrList) -> LinkerSpecificOverrideNode:
    linker_node = LinkerSpecificOverrideNode(name)
    linker_node.flags = flags
    return linker_node

def create_test_linker_node(common_flag: StrList, specificflags: LinkerSpecificOverrideNode) -> LinkersOverrideNode:
    linker_node = LinkersOverrideNode()
    linker_node.common_linker.flags = common_flag
    if specificflags:
        linker_node.linker_overrides[specificflags.name] = specificflags
    return linker_node

def create_str_list(values: list[str], add_modifiers: list[str], remove_modifiers: list[str]) -> StrList:
    str_list = StrList()
    for value in values:
        str_list.add_value(value)
    for modifier in add_modifiers:
        str_list.add_modifier_add(modifier)
    for modifier in remove_modifiers:
        str_list.add_modifier_remove(modifier)
    return str_list


def create_1() -> LinkersOverrideNode :
    """  
    linkers:
      add-flags: [C1, C2]
      remove-flags: [C1, C3]
        ld:
          add-flags: [LD1, C3, LD2]
          remove-flags: [LD2] 
    """
    common_flag = create_str_list([], ["C1", "C2"], ["C1", "C3"])
    ld_flags = create_str_list([], ["LD1", "C3", "LD2"], ["LD2"])
    ld_linker = create_specific_linker_node("ld", ld_flags)
    return create_test_linker_node( common_flag, ld_linker)

def create_2() -> LinkersOverrideNode:
    """
    linkers:
      flags: [C0]
      add-flags: [C1, C2]
      remove-flags: [C1, C3]
      ld:
        add-flags: [LD1, C3, LD2]
        remove-flags: [LD2]
    """
    common_flag = create_str_list(["C0"], ["C1", "C2"], ["C1", "C3"])
    ld_flags = create_str_list([], ["LD1", "C3", "LD2"], ["LD2"])
    ld_linker = create_specific_linker_node("ld", ld_flags)
    return create_test_linker_node( common_flag, ld_linker)

def create_3() -> LinkersOverrideNode:
    """
    linkers:
      add-flags: [C1, C2]
      remove-flags: [C1, C3]
        ld:
          flags: [LD0]
          add-flags: [LD1, C3, LD2]
          remove-flags: [LD2]
    """
    common_flag = create_str_list([], ["C1", "C2"], ["C1", "C3"])
    ld_flags = create_str_list(["LD0"], ["LD1", "C3", "LD2"], ["LD2"])
    ld_linker = create_specific_linker_node("ld", ld_flags)
    return create_test_linker_node( common_flag, ld_linker)

def create_4() -> LinkersOverrideNode:
    """
    linkers:
      flags: [C0]
      add-flags: [C1, C2]
      remove-flags: [C1, C3]
      ld:
       flags: [LD0]
       add-flags: [LD1, C3, LD2]
       remove-flags: [LD2]
    """
    common_flag = create_str_list(["C0"], ["C1", "C2"], ["C1", "C3"])
    ld_flags = create_str_list(["LD0"], ["LD1", "C3", "LD2"], ["LD2"])
    ld_linker = create_specific_linker_node("ld", ld_flags)
    return create_test_linker_node( common_flag, ld_linker)

def test_1() :
    #  linkers:
    #  add-flags: [C1, C2]
    #  remove-flags: [C1, C3]
    #    ld:
    #      add-flags: [LD1, C3, LD2]
    #      remove-flags: [LD2] 
    linker_node = create_1()

    #  linkers: (Extended)
    #   add-flags: [C1, C2] # Not changed
    #   remove-flags: [C1, C3] # Not changed
    #   ld:
    #    add-flags: [LD1, C3, C2] # LD2 removed 
    #    remove-flags: [LD2] # Not changed
    extended_linker_node = linker_node.resolve_extends(None, {})

    # Common must remains the same
    assert extended_linker_node.common_linker.flags.values == set([])
    assert extended_linker_node.common_linker.flags.add_modifiers.values == set(["C1", "C2"])
    assert extended_linker_node.common_linker.flags.remove_modifiers.values == set(["C1", "C3"])
    ld = extended_linker_node.linker_overrides.get("ld")
    assert ld.flags.values == set([])
    assert ld.flags.add_modifiers.values == set(["C2", "C3", "LD1"])
    assert ld.flags.remove_modifiers.values == set(["LD2"]) 

def test_2() :
    #  linkers:
    #    flags: [C0]
    #    add-flags: [C1, C2]
    #    remove-flags: [C1, C3]
    #    ld:
    #      add-flags: [LD1, C3, LD2]
    #      remove-flags: [LD2]
    linker_node = create_2()

    #  linkers: (Extended)
    #   flags: [C0] # Not changed
    #   add-flags: [C1, C2] # Not changed
    #   remove-flags: [C1, C3] # Not changed
    #   ld:
    #    add-flags: [LD1, C3, C2, C0] # C1 and LD2 removed
    #    remove-flags: [LD2] # Not changed
    extended_linker_node = linker_node.resolve_extends(None, {})

    # Common must remains the same
    assert extended_linker_node.common_linker.flags.values == set(["C0"])
    assert extended_linker_node.common_linker.flags.add_modifiers.values == set(["C1", "C2"])
    assert extended_linker_node.common_linker.flags.remove_modifiers.values == set(["C1", "C3"])
    ld = extended_linker_node.linker_overrides.get("ld")
    assert ld.flags.values == set([])
    assert ld.flags.add_modifiers.values == set(["C0", "C2", "C3", "LD1"])
    assert ld.flags.remove_modifiers.values == set(["LD2"]) 

def test_3() :
    #  linkers:
    #    flags: []
    #    add-flags: [C1, C2]
    #    remove-flags: [C1, C3]
    #      ld:
    #        flags: [LD0]
    #        add-flags: [LD1, C3, LD2]
    #        remove-flags: [LD2]
    linker_node = create_3()

    #  linkers: (Extended)
    #    flags: [] # Not changed
    #    add-flags: [C1, C2] # Not changed
    #    remove-flags: [C1, C3] # Not changed
    #      ld:
    #        flags: [LD0] # Not changed
    #        add-flags: [LD1, C3] # LD2 removed
    #        remove-flags: [LD2] # Not changed
    extended_linker_node = linker_node.resolve_extends(None, {})

    # Common must remains the same
    assert extended_linker_node.common_linker.flags.values == set([])
    assert extended_linker_node.common_linker.flags.add_modifiers.values == set(["C1", "C2"])
    assert extended_linker_node.common_linker.flags.remove_modifiers.values == set(["C1", "C3"])
    ld = extended_linker_node.linker_overrides.get("ld")
    assert ld.flags.values == set(["LD0"])
    assert ld.flags.add_modifiers.values == set(["C3", "LD1"])
    assert ld.flags.remove_modifiers.values == set(["LD2"]) 

def test_4() :
    # linkers:
    #   flags: [C0]
    #   add-flags: [C1, C2]
    #   remove-flags: [C1, C3]
    #   ld:
    #    flags: [LD0]
    #    add-flags: [LD1, C3, LD2]
    #    remove-flags: [LD2]
    linker_node = create_4()

    # linkers: (Extended)
    #   flags: [C0] # Not changed
    #   add-flags: [C1, C2] # Not changed
    #   remove-flags: [C1, C3] # Not changed
    #   ld:
    #    flags: [LD0] # Not changed
    #    add-flags: [LD1, C3] # LD2 removed
    #    remove-flags: [LD2] # Not changed
    extended_linker_node = linker_node.resolve_extends(None, {})

    # Common must remains the same
    assert extended_linker_node.common_linker.flags.values == set(["C0"])
    assert extended_linker_node.common_linker.flags.add_modifiers.values == set(["C1", "C2"])
    assert extended_linker_node.common_linker.flags.remove_modifiers.values == set(["C1", "C3"])
    ld = extended_linker_node.linker_overrides.get("ld")
    assert ld.flags.values == set(["LD0"])
    assert ld.flags.add_modifiers.values == set(["C3", "LD1"])
    assert ld.flags.remove_modifiers.values == set(["LD2"]) 

def test_empty_extends_1():
    #  linkers:
    #  add-flags: [C1, C2]
    #  remove-flags: [C1, C3]
    #    ld:
    #      add-flags: [LD1, C3, LD2]
    #      remove-flags: [LD2] 
    base_linker_node = create_1()

    #  linkers: (Extended)
    #   add-flags: [C1, C2] # Not changed
    #   remove-flags: [C1, C3] # Not changed
    #   ld:
    #    add-flags: [LD1, C3, C2] # LD2 removed 
    #    remove-flags: [LD2] # Not changed
    extended_base_linker_node = base_linker_node.resolve_extends(None, {})

    # child 'linkers:' extends extended_base_linker_node
    # linkers: (Result)
    #   add-flags: [C1, C2] # Not changed
    #   remove-flags: [C1, C3] # Not changed
    #   ld:
    #    add-flags: [LD1, C3, C2] # Not changed
    #    remove-flags: [LD2] # Not changed
    result = LinkersOverrideNode().resolve_extends(extended_base_linker_node, {})

    # Validate result
    assert result.common_linker.flags.values == set([])
    assert result.common_linker.flags.add_modifiers.values == set([])
    assert result.common_linker.flags.remove_modifiers.values == set([])

    # If the linker override is not specified in the child, it should be a copy of the parent
    # NOTE: The parent must already be extended before the child extends it, so that the child can get the correct values from the parent
    ld = result.linker_overrides.get("ld")
    assert ld.flags.values == set([])
    assert ld.flags.add_modifiers.values == set(["C2", "C3", "LD1"])
    assert ld.flags.remove_modifiers.values == set(["LD2"]) 

def test_empty_extends_2():
    #  linkers:
    #    flags: [C0]
    #    add-flags: [C1, C2]
    #    remove-flags: [C1, C3]
    #    ld:
    #      add-flags: [LD1, C3, LD2]
    #      remove-flags: [LD2]
    base_linker_node = create_2()

    #  linkers: (Extended)
    #   flags: [C0] # Not changed
    #   add-flags: [C1, C2] # Not changed
    #   remove-flags: [C1, C3] # Not changed
    #   ld:
    #    add-flags: [LD1, C3, C2, C0] # C1 and LD2 removed
    #    remove-flags: [LD2] # Not changed
    extended_base_linker_node = base_linker_node.resolve_extends(None, {})

    # child 'linkers:' extends extended_base_linker_node*
    # linkers: (Result)
    #   flags: [C0] # Not changed
    #   add-flags: [C1, C2] # Not changed
    #   remove-flags: [C1, C3] # Not changed
    #   ld:
    #    add-flags: [LD1, C3, C2, C0] # Not changed
    #    remove-flags: [LD2] # Not changed
    result = LinkersOverrideNode().resolve_extends(extended_base_linker_node, {})

    # Validate result
    assert result.common_linker.flags.values == set([])
    assert result.common_linker.flags.add_modifiers.values == set([])
    assert result.common_linker.flags.remove_modifiers.values == set([])

    # If the linker override is not specified in the child, it should be a copy of the parent
    # NOTE: The parent must already be extended before the child extends it, so that the child can get the correct values from the parent
    ld = result.linker_overrides.get("ld")
    assert ld.flags.values == set([])
    assert ld.flags.add_modifiers.values == set(["C0", "C2", "C3", "LD1"])
    assert ld.flags.remove_modifiers.values == set(["LD2"]) 

def test_empty_extends_3():
    #  linkers:
    #    flags: []
    #    add-flags: [C1, C2]
    #    remove-flags: [C1, C3]
    #      ld:
    #        flags: [LD0]
    #        add-flags: [LD1, C3, LD2]
    #        remove-flags: [LD2]
    base_linker_node = create_3()

    #  linkers: (Extended)
    #    flags: [] # Not changed
    #    add-flags: [C1, C2] # Not changed
    #    remove-flags: [C1, C3] # Not changed
    #      ld:
    #        flags: [LD0] # Not changed
    #        add-flags: [LD1, C3] # LD2 removed
    #        remove-flags: [LD2] # Not changed
    extended_base_linker_node = base_linker_node.resolve_extends(None, {})

    # child 'linkers:' extends extended_base_linker_node
    #  linkers: (Result)
    #    flags: [] # Not changed
    #    add-flags: [C1, C2] # Not changed
    #    remove-flags: [C1, C3] # Not changed
    #      ld:
    #        flags: [LD0] # Not changed
    #        add-flags: [LD1, C3] # LD2 removed
    #        remove-flags: [LD2] # Not changed
    result = LinkersOverrideNode().resolve_extends(extended_base_linker_node, {})

    # Validate result
    assert result.common_linker.flags.values == set([])
    assert result.common_linker.flags.add_modifiers.values == set([])
    assert result.common_linker.flags.remove_modifiers.values == set([])

    # If the linker override is not specified in the child, it should be a copy of the parent
    # NOTE: The parent must already be extended before the child extends it, so that the child can get the correct values from the parent
    ld = result.linker_overrides.get("ld")
    assert ld.flags.values == set(["LD0"])
    assert ld.flags.add_modifiers.values == set(["C3", "LD1"])
    assert ld.flags.remove_modifiers.values == set(["LD2"]) 

def test_empty_extends_4():
    # linkers:
    #   flags: [C0]
    #   add-flags: [C1, C2]
    #   remove-flags: [C1, C3]
    #   ld:
    #    flags: [LD0]
    #    add-flags: [LD1, C3, LD2]
    #    remove-flags: [LD2]
    base_linker_node = create_4()

    # linkers: (Extended)
    #   flags: [C0] # Not changed
    #   add-flags: [C1, C2] # Not changed
    #   remove-flags: [C1, C3] # Not changed
    #   ld:
    #    flags: [LD0] # Not changed
    #    add-flags: [LD1, C3] # LD2 removed
    #    remove-flags: [LD2] # Not changed
    extended_base_linker_node = base_linker_node.resolve_extends(None, {})

    # child 'linkers:' extends extended_base_linker_node
    # linkers: (Result)
    #   flags: [C0] # Not changed
    #   add-flags: [C1, C2] # Not changed
    #   remove-flags: [C1, C3] # Not changed
    #   ld:
    #    flags: [LD0] # Not changed
    #    add-flags: [LD1, C3] # LD2 removed
    #    remove-flags: [LD2] # Not changed
    result = LinkersOverrideNode().resolve_extends(extended_base_linker_node, {})

    # Validate result
    assert result.common_linker.flags.values == set([])
    assert result.common_linker.flags.add_modifiers.values == set([])
    assert result.common_linker.flags.remove_modifiers.values == set([])

    # If the linker override is not specified in the child, it should be a copy of the parent
    # NOTE: The parent must already be extended before the child extends it, so that the child can get the correct values from the parent
    ld = result.linker_overrides.get("ld")
    assert ld.flags.values == set(["LD0"])
    assert ld.flags.add_modifiers.values == set(["C3", "LD1"])
    assert ld.flags.remove_modifiers.values == set(["LD2"]) 

def create_common_only_1():
    # linkers:
    #   flags: [E0]
    #   add-flags: [E1, E3]
    #   remove-flags: [E1, E2]
    extends_common_flag = create_str_list(["E0"], ["E1", "E3"], ["E1", "E2"])
    return create_test_linker_node(extends_common_flag, None)

def create_common_only_2():
    # linkers:
    #   flags: []
    #   add-flags: [E1, E3]
    #   remove-flags: [E1, E2]
    extends_common_flag = create_str_list([], ["E1", "E3"], ["E1", "E2"])
    return create_test_linker_node(extends_common_flag, None)

def test_common_only_1_extends_1():
    #  linkers:
    #  add-flags: [C1, C2]
    #  remove-flags: [C1, C3]
    #    ld:
    #      add-flags: [LD1, C3, LD2]
    #      remove-flags: [LD2] 
    base_linker_node = create_1()

    #  linkers: (Extended)
    #   add-flags: [C1, C2] # Not changed
    #   remove-flags: [C1, C3] # Not changed
    #   ld:
    #    add-flags: [LD1, C3, C2] # LD2 and C3 removed
    #    remove-flags: [LD2] # Not changed
    extended_base_linker_node = base_linker_node.resolve_extends(None, {})

    # child 'linkers:' extends extended_base_linker_node
    # linkers:
    #   flags: [E0]
    #   add-flags: [E1, E3]
    #   remove-flags: [E1, E2]
    child_linker_node = create_common_only_1()

    # linkers: (Result)
    #   flags: [E0]
    #   add-flags: [E1, E3]
    #   remove-flags: [E1, E2]
    #   ld:
    #    add-flags: [LD1, C3, C2] # Not changed
    #    remove-flags: [LD2] # Not changed
    result = child_linker_node.resolve_extends(extended_base_linker_node, {})

    # Validate result
    assert result.common_linker.flags.values == set(["E0"])
    assert result.common_linker.flags.add_modifiers.values == set(["E1", "E3"])
    assert result.common_linker.flags.remove_modifiers.values == set(["E1", "E2"])
    # If the linker override is not specified in the child, it should be a copy of the parent
    # NOTE: The parent must already be extended before the child extends it, so that the child can get the correct values from the parent
    ld = result.linker_overrides.get("ld")
    assert ld.flags.values == set([])
    assert ld.flags.add_modifiers.values == set(["C2", "C3", "LD1"])
    assert ld.flags.remove_modifiers.values == set(["LD2"]) 

def test_common_only_1_extends_2():
    #  linkers:
    #    flags: [C0]
    #    add-flags: [C1, C2]
    #    remove-flags: [C1, C3]
    #    ld:
    #      add-flags: [LD1, C3, LD2]
    #      remove-flags: [LD2]
    base_linker_node = create_2()

    #  linkers: (Extended)
    #   flags: [C0] # Not changed
    #   add-flags: [C1, C2] # Not changed
    #   remove-flags: [C1, C3] # Not changed
    #   ld:
    #    add-flags: [LD1, C3, C2, C0] # C1 and LD2 removed
    #    remove-flags: [LD2] # Not changed
    extended_base_linker_node = base_linker_node.resolve_extends(None, {})

    # child 'linkers:' extends extended_base_linker_node
    # linkers:
    #   flags: [E0]
    #   add-flags: [E1, E3]
    #   remove-flags: [E1, E2]
    child_linker_node = create_common_only_1()

    # linkers: (Result)
    #   flags: [E0]
    #   add-flags: [E1, E3]
    #   remove-flags: [E1, E2]
    #   ld:
    #    add-flags: [LD1, C3, C2, C0] # Not changed
    #    remove-flags: [LD2] # Not changed
    result = child_linker_node.resolve_extends(extended_base_linker_node, {})
    
    # Validate result
    assert result.common_linker.flags.values == set(["E0"])
    assert result.common_linker.flags.add_modifiers.values == set(["E1", "E3"])
    assert result.common_linker.flags.remove_modifiers.values == set(["E1", "E2"])

    # If the linker override is not specified in the child, it should be a copy of the parent
    # NOTE: The parent must already be extended before the child extends it, so that the child can get the correct values from the parent
    ld = result.linker_overrides.get("ld")
    assert ld.flags.values == set([])
    assert ld.flags.add_modifiers.values == set(["C0", "C2", "C3", "LD1"])
    assert ld.flags.remove_modifiers.values == set(["LD2"]) 

def test_common_only_1_extends_3():
    #  linkers:
    #    flags: []
    #    add-flags: [C1, C2]
    #    remove-flags: [C1, C3]
    #      ld:
    #        flags: [LD0]
    #        add-flags: [LD1, C3, LD2]
    #        remove-flags: [LD2]
    base_linker_node = create_3()

    #  linkers: (Extended)
    #    flags: [] # Not changed
    #    add-flags: [C1, C2] # Not changed
    #    remove-flags: [C1, C3] # Not changed
    #      ld:
    #        flags: [LD0] # Not changed
    #        add-flags: [LD1, C3] # LD2 removed
    #        remove-flags: [LD2] # Not changed
    extended_base_linker_node = base_linker_node.resolve_extends(None, {})

    # child 'linkers:' extends extended_base_linker_node
    # linkers:
    #   flags: [E0]
    #   add-flags: [E1, E3]
    #   remove-flags: [E1, E2]
    child_linker_node = create_common_only_1()

    # linkers: (Result)
    #   flags: [E0]
    #   add-flags: [E1, E3]
    #   remove-flags: [E1, E2]
    #     ld:
    #       flags: [LD0] # Not changed
    #       add-flags: [LD1, C3] # Not changed
    #       remove-flags: [LD2] # Not changed
    result = child_linker_node.resolve_extends(extended_base_linker_node, {})

    # Validate result
    assert result.common_linker.flags.values == set(["E0"])
    assert result.common_linker.flags.add_modifiers.values == set(["E1", "E3"])
    assert result.common_linker.flags.remove_modifiers.values == set(["E1", "E2"])

    # If the linker override is not specified in the child, it should be a copy of the parent
    # NOTE: The parent must already be extended before the child extends it, so that the child can get the correct values from the parent
    ld = result.linker_overrides.get("ld")
    assert ld.flags.values == set(["LD0"])
    assert ld.flags.add_modifiers.values == set(["C3", "LD1"])
    assert ld.flags.remove_modifiers.values == set(["LD2"]) 

def test_common_only_1_extends_4():
    # linkers:
    #   flags: [C0]
    #   add-flags: [C1, C2]
    #   remove-flags: [C1, C3]
    #   ld:
    #    flags: [LD0]
    #    add-flags: [LD1, C3, LD2]
    #    remove-flags: [LD2]
    base_linker_node = create_4()

    # linkers: (Extended)
    #   flags: [C0] # Not changed
    #   add-flags: [C1, C2] # Not changed
    #   remove-flags: [C1, C3] # Not changed
    #   ld:
    #    flags: [LD0] # Not changed
    #    add-flags: [LD1, C3] # LD2 removed
    #    remove-flags: [LD2] # Not changed
    extended_base_linker_node = base_linker_node.resolve_extends(None, {})

    # child 'linkers:' extends extended_base_linker_node
    # linkers:
    #   flags: [E0]
    #   add-flags: [E1, E3]
    #   remove-flags: [E1, E2]
    child_linker_node = create_common_only_1()

    # linkers: (Result)
    #   flags: [E0]
    #   add-flags: [E1, E3]
    #   remove-flags: [E1, E2]
    #     ld:
    #       flags: [LD0] # Not changed
    #       add-flags: [LD1, C3] # Not changed
    #       remove-flags: [LD2] # Not changed
    result = child_linker_node.resolve_extends(extended_base_linker_node, {})

    # Validate result
    assert result.common_linker.flags.values == set(["E0"])
    assert result.common_linker.flags.add_modifiers.values == set(["E1", "E3"])
    assert result.common_linker.flags.remove_modifiers.values == set(["E1", "E2"])

    # If the linker override is not specified in the child, it should be a copy of the parent
    # NOTE: The parent must already be extended before the child extends it, so that the child can get the correct values from the parent
    ld = result.linker_overrides.get("ld")
    assert ld.flags.values == set(["LD0"])
    assert ld.flags.add_modifiers.values == set(["C3", "LD1"])
    assert ld.flags.remove_modifiers.values == set(["LD2"]) 

def test_common_only_2_extends_1():
    #  linkers:
    #  add-flags: [C1, C2]
    #  remove-flags: [C1, C3]
    #    ld:
    #      add-flags: [LD1, C3, LD2]
    #      remove-flags: [LD2] 
    base_linker_node = create_1()

    #  linkers: (Extended)
    #   add-flags: [C1, C2] # Not changed
    #   remove-flags: [C1, C3] # Not changed
    #   ld:
    #    add-flags: [LD1, C3, C2] # LD2 removed
    #    remove-flags: [LD2] # Not changed
    extended_base_linker_node = base_linker_node.resolve_extends(None, {})

    # child 'linkers:' extends extended_base_linker_node
    # linkers:
    #   flags: []
    #   add-flags: [E1, E3]
    #   remove-flags: [E1, E2]
    child_linker_node = create_common_only_2()

    # linkers: (Result)
    #   flags: []
    #   add-flags: [E1, E3]
    #   remove-flags: [E1, E2]
    #   ld:
    #    add-flags: [LD1, C3, C2] # Not changed
    #    remove-flags: [LD2] # Not changed
    result = child_linker_node.resolve_extends(extended_base_linker_node, {})

    # Validate result
    assert result.common_linker.flags.values == set([])
    assert result.common_linker.flags.add_modifiers.values == set(["E1", "E3"])
    assert result.common_linker.flags.remove_modifiers.values == set(["E1", "E2"])
    # If the linker override is not specified in the child, it should be a copy of the parent
    # NOTE: The parent must already be extended before the child extends it, so that the child can get the correct values from the parent
    ld = result.linker_overrides.get("ld")
    assert ld.flags.values == set([])
    assert ld.flags.add_modifiers.values == set(["C2", "C3", "LD1"])
    assert ld.flags.remove_modifiers.values == set(["LD2"]) 

def test_common_only_2_extends_2():
    #  linkers:
    #    flags: [C0]
    #    add-flags: [C1, C2]
    #    remove-flags: [C1, C3]
    #    ld:
    #      add-flags: [LD1, C3, LD2]
    #      remove-flags: [LD2]
    base_linker_node = create_2()

    #  linkers: (Extended)
    #   flags: [C0] # Not changed
    #   add-flags: [C1, C2] # Not changed
    #   remove-flags: [C1, C3] # Not changed
    #   ld:
    #    add-flags: [LD1, C3, C2, C0] # C1 and LD2 removed
    #    remove-flags: [LD2] # Not changed
    extended_base_linker_node = base_linker_node.resolve_extends(None, {})

    # child 'linkers:' extends extended_base_linker_node
    # linkers:
    #   flags: []
    #   add-flags: [E1, E3]
    #   remove-flags: [E1, E2]
    child_linker_node = create_common_only_2()

    # linkers: (Result)
    #   flags: []
    #   add-flags: [E1, E3]
    #   remove-flags: [E1, E2]
    #   ld:
    #    add-flags: [LD1, C3, C2, C0] # Not changed
    #    remove-flags: [LD2] # Not changed
    result = child_linker_node.resolve_extends(extended_base_linker_node, {})
    
    # Validate result
    assert result.common_linker.flags.values == set([])
    assert result.common_linker.flags.add_modifiers.values == set(["E1", "E3"])
    assert result.common_linker.flags.remove_modifiers.values == set(["E1", "E2"])

    # If the linker override is not specified in the child, it should be a copy of the parent
    # NOTE: The parent must already be extended before the child extends it, so that the child can get the correct values from the parent
    ld = result.linker_overrides.get("ld")
    assert ld.flags.values == set([])
    assert ld.flags.add_modifiers.values == set(["C0", "C2", "C3", "LD1"])
    assert ld.flags.remove_modifiers.values == set(["LD2"]) 

def test_common_only_2_extends_3():
    #  linkers:
    #    flags: []
    #    add-flags: [C1, C2]
    #    remove-flags: [C1, C3]
    #      ld:
    #        flags: [LD0]
    #        add-flags: [LD1, C3, LD2]
    #        remove-flags: [LD2]
    base_linker_node = create_3()

    #  linkers: (Extended)
    #    flags: [] # Not changed
    #    add-flags: [C1, C2] # Not changed
    #    remove-flags: [C1, C3] # Not changed
    #      ld:
    #        flags: [LD0] # Not changed
    #        add-flags: [LD1, C3] # LD2 removed
    #        remove-flags: [LD2] # Not changed
    extended_base_linker_node = base_linker_node.resolve_extends(None, {})

    # child 'linkers:' extends extended_base_linker_node
    # linkers:
    #   flags: []
    #   add-flags: [E1, E3]
    #   remove-flags: [E1, E2]
    child_linker_node = create_common_only_2()

    # linkers: (Result)
    #   flags: []
    #   add-flags: [E1, E3]
    #   remove-flags: [E1, E2]
    #     ld:
    #       flags: [LD0] # Not changed
    #       add-flags: [LD1, C3] # Not changed
    #       remove-flags: [LD2] # Not changed
    result = child_linker_node.resolve_extends(extended_base_linker_node, {})

    # Validate result
    assert result.common_linker.flags.values == set([])
    assert result.common_linker.flags.add_modifiers.values == set(["E1", "E3"])
    assert result.common_linker.flags.remove_modifiers.values == set(["E1", "E2"])

    # If the linker override is not specified in the child, it should be a copy of the parent
    # NOTE: The parent must already be extended before the child extends it, so that the child can get the correct values from the parent
    ld = result.linker_overrides.get("ld")
    assert ld.flags.values == set(["LD0"])
    assert ld.flags.add_modifiers.values == set(["C3", "LD1"])
    assert ld.flags.remove_modifiers.values == set(["LD2"]) 

def test_common_only_2_extends_4():
    # linkers:
    #   flags: [C0]
    #   add-flags: [C1, C2]
    #   remove-flags: [C1, C3]
    #   ld:
    #    flags: [LD0]
    #    add-flags: [LD1, C3, LD2]
    #    remove-flags: [LD2]
    base_linker_node = create_4()

    # linkers: (Extended)
    #   flags: [C0] # Not changed
    #   add-flags: [C1, C2] # Not changed
    #   remove-flags: [C1, C3] # Not changed
    #   ld:
    #    flags: [LD0] # Not changed
    #    add-flags: [LD1, C3] # LD2 removed
    #    remove-flags: [LD2] # Not changed
    extended_base_linker_node = base_linker_node.resolve_extends(None, {})

    # child 'linkers:' extends extended_base_linker_node
    # linkers:
    #   flags: []
    #   add-flags: [E1, E3]
    #   remove-flags: [E1, E2]
    child_linker_node = create_common_only_2()

    # linkers: (Result)
    #   flags: []
    #   add-flags: [E1, E3]
    #   remove-flags: [E1, E2]
    #     ld:
    #       flags: [LD0] # Not changed
    #       add-flags: [LD1, C3] # Not changed
    #       remove-flags: [LD2] # Not changed
    result = child_linker_node.resolve_extends(extended_base_linker_node, {})

    # Validate result
    assert result.common_linker.flags.values == set([])
    assert result.common_linker.flags.add_modifiers.values == set(["E1", "E3"])
    assert result.common_linker.flags.remove_modifiers.values == set(["E1", "E2"])

    # If the linker override is not specified in the child, it should be a copy of the parent
    # NOTE: The parent must already be extended before the child extends it, so that the child can get the correct values from the parent
    ld = result.linker_overrides.get("ld")
    assert ld.flags.values == set(["LD0"])
    assert ld.flags.add_modifiers.values == set(["C3", "LD1"])
    assert ld.flags.remove_modifiers.values == set(["LD2"]) 

def create_a():
    """
    linkers:
      add-flags: [AC1, AC3, AC4]
      remove-flags: [AC1, ALD1, AC2]
        ld:
          add-flags: [ALD1, ALD2, ALD3]
          remove-flags: [ALD2, AC4]
    """
    extends_common_flag = create_str_list([], ["AC1", "AC3", "AC4"], ["AC1", "ALD1", "AC2"])
    extends_ld_flags = create_str_list([], ["ALD1", "ALD2", "ALD3"], ["ALD2", "AC4"])
    ld_child_linker = create_specific_linker_node("ld", extends_ld_flags)
    return create_test_linker_node(extends_common_flag, ld_child_linker)

def create_b():
    """
    linkers:
      flags: [AC0]
      add-flags: [AC1, AC3, AC4]
      remove-flags: [AC1, ALD1, AC2]
      ld:
        add-flags: [ALD1, ALD2, ALD3]
        remove-flags: [ALD2, AC4]
    """
    extends_common_flag = create_str_list(["AC0"], ["AC1", "AC3", "AC4"], ["AC1", "ALD1", "AC2"])
    extends_ld_flags = create_str_list([], ["ALD1", "ALD2", "ALD3"], ["ALD2", "AC4"])
    ld_child_linker = create_specific_linker_node("ld", extends_ld_flags)
    return create_test_linker_node(extends_common_flag, ld_child_linker)

def create_c():
    """
    linkers:
      add-flags: [AC1, AC3, AC4]
      remove-flags: [AC1, ALD1, AC2]
      ld:
        flags: [ALD0]
        add-flags: [ALD1, ALD2, ALD3]
        remove-flags: [ALD2, AC4]
    """
    extends_common_flag = create_str_list(["AC0"], ["AC1", "AC3", "AC4"], ["AC1", "ALD1", "AC2"])
    extends_ld_flags = create_str_list(["ALD0"], ["ALD1", "ALD2", "ALD3"], ["ALD2", "AC4"])
    ld_child_linker = create_specific_linker_node("ld", extends_ld_flags)
    return create_test_linker_node(extends_common_flag, ld_child_linker)

def create_d():
    """
    linkers:
      flags: [AC0]
      add-flags: [AC1, AC3, AC4]
      remove-flags: [AC1, ALD1, AC2]
      ld:
        flags: [ALD0]
        add-flags: [ALD1, ALD2, ALD3]
        remove-flags: [ALD2, AC4]
    """
    extends_common_flag = create_str_list(["AC0"], ["AC1", "AC3", "AC4"], ["AC1", "ALD1", "AC2"])
    extends_ld_flags = create_str_list(["ALD0"], ["ALD1", "ALD2", "ALD3"], ["ALD2", "AC4"])
    ld_child_linker = create_specific_linker_node("ld", extends_ld_flags)
    return create_test_linker_node(extends_common_flag, ld_child_linker)

def test_a_extends_1():
    #  linkers:
    #  add-flags: [C1, C2]
    #  remove-flags: [C1, C3]
    #    ld:
    #      add-flags: [LD1, C3, LD2]
    #      remove-flags: [LD2] 
    base_linker_node = create_1()

    #  linkers: (Extended)
    #   add-flags: [C1, C2] # Not changed
    #   remove-flags: [C1, C3] # Not changed
    #   ld:
    #    add-flags: [LD1, C3, C2] # LD2 removed 
    #    remove-flags: [LD2] # Not changed
    extended_base_linker_node = base_linker_node.resolve_extends(None, {})

  
    # child 'linkers:' extends extended_base_linker_node
    # linkers:
    #   add-flags: [AC1, AC3, AC4]
    #   remove-flags: [AC1, ALD1, AC2]
    #     ld:
    #       add-flags: [ALD1, ALD2, ALD3]
    #       remove-flags: [ALD2, AC4]
    child_linker_node = create_a()

    # child
    # linkers: (Extended)
    #   add-flags: [AC1, AC3, AC4] # Not changed
    #   remove-flags: [AC1, ALD1, AC2] # Not changed
    #   ld:
    #    add-flags: [ALD1, LD1, C3, C2, ALD3, AC3]
    #    remove-flags: [ALD2, AC4] # Not changed
    result = child_linker_node.resolve_extends(extended_base_linker_node, {})

    # Validate result
    assert result.common_linker.flags.values == set([])
    assert result.common_linker.flags.add_modifiers.values == set(["AC1", "AC3", "AC4"])
    assert result.common_linker.flags.remove_modifiers.values == set(["AC1", "ALD1","AC2"])

    # If the linker override is not specified in the child, it should be a copy of the parent
    # NOTE: The parent must already be extended before the child extends it, so that the child can get the correct values from the parent
    ld = result.linker_overrides.get("ld")
    assert ld.flags.values == set([])
    assert ld.flags.add_modifiers.values == set(["ALD1", "LD1", "C3", "C2", "ALD3", "AC3"])
    assert ld.flags.remove_modifiers.values == set(["ALD2", "AC4"]) 

def test_b_extends_1():
    #  linkers:
    #  add-flags: [C1, C2]
    #  remove-flags: [C1, C3]
    #    ld:
    #      add-flags: [LD1, C3, LD2]
    #      remove-flags: [LD2] 
    base_linker_node = create_1()

    #  linkers: (Extended)
    #   add-flags: [C1, C2] # Not changed
    #   remove-flags: [C1, C3] # Not changed
    #   ld:
    #    add-flags: [LD1, C3, C2] # LD2 removed 
    #    remove-flags: [LD2] # Not changed
    extended_base_linker_node = base_linker_node.resolve_extends(None, {})

  
    # child 'linkers:' extends extended_base_linker_node
    # linkers:
    #   flags: [AC0]
    #   add-flags: [AC1, AC3, AC4]
    #   remove-flags: [AC1, ALD1, AC2]
    #   ld:
    #     add-flags: [ALD1, ALD2, ALD3]
    #     remove-flags: [ALD2, AC4]
    child_linker_node = create_b()

    # child
    # linkers: (Extended)
    #   flags: [AC0] # Not changed 
    #   add-flags: [AC1, AC3, AC4] # Not changed
    #   remove-flags: [AC1, ALD1, AC2] # Not changed
    #   ld:
    #    add-flags: [ALD1, ALD3, AC3, AC0]
    #    remove-flags: [ALD2, AC4] # Not changed
    result = child_linker_node.resolve_extends(extended_base_linker_node, {})

    # Validate result
    assert result.common_linker.flags.values == set(["AC0"])
    assert result.common_linker.flags.add_modifiers.values == set(["AC1", "AC3", "AC4"])
    assert result.common_linker.flags.remove_modifiers.values == set(["AC1", "ALD1","AC2"])

    # If the linker override is not specified in the child, it should be a copy of the parent
    # NOTE: The parent must already be extended before the child extends it, so that the child can get the correct values from the parent
    ld = result.linker_overrides.get("ld")
    assert ld.flags.values == set([])
    assert ld.flags.add_modifiers.values == set(["ALD1", "ALD3", "AC3", "AC0"])
    assert ld.flags.remove_modifiers.values == set(["ALD2", "AC4"]) 

def test_extends() :
    test_1()
    test_2()
    test_3()
    test_4()
    test_empty_extends_1()
    test_empty_extends_2()
    test_empty_extends_3()
    test_empty_extends_4()

    test_common_only_1_extends_1()
    test_common_only_1_extends_2()
    test_common_only_1_extends_3()
    test_common_only_1_extends_4()

    test_common_only_2_extends_1()

    test_a_extends_1()
    test_b_extends_1()


if __name__ == "__main__":
    test_extends()
    
    app()
    