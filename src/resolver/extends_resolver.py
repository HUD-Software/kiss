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

from operator import index
from os import name
from typing import Callable

from result import Result, Ok, Err
from toolchain.nodes.feature_node import ValidationError
from toolchain.nodes.property import PropertyDict


class ExtendResolver:
    def __init__(self, nodes):
        self.resolved = {}
        self.nodes = nodes

    def resolve_extends(self, resolve_fn: Callable[[object, object | None], object]) -> Result[dict, ValidationError]:
        for node in self.nodes:
            match self._resolve_chain(node, set(), resolve_fn):
                case Err() as err:
                    return err
                case Ok(resolved):
                    pass

        return Ok(self.resolved)

    def _resolve_chain(self, node_name, visited, resolve_fn) -> Result[Any, ValidationError]:
        if node_name in self.resolved:
            return Ok(self.resolved[node_name])

        if node_name in visited:
            raise ValueError(f"extends_resolver: circular dependency detected for '{node_name}'")

        if node_name not in self.nodes:
            raise ValueError(f"extends_resolver: '{node_name}' not found (referenced in extends)")

        node = self.nodes[node_name]
        visited.add(node_name)

        parent_name = node.extends
        parent = None
        # Resolve parent chain if any
        if parent_name:
            match self._resolve_chain(parent_name, visited, resolve_fn):
                case Err() as err:
                    return err
                case Ok(value):
                    parent = value

        # Resolve node with parent
        match resolve_fn(node, parent):
            case Err() as err:
                return err
            case Ok(value):
                node = value

        visited.discard(node_name)
        self.resolved[node.name] = node
        return Ok(node)