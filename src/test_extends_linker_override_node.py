from test_common import create_feature_str_list, create_specific_linker_override_node, create_str_list, create_linker_override_node
from toolchain.nodes.linker_nodes import LinkersOverrideNode


def create_1() -> LinkersOverrideNode :
    """  
    linkers:
      add-flags: [C1, C2]
      remove-flags: [C1, C3]
      add-features: [CF1, CF2]
      remove-features: [CF1, CF3]
        ld:
          add-flags: [LD1, C3, LD2]
          remove-flags: [LD2] 
          add-featres: [LDF1, CF3, LDF2]
          remove-flags: [LDF2] 
    """
    common_flag = create_str_list([], ["C1", "C2"], ["C1", "C3"])
    common_features = create_feature_str_list(False, ["CF1", "CF2"], ["CF1", "CF3"])
    ld_flags = create_str_list([], ["LD1", "C3", "LD2"], ["LD2"])
    ld_features = create_feature_str_list(False, ["LDF1", "CF3", "LDF2"], ["LDF2"])
    ld_linker = create_specific_linker_override_node("ld", ld_flags, ld_features)
    return create_linker_override_node(common_flag, common_features, ld_linker)

def create_2() -> LinkersOverrideNode:
    """
    linkers:
      flags: [C0]
      add-flags: [C1, C2]
      remove-flags: [C1, C3]
      features: [CF0]
      add-features: [CF1, CF2]
      remove-features: [CF1, CF3]
      ld:
        add-flags: [LD1, C3, LD2]
        remove-flags: [LD2]
        add-featres: [LDF1, CF3, LDF2]
        remove-flags: [LDF2] 
    """
    common_flag = create_str_list(["C0"], ["C1", "C2"], ["C1", "C3"])
    common_features = create_feature_str_list(True, ["CF0", "CF1", "CF2"], ["CF1", "CF3"])
    ld_flags = create_str_list([], ["LD1", "C3", "LD2"], ["LD2"])
    ld_features = create_feature_str_list(False, ["LDF1", "CF3", "LDF2"], ["LDF2"])
    ld_linker = create_specific_linker_override_node("ld", ld_flags, ld_features)
    return create_linker_override_node( common_flag, common_features, ld_linker)

def create_3() -> LinkersOverrideNode:
    """
    linkers:
      add-flags: [C1, C2]
      remove-flags: [C1, C3]
      add-features: [CF1, CF2]
      remove-features: [CF1, CF3]
        ld:
          flags: [LD0]
          add-flags: [LD1, C3, LD2]
          remove-flags: [LD2]
          features: [LDF0]
          add-featres: [LDF1, CF3, LDF2]
          remove-flags: [LDF2]
    """
    common_flag = create_str_list([], ["C1", "C2"], ["C1", "C3"])
    common_features = create_feature_str_list(False, ["CF1", "CF2"], ["CF1", "CF3"])
    ld_flags = create_str_list(["LD0"], ["LD1", "C3", "LD2"], ["LD2"])
    ld_features = create_feature_str_list(True, ["LDF0", "LDF1", "CF3", "LDF2"], ["LDF2"])
    ld_linker = create_specific_linker_override_node("ld", ld_flags, ld_features)
    return create_linker_override_node( common_flag, common_features, ld_linker)

def create_4() -> LinkersOverrideNode:
    """
    linkers:
      flags: [C0]
      add-flags: [C1, C2]
      remove-flags: [C1, C3]
      features: [CF0]
      add-features: [CF1, CF2]
      remove-features: [CF1, CF3]
      ld:
       flags: [LD0]
       add-flags: [LD1, C3, LD2]
       remove-flags: [LD2]
       features: [LDF0]
       add-featres: [LDF1, CF3, LDF2]
       remove-flags: [LDF2]
    """
    common_flag = create_str_list(["C0"], ["C1", "C2"], ["C1", "C3"])
    common_features = create_feature_str_list(True, ["CF0", "CF1", "CF2"], ["CF1", "CF3"])
    ld_flags = create_str_list(["LD0"], ["LD1", "C3", "LD2"], ["LD2"])
    ld_features = create_feature_str_list(True, ["LDF0", "LDF1", "CF3", "LDF2"], ["LDF2"])
    ld_linker = create_specific_linker_override_node("ld", ld_flags, ld_features)
    return create_linker_override_node( common_flag, common_features, ld_linker)

def test_1() :
    #  linkers:
    #  add-flags: [C1, C2]
    #  remove-flags: [C1, C3]
    #  add-features: [CF1, CF2]
    #  remove-features: [CF1, CF3]
    #  ld:
    #    add-flags: [LD1, C3, LD2]
    #    remove-flags: [LD2] 
    #    add-featres: [LDF1, CF3, LDF2]
    #    remove-flags: [LDF2] 
    base_linker_node = create_1()

    #  linkers: (Extended)
    #   add-flags: [C2] # C1 removed
    #   remove-flags: [] # Emptied
    #   add-features: [CF2] # CF1 removed
    #   remove-features: [] # Emptied
    #   ld:
    #     add-flags: [LD1, C3, C2] # C2 added, LD2 removed 
    #     remove-flags: [] # Emptied
    #     add-features: [LDF1, CF3, CF2] # CF2 added, LDF2 removed 
    #     remove-flags: [] # Emptied
    extended_base_linker_node = base_linker_node.resolve_extends(None, {}).unwrap()

    # Validate result
    assert extended_base_linker_node.common_linker.flags.values == set(["C2"])
    assert extended_base_linker_node.common_linker.flags.remove_modifiers.values == set([])
    assert extended_base_linker_node.common_linker.features.values == set(["CF2"])
    assert extended_base_linker_node.common_linker.features.remove_modifiers.values == set([])
    ld = extended_base_linker_node.linker_overrides.get("ld")
    assert ld.flags.values == set(["C2", "C3", "LD1"])
    assert ld.flags.remove_modifiers.values == set([]) 
    assert ld.features.values == set(["CF2", "CF3", "LDF1"])
    assert ld.features.remove_modifiers.values == set([]) 

def test_2() :
    #  linkers:
    #    flags: [C0]
    #    add-flags: [C1, C2]
    #    remove-flags: [C1, C3]
    #    features : [CF0]
    #    add-features: [CF1, CF2]
    #    remove-features: [CF1, CF3]
    #    ld:
    #      add-flags: [LD1, C3, LD2]
    #      remove-flags: [LD2]
    #      add-featres: [LDF1, CF3, LDF2]
    #      remove-flags: [LDF2]
    base_linker_node = create_2()

    #  linkers: (Extended)
    #   add-flags: [C0, C2] # C1 removed, C0 added
    #   remove-flags: [] # Emptied
    #   add-features: [CF1, CF2] # C1 removed, C0 added
    #   remove-features: [CF1, CF3]
    #   ld:
    #    add-flags: [LD1, C3, C2, C0] # C1 and LD2 removed
    #    remove-flags: [LD2] # Not changed
    extended_base_linker_node = base_linker_node.resolve_extends(None, {}).unwrap()

    # Validate result
    assert extended_base_linker_node.common_linker.flags.values == set(["C0", "C2"])
    assert extended_base_linker_node.common_linker.flags.remove_modifiers.values == set([])
    assert extended_base_linker_node.common_linker.features.values == set(["CF0", "CF2"])
    assert extended_base_linker_node.common_linker.features.remove_modifiers.values == set([])
    ld = extended_base_linker_node.linker_overrides.get("ld")
    assert ld.flags.values == set(["C0", "C2", "C3", "LD1"])
    assert ld.flags.remove_modifiers.values == set([]) 
    assert ld.features.values == set(["CF0", "CF2", "CF3", "LDF1"])
    assert ld.features.remove_modifiers.values == set([]) 

def test_3() :
    #  linkers:
    #    add-flags: [C1, C2]
    #    remove-flags: [C1, C3]
    #      ld:
    #        flags: [LD0]
    #        add-flags: [LD1, C3, LD2]
    #        remove-flags: [LD2]
    base_linker_node = create_3()

    #  linkers: (Extended)
    #    add-flags: [C2] # C1 removed
    #    remove-flags: [C1, C3] # Not changed
    #      ld:
    #        flags: [LD0] # Not changed
    #        add-flags: [LD1, C3] # LD2 removed
    #        remove-flags: [LD2] # Not changed
    extended_base_linker_node = base_linker_node.resolve_extends(None, {})

    # Validate result
    assert extended_base_linker_node.common_linker.flags.values == set(["C2"])
    assert extended_base_linker_node.common_linker.flags.remove_modifiers.values == set([])
    ld = extended_base_linker_node.linker_overrides.get("ld")
    assert ld.flags.values == set(["LD0", "C3", "LD1"])
    assert ld.flags.remove_modifiers.values == set([]) 

def test_4() :
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
    #   add-flags: [C0, C2] # C1 removed, C0 added
    #   remove-flags: [C1, C3] # Not changed
    #   ld:
    #    flags: [LD0] # Not changed
    #    add-flags: [LD1, C3] # LD2 removed
    #    remove-flags: [LD2] # Not changed
    extended_base_linker_node = base_linker_node.resolve_extends(None, {})

    # Validate result
    assert extended_base_linker_node.common_linker.flags.values == set(["C0", "C2"])
    assert extended_base_linker_node.common_linker.flags.remove_modifiers.values == set([])
    ld = extended_base_linker_node.linker_overrides.get("ld")
    assert ld.flags.values == set(["LD0", "C3", "LD1"])
    assert ld.flags.remove_modifiers.values == set([]) 

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
    assert result.common_linker.flags.remove_modifiers.values == set([])

    # If the linker override is not specified in the child, it should be a copy of the parent
    # NOTE: The parent must already be extended before the child extends it, so that the child can get the correct values from the parent
    ld = result.linker_overrides.get("ld")
    assert ld.flags.values == set(["C2", "C3", "LD1"])
    assert ld.flags.remove_modifiers.values == set([]) 

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
    assert result.common_linker.flags.remove_modifiers.values == set([])

    # If the linker override is not specified in the child, it should be a copy of the parent
    # NOTE: The parent must already be extended before the child extends it, so that the child can get the correct values from the parent
    ld = result.linker_overrides.get("ld")
    assert ld.flags.values == set(["C0", "C2", "C3", "LD1"])
    assert ld.flags.remove_modifiers.values == set([]) 

def test_empty_extends_3():
    #  linkers:
    #    add-flags: [C1, C2]
    #    remove-flags: [C1, C3]
    #      ld:
    #        flags: [LD0]
    #        add-flags: [LD1, C3, LD2]
    #        remove-flags: [LD2]
    base_linker_node = create_3()

    #  linkers: (Extended)
    #    add-flags: [C1, C2] # Not changed
    #    remove-flags: [C1, C3] # Not changed
    #      ld:
    #        flags: [LD0] # Not changed
    #        add-flags: [LD1, C3] # LD2 removed
    #        remove-flags: [LD2] # Not changed
    extended_base_linker_node = base_linker_node.resolve_extends(None, {})

    # child 'linkers:' extends extended_base_linker_node
    #  linkers: (Result)
    #    add-flags: [C1, C2] # Not changed
    #    remove-flags: [C1, C3] # Not changed
    #      ld:
    #        flags: [LD0] # Not changed
    #        add-flags: [LD1, C3] # LD2 removed
    #        remove-flags: [LD2] # Not changed
    result = LinkersOverrideNode().resolve_extends(extended_base_linker_node, {})

    # Validate result
    assert result.common_linker.flags.values == set([])
    assert result.common_linker.flags.remove_modifiers.values == set([])

    # If the linker override is not specified in the child, it should be a copy of the parent
    # NOTE: The parent must already be extended before the child extends it, so that the child can get the correct values from the parent
    ld = result.linker_overrides.get("ld")
    assert ld.flags.values == set(["LD0", "C3", "LD1"])
    assert ld.flags.remove_modifiers.values == set([]) 

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
    assert result.common_linker.flags.remove_modifiers.values == set([])

    # If the linker override is not specified in the child, it should be a copy of the parent
    # NOTE: The parent must already be extended before the child extends it, so that the child can get the correct values from the parent
    ld = result.linker_overrides.get("ld")
    assert ld.flags.values == set(["LD0", "C3", "LD1"])
    assert ld.flags.remove_modifiers.values == set([]) 

def create_common_only_1():
    # linkers:
    #   flags: [E0]
    #   add-flags: [E1, E3]
    #   remove-flags: [E1, E2]
    extends_common_flags = create_str_list(["E0"], ["E1", "E3"], ["E1", "E2"])
    extends_common_features = create_feature_str_list(True, ["EF0", "EF1", "EF3"], ["EF1", "EF2"])
    return create_linker_override_node(extends_common_flags, extends_common_features, None)

def create_common_only_2():
    # linkers:
    #   add-flags: [E1, E3]
    #   remove-flags: [E1, E2]
    extends_common_flags = create_str_list(False, ["E1", "E3"], ["E1", "E2"])
    extends_common_features = create_feature_str_list(False, ["EF1", "EF3"], ["EF1", "EF2"])
    return create_linker_override_node(extends_common_flags, extends_common_features,  None)

def test_common_only_1():
    # linkers:
    #   flags: [E0]
    #   add-flags: [E1, E3]
    #   remove-flags: [E1, E2]
    base_linker_node = create_common_only_1()

    # linkers:
    #   add-flags: [E0, E3] # E1 removed, E0 added
    #   remove-flags: [E1, E2] # Not changed
    extended_base_linker_node = base_linker_node.resolve_extends(None, {})

    # Validate result
    assert extended_base_linker_node.common_linker.flags.values == set(["E0", "E3"])
    assert extended_base_linker_node.common_linker.flags.remove_modifiers.values == set([])
    assert len(extended_base_linker_node.linker_overrides) == 0

def test_common_only_2():
    # linkers:
    #   add-flags: [E1, E3]
    #   remove-flags: [E1, E2]
    base_linker_node = create_common_only_2()

    # linkers:
    #   add-flags: [E3] # E1 removed
    #   remove-flags: [E1, E2] # Not changed
    extended_base_linker_node = base_linker_node.resolve_extends(None, {})

    # Validate result
    assert extended_base_linker_node.common_linker.flags.values == set(["E3"])
    assert extended_base_linker_node.common_linker.flags.remove_modifiers.values == set([])
    assert len(extended_base_linker_node.linker_overrides) == 0

def test_common_only_1_extends_1():
    #  linkers:
    #  add-flags: [C2]
    #  remove-flags: [C1, C3]
    #    ld:
    #      add-flags: [LD1, C3, LD2]
    #      remove-flags: [LD2] 
    base_linker_node = create_1()

    #  linkers: (Extended)
    #   add-flags: [C2] # C1 removed
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
    #   add-flags: [E0, E3] # E1 removed, E0 added
    #   remove-flags: [E1, E2] # Not changed
    #   ld:
    #     add-flags: [E0, E3] # E1 removed
    #     remove-flags: [E1, E2] # Not changed
    result = child_linker_node.resolve_extends(extended_base_linker_node, {})

    # Validate result
    assert result.common_linker.flags.values == set(["E0", "E3"])
    assert result.common_linker.flags.remove_modifiers.values == set([])
    # If the linker override is not specified in the child, it should be a copy of the parent
    # NOTE: The parent must already be extended before the child extends it, so that the child can get the correct values from the parent
    ld = result.linker_overrides.get("ld")
    assert ld.flags.values == set(["E0", "E3"])
    assert ld.flags.remove_modifiers.values == set([])

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
    #   add-flags: [C2] # C1 removed
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
    #   flags: [E0] # Not changed
    #   add-flags: [E3] # E1 removed
    #   remove-flags: [E1, E2] # Not changed
    #   ld:
    #     flags: [E0] # Not changed
    #     add-flags: [E3] # E1 removed
    #     remove-flags: [E1, E2] # Not changed
    result = child_linker_node.resolve_extends(extended_base_linker_node, {})
    
    # Validate result
    assert result.common_linker.flags.values == set(["E0", "E3"])
    assert result.common_linker.flags.remove_modifiers.values == set([])

    # If the linker override is not specified in the child, it should be a copy of the parent
    # NOTE: The parent must already be extended before the child extends it, so that the child can get the correct values from the parent
    ld = result.linker_overrides.get("ld")
    assert ld.flags.values == set(["E0", "E3"])
    assert ld.flags.remove_modifiers.values == set([])

def test_common_only_1_extends_3():
    #  linkers:
    #    add-flags: [C1, C2]
    #    remove-flags: [C1, C3]
    #      ld:
    #        flags: [LD0]
    #        add-flags: [LD1, C3, LD2]
    #        remove-flags: [LD2]
    base_linker_node = create_3()

    #  linkers: (Extended)
    #    add-flags: [C2] # C1 removed
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
    #   flags: [E0] # Not changed
    #   add-flags: [E3] # E1 removed
    #   remove-flags: [E1, E2] # Not changed
    #     ld:
    #       flags: [E0] # Not changed
    #       add-flags: [E3] # E1 removed
    #       remove-flags: [E1, E2] # Not changed
    result = child_linker_node.resolve_extends(extended_base_linker_node, {})

    # Validate result
    assert result.common_linker.flags.values == set(["E0", "E3"])
    assert result.common_linker.flags.remove_modifiers.values == set([])

    # If the linker override is not specified in the child, it should be a copy of the parent
    # NOTE: The parent must already be extended before the child extends it, so that the child can get the correct values from the parent
    ld = result.linker_overrides.get("ld")
    assert ld.flags.values == set(["E0", "E3"])
    assert ld.flags.remove_modifiers.values == set([])

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
    #   add-flags: [C2] # C1 removed
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
    #   flags: [E0] # Not changed
    #   add-flags: [E3] # E1 removed
    #   remove-flags: [E1, E2] # Not changed
    #     ld:
    #       flags: [E0] # Not changed
    #       add-flags: [E3] # E1 removed
    #       remove-flags: [E1, E2] # Not changed
    result = child_linker_node.resolve_extends(extended_base_linker_node, {})

    # Validate result
    assert result.common_linker.flags.values == set(["E0", "E3"])
    assert result.common_linker.flags.remove_modifiers.values == set([])

    # If the linker override is not specified in the child, it should be a copy of the parent
    # NOTE: The parent must already be extended before the child extends it, so that the child can get the correct values from the parent
    ld = result.linker_overrides.get("ld")
    assert ld.flags.values == set(["E0", "E3"])
    assert ld.flags.remove_modifiers.values == set([])

def test_common_only_2_extends_1():
    #  linkers:
    #  add-flags: [C1, C2]
    #  remove-flags: [C1, C3]
    #    ld:
    #      add-flags: [LD1, C3, LD2]
    #      remove-flags: [LD2] 
    base_linker_node = create_1()

    #  linkers: (Extended)
    #   add-flags: [C2] # C1 removed
    #   remove-flags: [C1, C3] # Not changed
    #   ld:
    #    add-flags: [LD1, C3, C2] # LD2 removed
    #    remove-flags: [LD2] # Not changed
    extended_base_linker_node = base_linker_node.resolve_extends(None, {})

    # child 'linkers:' extends extended_base_linker_node
    # linkers:
    #   add-flags: [E1, E3]
    #   remove-flags: [E1, E2]
    child_linker_node = create_common_only_2()

    # linkers: (Result)
    #   add-flags: [E3]
    #   remove-flags: [E1, E2]
    #   ld:
    #    add-flags: [E3, LD1, C3, C2] # E3 added
    #    remove-flags: [LD2] # Not changed
    result = child_linker_node.resolve_extends(extended_base_linker_node, {})

    # Validate result
    assert result.common_linker.flags.values == set(["E3"])
    assert result.common_linker.flags.remove_modifiers.values == set([])
    # If the linker override is not specified in the child, it should be a copy of the parent
    # NOTE: The parent must already be extended before the child extends it, so that the child can get the correct values from the parent
    ld = result.linker_overrides.get("ld")
    assert ld.flags.values == set(["E3", "C2", "C3", "LD1"])
    assert ld.flags.remove_modifiers.values == set([]) 

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
    #   add-flags: [C2] # C1 removed
    #   remove-flags: [C1, C3] # Not changed
    #   ld:
    #    add-flags: [LD1, C3, C2, C0] # C1 and LD2 removed
    #    remove-flags: [LD2] # Not changed
    extended_base_linker_node = base_linker_node.resolve_extends(None, {})

    # child 'linkers:' extends extended_base_linker_node
    # linkers:
    #   add-flags: [E1, E3]
    #   remove-flags: [E1, E2]
    child_linker_node = create_common_only_2()

    # linkers: (Result)
    #   add-flags: [E3] # E1 removed
    #   remove-flags: [E1, E2] # Not changed
    #   ld:
    #    add-flags: [E3, LD1, C3, C2, C0] # E3 added
    #    remove-flags: [LD2] # Not changed
    result = child_linker_node.resolve_extends(extended_base_linker_node, {})
    
    # Validate result
    assert result.common_linker.flags.values == set(["E3"])
    assert result.common_linker.flags.remove_modifiers.values == set([])

    # If the linker override is not specified in the child, it should be a copy of the parent
    # NOTE: The parent must already be extended before the child extends it, so that the child can get the correct values from the parent
    ld = result.linker_overrides.get("ld")
    assert ld.flags.values == set(["E3", "C0", "C2", "C3", "LD1"])
    assert ld.flags.remove_modifiers.values == set([]) 

def test_common_only_2_extends_3():
    #  linkers:
    #    add-flags: [C1, C2]
    #    remove-flags: [C1, C3]
    #      ld:
    #        flags: [LD0]
    #        add-flags: [LD1, C3, LD2]
    #        remove-flags: [LD2]
    base_linker_node = create_3()

    #  linkers: (Extended)
    #    add-flags: [C2] # C1 removed
    #    remove-flags: [C1, C3] # Not changed
    #      ld:
    #        flags: [LD0] # Not changed
    #        add-flags: [LD1, C3] # LD2 removed
    #        remove-flags: [LD2] # Not changed
    extended_base_linker_node = base_linker_node.resolve_extends(None, {})

    # child 'linkers:' extends extended_base_linker_node
    # linkers:
    #   add-flags: [E1, E3]
    #   remove-flags: [E1, E2]
    child_linker_node = create_common_only_2()

    # linkers: (Result)
    #   add-flags: [E3] # E1 removed
    #   remove-flags: [E1, E2] # Not changed
    #     ld:
    #       flags: [LD0] # Not changed
    #       add-flags: [E3, LD1, C3] # Not changed
    #       remove-flags: [LD2] # Not changed
    result = child_linker_node.resolve_extends(extended_base_linker_node, {})

    # Validate result
    assert result.common_linker.flags.values == set(["E3"])
    assert result.common_linker.flags.remove_modifiers.values == set([])

    # If the linker override is not specified in the child, it should be a copy of the parent
    # NOTE: The parent must already be extended before the child extends it, so that the child can get the correct values from the parent
    ld = result.linker_overrides.get("ld")
    assert ld.flags.values == set(["LD0", "E3", "C3", "LD1"])
    assert ld.flags.remove_modifiers.values == set([]) 

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
    #   add-flags: [C2] # C1 removed
    #   remove-flags: [C1, C3] # Not changed
    #   ld:
    #    flags: [LD0] # Not changed
    #    add-flags: [LD1, C3] # LD2 removed
    #    remove-flags: [LD2] # Not changed
    extended_base_linker_node = base_linker_node.resolve_extends(None, {})

    # child 'linkers:' extends extended_base_linker_node
    # linkers:
    #   add-flags: [E1, E3]
    #   remove-flags: [E1, E2]
    child_linker_node = create_common_only_2()

    # linkers: (Result)
    #   add-flags: [E3] # E1 removed
    #   remove-flags: [E1, E2]
    #     ld:
    #       flags: [LD0] # Not changed
    #       add-flags: [LD0, E3, LD1, C3] # Not changed
    #       remove-flags: [LD2] # Not changed
    result = child_linker_node.resolve_extends(extended_base_linker_node, {})

    # Validate result
    assert result.common_linker.flags.values == set(["E3"])
    assert result.common_linker.flags.remove_modifiers.values == set([])

    # If the linker override is not specified in the child, it should be a copy of the parent
    # NOTE: The parent must already be extended before the child extends it, so that the child can get the correct values from the parent
    ld = result.linker_overrides.get("ld")
    assert ld.flags.values == set(["E3", "LD0", "C3", "LD1"])
    assert ld.flags.remove_modifiers.values == set([]) 

def create_a():
    """
    linkers:
      add-flags: [AC1, AC3, AC4]
      remove-flags: [AC1, ALD1, AC2]
        ld:
          add-flags: [ALD1, ALD2, ALD3]
          remove-flags: [ALD2, AC4]
    """
    extends_common_flags = create_str_list([], ["AC1", "AC3", "AC4"], ["AC1", "ALD1", "AC2"])
    extends_common_features = create_feature_str_list(False, ["ACF1", "ACF3", "ACF4"], ["ACF1", "ALDF1", "ACF2"])
    extends_ld_flags = create_str_list([], ["ALD1", "ALD2", "ALD3"], ["ALD2", "AC4"])
    extends_ld_features = create_feature_str_list(False, ["ALDF1", "ALDF2", "ALDF3"], ["ALDF2", "ACF4"])
    ld_child_linker = create_specific_linker_override_node("ld", extends_ld_flags, extends_ld_features)
    return create_linker_override_node(extends_common_flags, extends_common_features, ld_child_linker)

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
    extends_common_flags = create_str_list(["AC0"], ["AC1", "AC3", "AC4"], ["AC1", "ALD1", "AC2"])
    extends_common_features = create_feature_str_list(True, ["ACF0", "ACF1", "ACF3", "ACF4"], ["ACF1", "ALDF1", "ACF2"])
    extends_ld_flags = create_str_list([], ["ALD1", "ALD2", "ALD3"], ["ALD2", "AC4"])
    extends_ld_features = create_feature_str_list(False, ["ALDF1", "ALDF2", "ALDF3"], ["ALDF2", "ACF4"])
    ld_child_linker = create_specific_linker_override_node("ld", extends_ld_flags, extends_ld_features)
    return create_linker_override_node(extends_common_flags, extends_common_features, ld_child_linker)

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
    extends_common_flags = create_str_list([], ["AC1", "AC3", "AC4"], ["AC1", "ALD1", "AC2"])
    extends_common_features = create_feature_str_list(False, ["ACF1", "ACF3", "ACF4"], ["ACF1", "ALDF1", "ACF2"])
    extends_ld_flags = create_str_list(["ALD0"], ["ALD1", "ALD2", "ALD3"], ["ALD2", "AC4"])
    extends_ld_features = create_feature_str_list(True, ["ALDF0" "ALDF1", "ALDF2", "ALDF3"], ["ALDF2", "ACF4"])
    ld_child_linker = create_specific_linker_override_node("ld", extends_ld_flags, extends_ld_features)
    return create_linker_override_node(extends_common_flags, extends_common_features, ld_child_linker)

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
    extends_common_flags = create_str_list(["AC0"], ["AC1", "AC3", "AC4"], ["AC1", "ALD1", "AC2"])
    extends_common_features = create_feature_str_list(True, ["ACF0", "ACF1", "ACF3", "ACF4"], ["ACF1", "ALDF1", "ACF2"])
    extends_ld_flags = create_str_list(["ALD0"], ["ALD1", "ALD2", "ALD3"], ["ALD2", "AC4"])
    extends_ld_features = create_feature_str_list(True, ["ALDF0", "ALDF1", "ALDF2", "ALDF3"], ["ALDF2", "ACF4"])
    ld_child_linker = create_specific_linker_override_node("ld", extends_ld_flags, extends_ld_features)
    return create_linker_override_node(extends_common_flags, extends_common_features, ld_child_linker)

def test_a_extends_1():
    #  linkers:
    #  add-flags: [C1, C2]
    #  remove-flags: [C1, C3]
    #    ld:
    #      add-flags: [LD1, C3, LD2]
    #      remove-flags: [LD2] 
    base_linker_node = create_1()

    #  linkers: (Extended)
    #   add-flags: [C2] # C1 removed
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
    #   add-flags: [AC3, AC4] # AC1 removed
    #   remove-flags: [AC1, ALD1, AC2] # Not changed
    #   ld:
    #    add-flags: [ALD1, LD1, C3, C2, ALD3, AC3]
    #    remove-flags: [ALD2, AC4] # Not changed
    result = child_linker_node.resolve_extends(extended_base_linker_node, {})

    # Validate result
    assert result.common_linker.flags.values == set(["AC3", "AC4"])
    assert result.common_linker.flags.remove_modifiers.values == set([])

    # If the linker override is not specified in the child, it should be a copy of the parent
    # NOTE: The parent must already be extended before the child extends it, so that the child can get the correct values from the parent
    ld = result.linker_overrides.get("ld")
    assert ld.flags.values == set(["ALD1", "LD1", "C3", "C2", "ALD3", "AC3"])
    assert ld.flags.remove_modifiers.values == set([]) 

def test_b_extends_1():
    #  linkers:
    #  add-flags: [C1, C2]
    #  remove-flags: [C1, C3]
    #    ld:
    #      add-flags: [LD1, C3, LD2]
    #      remove-flags: [LD2] 
    base_linker_node = create_1()

    #  linkers: (Extended)
    #   add-flags: [C2] # C1 removed
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
    #   add-flags: [AC3, AC4] # AC1 removed
    #   remove-flags: [AC1, ALD1, AC2] # Not changed
    #   ld:
    #    add-flags: [ALD1, ALD3, AC3, AC0]
    #    remove-flags: [ALD2, AC4] # Not changed
    result = child_linker_node.resolve_extends(extended_base_linker_node, {})

    # Validate result
    assert result.common_linker.flags.values == set(["AC0", "AC3", "AC4"])
    assert result.common_linker.flags.remove_modifiers.values == set([])

    # If the linker override is not specified in the child, it should be a copy of the parent
    # NOTE: The parent must already be extended before the child extends it, so that the child can get the correct values from the parent
    ld = result.linker_overrides.get("ld")
    assert ld.flags.values == set(["ALD1", "ALD3", "AC3", "AC0"])
    assert ld.flags.remove_modifiers.values == set([]) 

def test_c_extends_1():
    #  linkers:
    #  add-flags: [C1, C2]
    #  remove-flags: [C1, C3]
    #    ld:
    #      add-flags: [LD1, C3, LD2]
    #      remove-flags: [LD2] 
    base_linker_node = create_1()

    #  linkers: (Extended)
    #   add-flags: [C2] # C1 removed
    #   remove-flags: [C1, C3] # Not changed
    #   ld:
    #    add-flags: [LD1, C3, C2] # LD2 removed 
    #    remove-flags: [LD2] # Not changed
    extended_base_linker_node = base_linker_node.resolve_extends(None, {})

  
    # child 'linkers:' extends extended_base_linker_node
    # linkers:
    #   add-flags: [AC1, AC3, AC4]
    #   remove-flags: [AC1, ALD1, AC2]
    #   ld:
    #     flags: [ALD0]
    #     add-flags: [ALD1, ALD2, ALD3]
    #     remove-flags: [ALD2, AC4]
    child_linker_node = create_c()

    # child
    # linkers: (Extended)
    #   add-flags: [AC3, AC4] # AC1 removed
    #   remove-flags: [AC1, ALD1, AC2] # Not changed
    #   ld:
    #    flags: [ALD0] # Not changed
    #    add-flags: [ALD1, ALD3] # ALD2 Removed
    #    remove-flags: [ALD2, AC4] # Not changed
    result = child_linker_node.resolve_extends(extended_base_linker_node, {})

    # Validate result
    assert result.common_linker.flags.values == set(["AC3", "AC4"])
    assert result.common_linker.flags.remove_modifiers.values == set([])

    # If the linker override is not specified in the child, it should be a copy of the parent
    # NOTE: The parent must already be extended before the child extends it, so that the child can get the correct values from the parent
    ld = result.linker_overrides.get("ld")
    assert ld.flags.values == set(["ALD0", "ALD1", "ALD3"])
    assert ld.flags.remove_modifiers.values == set([]) 

def test_d_extends_1():
    #  linkers:
    #  add-flags: [C1, C2]
    #  remove-flags: [C1, C3]
    #    ld:
    #      add-flags: [LD1, C3, LD2]
    #      remove-flags: [LD2] 
    base_linker_node = create_1()

    #  linkers: (Extended)
    #   add-flags: [C2] # C1 removed
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
    #     flags: [ALD0]
    #     add-flags: [ALD1, ALD2, ALD3]
    #     remove-flags: [ALD2, AC4]
    child_linker_node = create_d()

    # child
    # linkers: (Extended)
    #   flags: [AC0] # Not changed
    #   add-flags: [AC3, AC4] # AC1 removed
    #   remove-flags: [AC1, ALD1, AC2] # Not changed
    #   ld:
    #    flags: [ALD0] # Not changed
    #    add-flags: [ALD1, ALD3] # ALD2 Removed
    #    remove-flags: [ALD2, AC4] # Not changed
    result = child_linker_node.resolve_extends(extended_base_linker_node, {})

    # Validate result
    assert result.common_linker.flags.values == set(["AC0", "AC3", "AC4"])
    assert result.common_linker.flags.remove_modifiers.values == set([])

    # If the linker override is not specified in the child, it should be a copy of the parent
    # NOTE: The parent must already be extended before the child extends it, so that the child can get the correct values from the parent
    ld = result.linker_overrides.get("ld")
    assert ld.flags.values == set(["ALD0", "ALD1", "ALD3"])
    assert ld.flags.remove_modifiers.values == set([]) 

def test_a_extends_2():
    #  linkers:
    #  flags: [C0]
    #  add-flags: [C1, C2]
    #  remove-flags: [C1, C3]
    #  ld:
    #    add-flags: [LD1, C3, LD2]
    #    remove-flags: [LD2]
    base_linker_node = create_2()

    #  linkers: (Extended)
    #   flags: [C0] # Not changed
    #   add-flags: [C2] # C1 removed
    #   remove-flags: [C1, C3] # Not changed
    #   ld:
    #    add-flags: [LD1, C3, C2, C0] # C1 and LD2 removed
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
    #   add-flags: [AC3, AC4] # AC1 removed
    #   remove-flags: [AC1, ALD1, AC2] # Not changed
    #   ld:
    #    add-flags: [ALD1, LD1, C3, C2, ALD3, AC3]
    #    remove-flags: [ALD2, AC4] # Not changed
    result = child_linker_node.resolve_extends(extended_base_linker_node, {})

    # Validate result
    assert result.common_linker.flags.values == set(["AC3", "AC4"])
    assert result.common_linker.flags.remove_modifiers.values == set([])

    # If the linker override is not specified in the child, it should be a copy of the parent
    # NOTE: The parent must already be extended before the child extends it, so that the child can get the correct values from the parent
    ld = result.linker_overrides.get("ld")
    assert ld.flags.values == set(["C0", "ALD1", "LD1", "C3", "C2", "ALD3", "AC3"])
    assert ld.flags.remove_modifiers.values == set([]) 

def test_b_extends_2():
    #  linkers:
    #  flags: [C0]
    #  add-flags: [C1, C2]
    #  remove-flags: [C1, C3]
    #  ld:
    #    add-flags: [LD1, C3, LD2]
    #    remove-flags: [LD2]
    base_linker_node = create_2()

    #  linkers: (Extended)
    #   add-flags: [C2] # C1 removed
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
    #   add-flags: [AC3, AC4] # AC1 removed
    #   remove-flags: [AC1, ALD1, AC2] # Not changed
    #   ld:
    #    add-flags: [ALD1, ALD3, AC3, AC0]
    #    remove-flags: [ALD2, AC4] # Not changed
    result = child_linker_node.resolve_extends(extended_base_linker_node, {})

    # Validate result
    assert result.common_linker.flags.values == set(["AC0", "AC3", "AC4"])
    assert result.common_linker.flags.remove_modifiers.values == set([])

    # If the linker override is not specified in the child, it should be a copy of the parent
    # NOTE: The parent must already be extended before the child extends it, so that the child can get the correct values from the parent
    ld = result.linker_overrides.get("ld")
    assert ld.flags.values == set(["ALD1", "ALD3", "AC3", "AC0"])
    assert ld.flags.remove_modifiers.values == set([]) 

def test_c_extends_2():
    #  linkers:
    #  flags: [C0]
    #  add-flags: [C1, C2]
    #  remove-flags: [C1, C3]
    #  ld:
    #    add-flags: [LD1, C3, LD2]
    #    remove-flags: [LD2]
    base_linker_node = create_2()

    #  linkers: (Extended)
    #   add-flags: [C2] # C1 removed
    #   remove-flags: [C1, C3] # Not changed
    #   ld:
    #    add-flags: [LD1, C3, C2] # LD2 removed 
    #    remove-flags: [LD2] # Not changed
    extended_base_linker_node = base_linker_node.resolve_extends(None, {})

  
    # child 'linkers:' extends extended_base_linker_node
    # linkers:
    #   add-flags: [AC1, AC3, AC4]
    #   remove-flags: [AC1, ALD1, AC2]
    #   ld:
    #     flags: [ALD0]
    #     add-flags: [ALD1, ALD2, ALD3]
    #     remove-flags: [ALD2, AC4]
    child_linker_node = create_c()

    # child
    # linkers: (Extended)
    #   add-flags: [AC3, AC4] # AC1 removed
    #   remove-flags: [AC1, ALD1, AC2] # Not changed
    #   ld:
    #    flags: [ALD0] # Not changed
    #    add-flags: [ALD1, ALD3] # ALD2 Removed
    #    remove-flags: [ALD2, AC4] # Not changed
    result = child_linker_node.resolve_extends(extended_base_linker_node, {})

    # Validate result
    assert result.common_linker.flags.values == set(["AC3", "AC4"])
    assert result.common_linker.flags.remove_modifiers.values == set([])

    # If the linker override is not specified in the child, it should be a copy of the parent
    # NOTE: The parent must already be extended before the child extends it, so that the child can get the correct values from the parent
    ld = result.linker_overrides.get("ld")
    assert ld.flags.values == set(["ALD0", "ALD1", "ALD3"])
    assert ld.flags.remove_modifiers.values == set([]) 

def test_d_extends_2():
    #  linkers:
    #  flags: [C0]
    #  add-flags: [C1, C2]
    #  remove-flags: [C1, C3]
    #  ld:
    #    add-flags: [LD1, C3, LD2]
    #    remove-flags: [LD2]
    base_linker_node = create_2()

    #  linkers: (Extended)
    #   add-flags: [C2] # C1 removed
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
    #     flags: [ALD0]
    #     add-flags: [ALD1, ALD2, ALD3]
    #     remove-flags: [ALD2, AC4]
    child_linker_node = create_d()

    # child
    # linkers: (Extended)
    #   flags: [AC0] # Not changed
    #   add-flags: [AC3, AC4] # AC1 removed
    #   remove-flags: [AC1, ALD1, AC2] # Not changed
    #   ld:
    #    flags: [ALD0] # Not changed
    #    add-flags: [ALD1, ALD3] # ALD2 Removed
    #    remove-flags: [ALD2, AC4] # Not changed
    result = child_linker_node.resolve_extends(extended_base_linker_node, {})

    # Validate result
    assert result.common_linker.flags.values == set(["AC0", "AC3", "AC4"])
    assert result.common_linker.flags.remove_modifiers.values == set([])

    # If the linker override is not specified in the child, it should be a copy of the parent
    # NOTE: The parent must already be extended before the child extends it, so that the child can get the correct values from the parent
    ld = result.linker_overrides.get("ld")
    assert ld.flags.values == set(["ALD0", "ALD1", "ALD3"])
    assert ld.flags.remove_modifiers.values == set([]) 

def test_a_extends_3():
    #  linkers:
    #    add-flags: [C1, C2]
    #    remove-flags: [C1, C3]
    #      ld:
    #        flags: [LD0]
    #        add-flags: [LD1, C3, LD2]
    #        remove-flags: [LD2]
    base_linker_node = create_3()

    #  linkers: (Extended)
    #    add-flags: [C2] # C1 removed
    #    remove-flags: [C1, C3] # Not changed
    #      ld:
    #        flags: [LD0] # Not changed
    #        add-flags: [LD1, C3] # LD2 removed
    #        remove-flags: [LD2] # Not changed
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
    #   add-flags: [AC3, AC4] # AC1 removed
    #   remove-flags: [AC1, ALD1, AC2] # Not changed
    #   ld:
    #    add-flags: [LD0, ALD1, LD1, C3, ALD3, AC3]
    #    remove-flags: [ALD2, AC4] # Not changed
    result = child_linker_node.resolve_extends(extended_base_linker_node, {})

    # Validate result
    assert result.common_linker.flags.values == set(["AC3", "AC4"])
    assert result.common_linker.flags.remove_modifiers.values == set([])

    # If the linker override is not specified in the child, it should be a copy of the parent
    # NOTE: The parent must already be extended before the child extends it, so that the child can get the correct values from the parent
    ld = result.linker_overrides.get("ld")
    assert ld.flags.values == set(["LD0", "ALD1", "LD1", "C3", "ALD3", "AC3"])
    assert ld.flags.remove_modifiers.values == set([]) 

def test_b_extends_3():
    #  linkers:
    #    add-flags: [C1, C2]
    #    remove-flags: [C1, C3]
    #      ld:
    #        flags: [LD0]
    #        add-flags: [LD1, C3, LD2]
    #        remove-flags: [LD2]
    base_linker_node = create_3()

    #  linkers: (Extended)
    #    add-flags: [C2] # C1 removed
    #    remove-flags: [C1, C3] # Not changed
    #      ld:
    #        flags: [LD0] # Not changed
    #        add-flags: [LD1, C3] # LD2 removed
    #        remove-flags: [LD2] # Not changed
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
    #   add-flags: [AC3, AC4] # AC1 removed
    #   remove-flags: [AC1, ALD1, AC2] # Not changed
    #   ld:
    #    add-flags: [ALD1, ALD3, AC3, AC0]
    #    remove-flags: [ALD2, AC4] # Not changed
    result = child_linker_node.resolve_extends(extended_base_linker_node, {})

    # Validate result
    assert result.common_linker.flags.values == set(["AC0", "AC3", "AC4"])
    assert result.common_linker.flags.remove_modifiers.values == set([])

    # If the linker override is not specified in the child, it should be a copy of the parent
    # NOTE: The parent must already be extended before the child extends it, so that the child can get the correct values from the parent
    ld = result.linker_overrides.get("ld")
    assert ld.flags.values == set(["ALD1", "ALD3", "AC3", "AC0"])
    assert ld.flags.remove_modifiers.values == set([]) 

def test_c_extends_3():
    #  linkers:
    #    add-flags: [C1, C2]
    #    remove-flags: [C1, C3]
    #      ld:
    #        flags: [LD0]
    #        add-flags: [LD1, C3, LD2]
    #        remove-flags: [LD2]
    base_linker_node = create_3()

    #  linkers: (Extended)
    #    add-flags: [C2] # C1 removed
    #    remove-flags: [C1, C3] # Not changed
    #      ld:
    #        flags: [LD0] # Not changed
    #        add-flags: [LD1, C3] # LD2 removed
    #        remove-flags: [LD2] # Not changed
    extended_base_linker_node = base_linker_node.resolve_extends(None, {})

  
    # child 'linkers:' extends extended_base_linker_node
    # linkers:
    #   add-flags: [AC1, AC3, AC4]
    #   remove-flags: [AC1, ALD1, AC2]
    #   ld:
    #     flags: [ALD0]
    #     add-flags: [ALD1, ALD2, ALD3]
    #     remove-flags: [ALD2, AC4]
    child_linker_node = create_c()

    # child
    # linkers: (Extended)
    #   add-flags: [AC3, AC4] # AC1 removed
    #   remove-flags: [AC1, ALD1, AC2] # Not changed
    #   ld:
    #    flags: [ALD0] # Not changed
    #    add-flags: [ALD1, ALD3] # ALD2 Removed
    #    remove-flags: [ALD2, AC4] # Not changed
    result = child_linker_node.resolve_extends(extended_base_linker_node, {})

    # Validate result
    assert result.common_linker.flags.values == set(["AC3", "AC4"])
    assert result.common_linker.flags.remove_modifiers.values == set([])

    # If the linker override is not specified in the child, it should be a copy of the parent
    # NOTE: The parent must already be extended before the child extends it, so that the child can get the correct values from the parent
    ld = result.linker_overrides.get("ld")
    assert ld.flags.values == set(["ALD0", "ALD1", "ALD3"])
    assert ld.flags.remove_modifiers.values == set([]) 

def test_d_extends_3():
    #  linkers:
    #    add-flags: [C1, C2]
    #    remove-flags: [C1, C3]
    #      ld:
    #        flags: [LD0]
    #        add-flags: [LD1, C3, LD2]
    #        remove-flags: [LD2]
    base_linker_node = create_3()

    #  linkers: (Extended)
    #    add-flags: [C2] # C1 removed
    #    remove-flags: [C1, C3] # Not changed
    #      ld:
    #        flags: [LD0] # Not changed
    #        add-flags: [LD1, C3] # LD2 removed
    #        remove-flags: [LD2] # Not changed
    extended_base_linker_node = base_linker_node.resolve_extends(None, {})
  
    # child 'linkers:' extends extended_base_linker_node
    # linkers:
    #   flags: [AC0]
    #   add-flags: [AC1, AC3, AC4]
    #   remove-flags: [AC1, ALD1, AC2]
    #   ld:
    #     flags: [ALD0]
    #     add-flags: [ALD1, ALD2, ALD3]
    #     remove-flags: [ALD2, AC4]
    child_linker_node = create_d()

    # child
    # linkers: (Extended)
    #   flags: [AC0] # Not changed
    #   add-flags: [AC3, AC4] # AC1 removed
    #   remove-flags: [AC1, ALD1, AC2] # Not changed
    #   ld:
    #    flags: [ALD0] # Not changed
    #    add-flags: [ALD1, ALD3] # ALD2 Removed
    #    remove-flags: [ALD2, AC4] # Not changed
    result = child_linker_node.resolve_extends(extended_base_linker_node, {})

    # Validate result
    assert result.common_linker.flags.values == set(["AC0", "AC3", "AC4"])
    assert result.common_linker.flags.remove_modifiers.values == set([])

    # If the linker override is not specified in the child, it should be a copy of the parent
    # NOTE: The parent must already be extended before the child extends it, so that the child can get the correct values from the parent
    ld = result.linker_overrides.get("ld")
    assert ld.flags.values == set(["ALD0", "ALD1", "ALD3"])
    assert ld.flags.remove_modifiers.values == set([]) 

def test_a_extends_4():
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
    #   add-flags: [C2] # C1 removed
    #   remove-flags: [C1, C3] # Not changed
    #   ld:
    #    flags: [LD0] # Not changed
    #    add-flags: [LD1, C3] # LD2 removed
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
    #   add-flags: [AC3, AC4] # AC1 removed
    #   remove-flags: [AC1, ALD1, AC2] # Not changed
    #   ld:
    #    add-flags: [LD0, ALD1, LD1, C3, ALD3, AC3]
    #    remove-flags: [ALD2, AC4] # Not changed
    result = child_linker_node.resolve_extends(extended_base_linker_node, {})

    # Validate result
    assert result.common_linker.flags.values == set(["AC3", "AC4"])
    assert result.common_linker.flags.remove_modifiers.values == set([])

    # If the linker override is not specified in the child, it should be a copy of the parent
    # NOTE: The parent must already be extended before the child extends it, so that the child can get the correct values from the parent
    ld = result.linker_overrides.get("ld")
    assert ld.flags.values == set(["LD0", "ALD1", "LD1", "C3", "ALD3", "AC3"])
    assert ld.flags.remove_modifiers.values == set([]) 

def test_b_extends_4():
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
    #   add-flags: [C2] # C1 removed
    #   remove-flags: [C1, C3] # Not changed
    #   ld:
    #    flags: [LD0] # Not changed
    #    add-flags: [LD1, C3] # LD2 removed
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
    #   add-flags: [AC3, AC4] # AC1 removed
    #   remove-flags: [AC1, ALD1, AC2] # Not changed
    #   ld:
    #    add-flags: [ALD1, ALD3, AC3, AC0]
    #    remove-flags: [ALD2, AC4] # Not changed
    result = child_linker_node.resolve_extends(extended_base_linker_node, {})

    # Validate result
    assert result.common_linker.flags.values == set(["AC0", "AC3", "AC4"])
    assert result.common_linker.flags.remove_modifiers.values == set([])

    # If the linker override is not specified in the child, it should be a copy of the parent
    # NOTE: The parent must already be extended before the child extends it, so that the child can get the correct values from the parent
    ld = result.linker_overrides.get("ld")
    assert ld.flags.values == set(["ALD1", "ALD3", "AC3", "AC0"])
    assert ld.flags.remove_modifiers.values == set([]) 

def test_c_extends_4():
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
    #   add-flags: [C2] # C1 removed
    #   remove-flags: [C1, C3] # Not changed
    #   ld:
    #    flags: [LD0] # Not changed
    #    add-flags: [LD1, C3] # LD2 removed
    #    remove-flags: [LD2] # Not changed
    extended_base_linker_node = base_linker_node.resolve_extends(None, {})
  
    # child 'linkers:' extends extended_base_linker_node
    # linkers:
    #   add-flags: [AC1, AC3, AC4]
    #   remove-flags: [AC1, ALD1, AC2]
    #   ld:
    #     flags: [ALD0]
    #     add-flags: [ALD1, ALD2, ALD3]
    #     remove-flags: [ALD2, AC4]
    child_linker_node = create_c()

    # child
    # linkers: (Extended)
    #   add-flags: [AC3, AC4] # AC1 removed
    #   remove-flags: [AC1, ALD1, AC2] # Not changed
    #   ld:
    #    flags: [ALD0] # Not changed
    #    add-flags: [ALD1, ALD3] # ALD2 Removed
    #    remove-flags: [ALD2, AC4] # Not changed
    result = child_linker_node.resolve_extends(extended_base_linker_node, {})

    # Validate result
    assert result.common_linker.flags.values == set(["AC3", "AC4"])
    assert result.common_linker.flags.remove_modifiers.values == set([])

    # If the linker override is not specified in the child, it should be a copy of the parent
    # NOTE: The parent must already be extended before the child extends it, so that the child can get the correct values from the parent
    ld = result.linker_overrides.get("ld")
    assert ld.flags.values == set(["ALD0", "ALD1", "ALD3"])
    assert ld.flags.remove_modifiers.values == set([]) 

def test_d_extends_4():
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
    #   add-flags: [C2] # C1 removed
    #   remove-flags: [C1, C3] # Not changed
    #   ld:
    #    flags: [LD0] # Not changed
    #    add-flags: [LD1, C3] # LD2 removed
    #    remove-flags: [LD2] # Not changed
    extended_base_linker_node = base_linker_node.resolve_extends(None, {})

    # child 'linkers:' extends extended_base_linker_node
    # linkers:
    #   flags: [AC0]
    #   add-flags: [AC1, AC3, AC4]
    #   remove-flags: [AC1, ALD1, AC2]
    #   ld:
    #     flags: [ALD0]
    #     add-flags: [ALD1, ALD2, ALD3]
    #     remove-flags: [ALD2, AC4]
    child_linker_node = create_d()

    # child
    # linkers: (Extended)
    #   flags: [AC0] # Not changed
    #   add-flags: [AC3, AC4] # AC1 removed
    #   remove-flags: [AC1, ALD1, AC2] # Not changed
    #   ld:
    #    flags: [ALD0] # Not changed
    #    add-flags: [ALD1, ALD3] # ALD2 Removed
    #    remove-flags: [ALD2, AC4] # Not changed
    result = child_linker_node.resolve_extends(extended_base_linker_node, {})

    # Validate result
    assert result.common_linker.flags.values == set(["AC0", "AC3", "AC4"])
    assert result.common_linker.flags.remove_modifiers.values == set([])

    # If the linker override is not specified in the child, it should be a copy of the parent
    # NOTE: The parent must already be extended before the child extends it, so that the child can get the correct values from the parent
    ld = result.linker_overrides.get("ld")
    assert ld.flags.values == set(["ALD0", "ALD1", "ALD3"])
    assert ld.flags.remove_modifiers.values == set([]) 

def test_a_extends_common_only_1():
    # linkers:
    #   flags: [E0]
    #   add-flags: [E1, E3]
    #   remove-flags: [E1, E2]
    base_linker_node = create_common_only_1()

    # linkers:
    #   flags: [E0] # Not changed
    #   add-flags: [E3] # E1 removed
    #   remove-flags: [E1, E2] # Not changed
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
    #   add-flags: [AC3, AC4] # AC1 removed
    #   remove-flags: [AC1, ALD1, AC2] # Not changed
    #   ld:
    #    add-flags: [E0, E3, ALD1, ALD2, ALD3]
    #    remove-flags: [ALD2, AC4] # Not changed
    result = child_linker_node.resolve_extends(extended_base_linker_node, {})

    # Validate result
    assert result.common_linker.flags.values == set(["AC3", "AC4"])
    assert result.common_linker.flags.remove_modifiers.values == set([])

    # If the linker override is not specified in the child, it should be a copy of the parent
    # NOTE: The parent must already be extended before the child extends it, so that the child can get the correct values from the parent
    ld = result.linker_overrides.get("ld")
    assert ld.flags.values == set(["E0", "E3", "AC3", "ALD1", "ALD3"])
    assert ld.flags.remove_modifiers.values == set([]) 

def test_b_extends_common_only_1():
    # linkers:
    #   flags: [E0]
    #   add-flags: [E1, E3]
    #   remove-flags: [E1, E2]
    base_linker_node = create_common_only_1()

    # linkers:
    #   flags: [E0] # Not changed
    #   add-flags: [E3] # E1 removed
    #   remove-flags: [E1, E2] # Not changed
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
    #   add-flags: [AC3, AC4] # AC1 removed
    #   remove-flags: [AC1, ALD1, AC2] # Not changed
    #   ld:
    #    add-flags: [ALD1, ALD3, AC3, AC0]
    #    remove-flags: [ALD2, AC4] # Not changed
    result = child_linker_node.resolve_extends(extended_base_linker_node, {})

    # Validate result
    assert result.common_linker.flags.values == set(["AC0", "AC3", "AC4"])
    assert result.common_linker.flags.remove_modifiers.values == set([])

    # If the linker override is not specified in the child, it should be a copy of the parent
    # NOTE: The parent must already be extended before the child extends it, so that the child can get the correct values from the parent
    ld = result.linker_overrides.get("ld")
    assert ld.flags.values == set(["ALD1", "ALD3", "AC3", "AC0"])
    assert ld.flags.remove_modifiers.values == set([]) 

def test_c_extends_common_only_1():
    # linkers:
    #   flags: [E0]
    #   add-flags: [E1, E3]
    #   remove-flags: [E1, E2]
    base_linker_node = create_common_only_1()

    # linkers:
    #   flags: [E0] # Not changed
    #   add-flags: [E3] # E1 removed
    #   remove-flags: [E1, E2] # Not changed
    extended_base_linker_node = base_linker_node.resolve_extends(None, {})

    # child 'linkers:' extends extended_base_linker_node
    # linkers:
    #   add-flags: [AC1, AC3, AC4]
    #   remove-flags: [AC1, ALD1, AC2]
    #   ld:
    #     flags: [ALD0]
    #     add-flags: [ALD1, ALD2, ALD3]
    #     remove-flags: [ALD2, AC4]
    child_linker_node = create_c()

    # child
    # linkers: (Extended)
    #   add-flags: [AC3, AC4] # AC1 removed
    #   remove-flags: [AC1, ALD1, AC2] # Not changed
    #   ld:
    #    flags: [ALD0] # Not changed
    #    add-flags: [ALD1, ALD3] # ALD2 Removed
    #    remove-flags: [ALD2, AC4] # Not changed
    result = child_linker_node.resolve_extends(extended_base_linker_node, {})

    # Validate result
    assert result.common_linker.flags.values == set(["AC3", "AC4"])
    assert result.common_linker.flags.remove_modifiers.values == set([])

    # If the linker override is not specified in the child, it should be a copy of the parent
    # NOTE: The parent must already be extended before the child extends it, so that the child can get the correct values from the parent
    ld = result.linker_overrides.get("ld")
    assert ld.flags.values == set(["ALD0", "ALD1", "ALD3"])
    assert ld.flags.remove_modifiers.values == set([]) 

def test_d_extends_common_only_1():
    # linkers:
    #   flags: [E0]
    #   add-flags: [E1, E3]
    #   remove-flags: [E1, E2]
    base_linker_node = create_common_only_1()

    # linkers:
    #   flags: [E0] # Not changed
    #   add-flags: [E3] # E1 removed
    #   remove-flags: [E1, E2] # Not changed
    extended_base_linker_node = base_linker_node.resolve_extends(None, {})

    # child 'linkers:' extends extended_base_linker_node
    # linkers:
    #   flags: [AC0]
    #   add-flags: [AC1, AC3, AC4]
    #   remove-flags: [AC1, ALD1, AC2]
    #   ld:
    #     flags: [ALD0]
    #     add-flags: [ALD1, ALD2, ALD3]
    #     remove-flags: [ALD2, AC4]
    child_linker_node = create_d()

    # child
    # linkers: (Extended)
    #   flags: [AC0] # Not changed
    #   add-flags: [AC3, AC4] # AC1 removed
    #   remove-flags: [AC1, ALD1, AC2] # Not changed
    #   ld:
    #    flags: [ALD0] # Not changed
    #    add-flags: [ALD1, ALD3] # ALD2 Removed
    #    remove-flags: [ALD2, AC4] # Not changed
    result = child_linker_node.resolve_extends(extended_base_linker_node, {})

    # Validate result
    assert result.common_linker.flags.values == set(["AC0", "AC3", "AC4"])
    assert result.common_linker.flags.remove_modifiers.values == set([])

    # If the linker override is not specified in the child, it should be a copy of the parent
    # NOTE: The parent must already be extended before the child extends it, so that the child can get the correct values from the parent
    ld = result.linker_overrides.get("ld")
    assert ld.flags.values == set(["ALD0", "ALD1", "ALD3"])
    assert ld.flags.remove_modifiers.values == set([]) 

def test_a_extends_common_only_2():
    # linkers:
    #   add-flags: [E1, E3]
    #   remove-flags: [E1, E2]
    base_linker_node = create_common_only_2()

    # linkers:
    #   add-flags: [E3] # E1 removed
    #   remove-flags: [E1, E2] # Not changed
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
    #   add-flags: [AC3, AC4] # AC1 removed
    #   remove-flags: [AC1, ALD1, AC2] # Not changed
    #   ld:
    #    add-flags: [E3, ALD1, ALD2, ALD3]
    #    remove-flags: [ALD2, AC4] # Not changed
    result = child_linker_node.resolve_extends(extended_base_linker_node, {})

    # Validate result
    assert result.common_linker.flags.values == set(["AC3", "AC4"])
    assert result.common_linker.flags.remove_modifiers.values == set([])

    # If the linker override is not specified in the child, it should be a copy of the parent
    # NOTE: The parent must already be extended before the child extends it, so that the child can get the correct values from the parent
    ld = result.linker_overrides.get("ld")
    assert ld.flags.values == set(["E3", "AC3", "ALD1", "ALD3"])
    assert ld.flags.remove_modifiers.values == set([]) 

def test_b_extends_common_only_2():
    # linkers:
    #   add-flags: [E1, E3]
    #   remove-flags: [E1, E2]
    base_linker_node = create_common_only_2()

    # linkers:
    #   add-flags: [E3] # E1 removed
    #   remove-flags: [E1, E2] # Not changed
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
    #   add-flags: [AC3, AC4] # AC1 removed
    #   remove-flags: [AC1, ALD1, AC2] # Not changed
    #   ld:
    #    add-flags: [ALD1, ALD3, AC3, AC0]
    #    remove-flags: [ALD2, AC4] # Not changed
    result = child_linker_node.resolve_extends(extended_base_linker_node, {})

    # Validate result
    assert result.common_linker.flags.values == set(["AC0", "AC3", "AC4"])
    assert result.common_linker.flags.remove_modifiers.values == set([])

    # If the linker override is not specified in the child, it should be a copy of the parent
    # NOTE: The parent must already be extended before the child extends it, so that the child can get the correct values from the parent
    ld = result.linker_overrides.get("ld")
    assert ld.flags.values == set(["ALD1", "ALD3", "AC3", "AC0"])
    assert ld.flags.remove_modifiers.values == set([]) 

def test_c_extends_common_only_2():
    # linkers:
    #   add-flags: [E1, E3]
    #   remove-flags: [E1, E2]
    base_linker_node = create_common_only_2()

    # linkers:
    #   add-flags: [E3] # E1 removed
    #   remove-flags: [E1, E2] # Not changed
    extended_base_linker_node = base_linker_node.resolve_extends(None, {})

    # child 'linkers:' extends extended_base_linker_node
    # linkers:
    #   add-flags: [AC1, AC3, AC4]
    #   remove-flags: [AC1, ALD1, AC2]
    #   ld:
    #     flags: [ALD0]
    #     add-flags: [ALD1, ALD2, ALD3]
    #     remove-flags: [ALD2, AC4]
    child_linker_node = create_c()

    # child
    # linkers: (Extended)
    #   add-flags: [AC3, AC4] # AC1 removed
    #   remove-flags: [AC1, ALD1, AC2] # Not changed
    #   ld:
    #    flags: [ALD0] # Not changed
    #    add-flags: [ALD1, ALD3] # ALD2 Removed
    #    remove-flags: [ALD2, AC4] # Not changed
    result = child_linker_node.resolve_extends(extended_base_linker_node, {})

    # Validate result
    assert result.common_linker.flags.values == set(["AC3", "AC4"])
    assert result.common_linker.flags.remove_modifiers.values == set([])

    # If the linker override is not specified in the child, it should be a copy of the parent
    # NOTE: The parent must already be extended before the child extends it, so that the child can get the correct values from the parent
    ld = result.linker_overrides.get("ld")
    assert ld.flags.values == set(["ALD0", "ALD1", "ALD3"])
    assert ld.flags.remove_modifiers.values == set([]) 

def test_d_extends_common_only_2():
    # linkers:
    #   add-flags: [E1, E3]
    #   remove-flags: [E1, E2]
    base_linker_node = create_common_only_2()

    # linkers:
    #   add-flags: [E3] # E1 removed
    #   remove-flags: [E1, E2] # Not changed
    extended_base_linker_node = base_linker_node.resolve_extends(None, {})

    # child 'linkers:' extends extended_base_linker_node
    # linkers:
    #   flags: [AC0]
    #   add-flags: [AC1, AC3, AC4]
    #   remove-flags: [AC1, ALD1, AC2]
    #   ld:
    #     flags: [ALD0]
    #     add-flags: [ALD1, ALD2, ALD3]
    #     remove-flags: [ALD2, AC4]
    child_linker_node = create_d()

    # child
    # linkers: (Extended)
    #   flags: [AC0] # Not changed
    #   add-flags: [AC3, AC4] # AC1 removed
    #   remove-flags: [AC1, ALD1, AC2] # Not changed
    #   ld:
    #    flags: [ALD0] # Not changed
    #    add-flags: [ALD1, ALD3] # ALD2 Removed
    #    remove-flags: [ALD2, AC4] # Not changed
    result = child_linker_node.resolve_extends(extended_base_linker_node, {})

    # Validate result
    assert result.common_linker.flags.values == set(["AC0", "AC3", "AC4"])
    assert result.common_linker.flags.remove_modifiers.values == set([])

    # If the linker override is not specified in the child, it should be a copy of the parent
    # NOTE: The parent must already be extended before the child extends it, so that the child can get the correct values from the parent
    ld = result.linker_overrides.get("ld")
    assert ld.flags.values == set(["ALD0", "ALD1", "ALD3"])
    assert ld.flags.remove_modifiers.values == set([]) 

def create_linker_only_1() : 
    # linkers:
    #   ld:
    #     flags: [LD0]
    #     add-flags: [LD1, LD3]
    #     remove-flags: [LD1, LD2]
    ld_flags = create_str_list(["LD0"], ["LD1", "LD3"], ["LD1", "LD2"])
    ld_features = create_str_list(["LDF0"], ["LDF1", "LDF3"], ["LDF1", "LDF2"])
    ld_linker = create_specific_linker_override_node("ld", ld_flags, ld_features)
    return create_linker_override_node(None, None, ld_linker)

def create_linker_only_2() : 
    # linkers:
    #   ld:
    #     add-flags: [LD1, LD3]
    #     remove-flags: [LD1, LD2]
    ld_flags = create_str_list([], ["LD1", "LD3"], ["LD1", "LD2"])
    ld_features = create_str_list([], ["LDF1", "LDF3"], ["LDF1", "LDF2"])
    ld_linker = create_specific_linker_override_node("ld", ld_flags, ld_features)
    return create_linker_override_node(None, None, ld_linker)

def test_linker_only_1():
    # linkers:
    #   ld:
    #     flags: [LD0]
    #     add-flags: [LD1, LD3]
    #     remove-flags: [LD1, LD2]
    base_linker_node = create_linker_only_1()

    # linkers:
    #   ld:
    #     flags: [LD0] # Not changed
    #     add-flags: [LD3] # LD1 removed
    #     remove-flags: [LD1, LD2] # Not changed
    extended_base_linker_node = base_linker_node.resolve_extends(None, {})

    # Validate result
    assert extended_base_linker_node.common_linker.flags.values == set([])
    assert extended_base_linker_node.common_linker.flags.remove_modifiers.values == set([])
    ld = extended_base_linker_node.linker_overrides.get("ld")
    assert ld.flags.values == set(["LD0", "LD3"])
    assert ld.flags.remove_modifiers.values == set([]) 

def test_linker_only_2():
    # linkers:
    #   ld:
    #     add-flags: [LD1, LD3]
    #     remove-flags: [LD1, LD2]
    base_linker_node = create_linker_only_2()

    # linkers:
    #   ld:
    #     add-flags: [LD3] # LD1 removed
    #     remove-flags: [LD1, LD2] # Not changed
    extended_base_linker_node = base_linker_node.resolve_extends(None, {})

    # Validate result
    assert extended_base_linker_node.common_linker.flags.values == set([])
    assert extended_base_linker_node.common_linker.flags.remove_modifiers.values == set([])
    ld = extended_base_linker_node.linker_overrides.get("ld")
    assert ld.flags.values == set(["LD3"])
    assert ld.flags.remove_modifiers.values == set([]) 

def test_linker_only_1_extends_common_only_1():
    # linkers:
    #   flags: [E0]
    #   add-flags: [E1, E3]
    #   remove-flags: [E1, E2]
    base_linker_node = create_common_only_1()

    # linkers:
    #   flags: [E0]
    #   add-flags: [E3] # E1 removed
    #   remove-flags: [E1, E2] # Not changed
    extended_base_linker_node = base_linker_node.resolve_extends(None, {})
    
    # child 'linkers:' extends extended_base_linker_node
    # linkers:
    #   ld:
    #     flags: [LD0]
    #     add-flags: [LD1, LD3]
    #     remove-flags: [LD1, LD2]
    child_linker_node = create_linker_only_1()

    # child
    # linkers: (Extended)
    #   ld:
    #     flags: [LD0] # Not changed
    #     add-flags: [LD3] # LD1 removed
    #     remove-flags: [LD1, LD2] # Not changed
    result = child_linker_node.resolve_extends(extended_base_linker_node, {})

    # Validate result
    assert result.common_linker.flags.values == set([])
    assert result.common_linker.flags.remove_modifiers.values == set([])
    ld = result.linker_overrides.get("ld")
    assert ld.flags.values == set(["LD0", "LD3"])
    assert ld.flags.remove_modifiers.values == set([]) 

def test_linker_only_1_extends_common_only_2():
    # linkers:
    #   add-flags: [E1, E3]
    #   remove-flags: [E1, E2]
    base_linker_node = create_common_only_2()

    # linkers:
    #   add-flags: [E3] # E1 removed
    #   remove-flags: [E1, E2] # Not changed
    extended_base_linker_node = base_linker_node.resolve_extends(None, {})
    
    # child 'linkers:' extends extended_base_linker_node
    # linkers:
    #   ld:
    #     flags: [LD0]
    #     add-flags: [LD1, LD3]
    #     remove-flags: [LD1, LD2]
    child_linker_node = create_linker_only_1()

    # child
    # linkers: (Extended)
    #   ld:
    #     flags: [LD0] # Not changed
    #     add-flags: [LD3] # LD1 removed
    #     remove-flags: [LD1, LD2] # Not changed
    result = child_linker_node.resolve_extends(extended_base_linker_node, {})

    # Validate result
    assert result.common_linker.flags.values == set([])
    assert result.common_linker.flags.remove_modifiers.values == set([])
    ld = result.linker_overrides.get("ld")
    assert ld.flags.values == set(["LD0", "LD3"])
    assert ld.flags.remove_modifiers.values == set([]) 

def test_linker_only_2_extends_common_only_1():
    # linkers:
    #   flags: [E0]
    #   add-flags: [E1, E3]
    #   remove-flags: [E1, E2]
    base_linker_node = create_common_only_1()

    # linkers:
    #   flags: [E0]
    #   add-flags: [E3] # E1 removed
    #   remove-flags: [E1, E2] # Not changed
    extended_base_linker_node = base_linker_node.resolve_extends(None, {})
    
    # child 'linkers:' extends extended_base_linker_node
    # linkers:
    #   ld:
    #     add-flags: [LD1, LD3]
    #     remove-flags: [LD1, LD2]
    child_linker_node = create_linker_only_2()

    # child
    # linkers: (Extended)
    #   ld:
    #     add-flags: [E0, E3, LD3] # LD1 removed, E0 E3 added
    #     remove-flags: [LD1, LD2] # Not changed
    result = child_linker_node.resolve_extends(extended_base_linker_node, {})

    # Validate result
    assert result.common_linker.flags.values == set([])
    assert result.common_linker.flags.remove_modifiers.values == set([])
    ld = result.linker_overrides.get("ld")
    assert ld.flags.values == set(["E0", "E3", "LD3"])
    assert ld.flags.remove_modifiers.values == set([]) 

def test_linker_only_2_extends_common_only_2():
    # linkers:
    #   add-flags: [E1, E3]
    #   remove-flags: [E1, E2]
    base_linker_node = create_common_only_2()

    # linkers:
    #   add-flags: [E3] # E1 removed
    #   remove-flags: [E1, E2] # Not changed
    extended_base_linker_node = base_linker_node.resolve_extends(None, {})
    
    # child 'linkers:' extends extended_base_linker_node
    # linkers:
    #   ld:
    #     add-flags: [LD1, LD3]
    #     remove-flags: [LD1, LD2]
    child_linker_node = create_linker_only_2()

    # child
    # linkers: (Extended)
    #   ld:
    #     add-flags: [E3, LD3] # LD1 removed, E3 added
    #     remove-flags: [LD1, LD2] # Not changed
    result = child_linker_node.resolve_extends(extended_base_linker_node, {})

    # Validate result
    assert result.common_linker.flags.values == set([])
    assert result.common_linker.flags.remove_modifiers.values == set([])
    ld = result.linker_overrides.get("ld")
    assert ld.flags.values == set(["E3", "LD3"])
    assert ld.flags.remove_modifiers.values == set([]) 

def test_common_only_1_extends_linker_only_1():
    # linkers:
    #   ld:
    #     flags: [LD0]
    #     add-flags: [LD1, LD3]
    #     remove-flags: [LD1, LD2]
    base_linker_node = create_linker_only_1()

    # linkers:
    #   ld:
    #     flags: [LD0] # Not changed
    #     add-flags: [LD3] # LD1 removed
    #     remove-flags: [LD1, LD2] # Not changed
    extended_base_linker_node = base_linker_node.resolve_extends(None, {})
    
    # child 'linkers:' extends extended_base_linker_node
    # linkers:
    #   flags: [E0]
    #   add-flags: [E1, E3]
    #   remove-flags: [E1, E2]
    child_linker_node = create_common_only_1()

    # child
    # linkers: (Extended)
    #   flags: [E0] # Not changed
    #   add-flags: [E3] # E1 removed
    #   remove-flags: [E1, E2] # Not changed
    #   ld:
    #     flags: [E0] # Not changed
    #     add-flags: [E3] # Not changed
    #     remove-flags: [E1, E2] # Not changed
    result = child_linker_node.resolve_extends(extended_base_linker_node, {})

    # Validate result
    assert result.common_linker.flags.values == set(["E0", "E3"])
    assert result.common_linker.flags.remove_modifiers.values == set([])
    ld = result.linker_overrides.get("ld")
    assert ld.flags.values == set(["E0", "E3"])
    assert ld.flags.remove_modifiers.values == set([]) 

def test_common_only_1_extends_linker_only_2():
    # linkers:
    #   ld:
    #     add-flags: [LD1, LD3]
    #     remove-flags: [LD1, LD2]
    base_linker_node = create_linker_only_2()

    # linkers:
    #   ld:
    #     add-flags: [LD3] # LD1 removed
    #     remove-flags: [LD1, LD2] # Not changed
    extended_base_linker_node = base_linker_node.resolve_extends(None, {})
    
    # child 'linkers:' extends extended_base_linker_node
    # linkers:
    #   flags: [E0]
    #   add-flags: [E1, E3]
    #   remove-flags: [E1, E2]
    child_linker_node = create_common_only_1()

    # child
    # linkers: (Extended)
    #   flags: [E0] # Not changed
    #   add-flags: [E3] # E1 removed
    #   remove-flags: [E1, E2] # Not changed
    #   ld:
    #     flags: [E0] # Not changed
    #     add-flags: [E3] # Not changed
    #     remove-flags: [E1, E2] # Not changed
    result = child_linker_node.resolve_extends(extended_base_linker_node, {})

    # Validate result
    assert result.common_linker.flags.values == set(["E0", "E3"])
    assert result.common_linker.flags.remove_modifiers.values == set([])
    ld = result.linker_overrides.get("ld")
    assert ld.flags.values == set(["E0", "E3"])
    assert ld.flags.remove_modifiers.values == set([]) 

def test_common_only_2_extends_linker_only_1():
    # linkers:
    #   ld:
    #     flags: [LD0]
    #     add-flags: [LD1, LD3]
    #     remove-flags: [LD1, LD2]
    base_linker_node = create_linker_only_1()

    # linkers:
    #   ld:
    #     flags: [LD0, LD3] # LD1 removed
    #     remove-flags: []
    extended_base_linker_node = base_linker_node.resolve_extends(None, {})
    
    # child 'linkers:' extends extended_base_linker_node
    # linkers:
    #   add-flags: [E1, E3]
    #   remove-flags: [E1, E2]
    child_linker_node = create_common_only_2()

    # child
    # linkers: (Extended)
    #   flags: [E3] # E1 removed
    #   remove-flags: []
    #   ld:
    #     flags: [LD0, LD3, E3] # Not changed
    #     remove-flags: []
    result = child_linker_node.resolve_extends(extended_base_linker_node, {})

    # Validate result
    assert result.common_linker.flags.values == set(["E3"])
    assert result.common_linker.flags.remove_modifiers.values == set([])
    ld = result.linker_overrides.get("ld")
    assert ld.flags.values == set(["LD0", "LD3", "E3"])
    assert ld.flags.remove_modifiers.values == set([]) 

def test_common_only_2_extends_linker_only_2():
    # linkers:
    #   ld:
    #     flags: [LD1, LD3]
    #     remove-flags: [LD1, LD2]
    base_linker_node = create_linker_only_2()

    # linkers:
    #   ld:
    #     flags: [LD3] # LD1 removed
    extended_base_linker_node = base_linker_node.resolve_extends(None, {})
    
    # child 'linkers:' extends extended_base_linker_node
    # linkers:
    #   add-flags: [E1, E3]
    #   remove-flags: [E1, E2]
    child_linker_node = create_common_only_2()

    # child
    # linkers: (Extended)
    #   flags: [E3]
    #   ld:
    #     add-flags: [LD3, E3]
    result = child_linker_node.resolve_extends(extended_base_linker_node, {})

    # Validate result
    assert result.common_linker.flags.values == set(["E3"])
    assert result.common_linker.flags.remove_modifiers.values == set([])
    ld = result.linker_overrides.get("ld")
    assert ld.flags.values == set(["LD3", "E3"])
    assert ld.flags.remove_modifiers.values == set([]) 

def test_extends_linker_override_node() :

    test_1()
    test_2()
    test_3()
    test_4()
    test_empty_extends_1()
    test_empty_extends_2()
    test_empty_extends_3()
    test_empty_extends_4()

    test_common_only_1()
    test_common_only_2()

    test_common_only_1_extends_1()
    test_common_only_1_extends_2()
    test_common_only_1_extends_3()
    test_common_only_1_extends_4()

    test_common_only_2_extends_1()
    test_common_only_2_extends_2()
    test_common_only_2_extends_3()
    test_common_only_2_extends_4()

    test_a_extends_1()
    test_b_extends_1()
    test_c_extends_1()
    test_d_extends_1()

    test_a_extends_2()
    test_b_extends_2()
    test_c_extends_2()
    test_d_extends_2()

    test_a_extends_3()
    test_b_extends_3()
    test_c_extends_3()
    test_d_extends_3()

    test_a_extends_4()
    test_b_extends_4()
    test_c_extends_4()
    test_d_extends_4()

    test_a_extends_common_only_1()
    test_b_extends_common_only_1()
    test_c_extends_common_only_1()
    test_d_extends_common_only_1()

    test_a_extends_common_only_2()
    test_b_extends_common_only_2()
    test_c_extends_common_only_2()
    test_d_extends_common_only_2()

    test_linker_only_1()
    test_linker_only_2()

    test_linker_only_1_extends_common_only_1()
    test_linker_only_1_extends_common_only_2()
    test_linker_only_2_extends_common_only_1()
    test_linker_only_2_extends_common_only_2()

    test_common_only_1_extends_linker_only_1()
    test_common_only_1_extends_linker_only_2()
    test_common_only_2_extends_linker_only_1()
    test_common_only_2_extends_linker_only_2()