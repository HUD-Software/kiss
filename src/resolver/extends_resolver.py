"""
extends_resolver.py
-------------------
Pass 1 of the resolution pipeline.

Delegates all merge logic to Property.resolve_extends().
The resolver itself is now only responsible for:
  1. Building the inheritance chain (extends)
  2. Detecting circular dependencies
  3. Calling node.resolve_extends(parent) in the right order

All merge semantics live in the Property subclasses (node.py).
"""

from toolchain.nodes.property import PropertyDict


def _resolve_chain(name: str, index: dict[str, PropertyDict], visited: set, resolved: dict[str, PropertyDict]) -> PropertyDict:
    if name in resolved:
        return resolved[name]

    if name in visited:
        raise ValueError(f"extends_resolver: circular dependency detected for '{name}'")

    if name not in index:
        raise ValueError(f"extends_resolver: '{name}' not found (referenced in extends)")

    node = index[name]
    visited.add(name)

    extends_prop = node.get_property("extends")
    if extends_prop:
        parent_name = extends_prop.value
        parent      = _resolve_chain(parent_name, index, visited, resolved)
        node        = node.resolve_extends(parent)
        node        = node.dispatch_globals()
    else:
        node = node.dispatch_globals()
        
    visited.discard(name)
    resolved[name] = node
    return node

def resolve_extends(nodes: dict[str, PropertyDict]) -> dict[str, PropertyDict]:
    """
    Resolve all 'extends' chains in a list of nodes.
    Returns a new list of fully merged nodes in original order.
    Each node's properties are merged via Property.resolve_extends().
    """
    resolved: dict[str, PropertyDict] = {}

    for name, node in nodes.items():
        _resolve_chain(name, nodes, set(), resolved)

    return resolved
