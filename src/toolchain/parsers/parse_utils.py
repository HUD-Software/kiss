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
    PropertyFeatureNameListModifier,
    PropertyInt,
    PropertyStr,
    PropertyBool,
    PropertyStrList,
    PropertyStrListModifier,
    StrList,
    StrListModifier,
    StrListModifierOperation,
)
# def _is_list_of_str(value) -> bool:
#     return isinstance(value, list) and all(isinstance(v, str) for v in value)

# def try_parse_list_modifier(key: str, value) -> PropertyStrListModifier | None:
#     if not _is_list_of_str(value):
#         return None

#     values = [str(v) for v in value]

#     prefix_mapping = {
#         "add-": StrListModifierOperation.ADD,
#         "enable-": StrListModifierOperation.ADD,
#         "remove-": StrListModifierOperation.REMOVE,
#         "disable-": StrListModifierOperation.REMOVE,
#     }
    
#     for prefix, operation in prefix_mapping.items():
#         if key.startswith(prefix):
#             base = key[len(prefix):]

#             modifier_cls = (
#                 PropertyFeatureNameListModifier
#                 if base == "features"
#                 else PropertyStrListModifier
#             )

#             return modifier_cls(
#                 base,
#                 values,
#                 operation,
#             )

#     return None

def try_parse_list_modifier(list_name:str, existing: StrList, key: str, value: list[str]) -> bool:

    # Is it a list name?
    if key == list_name:
        if not isinstance(value, list) or any(not isinstance(sl, str) for sl in value):
            raise ValueError(f"{list_name!r} must be a list of string -> {value}")
        if existing.values:
            raise ValueError(f"{list_name!r} must appear only once. To add or remove use modifier by using 'add-{list_name}' or 'remove-{list_name}' -> {value}")
        else:
            existing.values = value
        return True
    
    # Is it a modifier?
    str_list = StrListModifierOperation.split_modifier(key)
    if str_list:
        # Ignore modifier with empty list
        if not value:
            return True
        str_op, list_name = str_list
        existing.add_modifier(StrListModifier(str_op, value))
        return True

    # Not a list name or modifier
    return False

def parse_property(key: str, value) -> Property | None:
    """
    Convert a single YAML key/value pair into a Property.

    Returns None for:
    - complex structures handled by higher-level parsers (dict, node lists)
    - unsupported or special cases
    """

    # --- Try to parse list modifier that start with "add", "remove", etc...
    result = try_parse_list_modifier(key, value)
    if result:
        return result
    
    # --- Merge rules ---
    NON_MERGEABLE_KEYS = {"is_abstract"}
    NON_DISPATCHABLE_KEYS = {"description", "icon", "extends", "arch", "vendor", "os", "abi", "pointer-width", "endianness", "supported-compilers", "default-compiler"}
    is_mergeable = key not in NON_MERGEABLE_KEYS
    is_dispatchable = key not in NON_DISPATCHABLE_KEYS

    # --- Scalars ---
    if isinstance(value, bool):
        return PropertyBool(key, value, is_mergeable, is_dispatchable)

    if isinstance(value, str):
        return PropertyStr(key, value, is_mergeable, is_dispatchable)

    if isinstance(value, int):
        return PropertyInt(key, value, is_mergeable, is_dispatchable)

    # --- Lists ---
    if _is_list_of_str(value):
        return PropertyStrList(key, [str(v) for v in value], is_mergeable, is_dispatchable)

    # --- Complex structures handled elsewhere ---
    return None