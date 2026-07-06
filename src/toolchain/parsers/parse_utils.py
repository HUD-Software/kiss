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
            base,
            [str(v) for v in value],
            StrListModifierOperation.ADD,
        )
    
    if key.startswith(ENABLE_PREFIX) and _is_list_of_str(value)  :
        base = key[len(ENABLE_PREFIX):]
        return PropertyStrListModifier(
            base,
            [str(v) for v in value],
            StrListModifierOperation.ADD,
        )
    
    if key.startswith(REMOVE_PREFIX) and _is_list_of_str(value):
        base = key[len(REMOVE_PREFIX):]
        return PropertyStrListModifier(
            base,
            [str(v) for v in value],
            StrListModifierOperation.REMOVE,
        )
    if key.startswith(DISABLE_PREFIX) and _is_list_of_str(value):
        base = key[len(DISABLE_PREFIX):]
        return PropertyStrListModifier(
            base,
            [str(v) for v in value],
            StrListModifierOperation.REMOVE,
        )
    # --- Merge rules ---
    NON_MERGEABLE_KEYS = {"is_abstract"}
    NON_DISPATCHABLE_KEYS = {"description", "icon", "extends"}
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
