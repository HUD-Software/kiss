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


# import yaml

# from toolchain.parsers.linker_parser import parse_linker
# from toolchain.parsers.profile_parser import parse_profile
# from toolchain.parsers.project_parser import parse_project
# from toolchain.parsers.target_parser import parse_target

# # Add src to path
# sys.path.insert(0, os.path.dirname(__file__))

# from toolchain.parsers.compiler_parser import parse_compiler
# from workspace.loader import load_workspace
# from toolchain.nodes.node import (
#     PropertyStr, PropertyBool, PropertyStrList, PropertyNodeList, PropertyNodeDict
# )


# def print_node(node, indent: int = 0):
#     """Recursively print a node and its properties."""
#     prefix = "  " * indent
#     print(f"{prefix}[{node.__class__.__name__}] {node.name!r}")

#     for prop in node.properties.values():
#         if isinstance(prop, PropertyNodeList):
#             print(f"{prefix}  .{prop.name}:")
#             for child in prop.nodes:
#                 print_node(child, indent + 2)
#         elif isinstance(prop, PropertyNodeDict):
#             print(f"{prefix}  .{prop.name}:")
#             for key, child in prop.entries.items():
#                 print_node(child, indent + 2)
#         elif isinstance(prop, PropertyStrList):
#             print(f"{prefix}  .{prop.name}: {prop.values}")
#         elif isinstance(prop, PropertyStr):
#             print(f"{prefix}  .{prop.name}: {prop.value!r}")
#         elif isinstance(prop, PropertyBool):
#             print(f"{prefix}  .{prop.name}: {prop.value}")


# def print_section(title: str, nodes: list):
#     print(f"\n{'=' * 60}")
#     print(f"  {title} ({len(nodes)})")
#     print(f"{'=' * 60}")
#     for node in nodes:
#         print_node(node)
#         print("-" * 60)
        
# def load_all_yaml(data_dir: str):
#     """Charge tous les fichiers .yaml d'un répertoire."""
#     result = {}

#     compilers = []
#     linkers  = []
#     profiles = []
#     projects = []
#     targets = []
#     for filename in os.listdir(data_dir):
#         if filename.endswith(".yaml"):
#             path = os.path.join(data_dir, filename)
            
#             with open(path, "r") as f:
#                 data = yaml.safe_load(f)

#                 """Load and parse compilers.yaml, returning a list of CompilerNode."""
#                 for compiler_data in data.get("compilers", []):
#                     compilers.append(parse_compiler(compiler_data))

#                 """Load and parse linkers.yaml, returning a list of LinkerNode."""
#                 for linker_data in data.get("linkers", []):
#                     linkers.append(parse_linker(linker_data))
                
#                 """Load and parse profiles.yaml, returning a list of ProfileNode."""
#                 for profile_data in data.get("profiles", []):
#                     profiles.append(parse_profile(profile_data))
                
#                 """Load and parse projects.yaml, returning a list of ProjectTypeNode."""
#                 for project_data in data.get("project-types", []):
#                     projects.append(parse_project(project_data))
                
#                 """Load and parse targets.yaml, returning a list of TargetNode."""
#                 for target_data in data.get("targets", []):
#                     targets.append(parse_target(target_data))

#     print_section("COMPILERS", compilers)
#     print_section("LINKERS",   linkers)
#     print_section("PROFILES",  profiles)
#     print_section("PROJECTS",  projects)
#     print_section("TARGETS",   targets)
#     return result

# def main():
#     data_dir = sys.argv[1] if len(sys.argv) > 1 else os.path.join(os.path.dirname(__file__), "../data")
#     data_dir = os.path.abspath(data_dir)

#     print(f"Loading toolchain from: {data_dir}")

#     load_all_yaml(data_dir)
    
#     # Load kiss.yaml if present
#     kiss_yaml = os.path.join(os.getcwd(), "kiss.yaml")
#     if os.path.exists(kiss_yaml):
#         print(f"\n{'=' * 60}")
#         print(f"  WORKSPACE (kiss.yaml)")
#         print(f"{'=' * 60}")
#         workspace = load_workspace(kiss_yaml)
#         print_node(workspace)
#     else:
#         print(f"\n[info] No kiss.yaml found in {os.getcwd()}, skipping workspace load.")


    
# if __name__ == "__main__":
#     main()
