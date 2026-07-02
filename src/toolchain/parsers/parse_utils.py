"""
parse_utils.py
--------------
Generic utilities to convert raw YAML dicts into Node/Property objects.

Key detection rules (applied in order):
  add-foo  → PropertyStrListModifier("foo", ..., StrListModifierOperation.ADD)
  remove-foo  → PropertyStrListModifier("foo", ..., StrListModifierOperation.REMOVE)
  foo: str    → PropertyStr
  foo: bool   → PropertyBool
  foo: list   → PropertyStrList
  foo: dict   → parsed recursively as a child Node
"""

from toolchain.nodes.property import (
    Property,
    PropertyInt,
    PropertyStr,
    PropertyBool,
    PropertyStrList,
    PropertyStrListModifier,
    StrListModifierOperation,
)
def _is_list_of_str(value) -> bool:
    return isinstance(value, list) and all(isinstance(v, str) for v in value)

def parse_property(key: str, value) -> Property | None:
    """
    Convert a single YAML key/value pair into a Property.

    Returns None for:
    - complex structures handled by higher-level parsers (dict, node lists)
    - unsupported or special cases
    """

    ADD_PREFIX = "add-"
    ENABLE_PREFIX = "enable-"
    REMOVE_PREFIX = "remove-"
    DISABLE_PREFIX = "disable-"

    # --- Modifiers ---
    if key.startswith(ADD_PREFIX) and _is_list_of_str(value)  :
        base = key[len(ADD_PREFIX):]
        return PropertyStrListModifier(
            key,
            base,
            [str(v) for v in value],
            StrListModifierOperation.ADD,
        )
    
    if key.startswith(ENABLE_PREFIX) and _is_list_of_str(value)  :
        base = key[len(ENABLE_PREFIX):]
        return PropertyStrListModifier(
            key,
            base,
            [str(v) for v in value],
            StrListModifierOperation.ADD,
        )
    
    if key.startswith(REMOVE_PREFIX) and _is_list_of_str(value):
        base = key[len(REMOVE_PREFIX):]
        return PropertyStrListModifier(
            key,
            base,
            [str(v) for v in value],
            StrListModifierOperation.REMOVE,
        )
    if key.startswith(DISABLE_PREFIX) and _is_list_of_str(value):
        base = key[len(DISABLE_PREFIX):]
        return PropertyStrListModifier(
            key,
            base,
            [str(v) for v in value],
            StrListModifierOperation.REMOVE,
        )
    # --- Inheritance rules ---
    NON_INHERITABLE_KEYS = {"is_abstract"}
    inheritable = key not in NON_INHERITABLE_KEYS

    # --- Scalars ---
    if isinstance(value, bool):
        return PropertyBool(key, value, inheritable)

    if isinstance(value, str):
        return PropertyStr(key, value, inheritable)

    if isinstance(value, int):
        return PropertyInt(key, value, inheritable)

    # --- Lists ---
    if _is_list_of_str(value):
        return PropertyStrList(key, [str(v) for v in value], inheritable)

    # --- Complex structures handled elsewhere ---
    return None


# def parse_node_from_dict(name: str, data: dict, node_class=None) -> Node:
#     """
#     Recursively parse a dict into a Node, applying parse_property() on each key.
#     Dicts and named lists are handled recursively.
#     """
#     cls  = node_class or Node
#     node = cls(name)

#     for key, value in data.items():
#         prop = parse_property(key, value)

#         if prop is not None:
#             node.add_property(prop)
#             continue

#         # list of dicts → PropertyNodeList (named nodes)
#         if isinstance(value, list) and value and isinstance(value[0], dict):
#             child_nodes = [
#                 parse_node_from_dict(item.get("name", f"{key}_{i}"), item)
#                 for i, item in enumerate(value)
#             ]
#             node.add_property(PropertyNodeList(key, child_nodes))
#             continue

#         # dict → child Node stored in PropertyNodeDict
#         if isinstance(value, dict):
#             child_node = parse_node_from_dict(key, value)
#             # Store as PropertyNodeDict entry under parent key
#             existing = node.get_property(key)
#             if existing and isinstance(existing, PropertyNodeDict):
#                 existing.entries[key] = child_node
#             else:
#                 node.add_property(PropertyNodeDict(key, {key: child_node}))
#             continue

#         # empty list
#         if isinstance(value, list) and not value:
#             node.add_property(PropertyStrList(key, []))

#     return node
