"""
extends_resolver.py
-------------------
Pass 1 of the resolution pipeline.

Resolves 'extends' relationships between compilers, linkers and profiles.
For each node that has 'extends: <parent_name>', the parent's properties
are merged into the child (parent first, child overrides).

Supports multi-level chains: asan → debug → base
Detects circular dependencies and raises ValueError.
"""


# ── Helpers ───────────────────────────────────────────────────────────────────

def _deep_merge(base: dict, override: dict) -> dict:
    """
    Recursively merge two dicts.
    - Lists are CONCATENATED (base first, then override), deduplicating by order.
    - Dicts are merged recursively.
    - Scalar values: override wins.
    """
    result = dict(base)
    for key, val in override.items():
        if key in result:
            if isinstance(result[key], dict) and isinstance(val, dict):
                result[key] = _deep_merge(result[key], val)
            elif isinstance(result[key], list) and isinstance(val, list):
                # Deduplicate while preserving order (override items last)
                seen = list(result[key])
                for item in val:
                    if item not in seen:
                        seen.append(item)
                result[key] = seen
            else:
                result[key] = val   # scalar: override wins
        else:
            result[key] = val
    return result


def _resolve_chain(name: str, index: dict, visited: set, resolved: dict) -> dict:
    """
    Recursively resolve the extends chain for 'name'.
    Returns the fully merged dict for that node.
    """
    if name in resolved:
        return resolved[name]

    if name in visited:
        raise ValueError(f"extends_resolver: circular dependency detected for '{name}'")

    if name not in index:
        raise ValueError(f"extends_resolver: '{name}' not found (referenced in extends)")

    node = dict(index[name])   # shallow copy
    visited.add(name)

    parent_name = node.get("extends", None)  # keep for abstract parent lookup
    if parent_name:
        parent = _resolve_chain(parent_name, index, visited, resolved)
        node = _deep_merge(parent, node)

    visited.discard(name)
    resolved[name] = node
    return node


def resolve_extends(nodes: list[dict]) -> list[dict]:
    """
    Given a list of raw dicts (each with optional 'extends' key),
    return a new list where every node has been fully merged with its ancestors.

    Abstract nodes (is_abstract: true) are kept in the output so concrete
    nodes that extend them can still reference their features, but they are
    flagged and generators should ignore them.
    """
    index = {n["name"]: n for n in nodes}
    resolved: dict[str, dict] = {}

    for node in nodes:
        _resolve_chain(node["name"], index, set(), resolved)

    # Return in original order
    return [resolved[n["name"]] for n in nodes]
