import sys
import os

from toolchain.nodes.property import PropertyDict, PropertyStrList, PropertyStrListModifier, StrListModifierOperation

sys.path.insert(0, os.path.dirname(__file__))

from cli.app import app


def test_merge() :
    #-----------------------------------------------------------------------
    # Self        ----->    Parent     ----->    Result
    # f:[0]                 f:[10]               f:[10]
    # add-f:[1]             add-f:[11]           add-f:[11]
    # add-r:[2]             add-r:[12]           add-r:[2, 12]
    _self = PropertyDict()
    _self.add_property(PropertyStrList("f", ["0"]))
    _self.add_property(PropertyStrListModifier("f", ["1"], StrListModifierOperation.ADD ))
    _self.add_property(PropertyStrListModifier("r", ["2"], StrListModifierOperation.ADD ))

    _parent = PropertyDict()
    _parent.add_property(PropertyStrList("f", ["10"]))
    _parent.add_property(PropertyStrListModifier("f", ["11"], StrListModifierOperation.ADD ))
    _parent.add_property(PropertyStrListModifier("r", ["12"], StrListModifierOperation.ADD ))

    _result = _self.merge_with(_parent)

    # Validate result
    f_list = _result.get_property_as("f", PropertyStrList)
    assert f_list.name == "f"
    assert len(f_list.values) == 1
    assert "0" in f_list.values

    f_add = _result.get_property_as("add-f", PropertyStrListModifier)
    assert f_add.name == "add-f"
    assert f_add.list_name == "f" 
    assert f_add.operation == StrListModifierOperation.ADD
    assert len(f_add.values) == 1 
    assert set(["1"]) == set(f_add.values)

    r_add = _result.get_property_as("add-r", PropertyStrListModifier)
    assert r_add.name == "add-r"
    assert r_add.list_name == "r"
    assert f_add.operation == StrListModifierOperation.ADD
    assert len(r_add.values) == 2 
    assert set(["12", "2"]) == set(r_add.values)

    #-----------------------------------------------------------------------
    # Self        ----->    Parent     ----->    Result
    # f:[0]                                      f:[0]
    # add-f:[1]             add-f:[11]           add-f:[1]
    # add-r:[2]             add-r:[12]           add-r:[2, 12]
    _self = PropertyDict()
    _self.add_property(PropertyStrList("f", ["0"]))
    _self.add_property(PropertyStrListModifier("f", ["1"], StrListModifierOperation.ADD ))
    _self.add_property(PropertyStrListModifier("r", ["2"], StrListModifierOperation.ADD ))

    _parent = PropertyDict()
    _parent.add_property(PropertyStrListModifier("f", ["11"], StrListModifierOperation.ADD ))
    _parent.add_property(PropertyStrListModifier("r", ["12"], StrListModifierOperation.ADD ))

    _result = _self.merge_with(_parent)

    # Validate result
    f_list = _result.get_property_as("f", PropertyStrList)
    assert f_list.name == "f"
    assert len(f_list.values) == 1
    assert "0" in f_list.values

    f_add = _result.get_property_as("add-f", PropertyStrListModifier)
    assert f_add.name == "add-f"
    assert f_add.list_name == "f"
    assert f_add.operation == StrListModifierOperation.ADD
    assert len(f_add.values) == 1
    assert set(["1"]) == set(f_add.values)

    r_add = _result.get_property_as("add-r", PropertyStrListModifier)
    assert r_add.name == "add-r"
    assert r_add.list_name == "r"
    assert f_add.operation == StrListModifierOperation.ADD
    assert len(r_add.values) == 2 
    assert set(["12", "2"]) == set(r_add.values)

    #-----------------------------------------------------------------------
    # Self        ----->    Parent     ----->    Result
    #                       f:[10]               f:[10]
    # add-f:[1]             add-f:[11]           add-f:[11, 1]
    # add-r:[2]             add-r:[12]           add-r:[2, 12]
    _self = PropertyDict()
    _self.add_property(PropertyStrListModifier("f", ["1"], StrListModifierOperation.ADD ))
    _self.add_property(PropertyStrListModifier("r", ["2"], StrListModifierOperation.ADD ))

    _parent = PropertyDict()
    _parent.add_property(PropertyStrList("f", ["10"]))
    _parent.add_property(PropertyStrListModifier("f", ["11"], StrListModifierOperation.ADD ))
    _parent.add_property(PropertyStrListModifier("r", ["12"], StrListModifierOperation.ADD ))
    
    _result = _self.merge_with(_parent)

    # Validate result
    f_list = _result.get_property_as("f", PropertyStrList)
    assert f_list.name == "f"
    assert len(f_list.values) == 1
    assert "10" in f_list.values

    f_add = _result.get_property_as("add-f", PropertyStrListModifier)
    assert f_add.name == "add-f"
    assert f_add.list_name == "f"
    assert f_add.operation == StrListModifierOperation.ADD
    assert len(f_add.values) == 2
    assert set(["1", "11"]) == set(f_add.values)

    r_add = _result.get_property_as("add-r", PropertyStrListModifier)
    assert r_add.name == "add-r"
    assert r_add.list_name == "r"
    assert f_add.operation == StrListModifierOperation.ADD
    assert len(r_add.values) == 2 
    assert set(["12", "2"]) == set(r_add.values)

    #-----------------------------------------------------------------------
    # Self        ----->    Parent     ----->    Result
    # add-f:[1]             add-f:[11]           add-f:[1, 11]
    # add-r:[2]             add-r:[12]           add-r:[2, 12]
    _self = PropertyDict()
    _self.add_property(PropertyStrListModifier("f", ["1"], StrListModifierOperation.ADD ))
    _self.add_property(PropertyStrListModifier("r", ["2"], StrListModifierOperation.ADD ))

    _parent = PropertyDict()
    _parent.add_property(PropertyStrListModifier("f", ["11"], StrListModifierOperation.ADD ))
    _parent.add_property(PropertyStrListModifier("r", ["12"], StrListModifierOperation.ADD ))

    _result = _self.merge_with(_parent)

    # Validate result
    f_add = _result.get_property_as("add-f", PropertyStrListModifier)
    assert f_add.name == "add-f"
    assert f_add.list_name == "f"
    assert f_add.operation == StrListModifierOperation.ADD
    assert len(f_add.values) == 2
    assert set(["1", "11"]) == set(f_add.values)

    r_add = _result.get_property_as("add-r", PropertyStrListModifier)
    assert r_add.name == "add-r"
    assert r_add.list_name == "r"
    assert f_add.operation == StrListModifierOperation.ADD
    assert len(r_add.values) == 2 
    assert set(["12", "2"]) == set(r_add.values)


def test_dispatch() :
    #-----------------------------------------------------------------------
    # Top         ----->    Bottom     ----->    Result
    # f:[0]                 f:[10]               f:[10]
    # add-f:[1]             add-f:[11]           add-f:[11]
    # add-r:[2]             add-r:[12]           add-r:[2, 12]
    _top = PropertyDict()
    _top.add_property(PropertyStrList("f", ["0"]))
    _top.add_property(PropertyStrListModifier("f", ["1"], StrListModifierOperation.ADD ))
    _top.add_property(PropertyStrListModifier("r", ["2"], StrListModifierOperation.ADD ))

    _bottom = PropertyDict()
    _bottom.add_property(PropertyStrList("f", ["10"]))
    _bottom.add_property(PropertyStrListModifier("f", ["11"], StrListModifierOperation.ADD ))
    _bottom.add_property(PropertyStrListModifier("r", ["12"], StrListModifierOperation.ADD ))

    _result = _bottom.dispatch(_top)

    # Validate result
    f_list = _result.get_property_as("f", PropertyStrList)
    assert f_list.name == "f"
    assert len(f_list.values) == 1
    assert "10" in f_list.values

    f_add = _result.get_property_as("add-f", PropertyStrListModifier)
    assert f_add.name == "add-f"
    assert f_add.list_name == "f" 
    assert f_add.operation == StrListModifierOperation.ADD
    assert len(f_add.values) == 1 
    assert set(["11"]) == set(f_add.values)

    r_add = _result.get_property_as("add-r", PropertyStrListModifier)
    assert r_add.name == "add-r"
    assert r_add.list_name == "r"
    assert f_add.operation == StrListModifierOperation.ADD
    assert len(r_add.values) == 2 
    assert set(["12", "2"]) == set(r_add.values)

    #-----------------------------------------------------------------------
    # Top         ----->    Bottom     ----->    Result
    # f:[0]                                      f:[0]
    # add-f:[1]             add-f:[11]           add-f:[1, 11]
    # add-r:[2]             add-r:[12]           add-r:[2, 12]
    _top = PropertyDict()
    _top.add_property(PropertyStrList("f", ["0"]))
    _top.add_property(PropertyStrListModifier("f", ["1"], StrListModifierOperation.ADD ))
    _top.add_property(PropertyStrListModifier("r", ["2"], StrListModifierOperation.ADD ))

    _bottom = PropertyDict()
    _bottom.add_property(PropertyStrListModifier("f", ["11"], StrListModifierOperation.ADD ))
    _bottom.add_property(PropertyStrListModifier("r", ["12"], StrListModifierOperation.ADD ))

    _result = _bottom.dispatch(_top)

    # Validate result
    f_list = _result.get_property_as("f", PropertyStrList)
    assert f_list.name == "f"
    assert len(f_list.values) == 1
    assert "0" in f_list.values

    f_add = _result.get_property_as("add-f", PropertyStrListModifier)
    assert f_add.name == "add-f"
    assert f_add.list_name == "f"
    assert f_add.operation == StrListModifierOperation.ADD
    assert len(f_add.values) == 2
    assert set(["1", "11"]) == set(f_add.values)

    r_add = _result.get_property_as("add-r", PropertyStrListModifier)
    assert r_add.name == "add-r"
    assert r_add.list_name == "r"
    assert f_add.operation == StrListModifierOperation.ADD
    assert len(r_add.values) == 2 
    assert set(["12", "2"]) == set(r_add.values)

    #-----------------------------------------------------------------------
    # Top         ----->    Bottom     ----->    Result
    #                       f:[10]               f:[10]
    # add-f:[1]             add-f:[11]           add-f:[11]
    # add-r:[2]             add-r:[12]           add-r:[2, 12]
    _top = PropertyDict()
    _top.add_property(PropertyStrListModifier("f", ["1"], StrListModifierOperation.ADD ))
    _top.add_property(PropertyStrListModifier("r", ["2"], StrListModifierOperation.ADD ))

    _bottom = PropertyDict()
    _bottom.add_property(PropertyStrList("f", ["10"]))
    _bottom.add_property(PropertyStrListModifier("f", ["11"], StrListModifierOperation.ADD ))
    _bottom.add_property(PropertyStrListModifier("r", ["12"], StrListModifierOperation.ADD ))
    
    _result = _bottom.dispatch(_top)

    # Validate result
    f_list = _result.get_property_as("f", PropertyStrList)
    assert f_list.name == "f"
    assert len(f_list.values) == 1
    assert "10" in f_list.values

    f_add = _result.get_property_as("add-f", PropertyStrListModifier)
    assert f_add.name == "add-f"
    assert f_add.list_name == "f"
    assert f_add.operation == StrListModifierOperation.ADD
    assert len(f_add.values) == 1
    assert set(["11"]) == set(f_add.values)

    r_add = _result.get_property_as("add-r", PropertyStrListModifier)
    assert r_add.name == "add-r"
    assert r_add.list_name == "r"
    assert f_add.operation == StrListModifierOperation.ADD
    assert len(r_add.values) == 2 
    assert set(["12", "2"]) == set(r_add.values)

    #-----------------------------------------------------------------------
    # Top         ----->    Bottom     ----->    Result
    # add-f:[1]             add-f:[11]           add-f:[1, 11]
    # add-r:[2]             add-r:[12]           add-r:[2, 12]
    _top = PropertyDict()
    _top.add_property(PropertyStrListModifier("f", ["1"], StrListModifierOperation.ADD ))
    _top.add_property(PropertyStrListModifier("r", ["2"], StrListModifierOperation.ADD ))

    _bottom = PropertyDict()
    _bottom.add_property(PropertyStrListModifier("f", ["11"], StrListModifierOperation.ADD ))
    _bottom.add_property(PropertyStrListModifier("r", ["12"], StrListModifierOperation.ADD ))

    _result = _bottom.dispatch(_top)

    # Validate result
    f_add = _result.get_property_as("add-f", PropertyStrListModifier)
    assert f_add.name == "add-f"
    assert f_add.list_name == "f"
    assert f_add.operation == StrListModifierOperation.ADD
    assert len(f_add.values) == 2
    assert set(["1", "11"]) == set(f_add.values)

    r_add = _result.get_property_as("add-r", PropertyStrListModifier)
    assert r_add.name == "add-r"
    assert r_add.list_name == "r"
    assert f_add.operation == StrListModifierOperation.ADD
    assert len(r_add.values) == 2 
    assert set(["12", "2"]) == set(r_add.values)

if __name__ == "__main__":

    test_merge()
    test_dispatch()

    app()