import sys
import os


sys.path.insert(0, os.path.dirname(__file__))

from cli.app import app

if __name__ == "__main__":
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
                
#                 """Load and parse projects.yaml, returning a list of ProjectNode."""
#                 for project_data in data.get("projects", []):
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
