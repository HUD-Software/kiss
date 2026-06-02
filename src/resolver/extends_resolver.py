"""
extends_resolver.py
-------------------
Pass 1 of the resolution pipeline.

Resolves 'extends' relationships between compilers, linkers and profiles.

Generic list operations
------------------------
For ANY list property 'foo', the child node can use:

  foo:           replaces inherited list entirely (override, default)
  append-foo:    appends items to inherited list (deduplicated)
  remove-foo:    removes specific items from the result

These keys are consumed during resolution (not kept in the output).
Applied in order: foo (replace) → append-foo → remove-foo

Example:
  features:
    - name: OPT_LEVEL_3
      flags: ["/O2"]                    # replace
      append-flags: ["/Ob2", "/Oi"]     # then append
      remove-flags: ["/O1"]             # then remove

    - name: ASAN
      append-enable-features: [DEBUG_INFO]   # append to inherited enable-features
      remove-enable-features: [LTO]          # remove LTO if inherited

Named-item lists (features, feature-rules)
-------------------------------------------
Lists of dicts with a 'name' key are merged item by item:
  - Only in parent  → inherited as-is
  - In both         → child deep-merged onto parent
  - Only in child   → appended

OVERRIDE_LIST_KEYS
-------------------
Some lists default to override when the child redefines the base key
(without append- or remove- prefix):
  supported-linkers, supported-compilers

All other lists default to merge (concatenate + deduplicate).
"""


# Keys that belong to a node itself and must NOT be inherited by children.
NON_INHERITABLE_KEYS = {
    "name",
    "is_abstract",
    "description",
    "extends",
}

# Lists of dicts keyed by 'name' — merged item by item.
NAMED_LIST_KEYS = {
    "features",
    "feature-rules",
}

# List keys that default to OVERRIDE when the child redefines them directly.
# (append-foo / remove-foo still work normally for these)
OVERRIDE_LIST_KEYS = {
    "supported-linkers",
    "supported-compilers",
    "flags",
    "linker-flags",
}

APPEND_PREFIX = "append-"
REMOVE_PREFIX = "remove-"


# ── List operation helpers ────────────────────────────────────────────────────

def _is_append_key(key: str) -> tuple[bool, str]:
    """Return (True, base_key) if key is an append- operation."""
    if key.startswith(APPEND_PREFIX):
        return True, key[len(APPEND_PREFIX):]
    return False, key


def _is_remove_key(key: str) -> tuple[bool, str]:
    """Return (True, base_key) if key is a remove- operation."""
    if key.startswith(REMOVE_PREFIX):
        return True, key[len(REMOVE_PREFIX):]
    return False, key


def _collect_list_ops(child: dict) -> tuple[dict, dict, dict, dict]:
    """
    Scan child dict and extract all list operations.
    Returns (base_keys, appends, removes, rest) where:
      base_keys : {key: val}  — plain list assignments
      appends   : {key: val}  — append-foo operations
      removes   : {key: val}  — remove-foo operations
      rest      : {key: val}  — all non-list-op keys (dicts, scalars, named lists)
    Consumed keys are removed from child.
    """
    base_keys: dict = {}
    appends:   dict = {}
    removes:   dict = {}
    rest:      dict = {}

    for key, val in child.items():
        is_app, base = _is_append_key(key)
        if is_app:
            appends[base] = val
            continue
        is_rem, base = _is_remove_key(key)
        if is_rem:
            removes[base] = val
            continue
        rest[key] = val

    # Separate plain list assignments from non-list keys
    for key, val in list(rest.items()):
        if isinstance(val, list) and key not in NAMED_LIST_KEYS:
            base_keys[key] = val
            del rest[key]

    return base_keys, appends, removes, rest


def _apply_list_op(
    base_val:  list,
    new_val:   list | None,
    append_val: list | None,
    remove_val: list | None,
    key:       str,
) -> list:
    """
    Apply replace / append / remove operations on a list property.

    Step 1 — replace : if new_val provided, start from it; else keep base_val.
    Step 2 — append  : deduplicated append of append_val items.
    Step 3 — remove  : remove all items in remove_val.
    """
    # Step 1: replace or inherit
    if new_val is not None:
        result = list(new_val)
    else:
        result = list(base_val)

    # Step 2: append
    if append_val:
        for item in append_val:
            if item not in result:
                result.append(item)

    # Step 3: remove
    if remove_val:
        to_remove = set(remove_val)
        result = [i for i in result if i not in to_remove]

    return result


def _merge_plain_lists(base: list, child: list) -> list:
    """Default merge: concatenate + deduplicate (parent first, child last)."""
    seen = list(base)
    for item in child:
        if item not in seen:
            seen.append(item)
    return seen


# ── Named list merge ──────────────────────────────────────────────────────────

def _merge_named_list(base_list: list, child_list: list) -> list:
    """
    Merge two lists of dicts that each have a 'name' key.
    - Only in parent → inherited as-is.
    - In both        → child deep-merged onto parent.
    - Only in child  → appended.
    """
    base_idx  = {i["name"]: i for i in base_list  if isinstance(i, dict) and "name" in i}
    child_idx = {i["name"]: i for i in child_list if isinstance(i, dict) and "name" in i}

    result = []
    for name, base_item in base_idx.items():
        if name in child_idx:
            result.append(_deep_merge(base_item, child_idx[name]))
        else:
            result.append(dict(base_item))

    for name, child_item in child_idx.items():
        if name not in base_idx:
            result.append(dict(child_item))

    return result


# ── Core merge ────────────────────────────────────────────────────────────────

def _deep_merge(base: dict, override: dict) -> dict:
    """
    Recursively merge two dicts.

    For every list key 'foo' in either dict, the child may provide:
      foo:          replaces the inherited value
      append-foo:   appends to inherited (or replaced) value
      remove-foo:   removes items from the result

    Named lists (features, feature-rules) are merged by 'name' key.
    OVERRIDE_LIST_KEYS default to override when the child defines the base key.
    All other plain lists default to merge (concatenate + deduplicate).
    NON_INHERITABLE_KEYS are stripped from base before merging.
    """
    result = {k: v for k, v in base.items() if k not in NON_INHERITABLE_KEYS}
    child  = dict(override)

    # Extract list operations from child
    base_keys, appends, removes, rest = _collect_list_ops(child)

    # Gather all list keys that are touched (replace, append, or remove)
    all_list_keys = set(base_keys) | set(appends) | set(removes)

    for key in all_list_keys:
        base_val   = result.get(key, [])
        new_val    = base_keys.get(key)       # None if not redefined
        append_val = appends.get(key)
        remove_val = removes.get(key)

        has_any_op = new_val is not None or append_val or remove_val

        if not has_any_op:
            continue

        # If child only provides append/remove (no replace), always apply on top of inherited.
        # If child provides replace (base_keys), check OVERRIDE_LIST_KEYS for default behavior.
        if new_val is not None and key in OVERRIDE_LIST_KEYS and not append_val and not remove_val:
            # Pure override (no append/remove), OVERRIDE_LIST_KEY → replace only
            result[key] = list(new_val)
        else:
            result[key] = _apply_list_op(base_val, new_val, append_val, remove_val, key)

    # Handle named lists, dicts, and scalars from rest
    for key, val in rest.items():
        if key in NAMED_LIST_KEYS and isinstance(val, list):
            base_val = result.get(key, [])
            result[key] = _merge_named_list(base_val, val)

        elif key in result:
            if isinstance(result[key], dict) and isinstance(val, dict):
                result[key] = _deep_merge(result[key], val)
            elif isinstance(result[key], list) and isinstance(val, list):
                # Plain list not caught above (shouldn't happen, but safe fallback)
                result[key] = _merge_plain_lists(result[key], val)
            else:
                result[key] = val  # scalar: child wins
        else:
            result[key] = val  # new key

    return result


# ── Resolution chain ──────────────────────────────────────────────────────────

def _resolve_chain(name: str, index: dict, visited: set, resolved: dict) -> dict:
    if name in resolved:
        return resolved[name]
    if name in visited:
        raise ValueError(f"extends_resolver: circular dependency detected for '{name}'")
    if name not in index:
        raise ValueError(f"extends_resolver: '{name}' not found (referenced in extends)")

    node = dict(index[name])
    visited.add(name)

    parent_name = node.get("extends", None)
    if parent_name:
        parent = _resolve_chain(parent_name, index, visited, resolved)
        node   = _deep_merge(parent, node)

    visited.discard(name)
    resolved[name] = node
    return node


def resolve_extends(nodes: list[dict]) -> list[dict]:
    """
    Resolve all 'extends' chains.

    For any list property 'foo', child nodes may use:
      foo:          replace inherited list
      append-foo:   append to inherited list
      remove-foo:   remove items from result

    See module docstring for full details.
    """
    index    = {n["name"]: n for n in nodes}
    resolved: dict[str, dict] = {}

    for node in nodes:
        _resolve_chain(node["name"], index, set(), resolved)

    return [resolved[n["name"]] for n in nodes]