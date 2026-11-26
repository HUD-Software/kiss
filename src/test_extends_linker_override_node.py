from test_common import create_feature_str_list, create_specific_linker_override_node, create_str_list, create_linker_override_node, create_linker_override_node_1
from toolchain.nodes.linker_nodes import LinkersOverrideNode


def create_2() -> LinkersOverrideNode:
    """
    linkers:
      flags: [C0, C1, C2] # Override = True
      remove-flags: [C1, C3]
      features: [CF0, CF1, CF2] # Override = True
      remove-features: [CF1, CF3]
      ld:
        flags: [LD1, C3, LD2] # Override = False
        remove-flags: [LD2]
        features: [LDF1, CF3, LDF2] # Override = False
        remove-features: [LDF2] 
    """
    common_flag = create_str_list(True, ["C0", "C1", "C2"], ["C1", "C3"])
    common_features = create_feature_str_list(True, ["CF0", "CF1", "CF2"], ["CF1", "CF3"])
    ld_flags = create_str_list(False, ["LD1", "C3", "LD2"], ["LD2"])
    ld_features = create_feature_str_list(False, ["LDF1", "CF3", "LDF2"], ["LDF2"])
    ld_linker = create_specific_linker_override_node("ld", ld_flags, ld_features)
    linker_override_node = create_linker_override_node(common_flag, common_features, ld_linker)

    assert linker_override_node.common_linker.flags.override == True
    assert linker_override_node.common_linker.flags.values == set(["C0","C1", "C2"])
    assert linker_override_node.common_linker.flags.remove_modifiers.values == set(["C1", "C3"])
    assert linker_override_node.common_linker.features.override == True
    assert linker_override_node.common_linker.features.values == set(["CF0", "CF1", "CF2"])
    assert linker_override_node.common_linker.features.remove_modifiers.values == set(["CF1", "CF3"])
    ld = linker_override_node.linker_overrides.get("ld")
    assert ld
    assert ld.flags.override == False
    assert ld.flags.values == set(["LD1", "C3", "LD2"])
    assert ld.flags.remove_modifiers.values == set(["LD2"]) 
    assert ld.features.override == False
    assert ld.features.values == set(["LDF1", "CF3", "LDF2"])
    assert ld.features.remove_modifiers.values == set(["LDF2"]) 
    return linker_override_node

def create_3() -> LinkersOverrideNode:
    """
    linkers:
      flags: [C1, C2] # Override = False
      remove-flags: [C1, C3]
      features: [CF1, CF2] # Override = False
      remove-features: [CF1, CF3]
        ld:
          flags: [LD0, LD1, C3, LD2] # Override = True
          remove-flags: [LD2]
          features: [LDF0, LDF1, CF3, LDF2]# Override = True
          remove-features: [LDF2]
    """
    common_flag = create_str_list(False, ["C1", "C2"], ["C1", "C3"])
    common_features = create_feature_str_list(False, ["CF1", "CF2"], ["CF1", "CF3"])
    ld_flags = create_str_list(True, ["LD0", "LD1", "C3", "LD2"], ["LD2"])
    ld_features = create_feature_str_list(True, ["LDF0", "LDF1", "CF3", "LDF2"], ["LDF2"])
    ld_linker = create_specific_linker_override_node("ld", ld_flags, ld_features)
    linker_override_node = create_linker_override_node(common_flag, common_features, ld_linker)
        
    assert linker_override_node.common_linker.flags.override == False
    assert linker_override_node.common_linker.flags.values == set(["C1", "C2"])
    assert linker_override_node.common_linker.flags.remove_modifiers.values == set(["C1", "C3"])
    assert linker_override_node.common_linker.features.override == False
    assert linker_override_node.common_linker.features.values == set(["CF1", "CF2"])
    assert linker_override_node.common_linker.features.remove_modifiers.values == set(["CF1", "CF3"])
    ld = linker_override_node.linker_overrides.get("ld")
    assert ld
    assert ld.flags.override == True
    assert ld.flags.values == set(["LD0", "LD1", "C3", "LD2"])
    assert ld.flags.remove_modifiers.values == set(["LD2"]) 
    assert ld.features.override == True
    assert ld.features.values == set(["LDF0","LDF1", "CF3", "LDF2"])
    assert ld.features.remove_modifiers.values == set(["LDF2"]) 
    return linker_override_node

def create_4() -> LinkersOverrideNode:
    """
    linkers:
      flags: [C0, C1, C2] # Override = True
      remove-flags: [C1, C3] 
      features: [CF0, CF1, CF2] # Override = True
      remove-features: [CF1, CF3]
      ld:
       flags: [LD0, LD1, C3, LD2] # Override = True
       remove-flags: [LD2]
       features: [LDF0, LDF1, CF3, LDF2] # Override = True
       remove-features: [LDF2]
    """
    common_flag = create_str_list(True, ["C0", "C1", "C2"], ["C1", "C3"])
    common_features = create_feature_str_list(True, ["CF0", "CF1", "CF2"], ["CF1", "CF3"])
    ld_flags = create_str_list(True, ["LD0", "LD1", "C3", "LD2"], ["LD2"])
    ld_features = create_feature_str_list(True, ["LDF0", "LDF1", "CF3", "LDF2"], ["LDF2"])
    ld_linker = create_specific_linker_override_node("ld", ld_flags, ld_features)
    linker_override_node = create_linker_override_node(common_flag, common_features, ld_linker)
        
    assert linker_override_node.common_linker.flags.override == True
    assert linker_override_node.common_linker.flags.values == set(["C0","C1", "C2"])
    assert linker_override_node.common_linker.flags.remove_modifiers.values == set(["C1", "C3"])
    assert linker_override_node.common_linker.features.override == True
    assert linker_override_node.common_linker.features.values == set(["CF0", "CF1", "CF2"])
    assert linker_override_node.common_linker.features.remove_modifiers.values == set(["CF1", "CF3"])
    ld = linker_override_node.linker_overrides.get("ld")
    assert ld
    assert ld.flags.override == True
    assert ld.flags.values == set(["LD0", "LD1", "C3", "LD2"])
    assert ld.flags.remove_modifiers.values == set(["LD2"]) 
    assert ld.features.override == True
    assert ld.features.values == set(["LDF0","LDF1", "CF3", "LDF2"])
    assert ld.features.remove_modifiers.values == set(["LDF2"]) 
    return linker_override_node

def test_1() :
    # linkers:
    #   flags: [C1, C2] # Override = False
    #   remove-flags: [C1, C3]
    #   features: [CF1, CF2] # Override = False
    #   remove-features: [CF1, CF3]
    #   ld:
    #     flags: [LD1, C3, LD2] # Override = False
    #     remove-flags: [LD2]
    #     features: [LDF1, CF3, LDF2] # Override = False
    #     remove-features: [LDF2]
    base_linker_node = create_linker_override_node_1()

    #  linkers: (Extended)
    #   flags: [C2] # Override = False
    #   remove-flags: [C1, C3]
    #   features: [CF2] # Override = False
    #   remove-features: [CF1, CF3]
    #   ld:
    #     flags: [C2, LD1, C3] # Override = False
    #     remove-flags: [LD2]
    #     features: [CF2, LDF1, CF3] # Override = False
    #     remove-features: [LDF2]
    extended_base_linker_node = base_linker_node.resolve_extends(None, {}).unwrap()

    # Validate result
    assert extended_base_linker_node.common_linker.flags.override == False
    assert extended_base_linker_node.common_linker.flags.values == set(["C2"])
    assert extended_base_linker_node.common_linker.flags.remove_modifiers.values == set(["C1", "C3"])
    assert extended_base_linker_node.common_linker.features.override == False
    assert extended_base_linker_node.common_linker.features.values == set(["CF2"])
    assert extended_base_linker_node.common_linker.features.remove_modifiers.values == set(["CF1", "CF3"])
    ld = extended_base_linker_node.linker_overrides.get("ld")
    assert ld
    assert ld.flags.override == False
    assert ld.flags.values == set(["C2", "C3", "LD1"])
    assert ld.flags.remove_modifiers.values == set(["LD2"]) 
    assert ld.features.override == False
    assert ld.features.values == set(["CF2", "CF3", "LDF1"])
    assert ld.features.remove_modifiers.values == set(["LDF2"]) 

def test_2() :
    # linkers:
    #   flags: [C0, C1, C2] # Override = True
    #   remove-flags: [C1, C3]
    #   features: [CF0, CF1, CF2] # Override = True
    #   remove-features: [CF1, CF3]
    #   ld:
    #     flags: [LD1, C3, LD2] # Override = False
    #     remove-flags: [LD2]
    #     features: [LDF1, CF3, LDF2] # Override = False
    #     remove-features: [LDF2]
    base_linker_node = create_2()

    #  linkers: (Extended)
    #   flags: [C0, C2] # Override = True
    #   remove-flags: [C1, C3]
    #   features: [CF0, CF2] # Override = True
    #   remove-features: [CF1, CF3]
    #   ld:
    #     flags: [LD1, C3, C0, C2] # Override = False
    #     remove-flags: [LD2]
    #     features: [CF0, CF2, LDF1, CF3] # Override = False
    #     remove-features: [LDF2]
    extended_base_linker_node = base_linker_node.resolve_extends(None, {}).unwrap()

    # Validate result
    assert extended_base_linker_node.common_linker.flags.override == True
    assert extended_base_linker_node.common_linker.flags.values == set(["C0", "C2"])
    assert extended_base_linker_node.common_linker.flags.remove_modifiers.values == set(["C1", "C3"])
    assert extended_base_linker_node.common_linker.features.override == True
    assert extended_base_linker_node.common_linker.features.values == set(["CF0", "CF2"])
    assert extended_base_linker_node.common_linker.features.remove_modifiers.values == set(["CF1", "CF3"])
    ld = extended_base_linker_node.linker_overrides.get("ld")
    assert ld
    assert ld.flags.override == False
    assert ld.flags.values == set(["C0", "C2", "C3", "LD1"])
    assert ld.flags.remove_modifiers.values == set(["LD2"]) 
    assert ld.features.override == False
    assert ld.features.values == set(["CF0", "CF2", "CF3", "LDF1"])
    assert ld.features.remove_modifiers.values == set(["LDF2"]) 

def test_3() :
    # linkers:
    #   flags: [C1, C2] # Override = False
    #   remove-flags: [C1, C3]
    #   features: [CF1, CF2] # Override = False
    #   remove-features: [CF1, CF3]
    #   ld:
    #     flags: [LD0, LD1, C3, LD2] # Override = True
    #     remove-flags: [LD2]
    #     features: [LDF0, LDF1, CF3, LDF2] # Override = True
    #     remove-features: [LDF2]
    base_linker_node = create_3()

    #  linkers: (Extended)
    #   flags: [C2] # Override = False
    #   remove-flags: [C1, C3]
    #   features: [CF2] # Override = False
    #   remove-features: [CF1, CF3]
    #   ld:
    #     flags: [LD0, LD1, C3] # Override = True
    #     remove-flags: [LD2]
    #     features: [LDF0, LDF1, CF3] # Override = True
    #     remove-features: [LDF2]
    extended_base_linker_node = base_linker_node.resolve_extends(None, {}).unwrap()

    # Validate result
    assert extended_base_linker_node.common_linker.flags.override == False
    assert extended_base_linker_node.common_linker.flags.values == set(["C2"])
    assert extended_base_linker_node.common_linker.flags.remove_modifiers.values == set(["C1", "C3"])
    assert extended_base_linker_node.common_linker.features.override == False
    assert extended_base_linker_node.common_linker.features.values == set(["CF2"])
    assert extended_base_linker_node.common_linker.features.remove_modifiers.values == set(["CF1", "CF3"])
    ld = extended_base_linker_node.linker_overrides.get("ld")
    assert ld
    assert ld.flags.override == True
    assert ld.flags.values == set(["LD0", "LD1", "C3"])
    assert ld.flags.remove_modifiers.values == set(["LD2"]) 
    assert ld.features.override == True
    assert ld.features.values == set(["LDF0", "LDF1", "CF3"])
    assert ld.features.remove_modifiers.values == set(["LDF2"]) 

def test_4() :
    # linkers:
    #   flags: [C0, C1, C2] # Override = True
    #   remove-flags: [C1, C3]
    #   features: [CF0, CF1, CF2] # Override = True
    #   remove-features: [CF1, CF3]
    #   ld:
    #     flags: [LD0, LD1, C3, LD2] # Override = True
    #     remove-flags: [LD2]
    #     features: [LDF0, LDF1, CF3, LDF2] # Override = True
    #     remove-features: [LDF2]
    base_linker_node = create_4()

    # linkers: (Extended)
    #   flags: [C0, C2] # Override = True
    #   remove-flags: [C1, C3]
    #   features: [CF0, CF2] # Override = True
    #   remove-features: [CF1, CF3]
    #   ld:
    #     flags: [LD0, LD1, C3] # Override = True
    #     remove-flags: [LD2]
    #     features: [LDF0, LDF1, CF3] # Override = True
    #     remove-features: [LDF2]
    extended_base_linker_node = base_linker_node.resolve_extends(None, {}).unwrap()

    # Validate result
    assert extended_base_linker_node.common_linker.flags.override == True
    assert extended_base_linker_node.common_linker.flags.values == set(["C0", "C2"])
    assert extended_base_linker_node.common_linker.flags.remove_modifiers.values == set(["C1", "C3"])
    assert extended_base_linker_node.common_linker.features.override == True
    assert extended_base_linker_node.common_linker.features.values == set(["CF0", "CF2"])
    assert extended_base_linker_node.common_linker.features.remove_modifiers.values == set(["CF1", "CF3"])
    ld = extended_base_linker_node.linker_overrides.get("ld")
    assert ld
    assert ld.flags.override == True
    assert ld.flags.values == set(["LD0", "LD1", "C3"])
    assert ld.flags.remove_modifiers.values == set(["LD2"]) 
    assert ld.features.override == True
    assert ld.features.values == set(["LDF0", "LDF1", "CF3"])
    assert ld.features.remove_modifiers.values == set(["LDF2"]) 

def test_empty_extends_1():
    # linkers:
    #   flags: [C1, C2] # Override = False
    #   remove-flags: [C1, C3]
    #   features: [CF1, CF2] # Override = False
    #   remove-features: [CF1, CF3]
    #   ld:
    #     flags: [LD1, C3, LD2] # Override = False
    #     remove-flags: [LD2]
    #     features: [LDF1, CF3, LDF2] # Override = False
    #     remove-features: [LDF2]
    base_linker_node = create_linker_override_node_1()

    #  linkers: (Extended)
    #   flags: [C2] # Override = False
    #   remove-flags: [C1, C3]
    #   features: [CF2] # Override = False
    #   remove-features: [CF1, CF3]
    #   ld:
    #     flags: [C2, LD1, C3] # Override = False
    #     remove-flags: [LD2]
    #     features: [CF2, LDF1, CF3] # Override = False
    #     remove-features: [LDF2]
    extended_base_linker_node = base_linker_node.resolve_extends(None, {}).unwrap()
    
    # child 'linkers:' extends extended_base_linker_node
    #   flags: [] # Override = False
    #   remove-flags: []
    #   features: [] # Override = False
    #   remove-features: []
    #   ld:
    #     flags: [] # Override = False
    #     remove-flags: []
    #     features: [] # Override = False
    #     remove-features: []
    result = LinkersOverrideNode().resolve_extends(extended_base_linker_node, {}).unwrap()

    # Validate result
    assert result.common_linker.flags.override == False
    assert result.common_linker.flags.values == set([])
    assert result.common_linker.flags.remove_modifiers.values == set([])
    assert result.common_linker.features.override == False
    assert result.common_linker.features.values == set([])
    assert result.common_linker.features.remove_modifiers.values == set([])
    ld = result.linker_overrides.get("ld")
    assert ld
    assert ld.flags.override == False
    assert ld.flags.values == set(["C2", "C3", "LD1"])
    assert ld.flags.remove_modifiers.values == set(["LD2"]) 
    assert ld.features.override == False
    assert ld.features.values == set(["CF2", "CF3", "LDF1"])
    assert ld.features.remove_modifiers.values == set(["LDF2"]) 

def test_empty_extends_2():
    # linkers:
    #   flags: [C0, C1, C2] # Override = True
    #   remove-flags: [C1, C3]
    #   features: [CF0, CF1, CF2] # Override = True
    #   remove-features: [CF1, CF3]
    #   ld:
    #     flags: [LD1, C3, LD2] # Override = False
    #     remove-flags: [LD2]
    #     features: [LDF1, CF3, LDF2] # Override = False
    #     remove-features: [LDF2]
    base_linker_node = create_2()

    #  linkers: (Extended)
    #   flags: [C0, C2] # Override = True
    #   remove-flags: [C1, C3]
    #   features: [CF0, CF2] # Override = True
    #   remove-features: [CF1, CF3]
    #   ld:
    #     flags: [LD1, C3, C0, C2] # Override = False
    #     remove-flags: [LD2]
    #     features: [CF0, CF2, LDF1, CF3] # Override = False
    #     remove-features: [LDF2]
    extended_base_linker_node = base_linker_node.resolve_extends(None, {}).unwrap()

    # child 'linkers:' extends extended_base_linker_node
    #   flags: [] # Override = False
    #   remove-flags: []
    #   features: [] # Override = False
    #   remove-features: []
    #   ld:
    #     flags: [] # Override = False
    #     remove-flags: []
    #     features: [] # Override = False
    #     remove-features: []
    result = LinkersOverrideNode().resolve_extends(extended_base_linker_node, {}).unwrap()

    # Validate result
    assert result.common_linker.flags.override == False
    assert result.common_linker.flags.values == set([])
    assert result.common_linker.flags.remove_modifiers.values == set([])
    assert result.common_linker.features.override == False
    assert result.common_linker.features.values == set([])
    assert result.common_linker.features.remove_modifiers.values == set([])
    ld = result.linker_overrides.get("ld")
    assert ld
    assert ld.flags.override == False
    assert ld.flags.values == set(["LD1", "C3", "C0", "C2"])
    assert ld.flags.remove_modifiers.values == set(["LD2"]) 
    assert ld.features.override == False
    assert ld.features.values == set(["CF0", "CF2", "LDF1", "CF3"])
    assert ld.features.remove_modifiers.values == set(["LDF2"]) 

def test_empty_extends_3():
    # linkers:
    #   flags: [C1, C2] # Override = False
    #   remove-flags: [C1, C3]
    #   features: [CF1, CF2] # Override = False
    #   remove-features: [CF1, CF3]
    #   ld:
    #     flags: [LD0, LD1, C3, LD2] # Override = True
    #     remove-flags: [LD2]
    #     features: [LDF0, LDF1, CF3, LDF2] # Override = True
    #     remove-features: [LDF2]
    base_linker_node = create_3()

    #  linkers: (Extended)
    #   flags: [C2] # Override = False
    #   remove-flags: [C1, C3]
    #   features: [CF2] # Override = False
    #   remove-features: [CF1, CF3]
    #   ld:
    #     flags: [LD0, LD1, C3] # Override = True
    #     remove-flags: [LD2]
    #     features: [LDF0, LDF1, CF3] # Override = True
    #     remove-features: [LDF2]
    extended_base_linker_node = base_linker_node.resolve_extends(None, {}).unwrap()

    # child 'linkers:' extends extended_base_linker_node
    #   flags: [] # Override = False
    #   remove-flags: []
    #   features: [] # Override = False
    #   remove-features: []
    #   ld:
    #     flags: [] # Override = False
    #     remove-flags: []
    #     features: [] # Override = False
    #     remove-features: []
    result = LinkersOverrideNode().resolve_extends(extended_base_linker_node, {}).unwrap()

    # Validate result
    assert result.common_linker.flags.override == False
    assert result.common_linker.flags.values == set([])
    assert result.common_linker.flags.remove_modifiers.values == set([])
    assert result.common_linker.features.override == False
    assert result.common_linker.features.values == set([])
    assert result.common_linker.features.remove_modifiers.values == set([])
    ld = result.linker_overrides.get("ld")
    assert ld
    assert ld.flags.override == False
    assert ld.flags.values == set(["LD0", "LD1", "C3"])
    assert ld.flags.remove_modifiers.values == set(["LD2"]) 
    assert ld.features.override == False
    assert ld.features.values == set(["LDF0", "LDF1", "CF3"])
    assert ld.features.remove_modifiers.values == set(["LDF2"]) 

def test_empty_extends_4():
    # linkers:
    #   flags: [C0, C1, C2] # Override = True
    #   remove-flags: [C1, C3]
    #   features: [CF0, CF1, CF2] # Override = True
    #   remove-features: [CF1, CF3]
    #   ld:
    #     flags: [LD0, LD1, C3, LD2] # Override = True
    #     remove-flags: [LD2]
    #     features: [LDF0, LDF1, CF3, LDF2] # Override = True
    #     remove-features: [LDF2]
    base_linker_node = create_4()

    # linkers: (Extended)
    #   flags: [C0, C2] # Override = True
    #   remove-flags: []
    #   features: [CF0, CF2] # Override = True
    #   remove-features: []
    #   ld:
    #     flags: [LD0, LD1, C3] # Override = True
    #     remove-flags: [LD2]
    #     features: [LDF0, LDF1, CF3] # Override = True
    #     remove-features: [LDF2]
    extended_base_linker_node = base_linker_node.resolve_extends(None, {}).unwrap()

    # child 'linkers:' extends extended_base_linker_node
    #   flags: [] # Override = False
    #   remove-flags: []
    #   features: [] # Override = False
    #   remove-features: []
    #   ld:
    #     flags: [] # Override = False
    #     remove-flags: []
    #     features: [] # Override = False
    #     remove-features: []
    result = LinkersOverrideNode().resolve_extends(extended_base_linker_node, {}).unwrap()

    # Validate result
    assert result.common_linker.flags.override == False
    assert result.common_linker.flags.values == set([])
    assert result.common_linker.flags.remove_modifiers.values == set([])
    assert result.common_linker.features.override == False
    assert result.common_linker.features.values == set([])
    assert result.common_linker.features.remove_modifiers.values == set([])
    ld = result.linker_overrides.get("ld")
    assert ld
    assert ld.flags.override == False
    assert ld.flags.values == set(["LD0", "LD1", "C3"])
    assert ld.flags.remove_modifiers.values == set(["LD2"]) 
    assert ld.features.override == False
    assert ld.features.values == set(["LDF0", "LDF1", "CF3"])
    assert ld.features.remove_modifiers.values == set(["LDF2"]) 

def create_common_only_1():
    """
    linkers:
      flags: [E0, E1, E3] # Override = True
      remove-flags: [E1, E2]
      features: [EF0, EF1, EF3] # Override = True
      remove-features: [EF1, EF2]
    """
    extends_common_flags = create_str_list(True, ["E0", "E1", "E3"], ["E1", "E2"])
    extends_common_features = create_feature_str_list(True, ["EF0", "EF1", "EF3"], ["EF1", "EF2"])
    linker_override_node = create_linker_override_node(extends_common_flags, extends_common_features, None)
    assert linker_override_node.common_linker.flags.override == True
    assert linker_override_node.common_linker.flags.values == set(["E0","E1", "E3"])
    assert linker_override_node.common_linker.flags.remove_modifiers.values == set(["E1", "E2"])
    assert linker_override_node.common_linker.features.override == True
    assert linker_override_node.common_linker.features.values == set(["EF0", "EF1", "EF3"])
    assert linker_override_node.common_linker.features.remove_modifiers.values == set(["EF1", "EF2"])
    assert len(linker_override_node.linker_overrides) == 0
    return linker_override_node

def create_common_only_2():
    """
    linkers:
      flags: [E1, E3] # Override = False
      remove-flags: [E1, E2]
      features: [EF1, EF3] # Override = False
      remove-features: [EF1, EF2]
    """
    extends_common_flags = create_str_list(False, ["E1", "E3"], ["E1", "E2"])
    extends_common_features = create_feature_str_list(False, ["EF1", "EF3"], ["EF1", "EF2"])
    linker_override_node = create_linker_override_node(extends_common_flags, extends_common_features, None)
    assert linker_override_node.common_linker.flags.override == False
    assert linker_override_node.common_linker.flags.values == set(["E1", "E3"])
    assert linker_override_node.common_linker.flags.remove_modifiers.values == set(["E1", "E2"])
    assert linker_override_node.common_linker.features.override == False
    assert linker_override_node.common_linker.features.values == set(["EF1", "EF3"])
    assert linker_override_node.common_linker.features.remove_modifiers.values == set(["EF1", "EF2"])
    assert len(linker_override_node.linker_overrides) == 0
    return linker_override_node

def test_common_only_1():
    # linkers:
    #   flags: [E0, E1, E3] # Override = True
    #   remove-flags: [E1, E2]
    #   features: [EF0, EF1, EF3] # Override = True
    #   remove-features: [EF1, EF2]
    base_linker_node = create_common_only_1()

    # linkers:
    #   flags: [E0, E3] # Override = True
    #   remove-flags: [E1, E2]
    #   features: [EF0, EF3] # Override = True
    #   remove-features: [EF1, EF2]
    extended_base_linker_node = base_linker_node.resolve_extends(None, {}).unwrap()

    # Validate result
    assert extended_base_linker_node.common_linker.flags.override == True
    assert extended_base_linker_node.common_linker.flags.values == set(["E0", "E3"])
    assert extended_base_linker_node.common_linker.flags.remove_modifiers.values == set(["E1", "E2"])
    assert extended_base_linker_node.common_linker.features.override == True
    assert extended_base_linker_node.common_linker.features.values == set(["EF0", "EF3"])
    assert extended_base_linker_node.common_linker.features.remove_modifiers.values == set(["EF1", "EF2"])
    assert len(extended_base_linker_node.linker_overrides) == 0

def test_common_only_2():
    # linkers:
    #   flags: [E1, E3] # Override = False
    #   remove-flags: [E1, E2]
    #   features: [EF1, EF3] # Override = False
    #   remove-features: [EF1, EF2]
    base_linker_node = create_common_only_2()

    # linkers:
    #   flags: [E3] # Override = False
    #   remove-flags: [E1, E2]
    #   features: [EF3] # Override = False
    #   remove-features: [EF1, EF2]
    extended_base_linker_node = base_linker_node.resolve_extends(None, {}).unwrap()

    # Validate result
    assert extended_base_linker_node.common_linker.flags.override == False
    assert extended_base_linker_node.common_linker.flags.values == set(["E3"])
    assert extended_base_linker_node.common_linker.flags.remove_modifiers.values == set(["E1", "E2"])
    assert extended_base_linker_node.common_linker.features.override == False
    assert extended_base_linker_node.common_linker.features.values == set(["EF3"])
    assert extended_base_linker_node.common_linker.features.remove_modifiers.values == set(["EF1", "EF2"])
    assert len(extended_base_linker_node.linker_overrides) == 0

def test_common_only_1_extends_1():
    # linkers:
    #   flags: [C1, C2] # Override = False
    #   remove-flags: [C1, C3]
    #   features: [CF1, CF2] # Override = False
    #   remove-features: [CF1, CF3]
    #   ld:
    #     flags: [LD1, C3, LD2] # Override = False
    #     remove-flags: [LD2]
    #     features: [LDF1, CF3, LDF2] # Override = False
    #     remove-features: [LDF2]
    base_linker_node = create_linker_override_node_1()

    #  linkers: (Extended)
    #   flags: [C2] # Override = False
    #   remove-flags: [C1, C3]
    #   features: [CF2] # Override = False
    #   remove-features: [CF1, CF3]
    #   ld:
    #     flags: [C2, LD1, C3] # Override = False
    #     remove-flags: [LD2]
    #     features: [CF2, LDF1, CF3] # Override = False
    #     remove-features: [LDF2]
    extended_base_linker_node = base_linker_node.resolve_extends(None, {}).unwrap()

    # child 'linkers:' extends extended_base_linker_node
    # linkers:
    #   flags: [E0, E1, E3] # Override = True
    #   remove-flags: [E1, E2]
    #   features: [EF0, EF1, EF3] # Override = True
    #   remove-features: [EF1, EF2]
    child_linker_node = create_common_only_1()

    # linkers: (Result)
    #   flags: [E0, E3] # Override = True
    #   remove-flags: [E1, E2]
    #   features: [EF0, EF3] # Override = True
    #   remove-features: [EF1, EF2]
    #   ld:
    #     flags: [E0, E3] # Override = False
    #     remove-flags: [LD2]
    #     features: [EF0, EF3] # Override = False
    #     remove-features: [LDF2]
    result = child_linker_node.resolve_extends(extended_base_linker_node, {}).unwrap()

    # Validate result
    assert result.common_linker.flags.override == True
    assert result.common_linker.flags.values == set(["E0", "E3"])
    assert result.common_linker.flags.remove_modifiers.values == set(["E1", "E2"])
    assert result.common_linker.features.override == True
    assert result.common_linker.features.values == set(["EF0", "EF3"])
    assert result.common_linker.features.remove_modifiers.values == set(["EF1", "EF2"])
    ld = result.linker_overrides.get("ld")
    assert ld
    assert ld.flags.override == False
    assert ld.flags.values == set(["E0", "E3"])
    assert ld.flags.remove_modifiers.values == set(["LD2"]) 
    assert ld.features.override == False
    assert ld.features.values == set(["EF0", "EF3"])
    assert ld.features.remove_modifiers.values == set(["LDF2"]) 

def test_common_only_1_extends_2():
    # linkers:
    #   flags: [C0, C1, C2] # Override = True
    #   remove-flags: [C1, C3]
    #   features: [CF0, CF1, CF2] # Override = True
    #   remove-features: [CF1, CF3]
    #   ld:
    #     flags: [LD1, C3, LD2] # Override = False
    #     remove-flags: [LD2]
    #     features: [LDF1, CF3, LDF2] # Override = False
    #     remove-features: [LDF2]
    base_linker_node = create_2()

    #  linkers: (Extended)
    #   flags: [C0, C2] # Override = True
    #   remove-flags: [C1, C3]
    #   features: [CF0, CF2] # Override = True
    #   remove-features: [CF1, CF3]
    #   ld:
    #     flags: [LD1, C3, C0, C2] # Override = False
    #     remove-flags: [LD2]
    #     features: [CF0, CF2, LDF1, CF3] # Override = False
    #     remove-features: [LDF2]
    extended_base_linker_node = base_linker_node.resolve_extends(None, {}).unwrap()

    # child 'linkers:' extends extended_base_linker_node
    # linkers:
    #   flags: [E0, E1, E3] # Override = True
    #   remove-flags: [E1, E2]
    #   features: [EF0, EF1, EF3] # Override = True
    #   remove-features: [EF1, EF2]
    child_linker_node = create_common_only_1()

    # linkers: (Result)
    #   flags: [E0, E3] # Override = False
    #   remove-flags: [E1, E2]
    #   features: [EF0, EF3] # Override = False
    #   remove-features: [EF1, EF2]
    #   ld:
    #     flags: [E0, E3] # Override = True
    #     remove-flags: [LD2]
    #     features: [EF0, EF3] # Override = True
    #     remove-features: [LDF2]
    result = child_linker_node.resolve_extends(extended_base_linker_node, {}).unwrap()
    
    # Validate result
    assert result.common_linker.flags.override == True
    assert result.common_linker.flags.values == set(["E0", "E3"])
    assert result.common_linker.flags.remove_modifiers.values == set(["E1", "E2"])
    assert result.common_linker.features.override == True
    assert result.common_linker.features.values == set(["EF0", "EF3"])
    assert result.common_linker.features.remove_modifiers.values == set(["EF1", "EF2"])
    ld = result.linker_overrides.get("ld")
    assert ld
    assert ld.flags.override == False
    assert ld.flags.values == set(["E0", "E3"])
    assert ld.flags.remove_modifiers.values == set(["LD2"]) 
    assert ld.features.override == False
    assert ld.features.values == set(["EF0", "EF3"])
    assert ld.features.remove_modifiers.values == set(["LDF2"]) 

def test_common_only_1_extends_3():
    # linkers:
    #   flags: [C1, C2] # Override = False
    #   remove-flags: [C1, C3]
    #   features: [CF1, CF2] # Override = False
    #   remove-features: [CF1, CF3]
    #   ld:
    #     flags: [LD0, LD1, C3, LD2] # Override = True
    #     remove-flags: [LD2]
    #     features: [LDF0, LDF1, CF3, LDF2] # Override = True
    #     remove-features: [LDF2]
    base_linker_node = create_3()

    #  linkers: (Extended)
    #   flags: [C2] # Override = False
    #   remove-flags: [C1, C3]
    #   features: [CF2] # Override = False
    #   remove-features: [CF1, CF3]
    #   ld:
    #     flags: [LD0, LD1, C3] # Override = True
    #     remove-flags: [LD2]
    #     features: [LDF0, LDF1, CF3] # Override = True
    #     remove-features: [LDF2]
    extended_base_linker_node = base_linker_node.resolve_extends(None, {}).unwrap()

    # child 'linkers:' extends extended_base_linker_node
    # linkers:
    #   flags: [E0, E1, E3] # Override = True
    #   remove-flags: [E1, E2]
    #   features: [EF0, EF1, EF3] # Override = True
    #   remove-features: [EF1, EF2]
    child_linker_node = create_common_only_1()

    # linkers: (Result)
    #   flags: [E0, E3] # Override = True
    #   remove-flags: [E1, E2]
    #   features: [EF0, EF3] # Override = True
    #   remove-features:  [EF1, EF2]
    #   ld:
    #     flags: [E0, E3] # Override = False
    #     remove-flags: [LD2]
    #     features: [EF0, EF3] # Override = False
    #     remove-features: [LDF2]
    result = child_linker_node.resolve_extends(extended_base_linker_node, {}).unwrap()

    # Validate result
    assert result.common_linker.flags.override == True
    assert result.common_linker.flags.values == set(["E0", "E3"])
    assert result.common_linker.flags.remove_modifiers.values == set(["E1", "E2"])
    assert result.common_linker.features.override == True
    assert result.common_linker.features.values == set(["EF0", "EF3"])
    assert result.common_linker.features.remove_modifiers.values == set(["EF1", "EF2"])
    ld = result.linker_overrides.get("ld")
    assert ld
    assert ld.flags.override == False
    assert ld.flags.values == set(["E0", "E3"])
    assert ld.flags.remove_modifiers.values == set(["LD2"]) 
    assert ld.features.override == False
    assert ld.features.values == set(["EF0", "EF3"])
    assert ld.features.remove_modifiers.values == set(["LDF2"]) 

def test_common_only_1_extends_4():
    # linkers:
    #   flags: [C0, C1, C2] # Override = True
    #   remove-flags: [C1, C3]
    #   features: [CF0, CF1, CF2] # Override = True
    #   remove-features: [CF1, CF3]
    #   ld:
    #     flags: [LD0, LD1, C3, LD2] # Override = True
    #     remove-flags: [LD2]
    #     features: [LDF0, LDF1, CF3, LDF2] # Override = True
    #     remove-features: [LDF2]
    base_linker_node = create_4()

    # linkers: (Extended)
    #   flags: [C0, C2] # Override = True
    #   remove-flags: [C1, C3]
    #   features: [CF0, CF2] # Override = True
    #   remove-features: [CF1, CF3]
    #   ld:
    #     flags: [LD0, LD1, C3] # Override = True
    #     remove-flags: [LD2]
    #     features: [LDF0, LDF1, CF3] # Override = True
    #     remove-features: [LDF2]
    extended_base_linker_node = base_linker_node.resolve_extends(None, {}).unwrap()

    # child 'linkers:' extends extended_base_linker_node
    # linkers:
    #   flags: [E0, E1, E3] # Override = True
    #   remove-flags: [E1, E2]
    #   features: [EF0, EF1, EF3] # Override = True
    #   remove-features: [EF1, EF2]
    child_linker_node = create_common_only_1()

    # linkers: (Result)
    #   flags: [E0, E3] # Override = True
    #   remove-flags: [E1, E2]
    #   features: [EF0, EF3] # Override = True
    #   remove-features: [EF1, EF2]
    #   ld:
    #     flags: [E0, E3] # Override = False
    #     remove-flags: [LD2]
    #     features: [EF0, EF3] # Override = False
    #     remove-features: [LDF2]
    result = child_linker_node.resolve_extends(extended_base_linker_node, {}).unwrap()

    # Validate result
    assert result.common_linker.flags.override == True
    assert result.common_linker.flags.values == set(["E0", "E3"])
    assert result.common_linker.flags.remove_modifiers.values == set(["E1", "E2"])
    assert result.common_linker.features.override == True
    assert result.common_linker.features.values == set(["EF0", "EF3"])
    assert result.common_linker.features.remove_modifiers.values == set(["EF1", "EF2"])
    ld = result.linker_overrides.get("ld")
    assert ld
    assert ld.flags.override == False
    assert ld.flags.values == set(["E0", "E3"])
    assert ld.flags.remove_modifiers.values == set(["LD2"]) 
    assert ld.features.override == False
    assert ld.features.values == set(["EF0", "EF3"])
    assert ld.features.remove_modifiers.values == set(["LDF2"]) 

def test_common_only_2_extends_1():
    # linkers:
    #   flags: [C1, C2] # Override = False
    #   remove-flags: [C1, C3]
    #   features: [CF1, CF2] # Override = False
    #   remove-features: [CF1, CF3]
    #   ld:
    #     flags: [LD1, C3, LD2] # Override = False
    #     remove-flags: [LD2]
    #     features: [LDF1, CF3, LDF2] # Override = False
    #     remove-features: [LDF2]
    base_linker_node = create_linker_override_node_1()

    #  linkers: (Extended)
    #   flags: [C2] # Override = False
    #   remove-flags: []
    #   features: [CF2] # Override = False
    #   remove-features: []
    #   ld:
    #     flags: [C2, LD1, C3] # Override = False
    #     remove-flags: [LD2]
    #     features: [CF2, LDF1, CF3] # Override = False
    #     remove-features: [LDF2]
    extended_base_linker_node = base_linker_node.resolve_extends(None, {}).unwrap()

    # child 'linkers:' extends extended_base_linker_node
    # linkers:
    #   flags: [E1, E3] # Override = False
    #   remove-flags: [E1, E2]
    #   features: [EF1, EF3] # Override = False
    #   remove-features: [EF1, EF2]
    child_linker_node = create_common_only_2()

    # linkers: (Result)
    #   flags: [E3] # Override = False
    #   remove-flags: [E1, E2]
    #   features: [EF3] # Override = False
    #   remove-features: [EF1, EF2]
    #   ld:
    #     flags: [C2, LD1, C3, E3] # Override = False
    #     remove-flags: [LD2]
    #     features: [CF2, LDF1, CF3, EF3] # Override = False
    #     remove-features: [LDF2]
    result = child_linker_node.resolve_extends(extended_base_linker_node, {}).unwrap()

    # Validate result
    assert result.common_linker.flags.override == False
    assert result.common_linker.flags.values == set(["E3"])
    assert result.common_linker.flags.remove_modifiers.values == set(["E1", "E2"])
    assert result.common_linker.features.override == False
    assert result.common_linker.features.values == set(["EF3"])
    assert result.common_linker.features.remove_modifiers.values == set(["EF1", "EF2"])
    ld = result.linker_overrides.get("ld")
    assert ld
    assert ld.flags.override == False
    assert ld.flags.values == set(["C2", "LD1", "C3", "E3"])
    assert ld.flags.remove_modifiers.values == set(["LD2"]) 
    assert ld.features.override == False
    assert ld.features.values == set(["CF2", "LDF1", "CF3", "EF3"])
    assert ld.features.remove_modifiers.values == set(["LDF2"]) 

def test_common_only_2_extends_2():
    # linkers:
    #   flags: [C0, C1, C2] # Override = True
    #   remove-flags: [C1, C3]
    #   features: [CF0, CF1, CF2] # Override = True
    #   remove-features: [CF1, CF3]
    #   ld:
    #     flags: [LD1, C3, LD2] # Override = False
    #     remove-flags: [LD2]
    #     features: [LDF1, CF3, LDF2] # Override = False
    #     remove-features: [LDF2]
    base_linker_node = create_2()

    #  linkers: (Extended)
    #   flags: [C0, C2] # Override = True
    #   remove-flags: []
    #   features: [CF0, CF2] # Override = True
    #   remove-features: []
    #   ld:
    #     flags: [LD1, C3, C0, C2] # Override = False
    #     remove-flags: [LD2]
    #     features: [CF0, CF2, LDF1, CF3] # Override = False
    #     remove-features: [LDF2]
    extended_base_linker_node = base_linker_node.resolve_extends(None, {}).unwrap()

    # child 'linkers:' extends extended_base_linker_node
    # linkers:
    #   flags: [E1, E3] # Override = False
    #   remove-flags: [E1, E2]
    #   features: [EF1, EF3] # Override = False
    #   remove-features: [EF1, EF2]
    child_linker_node = create_common_only_2()

    # linkers: (Result)
    #   flags: [E3] # Override = False
    #   remove-flags: [E1, E2]
    #   features: [EF3] # Override = False
    #   remove-features: [EF1, EF2]
    #   ld:
    #     flags: [C0, C2, LD1, C3, E3] # Override = False
    #     remove-flags: [LD2]
    #     features: [CF0, CF2, LDF1, CF3, EF3] # Override = False
    #     remove-features: [LDF2]
    result = child_linker_node.resolve_extends(extended_base_linker_node, {}).unwrap()
    
    # Validate result
    assert result.common_linker.flags.override == False
    assert result.common_linker.flags.values == set(["E3"])
    assert result.common_linker.flags.remove_modifiers.values == set(["E1", "E2"])
    assert result.common_linker.features.override == False
    assert result.common_linker.features.values == set(["EF3"])
    assert result.common_linker.features.remove_modifiers.values == set(["EF1", "EF2"])
    ld = result.linker_overrides.get("ld")
    assert ld
    assert ld.flags.override == False
    assert ld.flags.values == set(["C0", "C2", "LD1", "C3", "E3"])
    assert ld.flags.remove_modifiers.values == set(["LD2"]) 
    assert ld.features.override == False
    assert ld.features.values == set(["CF0", "CF2", "LDF1", "CF3", "EF3"])
    assert ld.features.remove_modifiers.values == set(["LDF2"]) 

def test_common_only_2_extends_3():
    # linkers:
    #   flags: [C1, C2] # Override = False
    #   remove-flags: [C1, C3]
    #   features: [CF1, CF2] # Override = False
    #   remove-features: [CF1, CF3]
    #   ld:
    #     flags: [LD0, LD1, C3, LD2] # Override = True
    #     remove-flags: [LD2]
    #     features: [LDF0, LDF1, CF3, LDF2] # Override = True
    #     remove-features: [LDF2]
    base_linker_node = create_3()

    #  linkers: (Extended)
    #   flags: [C2] # Override = False
    #   remove-flags: [C1, C3]
    #   features: [CF2] # Override = False
    #   remove-features: [CF1, CF3]
    #   ld:
    #     flags: [LD0, LD1, C3] # Override = True
    #     remove-flags: [LD2]
    #     features: [LDF0, LDF1, CF3] # Override = True
    #     remove-features: [LDF2]
    extended_base_linker_node = base_linker_node.resolve_extends(None, {}).unwrap()

    # child 'linkers:' extends extended_base_linker_node
    # linkers:
    #   flags: [E1, E3] # Override = False
    #   remove-flags: [E1, E2]
    #   features: [EF1, EF3] # Override = False
    #   remove-features: [EF1, EF2]
    child_linker_node = create_common_only_2()

    # linkers: (Result)
    #   flags: [E3] # Override = False
    #   remove-flags: [C1, C3]
    #   features: [EF3] # Override = False
    #   remove-features: [CF1, CF3]
    #   ld:
    #     flags: [C2, LD1, C3, E3] # Override = False
    #     remove-flags: [LD2]
    #     features: [CF2, LDF1, CF3, EF3] # Override = False
    #     remove-features: [LDF2]
    result = child_linker_node.resolve_extends(extended_base_linker_node, {}).unwrap()

    # Validate result
    assert result.common_linker.flags.override == False
    assert result.common_linker.flags.values == set(["E3"])
    assert result.common_linker.flags.remove_modifiers.values == set(["E1", "E2"])
    assert result.common_linker.features.override == False
    assert result.common_linker.features.values == set(["EF3"])
    assert result.common_linker.features.remove_modifiers.values == set(["EF1", "EF2"])
    ld = result.linker_overrides.get("ld")
    assert ld
    assert ld.flags.override == False
    assert ld.flags.values == set(["LD0", "LD1", "C3", "E3"])
    assert ld.flags.remove_modifiers.values == set(["LD2"]) 
    assert ld.features.override == False
    assert ld.features.values == set(["LDF0", "LDF1", "CF3", "EF3"])
    assert ld.features.remove_modifiers.values == set(["LDF2"]) 

def test_common_only_2_extends_4():
    # linkers:
    #   flags: [C0, C1, C2] # Override = True
    #   remove-flags: [C1, C3]
    #   features: [CF0, CF1, CF2] # Override = True
    #   remove-features: [CF1, CF3]
    #   ld:
    #     flags: [LD0, LD1, C3, LD2] # Override = True
    #     remove-flags: [LD2]
    #     features: [LDF0, LDF1, CF3, LDF2] # Override = True
    #     remove-features: [LDF2]
    base_linker_node = create_4()

    # linkers: (Extended)
    #   flags: [C0, C2] # Override = True
    #   remove-flags: [C1, C3]
    #   features: [CF0, CF2] # Override = True
    #   remove-features: [CF1, CF3]
    #   ld:
    #     flags: [LD0, LD1, C3] # Override = True
    #     remove-flags: [LD2]
    #     features: [LDF0, LDF1, CF3] # Override = True
    #     remove-features: [LDF2]
    extended_base_linker_node = base_linker_node.resolve_extends(None, {}).unwrap()

    # child 'linkers:' extends extended_base_linker_node
    # linkers:
    #   flags: [E1, E3] # Override = False
    #   remove-flags: [E1, E2]
    #   features: [EF1, EF3] # Override = False
    #   remove-features: [EF1, EF2]
    child_linker_node = create_common_only_2()

    # linkers: (Result)
    #   flags: [E3] # Override = False
    #   remove-flags: [E1, E2]
    #   features: [EF3] # Override = False
    #   remove-features: [EF1, EF2]
    #   ld:
    #     flags: [C2, LD1, C3, E3] # Override = False
    #     remove-flags: [LD2]
    #     features: [CF2, LDF1, CF3, EF3] # Override = False
    #     remove-features: [LDF2]
    result = child_linker_node.resolve_extends(extended_base_linker_node, {}).unwrap()

    # Validate result
    assert result.common_linker.flags.override == False
    assert result.common_linker.flags.values == set(["E3"])
    assert result.common_linker.flags.remove_modifiers.values == set(["E1", "E2"])
    assert result.common_linker.features.override == False
    assert result.common_linker.features.values == set(["EF3"])
    assert result.common_linker.features.remove_modifiers.values == set(["EF1", "EF2"])
    ld = result.linker_overrides.get("ld")
    assert ld
    assert ld.flags.override == False
    assert ld.flags.values == set(["LD0", "LD1", "C3", "E3"])
    assert ld.flags.remove_modifiers.values == set(["LD2"]) 
    assert ld.features.override == False
    assert ld.features.values == set(["LDF0", "LDF1", "CF3", "EF3"])
    assert ld.features.remove_modifiers.values == set(["LDF2"]) 

def create_a():
    """
    linkers:
      flags: [AC1, AC3, AC4]  # Override = False
      remove-flags: [AC1, ALD1, AC2]
      features: [ACF1, ACF3, ACF4]  # Override = False
      remove-features: [ACF1, ALDF1, ACF2]
        ld:
          flags: [ALD1, ALD2, ALD3]  # Override = False
          remove-flags: [ALD2, AC4]
          features: [ALDF1, ALDF2, ALDF3]  # Override = False
          remove-features: [ALDF2, ACF4]
    """
    common_flags = create_str_list(False, ["AC1", "AC3", "AC4"], ["AC1", "ALD1", "AC2"])
    common_features = create_feature_str_list(False, ["ACF1", "ACF3", "ACF4"], ["ACF1", "ALDF1", "ACF2"])
    ld_flags = create_str_list(False, ["ALD1", "ALD2", "ALD3"], ["ALD2", "AC4"])
    ld_features = create_feature_str_list(False, ["ALDF1", "ALDF2", "ALDF3"], ["ALDF2", "ACF4"])
    ld_linker = create_specific_linker_override_node("ld", ld_flags, ld_features)
    linker_override_node = create_linker_override_node(common_flags, common_features, ld_linker)
    assert linker_override_node.common_linker.flags.override == False
    assert linker_override_node.common_linker.flags.values == set(["AC1", "AC3", "AC4"])
    assert linker_override_node.common_linker.flags.remove_modifiers.values == set(["AC1", "ALD1", "AC2"])
    assert linker_override_node.common_linker.features.override == False
    assert linker_override_node.common_linker.features.values == set(["ACF1", "ACF3", "ACF4"])
    assert linker_override_node.common_linker.features.remove_modifiers.values == set(["ACF1", "ALDF1", "ACF2"])
    ld = linker_override_node.linker_overrides.get("ld")
    assert ld
    assert ld.flags.override == False
    assert ld.flags.values == set(["ALD1", "ALD2", "ALD3"])
    assert ld.flags.remove_modifiers.values == set(["ALD2", "AC4"]) 
    assert ld.features.override == False
    assert ld.features.values == set(["ALDF1", "ALDF2", "ALDF3"])
    assert ld.features.remove_modifiers.values == set(["ALDF2", "ACF4"]) 
    return linker_override_node

def create_b():
    """
    linkers:
      flags: [AC0, AC1, AC3, AC4]  # Override = True
      remove-flags: [AC1, ALD1, AC2]
      features: [ACF0, ACF1, ACF3, ACF4]  # Override = True
      remove-features: [ACF1, ALDF1, ACF2]
      ld:
        flags: [ALD1, ALD2, ALD3]  # Override = False
        remove-flags: [ALD2, AC4]
        features: [ALDF1, ALDF2, ALDF3]  # Override = False
        remove-features: [ALDF2, ACF4]
    """
    common_flags = create_str_list(True, ["AC0", "AC1", "AC3", "AC4"], ["AC1", "ALD1", "AC2"])
    common_features = create_feature_str_list(True, ["ACF0", "ACF1", "ACF3", "ACF4"], ["ACF1", "ALDF1", "ACF2"])
    ld_flags = create_str_list(False, ["ALD1", "ALD2", "ALD3"], ["ALD2", "AC4"])
    ld_features = create_feature_str_list(False, ["ALDF1", "ALDF2", "ALDF3"], ["ALDF2", "ACF4"])
    ld_linker = create_specific_linker_override_node("ld", ld_flags, ld_features)
    linker_override_node = create_linker_override_node(common_flags, common_features, ld_linker)
    assert linker_override_node.common_linker.flags.override == True
    assert linker_override_node.common_linker.flags.values == set(["AC0", "AC1", "AC3", "AC4"])
    assert linker_override_node.common_linker.flags.remove_modifiers.values == set(["AC1", "ALD1", "AC2"])
    assert linker_override_node.common_linker.features.override == True
    assert linker_override_node.common_linker.features.values == set(["ACF0", "ACF1", "ACF3", "ACF4"])
    assert linker_override_node.common_linker.features.remove_modifiers.values == set(["ACF1", "ALDF1", "ACF2"])
    ld = linker_override_node.linker_overrides.get("ld")
    assert ld
    assert ld.flags.override == False
    assert ld.flags.values == set(["ALD1", "ALD2", "ALD3"])
    assert ld.flags.remove_modifiers.values == set(["ALD2", "AC4"]) 
    assert ld.features.override == False
    assert ld.features.values == set(["ALDF1", "ALDF2", "ALDF3"])
    assert ld.features.remove_modifiers.values == set(["ALDF2", "ACF4"]) 
    return linker_override_node

def create_c():
    """
    linkers:
      flags: [AC1, AC3, AC4]  # Override = False
      remove-flags: [AC1, ALD1, AC2]
      features: [ACF1, ACF3, ACF4]  # Override = False
      remove-features: [ACF1, ALDF1, ACF2]
      ld:
        flags: [ALD0, ALD1, ALD2, ALD3]  # Override = True
        remove-flags: [ALD2, AC4]
        features: [ALDF0, ALDF1, ALDF2, ALDF3]  # Override = True
        remove-features: [ALDF2, ACF4]
    """
    common_flags = create_str_list(False, ["AC1", "AC3", "AC4"], ["AC1", "ALD1", "AC2"])
    common_features = create_feature_str_list(False, ["ACF1", "ACF3", "ACF4"], ["ACF1", "ALDF1", "ACF2"])
    ld_flags = create_str_list(True, ["ALD0", "ALD1", "ALD2", "ALD3"], ["ALD2", "AC4"])
    ld_features = create_feature_str_list(True, ["ALDF0", "ALDF1", "ALDF2", "ALDF3"], ["ALDF2", "ACF4"])
    ld_linker = create_specific_linker_override_node("ld", ld_flags, ld_features)
    linker_override_node = create_linker_override_node(common_flags, common_features, ld_linker)
    assert linker_override_node.common_linker.flags.override == False
    assert linker_override_node.common_linker.flags.values == set(["AC1", "AC3", "AC4"])
    assert linker_override_node.common_linker.flags.remove_modifiers.values == set(["AC1", "ALD1", "AC2"])
    assert linker_override_node.common_linker.features.override == False
    assert linker_override_node.common_linker.features.values == set(["ACF1", "ACF3", "ACF4"])
    assert linker_override_node.common_linker.features.remove_modifiers.values == set(["ACF1", "ALDF1", "ACF2"])
    ld = linker_override_node.linker_overrides.get("ld")
    assert ld
    assert ld.flags.override == True
    assert ld.flags.values == set(["ALD0", "ALD1", "ALD2", "ALD3"])
    assert ld.flags.remove_modifiers.values == set(["ALD2", "AC4"]) 
    assert ld.features.override == True
    assert ld.features.values == set(["ALDF0", "ALDF1", "ALDF2", "ALDF3"])
    assert ld.features.remove_modifiers.values == set(["ALDF2", "ACF4"]) 
    return linker_override_node

def create_d():
    """
    linkers:
      flags: [AC0, AC1, AC3, AC4]  # Override = True
      remove-flags: [AC1, ALD1, AC2]
      features: [AC0, ACF1, ACF3, ACF4]  # Override = True
      remove-features: [ACF1, ALDF1, ACF2]
      ld:
        flags: [ALD0, ALD1, ALD2, ALD3]  # Override = True
        remove-flags: [ALD2, AC4]
        features: [ALDF0, ALDF1, ALDF2, ALDF3]  # Override = True
        remove-features: [ALDF2, ACF4]
    """
    common_flags = create_str_list(True, ["AC0", "AC1", "AC3", "AC4"], ["AC1", "ALD1", "AC2"])
    common_features = create_feature_str_list(True, ["ACF0", "ACF1", "ACF3", "ACF4"], ["ACF1", "ALDF1", "ACF2"])
    ld_flags = create_str_list(True, ["ALD0", "ALD1", "ALD2", "ALD3"], ["ALD2", "AC4"])
    ld_features = create_feature_str_list(True, ["ALDF0", "ALDF1", "ALDF2", "ALDF3"], ["ALDF2", "ACF4"])
    ld_linker = create_specific_linker_override_node("ld", ld_flags, ld_features)
    linker_override_node = create_linker_override_node(common_flags, common_features, ld_linker)
    assert linker_override_node.common_linker.flags.override == True
    assert linker_override_node.common_linker.flags.values == set(["AC0", "AC1", "AC3", "AC4"])
    assert linker_override_node.common_linker.flags.remove_modifiers.values == set(["AC1", "ALD1", "AC2"])
    assert linker_override_node.common_linker.features.override == True
    assert linker_override_node.common_linker.features.values == set(["ACF0", "ACF1", "ACF3", "ACF4"])
    assert linker_override_node.common_linker.features.remove_modifiers.values == set(["ACF1", "ALDF1", "ACF2"])
    ld = linker_override_node.linker_overrides.get("ld")
    assert ld
    assert ld.flags.override == True
    assert ld.flags.values == set(["ALD0", "ALD1", "ALD2", "ALD3"])
    assert ld.flags.remove_modifiers.values == set(["ALD2", "AC4"]) 
    assert ld.features.override == True
    assert ld.features.values == set(["ALDF0", "ALDF1", "ALDF2", "ALDF3"])
    assert ld.features.remove_modifiers.values == set(["ALDF2", "ACF4"]) 
    return linker_override_node

def test_a_extends_1():
    # linkers:
    #   flags: [C1, C2] # Override = False
    #   remove-flags: [C1, C3]
    #   features: [CF1, CF2] # Override = False
    #   remove-features: [CF1, CF3]
    #   ld:
    #     flags: [LD1, C3, LD2] # Override = False
    #     remove-flags: [LD2]
    #     features: [LDF1, CF3, LDF2] # Override = False
    #     remove-features: [LDF2]
    base_linker_node = create_linker_override_node_1()

    #  linkers: (Extended)
    #   flags: [C2] # Override = False
    #   remove-flags: [C1, C3]
    #   features: [CF2] # Override = False
    #   remove-features: [CF1, CF3]
    #   ld:
    #     flags: [C2, LD1, C3] # Override = False
    #     remove-flags: [LD2]
    #     features: [CF2, LDF1, CF3] # Override = False
    #     remove-features: [LDF2
    extended_base_linker_node = base_linker_node.resolve_extends(None, {}).unwrap()

  
    # child 'linkers:' extends extended_base_linker_node
    # linkers:
    #   flags: [AC1, AC3, AC4]  # Override = False
    #   remove-flags: [AC1, ALD1, AC2]
    #   features: [ACF1, ACF3, ACF4]  # Override = False
    #   remove-features: [ACF1, ALDF1, ACF2]
    #   ld:
    #     flags: [ALD1, ALD2, ALD3]  # Override = False
    #     remove-flags: [ALD2, AC4]
    #     features: [ALDF1, ALDF2, ALDF3]  # Override = False
    #     remove-features: [ALDF2, ACF4]
    child_linker_node = create_a()

    # child
    # linkers: (Extended)
    #   flags: [AC3, AC4]  # Override = False
    #   remove-flags: [AC1, ALD1, AC2]
    #   features: [ACF3, ACF4]  # Override = False
    #   remove-features: [ACF1, ALDF1, ACF2]
    #   ld:
    #     flags: [C2, LD1, C3, ALD1, ALD3, AC3]  # Override = False
    #     remove-flags: [ALD2, AC4]
    #     features: [CF2, LDF1, CF3, ACF3, ALDF1, ALDF3]  # Override = False
    #     remove-features: [ALDF2, ACF4]
    result = child_linker_node.resolve_extends(extended_base_linker_node, {}).unwrap()

    # Validate result
    assert result.common_linker.flags.override == False
    assert result.common_linker.flags.values == set(["AC3", "AC4"])
    assert result.common_linker.flags.remove_modifiers.values == set(["AC1", "ALD1", "AC2"])
    assert result.common_linker.features.override == False
    assert result.common_linker.features.values == set(["ACF3", "ACF4"])
    assert result.common_linker.features.remove_modifiers.values == set(["ACF1", "ALDF1", "ACF2"])
    ld = result.linker_overrides.get("ld")
    assert ld
    assert ld.flags.override == False
    assert ld.flags.values == set(["C2", "LD1", "C3", "ALD1", "ALD3", "AC3"])
    assert ld.flags.remove_modifiers.values == set(["ALD2", "AC4"]) 
    assert ld.features.override == False
    assert ld.features.values == set(["CF2", "LDF1", "CF3", "ACF3", "ALDF1", "ALDF3"])
    assert ld.features.remove_modifiers.values == set(["ALDF2", "ACF4"]) 

def test_b_extends_1():
    # linkers:
    #   flags: [C1, C2] # Override = False
    #   remove-flags: [C1, C3]
    #   features: [CF1, CF2] # Override = False
    #   remove-features: [CF1, CF3]
    #   ld:
    #     flags: [LD1, C3, LD2] # Override = False
    #     remove-flags: [LD2]
    #     features: [LDF1, CF3, LDF2] # Override = False
    #     remove-features: [LDF2]
    base_linker_node = create_linker_override_node_1()

    #  linkers: (Extended)
    #   flags: [C2] # Override = False
    #   remove-flags: [C1, C3]
    #   features: [CF2] # Override = False
    #   remove-features: [CF1, CF3]
    #   ld:
    #     flags: [C2, LD1, C3] # Override = False
    #     remove-flags: [LD2]
    #     features: [CF2, LDF1, CF3] # Override = False
    #     remove-features: [LDF2]
    extended_base_linker_node = base_linker_node.resolve_extends(None, {}).unwrap()

  
    # child 'linkers:' extends extended_base_linker_node
    # linkers:
    #   flags: [AC0, AC1, AC3, AC4] # Override = True
    #   remove-flags: [AC1, ALD1, AC2]
    #   features: [ACF0, ACF1, ACF3, ACF4] # Override = True
    #   remove-features: [ACF1, ALDF1, ACF2]
    #   ld:
    #     flags: [ALD1, ALD2, ALD3] # Override = False
    #     remove-flags: [ALD2, AC4]
    #     features: [ALDF1, ALDF2, ALDF3] # Override = False
    #     remove-features: [ALDF2, ACF4]
    child_linker_node = create_b()

    # child
    # linkers: (Extended)
    #   flags: [AC0, AC3, AC4] # Override = True
    #   remove-flags: [AC1, ALD1, AC2]
    #   features: [ACF0, ACF3, ACF4] # Override = True
    #   remove-features: [ACF1, ALDF1, ACF2]
    #   ld:
    #     flags: [AC0, AC3, ALD1, ALD3] # Override = False
    #     remove-flags: [ALD2, AC4]
    #     features: [ACF0, ACF3, ALDF1, ALDF3] # Override = False
    #     remove-features: [ALDF2, ACF4]
    result = child_linker_node.resolve_extends(extended_base_linker_node, {}).unwrap()

    # Validate result
    assert result.common_linker.flags.override == True
    assert result.common_linker.flags.values == set(["AC0", "AC3", "AC4"])
    assert result.common_linker.flags.remove_modifiers.values == set(["AC1", "ALD1", "AC2"])
    assert result.common_linker.features.override == True
    assert result.common_linker.features.values == set(["ACF0", "ACF3", "ACF4"])
    assert result.common_linker.features.remove_modifiers.values == set(["ACF1", "ALDF1", "ACF2"])
    ld = result.linker_overrides.get("ld")
    assert ld
    assert ld.flags.override == False
    assert ld.flags.values == set(["AC0", "AC3", "ALD1", "ALD3"])
    assert ld.flags.remove_modifiers.values == set(["ALD2", "AC4"]) 
    assert ld.features.override == False
    assert ld.features.values == set(["ACF0", "ACF3", "ALDF1", "ALDF3"])
    assert ld.features.remove_modifiers.values == set(["ALDF2", "ACF4"]) 

def test_c_extends_1():
    # linkers:
    #   flags: [C1, C2] # Override = False
    #   remove-flags: [C1, C3]
    #   features: [CF1, CF2] # Override = False
    #   remove-features: [CF1, CF3]
    #   ld:
    #     flags: [LD1, C3, LD2] # Override = False
    #     remove-flags: [LD2]
    #     features: [LDF1, CF3, LDF2] # Override = False
    #     remove-features: [LDF2]
    base_linker_node = create_linker_override_node_1()

    #  linkers: (Extended)
    #   flags: [C2] # Override = False
    #   remove-flags: [C1, C3]
    #   features: [CF2] # Override = False
    #   remove-features: [CF1, CF3]
    #   ld:
    #     flags: [C2, LD1, C3] # Override = False
    #     remove-flags: [LD2]
    #     features: [CF2, LDF1, CF3] # Override = False
    #     remove-features: [LDF2]
    extended_base_linker_node = base_linker_node.resolve_extends(None, {}).unwrap()

  
    # child 'linkers:' extends extended_base_linker_node
    # linkers:
    #   flags: [AC1, AC3, AC4]  # Override = False
    #   remove-flags: [AC1, ALD1, AC2]
    #   features: [ACF1, ACF3, ACF4]  # Override = False
    #   remove-features: [ACF1, ALDF1, ACF2]
    #   ld:
    #     flags: [ALD0, ALD1, ALD2, ALD3]  # Override = True
    #     remove-flags: [ALD2, AC4]
    #     features: [ALDF0, ALDF1, ALDF2, ALDF3]  # Override = True
    #     remove-features: [ALDF2, ACF4]
    child_linker_node = create_c()

    # child
    # linkers: (Extended)
    #   flags: [AC3, AC4]  # Override = False
    #   remove-flags: [AC1, ALD1, AC2]
    #   features: [ACF3, ACF4]  # Override = False
    #   remove-features: [ACF1, ALDF1, ACF2]
    #   ld:
    #     flags: [ALD0, ALD1, ALD3]  # Override = True
    #     remove-flags: [ALD2, AC4]
    #     features: [ALDF0, ALDF1, ALDF3]  # Override = True
    #     remove-features: [ALDF2, ACF4]
    result = child_linker_node.resolve_extends(extended_base_linker_node, {}).unwrap()

    # Validate result
    assert result.common_linker.flags.override == False
    assert result.common_linker.flags.values == set(["AC3", "AC4"])
    assert result.common_linker.flags.remove_modifiers.values == set(["AC1", "ALD1", "AC2"])
    assert result.common_linker.features.override == False
    assert result.common_linker.features.values == set(["ACF3", "ACF4"])
    assert result.common_linker.features.remove_modifiers.values == set(["ACF1", "ALDF1", "ACF2"])
    ld = result.linker_overrides.get("ld")
    assert ld
    assert ld.flags.override == True
    assert ld.flags.values == set(["ALD0", "ALD1", "ALD3"])
    assert ld.flags.remove_modifiers.values == set(["ALD2", "AC4"]) 
    assert ld.features.override == True
    assert ld.features.values == set(["ALDF0", "ALDF1", "ALDF3"])
    assert ld.features.remove_modifiers.values == set(["ALDF2", "ACF4"]) 

def test_d_extends_1():
    # linkers:
    #   flags: [C1, C2] # Override = False
    #   remove-flags: [C1, C3]
    #   features: [CF1, CF2] # Override = False
    #   remove-features: [CF1, CF3]
    #   ld:
    #     flags: [LD1, C3, LD2] # Override = False
    #     remove-flags: [LD2]
    #     features: [LDF1, CF3, LDF2] # Override = False
    #     remove-features: [LDF2]
    base_linker_node = create_linker_override_node_1()

    #  linkers: (Extended)
    #   flags: [C2] # Override = False
    #   remove-flags: [C1, C3]
    #   features: [CF2] # Override = False
    #   remove-features: [CF1, CF3]
    #   ld:
    #     flags: [C2, LD1, C3] # Override = False
    #     remove-flags: [LD2]
    #     features: [CF2, LDF1, CF3] # Override = False
    #     remove-features: [LDF2]
    extended_base_linker_node = base_linker_node.resolve_extends(None, {}).unwrap()

    # child 'linkers:' extends extended_base_linker_node
    # linkers:
    #   flags: [AC0, AC1, AC3, AC4]  # Override = True
    #   remove-flags: [AC1, ALD1, AC2]
    #   features: [AC0, ACF1, ACF3, ACF4]  # Override = True
    #   remove-features: [ACF1, ALDF1, ACF2]
    #   ld:
    #     flags: [ALD0, ALD1, ALD2, ALD3]  # Override = True
    #     remove-flags: [ALD2, AC4]
    #     features: [ALDF0, ALDF1, ALDF2, ALDF3]  # Override = True
    #     remove-features: [ALDF2, ACF4]
    child_linker_node = create_d()

    # child
    # linkers:
    #   flags: [AC0, AC3, AC4]  # Override = True
    #   remove-flags: [AC1, ALD1, AC2]
    #   features: [AC0, ACF3, ACF4]  # Override = True
    #   remove-features: [ACF1, ALDF1, ACF2]
    #   ld:
    #     flags: [ALD0, ALD1, ALD3]  # Override = True
    #     remove-flags: [ALD2, AC4]
    #     features: [ALDF0, ALDF1, ALDF3]  # Override = True
    #     remove-features: [ALDF2, ACF4]
    result = child_linker_node.resolve_extends(extended_base_linker_node, {}).unwrap()

    # Validate result
    assert result.common_linker.flags.override == True
    assert result.common_linker.flags.values == set(["AC0","AC3", "AC4"])
    assert result.common_linker.flags.remove_modifiers.values == set(["AC1", "ALD1", "AC2"])
    assert result.common_linker.features.override == True
    assert result.common_linker.features.values == set(["ACF0", "ACF3", "ACF4"])
    assert result.common_linker.features.remove_modifiers.values == set(["ACF1", "ALDF1", "ACF2"])
    ld = result.linker_overrides.get("ld")
    assert ld
    assert ld.flags.override == True
    assert ld.flags.values == set(["ALD0", "ALD1", "ALD3"])
    assert ld.flags.remove_modifiers.values == set(["ALD2", "AC4"]) 
    assert ld.features.override == True
    assert ld.features.values == set(["ALDF0", "ALDF1", "ALDF3"])
    assert ld.features.remove_modifiers.values == set(["ALDF2", "ACF4"]) 

def test_a_extends_2():
    # linkers:
    #   flags: [C0, C1, C2] # Override = True
    #   remove-flags: [C1, C3]
    #   features: [CF0, CF1, CF2] # Override = True
    #   remove-features: [CF1, CF3]
    #   ld:
    #     flags: [LD1, C3, LD2] # Override = False
    #     remove-flags: [LD2]
    #     features: [LDF1, CF3, LDF2] # Override = False
    #     remove-features: [LDF2]
    base_linker_node = create_2()

    #  linkers: (Extended)
    #   flags: [C0, C2] # Override = True
    #   remove-flags: [C1, C3]
    #   features: [CF0, CF2] # Override = True
    #   remove-features: [CF1, CF3]
    #   ld:
    #     flags: [LD1, C3, C0, C2] # Override = False
    #     remove-flags: [LD2]
    #     features: [CF0, CF2, LDF1, CF3] # Override = False
    #     remove-features: [LDF2]
    extended_base_linker_node = base_linker_node.resolve_extends(None, {}).unwrap()

    # child 'linkers:' extends extended_base_linker_node
    # linkers:
    #   flags: [AC1, AC3, AC4]  # Override = False
    #   remove-flags: [AC1, ALD1, AC2]
    #   features: [ACF1, ACF3, ACF4]  # Override = False
    #   remove-features: [ACF1, ALDF1, ACF2]
    #   ld:
    #     flags: [ALD1, ALD2, ALD3]  # Override = False
    #     remove-flags: [ALD2, AC4]
    #     features: [ALDF1, ALDF2, ALDF3]  # Override = False
    #     remove-features: [ALDF2, ACF4]
    child_linker_node = create_a()

    # child
    # linkers: (Extended)
    #   flags: [AC3, AC4]  # Override = False
    #   remove-flags: [AC1, ALD1, AC2]
    #   features: [ACF3, ACF4]  # Override = False
    #   remove-features: [ACF1, ALDF1, ACF2]
    #   ld:
    #     flags: [ALD1, ALD3, AC3, LD1, C3, C0, C2]  # Override = False
    #     remove-flags: [ALD2, AC4]
    #     features: [ALDF1, ALDF3, ACF3, CF0, CF2, LDF1, CF3]  # Override = False
    #     remove-features: [ALDF2, ACF4]
    result = child_linker_node.resolve_extends(extended_base_linker_node, {}).unwrap()

    # Validate result
    assert result.common_linker.flags.override == False
    assert result.common_linker.flags.values == set(["AC3", "AC4"])
    assert result.common_linker.flags.remove_modifiers.values == set(["AC1", "ALD1", "AC2"])
    assert result.common_linker.features.override == False
    assert result.common_linker.features.values == set(["ACF3", "ACF4"])
    assert result.common_linker.features.remove_modifiers.values == set(["ACF1", "ALDF1", "ACF2"])
    ld = result.linker_overrides.get("ld")
    assert ld
    assert ld.flags.override == False
    assert ld.flags.values == set(["ALD1", "ALD3", "AC3", "LD1", "C3", "C0", "C2"])
    assert ld.flags.remove_modifiers.values == set(["ALD2", "AC4"]) 
    assert ld.features.override == False
    assert ld.features.values == set(["ALDF1", "ALDF3", "ACF3", "CF0", "CF2", "LDF1", "CF3"])
    assert ld.features.remove_modifiers.values == set(["ALDF2", "ACF4"]) 

def test_b_extends_2():
    # linkers:
    #   flags: [C0, C1, C2] # Override = True
    #   remove-flags: [C1, C3]
    #   features: [CF0, CF1, CF2] # Override = True
    #   remove-features: [CF1, CF3]
    #   ld:
    #     flags: [LD1, C3, LD2] # Override = False
    #     remove-flags: [LD2]
    #     features: [LDF1, CF3, LDF2] # Override = False
    #     remove-features: [LDF2]
    base_linker_node = create_2()

    #  linkers: (Extended)
    #   flags: [C0, C2] # Override = True
    #   remove-flags: [C1, C3]
    #   features: [CF0, CF2] # Override = True
    #   remove-features: [CF1, CF3]
    #   ld:
    #     flags: [LD1, C3, C0, C2] # Override = False
    #     remove-flags: [LD2]
    #     features: [CF0, CF2, LDF1, CF3] # Override = False
    #     remove-features: [LDF2]
    extended_base_linker_node = base_linker_node.resolve_extends(None, {}).unwrap()

    # child 'linkers:' extends extended_base_linker_node
    # linkers:
    #   flags: [AC0, AC1, AC3, AC4] # Override = True
    #   remove-flags: [AC1, ALD1, AC2]
    #   features: [ACF0, ACF1, ACF3, ACF4] # Override = True
    #   remove-features: [ACF1, ALDF1, ACF2]
    #   ld:
    #     flags: [ALD1, ALD2, ALD3] # Override = False
    #     remove-flags: [ALD2, AC4]
    #     features: [ALDF1, ALDF2, ALDF3] # Override = False
    #     remove-features: [ALDF2, ACF4]
    child_linker_node = create_b()

    # child
    # linkers: (Extended)
    #   flags: [AC0, AC3, AC4] # Override = True
    #   remove-flags: [AC1, ALD1, AC2]
    #   features: [ACF0, ACF3, ACF4] # Override = True
    #   remove-features: [ACF1, ALDF1, ACF2]
    #   ld:
    #     flags: [ALD1, ALD3, AC0, AC3] # Override = False
    #     remove-flags: [ALD2, AC4]
    #     features: [ALDF1, ALDF3, ACF0, ACF3] # Override = False
    #     remove-features: [ALDF2, ACF4]
    result = child_linker_node.resolve_extends(extended_base_linker_node, {}).unwrap()

    # Validate result
    assert result.common_linker.flags.override == True
    assert result.common_linker.flags.values == set(["AC0", "AC3", "AC4"])
    assert result.common_linker.flags.remove_modifiers.values == set(["AC1", "ALD1", "AC2"])
    assert result.common_linker.features.override == True
    assert result.common_linker.features.values == set(["ACF0", "ACF3", "ACF4"])
    assert result.common_linker.features.remove_modifiers.values == set(["ACF1", "ALDF1", "ACF2"])
    ld = result.linker_overrides.get("ld")
    assert ld
    assert ld.flags.override == False
    assert ld.flags.values == set(["ALD1", "ALD3", "AC0", "AC3"])
    assert ld.flags.remove_modifiers.values == set(["ALD2", "AC4"]) 
    assert ld.features.override == False
    assert ld.features.values == set(["ALDF1", "ALDF3", "ACF0", "ACF3"])
    assert ld.features.remove_modifiers.values == set(["ALDF2", "ACF4"]) 

def test_c_extends_2():
    # linkers:
    #   flags: [C0, C1, C2] # Override = True
    #   remove-flags: [C1, C3]
    #   features: [CF0, CF1, CF2] # Override = True
    #   remove-features: [CF1, CF3]
    #   ld:
    #     flags: [LD1, C3, LD2] # Override = False
    #     remove-flags: [LD2]
    #     features: [LDF1, CF3, LDF2] # Override = False
    #     remove-features: [LDF2]
    base_linker_node = create_2()

    #  linkers: (Extended)
    #   flags: [C0, C2] # Override = True
    #   remove-flags: [C1, C3]
    #   features: [CF0, CF2] # Override = True
    #   remove-features: [CF1, CF3]
    #   ld:
    #     flags: [LD1, C3, C0, C2] # Override = False
    #     remove-flags: [LD2]
    #     features: [CF0, CF2, LDF1, CF3] # Override = False
    #     remove-features: [LDF2]
    extended_base_linker_node = base_linker_node.resolve_extends(None, {}).unwrap()

  
    # child 'linkers:' extends extended_base_linker_node
    # linkers:
    #   flags: [AC1, AC3, AC4]  # Override = False
    #   remove-flags: [AC1, ALD1, AC2]
    #   features: [ACF1, ACF3, ACF4]  # Override = False
    #   remove-features: [ACF1, ALDF1, ACF2]
    #   ld:
    #     flags: [ALD0, ALD1, ALD2, ALD3]  # Override = True
    #     remove-flags: [ALD2, AC4]
    #     features: [ALDF0, ALDF1, ALDF2, ALDF3]  # Override = True
    #     remove-features: [ALDF2, ACF4]
    child_linker_node = create_c()

    # child
    # linkers: (Extended)
    #   flags: [AC3, AC4]  # Override = False
    #   remove-flags: [AC1, ALD1, AC2]
    #   features: [ACF3, ACF4]  # Override = False
    #   remove-features: [ACF1, ALDF1, ACF2]
    #   ld:
    #     flags: [ALD0, ALD1, ALD3]  # Override = True
    #     remove-flags: [ALD2, AC4]
    #     features: [ALDF0, ALDF1, ALDF3]  # Override = True
    #     remove-features: [ALDF2, ACF4]
    result = child_linker_node.resolve_extends(extended_base_linker_node, {}).unwrap()

    # Validate result
    assert result.common_linker.flags.override == False
    assert result.common_linker.flags.values == set(["AC3", "AC4"])
    assert result.common_linker.flags.remove_modifiers.values == set(["AC1", "ALD1", "AC2"])
    assert result.common_linker.features.override == False
    assert result.common_linker.features.values == set(["ACF3", "ACF4"])
    assert result.common_linker.features.remove_modifiers.values == set(["ACF1", "ALDF1", "ACF2"])
    ld = result.linker_overrides.get("ld")
    assert ld
    assert ld.flags.override == True
    assert ld.flags.values == set(["ALD0", "ALD1", "ALD3"])
    assert ld.flags.remove_modifiers.values == set(["ALD2", "AC4"]) 
    assert ld.features.override == True
    assert ld.features.values == set(["ALDF0", "ALDF1", "ALDF3"])
    assert ld.features.remove_modifiers.values == set(["ALDF2", "ACF4"]) 

def test_d_extends_2():
    # linkers:
    #   flags: [C0, C1, C2] # Override = True
    #   remove-flags: [C1, C3]
    #   features: [CF0, CF1, CF2] # Override = True
    #   remove-features: [CF1, CF3]
    #   ld:
    #     flags: [LD1, C3, LD2] # Override = False
    #     remove-flags: [LD2]
    #     features: [LDF1, CF3, LDF2] # Override = False
    #     remove-features: [LDF2]
    base_linker_node = create_2()

    #  linkers: (Extended)
    #   flags: [C0, C2] # Override = True
    #   remove-flags: [C1, C3]
    #   features: [CF0, CF2] # Override = True
    #   remove-features: [CF1, CF3]
    #   ld:
    #     flags: [LD1, C3, C0, C2] # Override = False
    #     remove-flags: [LD2]
    #     features: [CF0, CF2, LDF1, CF3] # Override = False
    #     remove-features: [LDF2]
    extended_base_linker_node = base_linker_node.resolve_extends(None, {}).unwrap()

    # child 'linkers:' extends extended_base_linker_node
    # linkers:
    #   flags: [AC0, AC1, AC3, AC4]  # Override = True
    #   remove-flags: [AC1, ALD1, AC2]
    #   features: [AC0, ACF1, ACF3, ACF4]  # Override = True
    #   remove-features: [ACF1, ALDF1, ACF2]
    #   ld:
    #     flags: [ALD0, ALD1, ALD2, ALD3]  # Override = True
    #     remove-flags: [ALD2, AC4]
    #     features: [ALDF0, ALDF1, ALDF2, ALDF3]  # Override = True
    #     remove-features: [ALDF2, ACF4]
    child_linker_node = create_d()

    # child
    # linkers:
    #   flags: [AC0, AC3, AC4]  # Override = True
    #   remove-flags: [AC1, ALD1, AC2]
    #   features: [AC0, ACF3, ACF4]  # Override = True
    #   remove-features: [ACF1, ALDF1, ACF2]
    #   ld:
    #     flags: [ALD0, ALD1, ALD3]  # Override = True
    #     remove-flags: [ALD2, AC4]
    #     features: [ALDF0, ALDF1, ALDF3]  # Override = True
    #     remove-features: [ALDF2, ACF4]
    result = child_linker_node.resolve_extends(extended_base_linker_node, {}).unwrap()

    # Validate result
    assert result.common_linker.flags.override == True
    assert result.common_linker.flags.values == set(["AC0","AC3", "AC4"])
    assert result.common_linker.flags.remove_modifiers.values == set(["AC1", "ALD1", "AC2"])
    assert result.common_linker.features.override == True
    assert result.common_linker.features.values == set(["ACF0", "ACF3", "ACF4"])
    assert result.common_linker.features.remove_modifiers.values == set(["ACF1", "ALDF1", "ACF2"])
    ld = result.linker_overrides.get("ld")
    assert ld
    assert ld.flags.override == True
    assert ld.flags.values == set(["ALD0", "ALD1", "ALD3"])
    assert ld.flags.remove_modifiers.values == set(["ALD2", "AC4"]) 
    assert ld.features.override == True
    assert ld.features.values == set(["ALDF0", "ALDF1", "ALDF3"])
    assert ld.features.remove_modifiers.values == set(["ALDF2", "ACF4"]) 

def test_a_extends_3():
    # linkers:
    #   flags: [C1, C2] # Override = False
    #   remove-flags: [C1, C3]
    #   features: [CF1, CF2] # Override = False
    #   remove-features: [CF1, CF3]
    #   ld:
    #     flags: [LD0, LD1, C3, LD2] # Override = True
    #     remove-flags: [LD2]
    #     features: [LDF0, LDF1, CF3, LDF2] # Override = True
    #     remove-features: [LDF2]
    base_linker_node = create_3()

    #  linkers: (Extended)
    #   flags: [C2] # Override = False
    #   remove-flags: [C1, C3]
    #   features: [CF2] # Override = False
    #   remove-features: [CF1, CF3]
    #   ld:
    #     flags: [LD0, LD1, C3] # Override = True
    #     remove-flags: [LD2]
    #     features: [LDF0, LDF1, CF3] # Override = True
    #     remove-features: [LDF2]
    extended_base_linker_node = base_linker_node.resolve_extends(None, {}).unwrap()

    # child 'linkers:' extends extended_base_linker_node
    # linkers:
    #   flags: [AC1, AC3, AC4]  # Override = False
    #   remove-flags: [AC1, ALD1, AC2]
    #   features: [ACF1, ACF3, ACF4]  # Override = False
    #   remove-features: [ACF1, ALDF1, ACF2]
    #   ld:
    #     flags: [ALD1, ALD2, ALD3]  # Override = False
    #     remove-flags: [ALD2, AC4]
    #     features: [ALDF1, ALDF2, ALDF3]  # Override = False
    #     remove-features: [ALDF2, ACF4]
    child_linker_node = create_a()

    # child
    # linkers: (Extended)
    #   flags: [AC3, AC4]  # Override = False
    #   remove-flags: [AC1, ALD1, AC2]
    #   features: [ACF3, ACF4]  # Override = False
    #   remove-features: [ACF1, ALDF1, ACF2]
    #   ld:
    #     flags: [ALD1, ALD3, AC3, LD0, LD1, C3]  # Override = False
    #     remove-flags: [ALD2, AC4]
    #     features: [ALDF1, ALDF3, ACF3, CF0, CF2, LDF1, CF3]  # Override = False
    #     remove-features: [ALDF2, ACF4]
    result = child_linker_node.resolve_extends(extended_base_linker_node, {}).unwrap()

    # Validate result
    assert result.common_linker.flags.override == False
    assert result.common_linker.flags.values == set(["AC3", "AC4"])
    assert result.common_linker.flags.remove_modifiers.values == set(["AC1", "ALD1", "AC2"])
    assert result.common_linker.features.override == False
    assert result.common_linker.features.values == set(["ACF3", "ACF4"])
    assert result.common_linker.features.remove_modifiers.values == set(["ACF1", "ALDF1", "ACF2"])
    ld = result.linker_overrides.get("ld")
    assert ld
    assert ld.flags.override == False
    assert ld.flags.values == set(["ALD1", "ALD3", "AC3", "LD0", "LD1", "C3"])
    assert ld.flags.remove_modifiers.values == set(["ALD2", "AC4"]) 
    assert ld.features.override == False
    assert ld.features.values == set(["ALDF1", "ALDF3", "ACF3", "LDF0", "LDF1", "CF3"])
    assert ld.features.remove_modifiers.values == set(["ALDF2", "ACF4"]) 

def test_b_extends_3():
    # linkers:
    #   flags: [C1, C2] # Override = False
    #   remove-flags: [C1, C3]
    #   features: [CF1, CF2] # Override = False
    #   remove-features: [CF1, CF3]
    #   ld:
    #     flags: [LD0, LD1, C3, LD2] # Override = True
    #     remove-flags: [LD2]
    #     features: [LDF0, LDF1, CF3, LDF2] # Override = True
    #     remove-features: [LDF2]
    base_linker_node = create_3()

    #  linkers: (Extended)
    #   flags: [C2] # Override = False
    #   remove-flags: [C1, C3]
    #   features: [CF2] # Override = False
    #   remove-features: [CF1, CF3]
    #   ld:
    #     flags: [LD0, LD1, C3] # Override = True
    #     remove-flags: [LD2]
    #     features: [LDF0, LDF1, CF3] # Override = True
    #     remove-features: [LDF2]
    extended_base_linker_node = base_linker_node.resolve_extends(None, {}).unwrap()
  
    # child 'linkers:' extends extended_base_linker_node
    # linkers:
    #   flags: [AC0, AC1, AC3, AC4] # Override = True
    #   remove-flags: [AC1, ALD1, AC2]
    #   features: [ACF0, ACF1, ACF3, ACF4] # Override = True
    #   remove-features: [ACF1, ALDF1, ACF2]
    #   ld:
    #     flags: [ALD1, ALD2, ALD3] # Override = False
    #     remove-flags: [ALD2, AC4]
    #     features: [ALDF1, ALDF2, ALDF3] # Override = False
    #     remove-features: [ALDF2, ACF4]
    child_linker_node = create_b()

    # child
    # linkers: (Extended)
    #   flags: [AC0, AC3, AC4] # Override = True
    #   remove-flags: [AC1, ALD1, AC2]
    #   features: [ACF0, ACF3, ACF4] # Override = True
    #   remove-features: [ACF1, ALDF1, ACF2]
    #   ld:
    #     flags: [ALD1, ALD3, AC0, AC3] # Override = False
    #     remove-flags: [ALD2, AC4]
    #     features: [ALDF1, ALDF3, ACF0, ACF3] # Override = False
    #     remove-features: [ALDF2, ACF4]
    result = child_linker_node.resolve_extends(extended_base_linker_node, {}).unwrap()

    # Validate result
    assert result.common_linker.flags.override == True
    assert result.common_linker.flags.values == set(["AC0", "AC3", "AC4"])
    assert result.common_linker.flags.remove_modifiers.values == set(["AC1", "ALD1", "AC2"])
    assert result.common_linker.features.override == True
    assert result.common_linker.features.values == set(["ACF0", "ACF3", "ACF4"])
    assert result.common_linker.features.remove_modifiers.values == set(["ACF1", "ALDF1", "ACF2"])
    ld = result.linker_overrides.get("ld")
    assert ld
    assert ld.flags.override == False
    assert ld.flags.values == set(["ALD1", "ALD3", "AC0", "AC3"])
    assert ld.flags.remove_modifiers.values == set(["ALD2", "AC4"]) 
    assert ld.features.override == False
    assert ld.features.values == set(["ALDF1", "ALDF3", "ACF0", "ACF3"])
    assert ld.features.remove_modifiers.values == set(["ALDF2", "ACF4"]) 

def test_c_extends_3():
    # linkers:
    #   flags: [C1, C2] # Override = False
    #   remove-flags: [C1, C3]
    #   features: [CF1, CF2] # Override = False
    #   remove-features: [CF1, CF3]
    #   ld:
    #     flags: [LD0, LD1, C3, LD2] # Override = True
    #     remove-flags: [LD2]
    #     features: [LDF0, LDF1, CF3, LDF2] # Override = True
    #     remove-features: [LDF2]
    base_linker_node = create_3()

    #  linkers: (Extended)
    #   flags: [C2] # Override = False
    #   remove-flags: [C1, C3]
    #   features: [CF2] # Override = False
    #   remove-features: [CF1, CF3]
    #   ld:
    #     flags: [LD0, LD1, C3] # Override = True
    #     remove-flags: [LD2]
    #     features: [LDF0, LDF1, CF3] # Override = True
    #     remove-features: [LDF2]
    extended_base_linker_node = base_linker_node.resolve_extends(None, {}).unwrap()

    # child 'linkers:' extends extended_base_linker_node
    # linkers:
    #   flags: [AC1, AC3, AC4]  # Override = False
    #   remove-flags: [AC1, ALD1, AC2]
    #   features: [ACF1, ACF3, ACF4]  # Override = False
    #   remove-features: [ACF1, ALDF1, ACF2]
    #   ld:
    #     flags: [ALD0, ALD1, ALD2, ALD3]  # Override = True
    #     remove-flags: [ALD2, AC4]
    #     features: [ALDF0, ALDF1, ALDF2, ALDF3]  # Override = True
    #     remove-features: [ALDF2, ACF4]
    child_linker_node = create_c()

    # child
    # linkers: (Extended)
    #   flags: [AC3, AC4]  # Override = False
    #   remove-flags: [AC1, ALD1, AC2]
    #   features: [ ACF3, ACF4]  # Override = False
    #   remove-features: [ACF1, ALDF1, ACF2]
    #   ld:
    #     flags: [ALD0, ALD1, ALD3]  # Override = True
    #     remove-flags: [ALD2, AC4]
    #     features: [ALDF0, ALDF1, ALDF3]  # Override = True
    #     remove-features: [ALDF2, ACF4]
    result = child_linker_node.resolve_extends(extended_base_linker_node, {}).unwrap()

    # Validate result
    assert result.common_linker.flags.override == False
    assert result.common_linker.flags.values == set(["AC3", "AC4"])
    assert result.common_linker.flags.remove_modifiers.values == set(["AC1", "ALD1", "AC2"])
    assert result.common_linker.features.override == False
    assert result.common_linker.features.values == set(["ACF3", "ACF4"])
    assert result.common_linker.features.remove_modifiers.values == set(["ACF1", "ALDF1", "ACF2"])
    ld = result.linker_overrides.get("ld")
    assert ld
    assert ld.flags.override == True
    assert ld.flags.values == set(["ALD0", "ALD1", "ALD3"])
    assert ld.flags.remove_modifiers.values == set(["ALD2", "AC4"]) 
    assert ld.features.override == True
    assert ld.features.values == set(["ALDF0", "ALDF1", "ALDF3"])
    assert ld.features.remove_modifiers.values == set(["ALDF2", "ACF4"]) 

def test_d_extends_3():
    # linkers:
    #   flags: [C1, C2] # Override = False
    #   remove-flags: [C1, C3]
    #   features: [CF1, CF2] # Override = False
    #   remove-features: [CF1, CF3]
    #   ld:
    #     flags: [LD0, LD1, C3, LD2] # Override = True
    #     remove-flags: [LD2]
    #     features: [LDF0, LDF1, CF3, LDF2] # Override = True
    #     remove-features: [LDF2]
    base_linker_node = create_3()

    #  linkers: (Extended)
    #   flags: [C2] # Override = False
    #   remove-flags: [C1, C3]
    #   features: [CF2] # Override = False
    #   remove-features: [CF1, CF3]
    #   ld:
    #     flags: [LD0, LD1, C3] # Override = True
    #     remove-flags: [LD2]
    #     features: [LDF0, LDF1, CF3] # Override = True
    #     remove-features: [LDF2]
    extended_base_linker_node = base_linker_node.resolve_extends(None, {}).unwrap()
  
    # child 'linkers:' extends extended_base_linker_node
    # linkers:
    #   flags: [AC0, AC1, AC3, AC4]  # Override = True
    #   remove-flags: [AC1, ALD1, AC2]
    #   features: [AC0, ACF1, ACF3, ACF4]  # Override = True
    #   remove-features: [ACF1, ALDF1, ACF2]
    #   ld:
    #     flags: [ALD0, ALD1, ALD2, ALD3]  # Override = True
    #     remove-flags: [ALD2, AC4]
    #     features: [ALDF0, ALDF1, ALDF2, ALDF3]  # Override = True
    #     remove-features: [ALDF2, ACF4]
    child_linker_node = create_d()

    # child
    # linkers:
    #   flags: [AC0, AC3, AC4]  # Override = True
    #   remove-flags: [AC1, ALD1, AC2]
    #   features: [AC0, ACF3, ACF4]  # Override = True
    #   remove-features: [ACF1, ALDF1, ACF2]
    #   ld:
    #     flags: [ALD0, ALD1, ALD3]  # Override = True
    #     remove-flags: [ALD2, AC4]
    #     features: [ALDF0, ALDF1, ALDF3]  # Override = True
    #     remove-features: [ALDF2, ACF4]
    result = child_linker_node.resolve_extends(extended_base_linker_node, {}).unwrap()

    # Validate result
    assert result.common_linker.flags.override == True
    assert result.common_linker.flags.values == set(["AC0","AC3", "AC4"])
    assert result.common_linker.flags.remove_modifiers.values == set(["AC1", "ALD1", "AC2"])
    assert result.common_linker.features.override == True
    assert result.common_linker.features.values == set(["ACF0", "ACF3", "ACF4"])
    assert result.common_linker.features.remove_modifiers.values == set(["ACF1", "ALDF1", "ACF2"])
    ld = result.linker_overrides.get("ld")
    assert ld
    assert ld.flags.override == True
    assert ld.flags.values == set(["ALD0", "ALD1", "ALD3"])
    assert ld.flags.remove_modifiers.values == set(["ALD2", "AC4"]) 
    assert ld.features.override == True
    assert ld.features.values == set(["ALDF0", "ALDF1", "ALDF3"])
    assert ld.features.remove_modifiers.values == set(["ALDF2", "ACF4"]) 

def test_a_extends_4():
    # linkers:
    #   flags: [C0, C1, C2] # Override = True
    #   remove-flags: [C1, C3]
    #   features: [CF0, CF1, CF2] # Override = True
    #   remove-features: [CF1, CF3]
    #   ld:
    #     flags: [LD0, LD1, C3, LD2] # Override = True
    #     remove-flags: [LD2]
    #     features: [LDF0, LDF1, CF3, LDF2] # Override = True
    #     remove-features: [LDF2]
    base_linker_node = create_4()

    # linkers: (Extended)
    #   flags: [C0, C2] # Override = True
    #   remove-flags: [C1, C3]
    #   features: [CF0, CF2] # Override = True
    #   remove-features: [CF1, CF3]
    #   ld:
    #     flags: [LD0, LD1, C3] # Override = True
    #     remove-flags: [LD2]
    #     features: [LDF0, LDF1, CF3] # Override = True
    #     remove-features: [LDF2]
    extended_base_linker_node = base_linker_node.resolve_extends(None, {}).unwrap()

    # child 'linkers:' extends extended_base_linker_node
    # linkers:
    #   flags: [AC1, AC3, AC4]  # Override = False
    #   remove-flags: [AC1, ALD1, AC2]
    #   features: [ACF1, ACF3, ACF4]  # Override = False
    #   remove-features: [ACF1, ALDF1, ACF2]
    #   ld:
    #     flags: [ALD1, ALD2, ALD3]  # Override = False
    #     remove-flags: [ALD2, AC4]
    #     features: [ALDF1, ALDF2, ALDF3]  # Override = False
    #     remove-features: [ALDF2, ACF4]
    child_linker_node = create_a()

    # child
    # linkers: (Extended)
    #   flags: [AC3, AC4]  # Override = False
    #   remove-flags: [AC1, ALD1, AC2]
    #   features: [ACF3, ACF4]  # Override = False
    #   remove-features: [ACF1, ALDF1, ACF2]
    #   ld:
    #     flags: [ALD1, ALD3, AC3, LD0, LD1, C3]  # Override = False
    #     remove-flags:  [ALD2, AC4]
    #     features: [ALDF1, ALDF3, ACF3, CF0, CF2, LDF1, CF3]  # Override = False
    #     remove-features:  [ALDF2, ACF4]
    result = child_linker_node.resolve_extends(extended_base_linker_node, {}).unwrap()

    # Validate result
    assert result.common_linker.flags.override == False
    assert result.common_linker.flags.values == set(["AC3", "AC4"])
    assert result.common_linker.flags.remove_modifiers.values == set(["AC1", "ALD1", "AC2"])
    assert result.common_linker.features.override == False
    assert result.common_linker.features.values == set(["ACF3", "ACF4"])
    assert result.common_linker.features.remove_modifiers.values == set(["ACF1", "ALDF1", "ACF2"])
    ld = result.linker_overrides.get("ld")
    assert ld
    assert ld.flags.override == False
    assert ld.flags.values == set(["ALD1", "ALD3", "AC3", "LD0", "LD1", "C3"])
    assert ld.flags.remove_modifiers.values == set(["ALD2", "AC4"]) 
    assert ld.features.override == False
    assert ld.features.values == set(["ALDF1", "ALDF3", "ACF3", "LDF0", "LDF1", "CF3"])
    assert ld.features.remove_modifiers.values == set(["ALDF2", "ACF4"]) 

def test_b_extends_4():
    # linkers:
    #   flags: [C0, C1, C2] # Override = True
    #   remove-flags: [C1, C3]
    #   features: [CF0, CF1, CF2] # Override = True
    #   remove-features: [CF1, CF3]
    #   ld:
    #     flags: [LD0, LD1, C3, LD2] # Override = True
    #     remove-flags: [LD2]
    #     features: [LDF0, LDF1, CF3, LDF2] # Override = True
    #     remove-features: [LDF2]
    base_linker_node = create_4()

    # linkers: (Extended)
    #   flags: [C0, C2] # Override = True
    #   remove-flags: [C1, C3]
    #   features: [CF0, CF2] # Override = True
    #   remove-features: [CF1, CF3]
    #   ld:
    #     flags: [LD0, LD1, C3] # Override = True
    #     remove-flags: [LD2]
    #     features: [LDF0, LDF1, CF3] # Override = True
    #     remove-features: [LDF2]
    extended_base_linker_node = base_linker_node.resolve_extends(None, {}).unwrap()
  
    # child 'linkers:' extends extended_base_linker_node
    # linkers:
    #   flags: [AC0, AC1, AC3, AC4] # Override = True
    #   remove-flags: [AC1, ALD1, AC2]
    #   features: [ACF0, ACF1, ACF3, ACF4] # Override = True
    #   remove-features: [ACF1, ALDF1, ACF2]
    #   ld:
    #     flags: [ALD1, ALD2, ALD3] # Override = False
    #     remove-flags: [ALD2, AC4]
    #     features: [ALDF1, ALDF2, ALDF3] # Override = False
    #     remove-features: [ALDF2, ACF4]
    child_linker_node = create_b()

    # child
    # linkers: (Extended)
    #   flags: [AC0, AC3, AC4] # Override = True
    #   remove-flags: [AC1, ALD1, AC2]
    #   features: [ACF0, ACF3, ACF4] # Override = True
    #   remove-features: [ACF1, ALDF1, ACF2]
    #   ld:
    #     flags: [ALD1, ALD3, AC0, AC3] # Override = False
    #     remove-flags: [ALD2, AC4]
    #     features: [ALDF1, ALDF3, ACF0, ACF3] # Override = False
    #     remove-features: [ALDF2, ACF4]
    result = child_linker_node.resolve_extends(extended_base_linker_node, {}).unwrap()

    # Validate result
    assert result.common_linker.flags.override == True
    assert result.common_linker.flags.values == set(["AC0", "AC3", "AC4"])
    assert result.common_linker.flags.remove_modifiers.values == set(["AC1", "ALD1", "AC2"])
    assert result.common_linker.features.override == True
    assert result.common_linker.features.values == set(["ACF0", "ACF3", "ACF4"])
    assert result.common_linker.features.remove_modifiers.values == set(["ACF1", "ALDF1", "ACF2"])
    ld = result.linker_overrides.get("ld")
    assert ld
    assert ld.flags.override == False
    assert ld.flags.values == set(["ALD1", "ALD3", "AC0", "AC3"])
    assert ld.flags.remove_modifiers.values == set(["ALD2", "AC4"]) 
    assert ld.features.override == False
    assert ld.features.values == set(["ALDF1", "ALDF3", "ACF0", "ACF3"])
    assert ld.features.remove_modifiers.values == set(["ALDF2", "ACF4"]) 

def test_c_extends_4():
    # linkers:
    #   flags: [C0, C1, C2] # Override = True
    #   remove-flags: [C1, C3]
    #   features: [CF0, CF1, CF2] # Override = True
    #   remove-features: [CF1, CF3]
    #   ld:
    #     flags: [LD0, LD1, C3, LD2] # Override = True
    #     remove-flags: [LD2]
    #     features: [LDF0, LDF1, CF3, LDF2] # Override = True
    #     remove-features: [LDF2]
    base_linker_node = create_4()

    # linkers: (Extended)
    #   flags: [C0, C2] # Override = True
    #   remove-flags: [C1, C3]
    #   features: [CF0, CF2] # Override = True
    #   remove-features: [CF1, CF3]
    #   ld:
    #     flags: [LD0, LD1, C3] # Override = True
    #     remove-flags: [LD2]
    #     features: [LDF0, LDF1, CF3] # Override = True
    #     remove-features: [LDF2]
    extended_base_linker_node = base_linker_node.resolve_extends(None, {}).unwrap()
  
    # child 'linkers:' extends extended_base_linker_node
    # linkers:
    #   flags: [AC1, AC3, AC4]  # Override = False
    #   remove-flags: [AC1, ALD1, AC2]
    #   features: [ACF1, ACF3, ACF4]  # Override = False
    #   remove-features: [ACF1, ALDF1, ACF2]
    #   ld:
    #     flags: [ALD0, ALD1, ALD2, ALD3]  # Override = True
    #     remove-flags: [ALD2, AC4]
    #     features: [ALDF0, ALDF1, ALDF2, ALDF3]  # Override = True
    #     remove-features: [ALDF2, ACF4]
    child_linker_node = create_c()

    # child
    # linkers: (Extended)
    #   flags: [AC3, AC4]  # Override = False
    #   remove-flags: [AC1, ALD1, AC2]
    #   features: [ ACF3, ACF4]  # Override = False
    #   remove-features: [ACF1, ALDF1, ACF2]
    #   ld:
    #     flags: [ALD0, ALD1, ALD3]  # Override = True
    #     remove-flags: [ALD2, AC4]
    #     features: [ALDF0, ALDF1, ALDF3]  # Override = True
    #     remove-features: [ALDF2, ACF4]
    result = child_linker_node.resolve_extends(extended_base_linker_node, {}).unwrap()

    # Validate result
    assert result.common_linker.flags.override == False
    assert result.common_linker.flags.values == set(["AC3", "AC4"])
    assert result.common_linker.flags.remove_modifiers.values == set(["AC1", "ALD1", "AC2"])
    assert result.common_linker.features.override == False
    assert result.common_linker.features.values == set(["ACF3", "ACF4"])
    assert result.common_linker.features.remove_modifiers.values == set(["ACF1", "ALDF1", "ACF2"])
    ld = result.linker_overrides.get("ld")
    assert ld
    assert ld.flags.override == True
    assert ld.flags.values == set(["ALD0", "ALD1", "ALD3"])
    assert ld.flags.remove_modifiers.values == set(["ALD2", "AC4"]) 
    assert ld.features.override == True
    assert ld.features.values == set(["ALDF0", "ALDF1", "ALDF3"])
    assert ld.features.remove_modifiers.values == set(["ALDF2", "ACF4"]) 

def test_d_extends_4():
    # linkers:
    #   flags: [C0, C1, C2] # Override = True
    #   remove-flags: [C1, C3]
    #   features: [CF0, CF1, CF2] # Override = True
    #   remove-features: [CF1, CF3]
    #   ld:
    #     flags: [LD0, LD1, C3, LD2] # Override = True
    #     remove-flags: [LD2]
    #     features: [LDF0, LDF1, CF3, LDF2] # Override = True
    #     remove-features: [LDF2]
    base_linker_node = create_4()

    # linkers: (Extended)
    #   flags: [C0, C2] # Override = True
    #   remove-flags: [C1, C3]
    #   features: [CF0, CF2] # Override = True
    #   remove-features: [CF1, CF3]
    #   ld:
    #     flags: [LD0, LD1, C3] # Override = True
    #     remove-flags: [LD2]
    #     features: [LDF0, LDF1, CF3] # Override = True
    #     remove-features: [LDF2]
    extended_base_linker_node = base_linker_node.resolve_extends(None, {}).unwrap()

    # child 'linkers:' extends extended_base_linker_node
    # linkers:
    #   flags: [AC0, AC1, AC3, AC4]  # Override = True
    #   remove-flags: [AC1, ALD1, AC2]
    #   features: [AC0, ACF1, ACF3, ACF4]  # Override = True
    #   remove-features: [ACF1, ALDF1, ACF2]
    #   ld:
    #     flags: [ALD0, ALD1, ALD2, ALD3]  # Override = True
    #     remove-flags: [ALD2, AC4]
    #     features: [ALDF0, ALDF1, ALDF2, ALDF3]  # Override = True
    #     remove-features: [ALDF2, ACF4]
    child_linker_node = create_d()

    # child
    # linkers:
    #   flags: [AC0, AC3, AC4]  # Override = True
    #   remove-flags: [AC1, ALD1, AC2]
    #   features: [AC0, ACF3, ACF4]  # Override = True
    #   remove-features: [ACF1, ALDF1, ACF2]
    #   ld:
    #     flags: [ALD0, ALD1, ALD3]  # Override = True
    #     remove-flags: [ALD2, AC4]
    #     features: [ALDF0, ALDF1, ALDF3]  # Override = True
    #     remove-features: [ALDF2, ACF4]
    result = child_linker_node.resolve_extends(extended_base_linker_node, {}).unwrap()

    # Validate result
    assert result.common_linker.flags.override == True
    assert result.common_linker.flags.values == set(["AC0","AC3", "AC4"])
    assert result.common_linker.flags.remove_modifiers.values == set(["AC1", "ALD1", "AC2"])
    assert result.common_linker.features.override == True
    assert result.common_linker.features.values == set(["ACF0", "ACF3", "ACF4"])
    assert result.common_linker.features.remove_modifiers.values == set(["ACF1", "ALDF1", "ACF2"])
    ld = result.linker_overrides.get("ld")
    assert ld
    assert ld.flags.override == True
    assert ld.flags.values == set(["ALD0", "ALD1", "ALD3"])
    assert ld.flags.remove_modifiers.values == set(["ALD2", "AC4"]) 
    assert ld.features.override == True
    assert ld.features.values == set(["ALDF0", "ALDF1", "ALDF3"])
    assert ld.features.remove_modifiers.values == set(["ALDF2", "ACF4"]) 

def test_a_extends_common_only_1():
    # linkers:
    #   flags: [E0, E1, E3] # Override = True
    #   remove-flags: [E1, E2]
    #   features: [EF0, EF1, EF3] # Override = True
    #   remove-features: [EF1, EF2]
    base_linker_node = create_common_only_1()

    # linkers:
    #   flags: [E0, E3] # Override = True
    #   remove-flags:  [E1, E2]
    #   features: [EF0, EF3] # Override = True
    #   remove-features: [EF1, EF2]
    extended_base_linker_node = base_linker_node.resolve_extends(None, {}).unwrap()

    # child 'linkers:' extends extended_base_linker_node
    # linkers:
    #   flags: [AC1, AC3, AC4]  # Override = False
    #   remove-flags: [AC1, ALD1, AC2]
    #   features: [ACF1, ACF3, ACF4]  # Override = False
    #   remove-features: [ACF1, ALDF1, ACF2]
    #   ld:
    #     flags: [ALD1, ALD2, ALD3]  # Override = False
    #     remove-flags: [ALD2, AC4]
    #     features: [ALDF1, ALDF2, ALDF3]  # Override = False
    #     remove-features: [ALDF2, ACF4]
    child_linker_node = create_a()

    # child
    # linkers: (Extended)
    #   flags: [AC3, AC4]  # Override = False
    #   remove-flags: [AC1, ALD1, AC2]
    #   features: [ACF3, ACF4]  # Override = False
    #   remove-features: [ACF1, ALDF1, ACF2]
    #   ld:
    #     flags: [ALD1, ALD3, AC3, E0, E3]  # Override = False
    #     remove-flags: [ALD2, AC4]
    #     features: [ALDF1, ALDF3, ACF3,  EF0, EF3]  # Override = False
    #     remove-features: [ALDF2, ACF4]
    result = child_linker_node.resolve_extends(extended_base_linker_node, {}).unwrap()

    # Validate result
    assert result.common_linker.flags.override == False
    assert result.common_linker.flags.values == set(["AC3", "AC4"])
    assert result.common_linker.flags.remove_modifiers.values == set(["AC1", "ALD1", "AC2"])
    assert result.common_linker.features.override == False
    assert result.common_linker.features.values == set(["ACF3", "ACF4"])
    assert result.common_linker.features.remove_modifiers.values == set(["ACF1", "ALDF1", "ACF2"])
    ld = result.linker_overrides.get("ld")
    assert ld
    assert ld.flags.override == False
    assert ld.flags.values == set(["ALD1", "ALD3", "AC3", "E0", "E3"])
    assert ld.flags.remove_modifiers.values == set(["ALD2", "AC4"]) 
    assert ld.features.override == False
    assert ld.features.values == set(["ALDF1", "ALDF3", "ACF3", "EF0", "EF3"])
    assert ld.features.remove_modifiers.values == set(["ALDF2", "ACF4"]) 

def test_b_extends_common_only_1():
    # linkers:
    #   flags: [E0, E1, E3] # Override = True
    #   remove-flags: [E1, E2]
    #   features: [EF0, EF1, EF3] # Override = True
    #   remove-features: [EF1, EF2]
    base_linker_node = create_common_only_1()

    # linkers:
    #   flags: [E0, E3] # Override = True
    #   remove-flags: [E1, E2]
    #   features: [EF0, EF3] # Override = True
    #   remove-features: [EF1, EF2]
    extended_base_linker_node = base_linker_node.resolve_extends(None, {}).unwrap()

    # child 'linkers:' extends extended_base_linker_node
    # linkers:
    #   flags: [AC0, AC1, AC3, AC4] # Override = True
    #   remove-flags: [AC1, ALD1, AC2]
    #   features: [ACF0, ACF1, ACF3, ACF4] # Override = True
    #   remove-features: [ACF1, ALDF1, ACF2]
    #   ld:
    #     flags: [ALD1, ALD2, ALD3] # Override = False
    #     remove-flags: [ALD2, AC4]
    #     features: [ALDF1, ALDF2, ALDF3] # Override = False
    #     remove-features: [ALDF2, ACF4]
    child_linker_node = create_b()

    # child
    # linkers: (Extended)
    #   flags: [AC0, AC3, AC4] # Override = True
    #   remove-flags: [AC1, ALD1, AC2]
    #   features: [ACF0, ACF3, ACF4] # Override = True
    #   remove-features: [ACF1, ALDF1, ACF2]
    #   ld:
    #     flags: [ALD1, ALD3, AC0, AC3] # Override = False
    #     remove-flags: [ALD2, AC4]
    #     features: [ALDF1, ALDF3, ACF0, ACF3] # Override = False
    #     remove-features: [ALDF2, ACF4]
    result = child_linker_node.resolve_extends(extended_base_linker_node, {}).unwrap()

    # Validate result
    assert result.common_linker.flags.override == True
    assert result.common_linker.flags.values == set(["AC0", "AC3", "AC4"])
    assert result.common_linker.flags.remove_modifiers.values == set(["AC1", "ALD1", "AC2"])
    assert result.common_linker.features.override == True
    assert result.common_linker.features.values == set(["ACF0", "ACF3", "ACF4"])
    assert result.common_linker.features.remove_modifiers.values == set(["ACF1", "ALDF1", "ACF2"])
    ld = result.linker_overrides.get("ld")
    assert ld
    assert ld.flags.override == False
    assert ld.flags.values == set(["ALD1", "ALD3", "AC0", "AC3"])
    assert ld.flags.remove_modifiers.values == set(["ALD2", "AC4"]) 
    assert ld.features.override == False
    assert ld.features.values == set(["ALDF1", "ALDF3", "ACF0", "ACF3"])
    assert ld.features.remove_modifiers.values == set(["ALDF2", "ACF4"]) 

def test_c_extends_common_only_1():
    # linkers:
    #   flags: [E0, E1, E3] # Override = True
    #   remove-flags: [E1, E2]
    #   features: [EF0, EF1, EF3] # Override = True
    #   remove-features: [EF1, EF2]
    base_linker_node = create_common_only_1()

    # linkers:
    #   flags: [E0, E3] # Override = True
    #   remove-flags: [E1, E2]
    #   features: [EF0, EF3] # Override = True
    #   remove-features: [EF1, EF2]
    extended_base_linker_node = base_linker_node.resolve_extends(None, {}).unwrap()

    # child 'linkers:' extends extended_base_linker_node
    # linkers:
    #   flags: [AC1, AC3, AC4]  # Override = False
    #   remove-flags: [AC1, ALD1, AC2]
    #   features: [ACF1, ACF3, ACF4]  # Override = False
    #   remove-features: [ACF1, ALDF1, ACF2]
    #   ld:
    #     flags: [ALD0, ALD1, ALD2, ALD3]  # Override = True
    #     remove-flags: [ALD2, AC4]
    #     features: [ALDF0, ALDF1, ALDF2, ALDF3]  # Override = True
    #     remove-features: [ALDF2, ACF4]
    child_linker_node = create_c()

    # child
    # linkers: (Extended)
    #   flags: [AC3, AC4]  # Override = False
    #   remove-flags: [AC1, ALD1, AC2]
    #   features: [ACF3, ACF4]  # Override = False
    #   remove-features: [ACF1, ALDF1, ACF2]
    #   ld:
    #     flags: [ALD0, ALD1, ALD3]  # Override = True
    #     remove-flags: [ALD2, AC4]
    #     features: [ALDF0, ALDF1, ALDF3]  # Override = True
    #     remove-features: [ALDF2, ACF4]
    result = child_linker_node.resolve_extends(extended_base_linker_node, {}).unwrap()

    # Validate result
    assert result.common_linker.flags.override == False
    assert result.common_linker.flags.values == set(["AC3", "AC4"])
    assert result.common_linker.flags.remove_modifiers.values == set(["AC1", "ALD1", "AC2"])
    assert result.common_linker.features.override == False
    assert result.common_linker.features.values == set(["ACF3", "ACF4"])
    assert result.common_linker.features.remove_modifiers.values == set(["ACF1", "ALDF1", "ACF2"])
    ld = result.linker_overrides.get("ld")
    assert ld
    assert ld.flags.override == True
    assert ld.flags.values == set(["ALD0", "ALD1", "ALD3"])
    assert ld.flags.remove_modifiers.values == set(["ALD2", "AC4"]) 
    assert ld.features.override == True
    assert ld.features.values == set(["ALDF0", "ALDF1", "ALDF3"])
    assert ld.features.remove_modifiers.values == set(["ALDF2", "ACF4"]) 
    
def test_d_extends_common_only_1():
    # linkers:
    #   flags: [E0, E1, E3] # Override = True
    #   remove-flags: [E1, E2]
    #   features: [EF0, EF1, EF3] # Override = True
    #   remove-features: [EF1, EF2]
    base_linker_node = create_common_only_1()

    # linkers:
    #   flags: [E0, E3] # Override = True
    #   remove-flags: [E1, E2]
    #   features: [EF0, EF3] # Override = True
    #   remove-features: [EF1, EF2]
    extended_base_linker_node = base_linker_node.resolve_extends(None, {}).unwrap()

    # child 'linkers:' extends extended_base_linker_node
    # linkers:
    #   flags: [AC0, AC1, AC3, AC4]  # Override = True
    #   remove-flags: [AC1, ALD1, AC2]
    #   features: [AC0, ACF1, ACF3, ACF4]  # Override = True
    #   remove-features: [ACF1, ALDF1, ACF2]
    #   ld:
    #     flags: [ALD0, ALD1, ALD2, ALD3]  # Override = True
    #     remove-flags: [ALD2, AC4]
    #     features: [ALDF0, ALDF1, ALDF2, ALDF3]  # Override = True
    #     remove-features: [ALDF2, ACF4]
    child_linker_node = create_d()

    # child
    # linkers: (Extended)
    #   flags: [AC0, AC3, AC4]  # Override = True
    #   remove-flags: [AC1, ALD1, AC2]
    #   features: [AC0, ACF3, ACF4]  # Override = True
    #   remove-features: [ACF1, ALDF1, ACF2]
    #   ld:
    #     flags: [ALD0, ALD1, ALD3]  # Override = True
    #     remove-flags: [ALD2, AC4]
    #     features: [ALDF0, ALDF1, ALDF3]  # Override = True
    #     remove-features: [ALDF2, ACF4]
    result = child_linker_node.resolve_extends(extended_base_linker_node, {}).unwrap()

    # Validate result
    assert result.common_linker.flags.override == True
    assert result.common_linker.flags.values == set(["AC0", "AC3", "AC4"])
    assert result.common_linker.flags.remove_modifiers.values == set(["AC1", "ALD1", "AC2"])
    assert result.common_linker.features.override == True
    assert result.common_linker.features.values == set(["ACF0", "ACF3", "ACF4"])
    assert result.common_linker.features.remove_modifiers.values == set(["ACF1", "ALDF1", "ACF2"])
    ld = result.linker_overrides.get("ld")
    assert ld
    assert ld.flags.override == True
    assert ld.flags.values == set(["ALD0", "ALD1", "ALD3"])
    assert ld.flags.remove_modifiers.values == set(["ALD2", "AC4"]) 
    assert ld.features.override == True
    assert ld.features.values == set(["ALDF0", "ALDF1", "ALDF3"])
    assert ld.features.remove_modifiers.values == set(["ALDF2", "ACF4"]) 

def test_a_extends_common_only_2():
    # linkers:
    #   flags: [E1, E3] # Override = False
    #   remove-flags: [E1, E2]
    #   features: [EF1, EF3] # Override = False
    #   remove-features: [EF1, EF2]
    base_linker_node = create_common_only_2()

    # linkers:
    #   flags: [E3] # Override = False
    #   remove-flags: [E1, E2]
    #   features: [EF3] # Override = False
    #   remove-features: [EF1, EF2]
    extended_base_linker_node = base_linker_node.resolve_extends(None, {}).unwrap()

    # child 'linkers:' extends extended_base_linker_node
    # linkers:
    #   flags: [AC1, AC3, AC4]  # Override = False
    #   remove-flags: [AC1, ALD1, AC2]
    #   features: [ACF1, ACF3, ACF4]  # Override = False
    #   remove-features: [ACF1, ALDF1, ACF2]
    #   ld:
    #     flags: [ALD1, ALD2, ALD3]  # Override = False
    #     remove-flags: [ALD2, AC4]
    #     features: [ALDF1, ALDF2, ALDF3]  # Override = False
    #     remove-features: [ALDF2, ACF4]
    child_linker_node = create_a()

    # child
    # linkers: (Extended)
    #   flags: [AC3, AC4]  # Override = False
    #   remove-flags: [AC1, ALD1, AC2]
    #   features: [ACF3, ACF4]  # Override = False
    #   remove-features: [ACF1, ALDF1, ACF2]
    #   ld:
    #     flags: [ALD1, ALD3, AC3, E3]  # Override = False
    #     remove-flags: [ALD2, AC4]
    #     features: [ALDF1, ALDF3, ACF3, EF3]  # Override = False
    #     remove-features: [ALDF2, ACF4]
    result = child_linker_node.resolve_extends(extended_base_linker_node, {}).unwrap()

    # Validate result
    assert result.common_linker.flags.override == False
    assert result.common_linker.flags.values == set(["AC3", "AC4"])
    assert result.common_linker.flags.remove_modifiers.values == set(["AC1", "ALD1", "AC2"])
    assert result.common_linker.features.override == False
    assert result.common_linker.features.values == set(["ACF3", "ACF4"])
    assert result.common_linker.features.remove_modifiers.values == set(["ACF1", "ALDF1", "ACF2"])
    ld = result.linker_overrides.get("ld")
    assert ld
    assert ld.flags.override == False
    assert ld.flags.values == set(["ALD1", "ALD3", "AC3", "E3"])
    assert ld.flags.remove_modifiers.values == set(["ALD2", "AC4"]) 
    assert ld.features.override == False
    assert ld.features.values == set(["ALDF1", "ALDF3", "ACF3", "EF3"])
    assert ld.features.remove_modifiers.values == set(["ALDF2", "ACF4"]) 

def test_b_extends_common_only_2():
    # linkers:
    #   flags: [E1, E3] # Override = False
    #   remove-flags: [E1, E2]
    #   features: [EF1, EF3] # Override = False
    #   remove-features: [EF1, EF2]
    base_linker_node = create_common_only_2()

    # linkers:
    #   flags: [E3] # Override = False
    #   remove-flags: [E1, E2]
    #   features: [EF3] # Override = False
    #   remove-features: [EF1, EF2]
    extended_base_linker_node = base_linker_node.resolve_extends(None, {}).unwrap()

    # child 'linkers:' extends extended_base_linker_node
    # linkers:
    #   flags: [AC0, AC1, AC3, AC4] # Override = True
    #   remove-flags: [AC1, ALD1, AC2]
    #   features: [ACF0, ACF1, ACF3, ACF4] # Override = True
    #   remove-features: [ACF1, ALDF1, ACF2]
    #   ld:
    #     flags: [ALD1, ALD2, ALD3] # Override = False
    #     remove-flags: [ALD2, AC4]
    #     features: [ALDF1, ALDF2, ALDF3] # Override = False
    #     remove-features: [ALDF2, ACF4]
    child_linker_node = create_b()

    # child
    # linkers: (Extended)
    #   flags: [AC0, AC3, AC4] # Override = True
    #   remove-flags: [AC1, ALD1, AC2]
    #   features: [ACF0, ACF3, ACF4] # Override = True
    #   remove-features: [ACF1, ALDF1, ACF2]
    #   ld:
    #     flags: [ALD1, ALD3, AC0, AC3] # Override = False
    #     remove-flags: [ALD2, AC4]
    #     features: [ALDF1, ALDF3, ACF0, ACF3] # Override = False
    #     remove-features: [ALDF2, ACF4]
    result = child_linker_node.resolve_extends(extended_base_linker_node, {}).unwrap()

    # Validate result
    assert result.common_linker.flags.override == True
    assert result.common_linker.flags.values == set(["AC0", "AC3", "AC4"])
    assert result.common_linker.flags.remove_modifiers.values == set(["AC1", "ALD1", "AC2"])
    assert result.common_linker.features.override == True
    assert result.common_linker.features.values == set(["ACF0", "ACF3", "ACF4"])
    assert result.common_linker.features.remove_modifiers.values == set(["ACF1", "ALDF1", "ACF2"])
    ld = result.linker_overrides.get("ld")
    assert ld
    assert ld.flags.override == False
    assert ld.flags.values == set(["ALD1", "ALD3", "AC0", "AC3"])
    assert ld.flags.remove_modifiers.values == set(["ALD2", "AC4"]) 
    assert ld.features.override == False
    assert ld.features.values == set(["ALDF1", "ALDF3", "ACF0", "ACF3"])
    assert ld.features.remove_modifiers.values == set(["ALDF2", "ACF4"]) 

def test_c_extends_common_only_2():
   # linkers:
    #   flags: [E1, E3] # Override = False
    #   remove-flags: [E1, E2]
    #   features: [EF1, EF3] # Override = False
    #   remove-features: [EF1, EF2]
    base_linker_node = create_common_only_2()

    # linkers:
    #   flags: [E3] # Override = False
    #   remove-flags: [E1, E2]
    #   features: [EF3] # Override = False
    #   remove-features: [EF1, EF2]
    extended_base_linker_node = base_linker_node.resolve_extends(None, {}).unwrap()

    # child 'linkers:' extends extended_base_linker_node
    # linkers:
    #   flags: [AC1, AC3, AC4]  # Override = False
    #   remove-flags: [AC1, ALD1, AC2]
    #   features: [ACF1, ACF3, ACF4]  # Override = False
    #   remove-features: [ACF1, ALDF1, ACF2]
    #   ld:
    #     flags: [ALD0, ALD1, ALD2, ALD3]  # Override = True
    #     remove-flags: [ALD2, AC4]
    #     features: [ALDF0, ALDF1, ALDF2, ALDF3]  # Override = True
    #     remove-features: [ALDF2, ACF4]
    child_linker_node = create_c()

    # child
    # linkers: (Extended)
    #   flags: [AC3, AC4]  # Override = False
    #   remove-flags: [AC1, ALD1, AC2]
    #   features: [ACF3, ACF4]  # Override = False
    #   remove-features:[ACF1, ALDF1, ACF2]
    #   ld:
    #     flags: [ALD0, ALD1, ALD3]  # Override = True
    #     remove-flags: [ALD2, AC4]
    #     features: [ALDF0, ALDF1, ALDF3]  # Override = True
    #     remove-features:  [ALDF2, ACF4]
    result = child_linker_node.resolve_extends(extended_base_linker_node, {}).unwrap()

    # Validate result
    assert result.common_linker.flags.override == False
    assert result.common_linker.flags.values == set(["AC3", "AC4"])
    assert result.common_linker.flags.remove_modifiers.values == set(["AC1", "ALD1", "AC2"])
    assert result.common_linker.features.override == False
    assert result.common_linker.features.values == set(["ACF3", "ACF4"])
    assert result.common_linker.features.remove_modifiers.values == set(["ACF1", "ALDF1", "ACF2"])
    ld = result.linker_overrides.get("ld")
    assert ld
    assert ld.flags.override == True
    assert ld.flags.values == set(["ALD0", "ALD1", "ALD3"])
    assert ld.flags.remove_modifiers.values == set(["ALD2", "AC4"]) 
    assert ld.features.override == True
    assert ld.features.values == set(["ALDF0", "ALDF1", "ALDF3"])
    assert ld.features.remove_modifiers.values == set(["ALDF2", "ACF4"]) 

def test_d_extends_common_only_2():
    # linkers:
    #   flags: [E1, E3] # Override = False
    #   remove-flags: [E1, E2]
    #   features: [EF1, EF3] # Override = False
    #   remove-features: [EF1, EF2]
    base_linker_node = create_common_only_2()

    # linkers:
    #   flags: [E3] # Override = False
    #   remove-flags: [E1, E2]
    #   features: [EF3] # Override = False
    #   remove-features: [EF1, EF2]
    extended_base_linker_node = base_linker_node.resolve_extends(None, {}).unwrap()

    # child 'linkers:' extends extended_base_linker_node
    # linkers:
    #   flags: [AC0, AC1, AC3, AC4]  # Override = True
    #   remove-flags: [AC1, ALD1, AC2]
    #   features: [AC0, ACF1, ACF3, ACF4]  # Override = True
    #   remove-features: [ACF1, ALDF1, ACF2]
    #   ld:
    #     flags: [ALD0, ALD1, ALD2, ALD3]  # Override = True
    #     remove-flags: [ALD2, AC4]
    #     features: [ALDF0, ALDF1, ALDF2, ALDF3]  # Override = True
    #     remove-features: [ALDF2, ACF4]
    child_linker_node = create_d()

    # child
    # linkers: (Extended)
    #   flags: [AC0, AC3, AC4]  # Override = True
    #   remove-flags: [AC1, ALD1, AC2]
    #   features: [AC0, ACF3, ACF4]  # Override = True
    #   remove-features: [ACF1, ALDF1, ACF2]
    #   ld:
    #     flags: [ALD0, ALD1, ALD3]  # Override = True
    #     remove-flags: [ALD2, AC4]
    #     features: [ALDF0, ALDF1, ALDF3]  # Override = True
    #     remove-features: [ALDF2, ACF4]
    result = child_linker_node.resolve_extends(extended_base_linker_node, {}).unwrap()

    # Validate result
    assert result.common_linker.flags.override == True
    assert result.common_linker.flags.values == set(["AC0", "AC3", "AC4"])
    assert result.common_linker.flags.remove_modifiers.values == set(["AC1", "ALD1", "AC2"])
    assert result.common_linker.features.override == True
    assert result.common_linker.features.values == set(["ACF0", "ACF3", "ACF4"])
    assert result.common_linker.features.remove_modifiers.values == set(["ACF1", "ALDF1", "ACF2"])
    ld = result.linker_overrides.get("ld")
    assert ld
    assert ld.flags.override == True
    assert ld.flags.values == set(["ALD0", "ALD1", "ALD3"])
    assert ld.flags.remove_modifiers.values == set(["ALD2", "AC4"]) 
    assert ld.features.override == True
    assert ld.features.values == set(["ALDF0", "ALDF1", "ALDF3"])
    assert ld.features.remove_modifiers.values == set(["ALDF2", "ACF4"]) 

def create_linker_only_1() : 
    """  
    linkers:
      ld:
        flags: [LD0, LD1, LD3] # Override = True
        remove-flags: [LD1, LD2] 
        features: [LDF0, LDF1, LDF3] # Override = True
        remove-features: [LDF1, LDF2] 
    """
    ld_flags = create_str_list(True, ["LD0", "LD1", "LD3"], ["LD1", "LD2"])
    ld_features = create_feature_str_list(True, ["LDF0", "LDF1", "LDF3"], ["LDF1", "LDF2"])
    ld_linker = create_specific_linker_override_node("ld", ld_flags, ld_features)
    linker_override_node = create_linker_override_node(None, None, ld_linker)
    assert linker_override_node.common_linker.flags.override == False
    assert linker_override_node.common_linker.flags.values == set([])
    assert linker_override_node.common_linker.flags.remove_modifiers.values == set([])
    assert linker_override_node.common_linker.features.override == False
    assert linker_override_node.common_linker.features.values == set([])
    assert linker_override_node.common_linker.features.remove_modifiers.values == set([])
    ld = linker_override_node.linker_overrides.get("ld")
    assert ld
    assert ld.flags.override == True
    assert ld.flags.values == set(["LD0", "LD1", "LD3"])
    assert ld.flags.remove_modifiers.values == set(["LD1", "LD2"]) 
    assert ld.features.override == True
    assert ld.features.values == set(["LDF0", "LDF1", "LDF3"])
    assert ld.features.remove_modifiers.values == set(["LDF1", "LDF2"]) 
    return linker_override_node

def create_linker_only_2() : 
    """  
    linkers:
        ld:
        flags: [LD1, LD3] # Override = False
        remove-flags: [LD1, LD2] 
        features: [LDF1, LDF3] # Override = False
        remove-features: [LDF1, LDF2] 
    """
    ld_flags = create_str_list(False, ["LD1", "LD3"], ["LD1", "LD2"])
    ld_features = create_feature_str_list(False, ["LDF1", "LDF3"], ["LDF1", "LDF2"])
    ld_linker = create_specific_linker_override_node("ld", ld_flags, ld_features)
    linker_override_node = create_linker_override_node(None, None, ld_linker)
    assert linker_override_node.common_linker.flags.override == False
    assert linker_override_node.common_linker.flags.values == set([])
    assert linker_override_node.common_linker.flags.remove_modifiers.values == set([])
    assert linker_override_node.common_linker.features.override == False
    assert linker_override_node.common_linker.features.values == set([])
    assert linker_override_node.common_linker.features.remove_modifiers.values == set([])
    ld = linker_override_node.linker_overrides.get("ld")
    assert ld
    assert ld.flags.override == False
    assert ld.flags.values == set(["LD1", "LD3"])
    assert ld.flags.remove_modifiers.values == set(["LD1", "LD2"]) 
    assert ld.features.override == False
    assert ld.features.values == set(["LDF1", "LDF3"])
    assert ld.features.remove_modifiers.values == set(["LDF1", "LDF2"]) 
    return linker_override_node
    

def test_linker_only_1():
    # linkers:
    #   ld:
    #     flags: [LD0, LD1, LD3] # Override = True
    #     remove-flags: [LD1, LD2] 
    #     features: [LDF0, LDF1, LDF3] # Override = True
    #     remove-features: [LDF1, LDF2]
    base_linker_node = create_linker_only_1()

    # linkers:
    #   ld:
    #     flags: [LD0, LD3] # Override = True
    #     remove-flags: [LD1, LD2] 
    #     features: [LDF0, LDF3] # Override = True
    #     remove-features: [LDF1, LDF2]
    result = base_linker_node.resolve_extends(None, {}).unwrap()

    # Validate result
    assert result.common_linker.flags.override == False
    assert result.common_linker.flags.values == set([])
    assert result.common_linker.flags.remove_modifiers.values == set([])
    assert result.common_linker.features.override == False
    assert result.common_linker.features.values == set([])
    assert result.common_linker.features.remove_modifiers.values == set([])
    ld = result.linker_overrides.get("ld")
    assert ld
    assert ld.flags.override == True
    assert ld.flags.values == set(["LD0", "LD3"])
    assert ld.flags.remove_modifiers.values == set(["LD1", "LD2"]) 
    assert ld.features.override == True
    assert ld.features.values == set(["LDF0", "LDF3"])
    assert ld.features.remove_modifiers.values == set(["LDF1", "LDF2"]) 

def test_linker_only_2():
    # linkers:
    #   ld:
    #     flags: [LD1, LD3] # Override = False
    #     remove-flags: [LD1, LD2] 
    #     features: [LDF1, LDF3] # Override = False
    #     remove-features: [LDF1, LDF2]
    base_linker_node = create_linker_only_2()

    # linkers:
    #   ld:
    #     flags: [LD3] # Override = False
    #     remove-flags: [LD1, LD2] 
    #     features: [LDF3] # Override = False
    #     remove-features: [LDF1, LDF2]
    result = base_linker_node.resolve_extends(None, {}).unwrap()

    # Validate result
    assert result.common_linker.flags.override == False
    assert result.common_linker.flags.values == set([])
    assert result.common_linker.flags.remove_modifiers.values == set([])
    assert result.common_linker.features.override == False
    assert result.common_linker.features.values == set([])
    assert result.common_linker.features.remove_modifiers.values == set([])
    ld = result.linker_overrides.get("ld")
    assert ld
    assert ld.flags.override == False
    assert ld.flags.values == set(["LD3"])
    assert ld.flags.remove_modifiers.values == set(["LD1", "LD2"]) 
    assert ld.features.override == False
    assert ld.features.values == set(["LDF3"])
    assert ld.features.remove_modifiers.values == set(["LDF1", "LDF2"]) 

def test_linker_only_1_extends_common_only_1():
    # linkers:
    #   flags: [E0, E1, E3] # Override = True
    #   remove-flags: [E1, E2]
    #   features: [EF0, EF1, EF3] # Override = True
    #   remove-features: [EF1, EF2]
    base_linker_node = create_common_only_1()

    # linkers:
    #   flags: [E0, E3] # Override = True
    #   remove-flags: [E1, E2]
    #   features: [EF0, EF3] # Override = True
    #   remove-features: [EF1, EF2]
    extended_base_linker_node = base_linker_node.resolve_extends(None, {}).unwrap()
    
    # child 'linkers:' extends extended_base_linker_node
    # linkers:
    #   ld:
    #     flags: [LD0, LD1, LD3] # Override = True
    #     remove-flags: [LD1, LD2] 
    #     features: [LDF0, LDF1, LDF3] # Override = True
    #     remove-features: [LDF1, LDF2]
    child_linker_node = create_linker_only_1()

    # child
    # linkers: (Extended)
    #   ld:
    #     flags: [LD0, LD3] # Override = True
    #     remove-flags: [LD1, LD2] 
    #     features: [LDF0, LDF3] # Override = True
    #     remove-features: [LDF1, LDF2]
    result = child_linker_node.resolve_extends(extended_base_linker_node, {}).unwrap()

    # Validate result
    assert result.common_linker.flags.override == False
    assert result.common_linker.flags.values == set([])
    assert result.common_linker.flags.remove_modifiers.values == set([])
    assert result.common_linker.features.override == False
    assert result.common_linker.features.values == set([])
    assert result.common_linker.features.remove_modifiers.values == set([])
    ld = result.linker_overrides.get("ld")
    assert ld
    assert ld.flags.override == True
    assert ld.flags.values == set(["LD0", "LD3"])
    assert ld.flags.remove_modifiers.values == set(["LD1", "LD2"]) 
    assert ld.features.override == True
    assert ld.features.values == set(["LDF0", "LDF3"])
    assert ld.features.remove_modifiers.values == set(["LDF1", "LDF2"])  

def test_linker_only_1_extends_common_only_2():
    # linkers:
    #   flags: [E1, E3] # Override = False
    #   remove-flags: [E1, E2]
    #   features: [EF1, EF3] # Override = False
    #   remove-features: [EF1, EF2]
    base_linker_node = create_common_only_2()

    # linkers:
    #   flags: [E3] # Override = False
    #   remove-flags: [E1, E2]
    #   features: [EF3] # Override = False
    #   remove-features: [EF1, EF2]
    extended_base_linker_node = base_linker_node.resolve_extends(None, {}).unwrap()
    
    # child 'linkers:' extends extended_base_linker_node
    # linkers:
    #   ld:
    #     flags: [LD0, LD1, LD3] # Override = True
    #     remove-flags: [LD1, LD2] 
    #     features: [LDF0, LDF1, LDF3] # Override = True
    #     remove-features: [LDF1, LDF2]
    child_linker_node = create_linker_only_1()

    # child
    # linkers: (Extended)
    #   ld:
    #     flags: [LD0, LD3] # Override = True
    #     remove-flags: [LD1, LD2] 
    #     features: [LDF0, LDF3] # Override = True
    #     remove-features: [LDF1, LDF2]
    result = child_linker_node.resolve_extends(extended_base_linker_node, {}).unwrap()

    # Validate result
    assert result.common_linker.flags.override == False
    assert result.common_linker.flags.values == set([])
    assert result.common_linker.flags.remove_modifiers.values == set([])
    assert result.common_linker.features.override == False
    assert result.common_linker.features.values == set([])
    assert result.common_linker.features.remove_modifiers.values == set([])
    ld = result.linker_overrides.get("ld")
    assert ld
    assert ld.flags.override == True
    assert ld.flags.values == set(["LD0", "LD3"])
    assert ld.flags.remove_modifiers.values == set(["LD1", "LD2"]) 
    assert ld.features.override == True
    assert ld.features.values == set(["LDF0", "LDF3"])
    assert ld.features.remove_modifiers.values == set(["LDF1", "LDF2"])  

def test_linker_only_2_extends_common_only_1():
    # linkers:
    #   flags: [E0, E1, E3] # Override = True
    #   remove-flags: [E1, E2]
    #   features: [EF0, EF1, EF3] # Override = True
    #   remove-features: [EF1, EF2]
    base_linker_node = create_common_only_1()

    # linkers:
    #   flags: [E0, E3] # Override = True
    #   remove-flags: [E1, E2]
    #   features: [EF0, EF3] # Override = True
    #   remove-features: [EF1, EF2]
    extended_base_linker_node = base_linker_node.resolve_extends(None, {}).unwrap()
    
    # child 'linkers:' extends extended_base_linker_node
    #   ld:
    #     flags: [LD1, LD3] # Override = False
    #     remove-flags: [LD1, LD2] 
    #     features: [LDF1, LDF3] # Override = False
    #     remove-features: [LDF1, LDF2]
    child_linker_node = create_linker_only_2()

    # child
    # linkers: (Extended)
    #   ld:
    #     flags: [E0, E3, LD3] # Override = False
    #     remove-flags: [LD1, LD2] 
    #     features: [EF0, EF3, LDF3] # Override = False
    #     remove-features: [LDF1, LDF2]
    result = child_linker_node.resolve_extends(extended_base_linker_node, {}).unwrap()

    # Validate result
    assert result.common_linker.flags.override == False
    assert result.common_linker.flags.values == set([])
    assert result.common_linker.flags.remove_modifiers.values == set([])
    assert result.common_linker.features.override == False
    assert result.common_linker.features.values == set([])
    assert result.common_linker.features.remove_modifiers.values == set([])
    ld = result.linker_overrides.get("ld")
    assert ld
    assert ld.flags.override == False
    assert ld.flags.values == set(["E0", "E3", "LD3"])
    assert ld.flags.remove_modifiers.values == set(["LD1", "LD2"]) 
    assert ld.features.override == False
    assert ld.features.values == set(["EF0", "EF3", "LDF3"])
    assert ld.features.remove_modifiers.values == set(["LDF1", "LDF2"])  

def test_linker_only_2_extends_common_only_2():
    # linkers:
    #   flags: [E1, E3] # Override = False
    #   remove-flags: [E1, E2]
    #   features: [EF1, EF3] # Override = False
    #   remove-features: [EF1, EF2]
    base_linker_node = create_common_only_2()

    # linkers:
    #   flags: [E3] # Override = False
    #   remove-flags: [E1, E2]
    #   features: [EF3] # Override = False
    #   remove-features: [EF1, EF2]
    extended_base_linker_node = base_linker_node.resolve_extends(None, {}).unwrap()
    
    # child 'linkers:' extends extended_base_linker_node
    #   ld:
    #     flags: [LD1, LD3] # Override = False
    #     remove-flags: [LD1, LD2] 
    #     features: [LDF1, LDF3] # Override = False
    #     remove-features: [LDF1, LDF2]
    child_linker_node = create_linker_only_2()

    # child
    # linkers: (Extended)
    #   ld:
    #     flags: [E3, LD3] # Override = False
    #     remove-flags: [LD1, LD2] 
    #     features: [EF3, LDF3] # Override = False
    #     remove-features: [LDF1, LDF2]
    result = child_linker_node.resolve_extends(extended_base_linker_node, {}).unwrap()

    # Validate result
    assert result.common_linker.flags.override == False
    assert result.common_linker.flags.values == set([])
    assert result.common_linker.flags.remove_modifiers.values == set([])
    assert result.common_linker.features.override == False
    assert result.common_linker.features.values == set([])
    assert result.common_linker.features.remove_modifiers.values == set([])
    ld = result.linker_overrides.get("ld")
    assert ld
    assert ld.flags.override == False
    assert ld.flags.values == set(["E3", "LD3"])
    assert ld.flags.remove_modifiers.values == set(["LD1", "LD2"]) 
    assert ld.features.override == False
    assert ld.features.values == set(["EF3", "LDF3"])
    assert ld.features.remove_modifiers.values == set(["LDF1", "LDF2"])  

def test_common_only_1_extends_linker_only_1():
    # linkers:
    #   flags: [E0, E1, E3] # Override = True
    #   remove-flags: [E1, E2]
    #   features: [EF0, EF1, EF3] # Override = True
    #   remove-features: [EF1, EF2]
    base_linker_node = create_common_only_1()

    # linkers:
    #   flags: [E0, E3] # Override = True
    #   remove-flags: [E1, E2]
    #   features: [EF0, EF3] # Override = True
    #   remove-features: [EF1, EF2]
    extended_base_linker_node = base_linker_node.resolve_extends(None, {}).unwrap()
    
    # child 'linkers:' extends extended_base_linker_node
    # linkers:
    #   ld:
    #     flags: [LD0, LD1, LD3] # Override = True
    #     remove-flags: [LD1, LD2] 
    #     features: [LDF0, LDF1, LDF3] # Override = True
    #     remove-features: [LDF1, LDF2]
    child_linker_node = create_linker_only_1()

    # child
    # linkers: (Extended)
    #   ld:
    #     flags: [LD0, LD3] # Override = True
    #     remove-flags: [LD1, LD2] 
    #     features: [LDF0, LDF3] # Override = True
    #     remove-features: [LDF1, LDF2]
    result = child_linker_node.resolve_extends(extended_base_linker_node, {}).unwrap()

    # Validate result
    assert result.common_linker.flags.override == False
    assert result.common_linker.flags.values == set([])
    assert result.common_linker.flags.remove_modifiers.values == set([])
    assert result.common_linker.features.override == False
    assert result.common_linker.features.values == set([])
    assert result.common_linker.features.remove_modifiers.values == set([])
    ld = result.linker_overrides.get("ld")
    assert ld
    assert ld.flags.override == True
    assert ld.flags.values == set(["LD0", "LD3"])
    assert ld.flags.remove_modifiers.values == set(["LD1", "LD2"]) 
    assert ld.features.override == True
    assert ld.features.values == set(["LDF0", "LDF3"])
    assert ld.features.remove_modifiers.values == set(["LDF1", "LDF2"]) 

def test_common_only_1_extends_linker_only_2():
    # linkers:
    #   flags: [E1, E3] # Override = False
    #   remove-flags: [E1, E2]
    #   features: [EF1, EF3] # Override = False
    #   remove-features: [EF1, EF2]
    base_linker_node = create_common_only_2()

    # linkers:
    #   flags: [E3] # Override = False
    #   remove-flags: [E1, E2]
    #   features: [EF3] # Override = False
    #   remove-features: [EF1, EF2]
    extended_base_linker_node = base_linker_node.resolve_extends(None, {}).unwrap()
    
    # child 'linkers:' extends extended_base_linker_node
    # linkers:
    #   ld:
    #     flags: [LD0, LD1, LD3] # Override = True
    #     remove-flags: [LD1, LD2] 
    #     features: [LDF0, LDF1, LDF3] # Override = True
    #     remove-features: [LDF1, LDF2]
    child_linker_node = create_linker_only_1()

    # child
    # linkers: (Extended)
    #   ld:
    #     flags: [LD0, LD3] # Override = True
    #     remove-flags: [LD1, LD2] 
    #     features: [LDF0, LDF3] # Override = True
    #     remove-features: [LDF1, LDF2]
    result = child_linker_node.resolve_extends(extended_base_linker_node, {}).unwrap()

    # Validate result
    assert result.common_linker.flags.override == False
    assert result.common_linker.flags.values == set([])
    assert result.common_linker.flags.remove_modifiers.values == set([])
    assert result.common_linker.features.override == False
    assert result.common_linker.features.values == set([])
    assert result.common_linker.features.remove_modifiers.values == set([])
    ld = result.linker_overrides.get("ld")
    assert ld
    assert ld.flags.override == True
    assert ld.flags.values == set(["LD0", "LD3"])
    assert ld.flags.remove_modifiers.values == set(["LD1", "LD2"]) 
    assert ld.features.override == True
    assert ld.features.values == set(["LDF0", "LDF3"])
    assert ld.features.remove_modifiers.values == set(["LDF1", "LDF2"]) 

def test_common_only_2_extends_linker_only_1():
    # linkers:
    #   flags: [E0, E1, E3] # Override = True
    #   remove-flags: [E1, E2]
    #   features: [EF0, EF1, EF3] # Override = True
    #   remove-features: [EF1, EF2]
    base_linker_node = create_common_only_1()

    # linkers:
    #   flags: [E0, E3] # Override = True
    #   remove-flags: [E1, E2]
    #   features: [EF0, EF3] # Override = True
    #   remove-features: [EF1, EF2]
    extended_base_linker_node = base_linker_node.resolve_extends(None, {}).unwrap()
    
    # child 'linkers:' extends extended_base_linker_node
    #   flags: [E1, E3] # Override = False
    #   remove-flags: [E1, E2]
    #   features: [EF1, EF3] # Override = False
    #   remove-features: [EF1, EF2]
    child_linker_node = create_common_only_2()

    # child
    # linkers: (Extended)
    #   flags: [E3] # Override = False
    #   remove-flags: [E1, E2]
    #   features: [EF3] # Override = False
    #   remove-features: [EF1, EF2]
    result = child_linker_node.resolve_extends(extended_base_linker_node, {}).unwrap()

    # Validate result
    assert result.common_linker.flags.override == False
    assert result.common_linker.flags.values == set(["E3"])
    assert result.common_linker.flags.remove_modifiers.values == set(["E1", "E2"])
    assert result.common_linker.features.override == False
    assert result.common_linker.features.values == set(["EF3"])
    assert result.common_linker.features.remove_modifiers.values == set(["EF1", "EF2"])
    assert len(result.linker_overrides) == 0

def test_common_only_2_extends_linker_only_2():
    # linkers:
    #   flags: [E1, E3] # Override = False
    #   remove-flags: [E1, E2]
    #   features: [EF1, EF3] # Override = False
    #   remove-features: [EF1, EF2]
    base_linker_node = create_common_only_2()

    # linkers:
    #   flags: [E3] # Override = False
    #   remove-flags: [E1, E2]
    #   features: [EF3] # Override = False
    #   remove-features: [EF1, EF2]
    extended_base_linker_node = base_linker_node.resolve_extends(None, {}).unwrap()
    
    # child 'linkers:' extends extended_base_linker_node
    #   flags: [E1, E3] # Override = False
    #   remove-flags: [E1, E2]
    #   features: [EF1, EF3] # Override = False
    #   remove-features: [EF1, EF2]
    child_linker_node = create_common_only_2()

    # child
    # linkers: (Extended)
    #   flags: [E3] # Override = False
    #   remove-flags: [E1, E2]
    #   features: [EF3] # Override = False
    #   remove-features: [EF1, EF2]
    result = child_linker_node.resolve_extends(extended_base_linker_node, {}).unwrap()

    # Validate result
    assert result.common_linker.flags.override == False
    assert result.common_linker.flags.values == set(["E3"])
    assert result.common_linker.flags.remove_modifiers.values == set(["E1", "E2"])
    assert result.common_linker.features.override == False
    assert result.common_linker.features.values == set(["EF3"])
    assert result.common_linker.features.remove_modifiers.values == set(["EF1", "EF2"])
    assert len(result.linker_overrides) == 0

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