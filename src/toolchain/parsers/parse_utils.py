"""
parse_utils.py
--------------
Generic utilities to convert raw YAML dicts into Node/Property objects.

Key detection rules (applied in order):
  append-foo  → PropertyStrListAppend("foo", ...)
  remove-foo  → PropertyStrListRemove("foo", ...)
  foo: str    → PropertyStr
  foo: bool   → PropertyBool
  foo: list   → PropertyStrList
  foo: dict   → parsed recursively as a child Node
"""

from toolchain.nodes.node import (
    Node,
    Property,
    PropertyStr,
    PropertyBool,
    PropertyStrList,
    PropertyStrListAppend,
    PropertyStrListRemove,
    PropertyNodeList,
    PropertyNodeDict,
)

APPEND_PREFIX = "append-"
REMOVE_PREFIX = "remove-"

NON_INHERITABLE_KEYS = ["is_abstract"]

def parse_property(key: str, value) -> Property | None:
    """
    Convert a single YAML key/value pair into a Property.
    Returns None for keys that should be skipped (handled by caller).
    """
    inheritable = next((False for k in NON_INHERITABLE_KEYS if k == key), True)
    # append-foo
    if key.startswith(APPEND_PREFIX):
        base = key[len(APPEND_PREFIX):]
        if isinstance(value, list):
            return PropertyStrListAppend(base, [str(v) for v in value], inheritable)

    # remove-foo
    if key.startswith(REMOVE_PREFIX):
        base = key[len(REMOVE_PREFIX):]
        if isinstance(value, list):
            return PropertyStrListRemove(base, [str(v) for v in value], inheritable)

    # scalar
    if isinstance(value, bool):
        return PropertyBool(key, value, inheritable)
    if isinstance(value, str):
        return PropertyStr(key, value, inheritable)
    if isinstance(value, int):
        return PropertyStr(key, str(value), inheritable)

    # list of scalars
    if isinstance(value, list) and all(not isinstance(v, dict) for v in value):
        return PropertyStrList(key, [str(v) for v in value], inheritable)

    # list of dicts (named nodes) — caller handles via parse_named_node_list
    # dict — caller handles via parse_node_from_dict
    return None  # caller must handle


def parse_node_from_dict(name: str, data: dict, node_class=None) -> Node:
    """
    Recursively parse a dict into a Node, applying parse_property() on each key.
    Dicts and named lists are handled recursively.
    """
    cls  = node_class or Node
    node = cls(name)

    for key, value in data.items():
        prop = parse_property(key, value)

        if prop is not None:
            node.add_property(prop)
            continue

        # list of dicts → PropertyNodeList (named nodes)
        if isinstance(value, list) and value and isinstance(value[0], dict):
            child_nodes = [
                parse_node_from_dict(item.get("name", f"{key}_{i}"), item)
                for i, item in enumerate(value)
            ]
            node.add_property(PropertyNodeList(key, child_nodes))
            continue

        # dict → child Node stored in PropertyNodeDict
        if isinstance(value, dict):
            child_node = parse_node_from_dict(key, value)
            # Store as PropertyNodeDict entry under parent key
            existing = node.get_property(key)
            if existing and isinstance(existing, PropertyNodeDict):
                existing.entries[key] = child_node
            else:
                node.add_property(PropertyNodeDict(key, {key: child_node}))
            continue

        # empty list
        if isinstance(value, list) and not value:
            node.add_property(PropertyStrList(key, []))

    return node
