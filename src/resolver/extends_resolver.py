"""
extends_resolver.py
-------------------
Pass 1 of the resolution pipeline.

Delegates all merge logic to Property.merge_with_parent().
The resolver itself is now only responsible for:
  1. Building the inheritance chain (extends)
  2. Detecting circular dependencies
  3. Calling Node.merge(child) in the right order

All merge semantics live in the Property subclasses (node.py).
"""

from toolchain.nodes.node import Node


def _resolve_chain(name: str, index: dict[str, Node], visited: set, resolved: dict[str, Node]) -> Node:
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
        node        = node.merge_with_parent(parent)
        #node        = parent.merge(node)

    visited.discard(name)
    resolved[name] = node
    return node

from typing import TypeVar
T = TypeVar("T", bound=Node)

def resolve_extends(nodes: list[T]) -> list[T]:
    """
    Resolve all 'extends' chains in a list of nodes.
    Returns a new list of fully merged nodes in original order.
    Each node's properties are merged via Property.merge_with_parent().
    """
    index: dict[str, Node] = {n.name: n for n in nodes}
    resolved: dict[str, Node] = {}

    for node in nodes:
        _resolve_chain(node.name, index, set(), resolved)

    return [resolved[n.name] for n in nodes]
