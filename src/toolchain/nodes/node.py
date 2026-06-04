"""
node.py
-------
Base classes for all Kiss nodes and properties.

Property.merge_with_parent(parent)
------------------------------------
Every Property subclass decides how it combines with its parent's value.
The child (self) drives the merge — it knows what it wants from the parent.

Default behaviors:
  Property / PropertyStr / PropertyBool  → child replaces parent
  PropertyStrList                        → child replaces parent (override)
  PropertyStrListAppend                  → append child items to parent
  PropertyStrListRemove                  → remove child items from parent
  PropertyNodeList                       → merged by 'name' key
  PropertyNodeDict                       → merged by dict key

Multiple ops on the same property key
---------------------------------------
A Node stores properties as an ordered list (not a dict) so that
multiple operations on the same key (e.g. append-flags then remove-flags)
are applied in declaration order. Node.get_property() returns the last one.
"""
from __future__ import annotations
from abc import ABC, abstractmethod


# Keys that belong to a node itself and must NOT be inherited by children.


# ── Base ──────────────────────────────────────────────────────────────────────

class Property(ABC):
    """Base class. Default merge: child replaces parent."""

    def __init__(self, name: str, inheritable : bool = True):
        self.name = name
        self.inheritable = inheritable
    
    @abstractmethod
    def merge_with_parent(self, parent: Property) -> Property:
        pass
    
    @abstractmethod
    def clone(self) -> Property:
        pass
    
    def __repr__(self):
        return f"{self.__class__.__name__}(name={self.name!r})"


# ── Scalars ───────────────────────────────────────────────────────────────────

class PropertyStr(Property):
    def __init__(self, name: str, value: str, inheritable : bool = True):
        super().__init__(name, inheritable)
        self.value = value

    def clone(self) -> PropertyStr:
        return PropertyStr(self.name, self.value)
    
    def merge_with_parent(self, parent: PropertyStr) -> PropertyStr:
        return PropertyStr(self.name, self.value)
    
    def __repr__(self):
        return f"PropertyStr(name={self.name!r}, value={self.value!r})"


class PropertyBool(Property):
    def __init__(self, name: str, value: bool, inheritable : bool = True):
        super().__init__(name, inheritable)
        self.value = value

    def clone(self) -> PropertyBool:
        return PropertyBool(self.name, self.value)
    
    def merge_with_parent(self, parent: PropertyStr) -> PropertyStr:
        return PropertyBool(self.name, self.value)
    
    def __repr__(self):
        return f"PropertyBool(name={self.name!r}, value={self.value!r})"


# ── String lists ──────────────────────────────────────────────────────────────

class PropertyStrList(Property):
    """List of strings. Default merge: child replaces parent (override)."""

    def __init__(self, name: str, values: list[str], inheritable : bool = True):
        super().__init__(name, inheritable)
        self.values: list[str] = list(values)

    def clone(self) -> PropertyStrList:
        return PropertyStrList(self.name, self.values.copy())
    
    def merge_with_parent(self, parent: PropertyStrList) -> PropertyStrList:
        return PropertyStrList(self.name, list(self.values))
    
    @staticmethod
    def _append(base: list[str], extra: list[str]) -> list[str]:
        result = list(base)
        for item in extra:
            if item not in result:
                result.append(item)
        return result

    def __repr__(self):
        return f"PropertyStrList(name={self.name!r}, values={self.values})"


class PropertyStrListAppend(PropertyStrList):
    """Created by parser from 'append-foo'. Appends to parent list."""

    def merge_with_parent(self, parent: PropertyStrList) -> PropertyStrList:
        merged = self._append(parent.values, self.values)
        return PropertyStrList(self.name, merged)  # consumed → plain list


class PropertyStrListRemove(PropertyStrList):
    """Created by parser from 'remove-foo'. Removes items from parent list."""

    def merge_with_parent(self, parent: PropertyStrList) -> PropertyStrList:
        to_remove = set(self.values)
        remaining = [v for v in parent.values if v not in to_remove]
        return PropertyStrList(self.name, remaining)  # consumed → plain list


# ── Node lists ────────────────────────────────────────────────────────────────

class PropertyNodeList(Property):
    """List of Nodes merged by 'name' key (features, feature-rules)."""

    def __init__(self, name: str, nodes: list):
        super().__init__(name)
        self.nodes: list[Node] = list(nodes)

    def get_node(self, name: str) -> Optional[Node]:
        return next((n for n in self.nodes if n.name == name), None)
    
    def merge_with_parent(self, parent: PropertyNodeList) -> PropertyNodeList:
        result = []
        # Check all parents nodes
        # If not in self, add it
        # if in self, merge it
        for parent_node in parent.nodes:
            self_node = self.get_node(parent_node.name)
            if not self_node:
                result.append(parent_node.clone())
            else:
                result.append(self_node.merge_with_parent(parent_node))
        # Add all self node that are not in parent
        for self_node in self.nodes: 
            parent_node = parent.get_node(self_node.name)
            if not parent_node:
                result.append(self_node.clone())

        return PropertyNodeList(self.name, result)

    def clone(self) -> "PropertyNodeList":
        return PropertyNodeList(self.name, [n.clone() for n in self.nodes])
    
    def __repr__(self):
        return f"PropertyNodeList(name={self.name!r}, nodes={[n.name for n in self.nodes]})"


class PropertyNodeDict(Property):
    """Dict of named Nodes (per-compiler overrides)."""

    def __init__(self, name: str, entries: dict):
        super().__init__(name)
        self.entries: dict[str, Node] = dict(entries)

    def merge_with_parent(self, parent: PropertyNodeDict) -> PropertyNodeDict:
        result = {}
        # Check all parents entries
        # If not in self, add it
        # if in self, merge it
        for name, parent_prop in parent.entries.items():
            self_prop = self.entries.get(name)
            if not self_prop:
                result[name] = parent_prop.clone()
            else:
                result[name] = self_prop.merge_with_parent(parent_prop)
        # Add all self node that are not in parent
        for name, self_prop in self.entries.items(): 
            if name not in parent.entries: 
                result[name] = self_prop.clone()

        return PropertyNodeDict(self.name, result)

    def clone(self) -> PropertyNodeList:
        return PropertyNodeDict(self.name, {k: v.clone() for k, v in self.entries.items()})
    
    def __repr__(self):
        return f"PropertyNodeDict(name={self.name!r}, entries={list(self.entries.keys())})"


# ── Node ──────────────────────────────────────────────────────────────────────
from typing import Optional, TypeVar, Type
T = TypeVar("T", bound=Property)

class Node(ABC):
    """
    Base class for all Kiss nodes.
    get_property() returns the last property with the given name.
    """

    def __init__(self, name: str):
        self.name = name
        self.properties: dict[str, Property] = {}

    def clone(self) -> Node:
        result = self.__class__(self.name)
        for prop in self.properties.values():
            result.add_property(prop.clone())
        return result
    
    def add_property(self, prop: Property):
        if prop.name in self.properties:
            raise ValueError(f"Duplicate property '{prop.name}' in node '{self.name}'")
        self.properties[prop.name] = prop

    def get_property(self, name: str) -> Property | None:
        return self.properties.get(name)

    def get_property_as(self, name: str, prop_type: Type[T]) -> T | None:
        """Return the last property with this name if it matches prop_type, else None."""
        prop = self.get_property(name)
        if isinstance(prop, prop_type):
            return prop
        return None

    # def merge(self, child: "Node") -> "Node":
    #     """
    #     Merge self with child.
    #     Child drives every property merge via merge_with_parent().
    #     NON_INHERITABLE_KEYS are taken from child only.
    #     Multiple ops on the same key are applied sequentially in order.
    #     """
    #     result = child.__class__(child.name)

    #     # Non-inheritable: from child only
    #     for prop in child._props:
    #         if prop.name in NON_INHERITABLE_KEYS:
    #             result.add_property(prop)

    #     # Build parent lookup (last value per key)
    #     parent_lookup: dict[str, Property] = {
    #         p.name: p for p in self._props
    #         if p.name not in NON_INHERITABLE_KEYS
    #     }

    #     # Apply child ops in declaration order, tracking running result per key
    #     running: dict[str, Property] = {}
    #     touched: set[str] = set()

    #     for prop in child._props:
    #         if prop.name in NON_INHERITABLE_KEYS:
    #             continue
    #         key = prop.name

    #         # Current base: previous op result, or parent value, or empty placeholder
    #         if key in running:
    #             current = running[key]
    #         elif key in parent_lookup:
    #             current = parent_lookup[key]
    #         else:
    #             # No parent — treat as empty base of same type
    #             current = prop.__class__(key, [] if hasattr(prop, 'values') else {})

    #         running[key] = prop.merge_with_parent(current)
    #         touched.add(key)

    #     # Add all resolved child ops
    #     for key, prop in running.items():
    #         result.add_property(prop)

    #     # Inherit parent keys not touched by any child op
    #     for key, prop in parent_lookup.items():
    #         if key not in touched:
    #             result.add_property(prop)

    #     return result

    def merge_with_parent(self, parent: Node) -> Node:
        result = self.__class__(self.name)
        # For all property that are in parents
        # If in self (child), merge it
        # If not in self (child), add it
        for name, parent_prop in parent.properties.items():
            # Do not inherite property if not inheritable
            if not parent_prop.inheritable:
                continue
            self_prop = self.get_property(name)
            if self_prop:
                result.add_property(self_prop.merge_with_parent(parent_prop))
            else:
                result.add_property(parent_prop.clone())
                

        # For all property that are in self (child) and not is parent
        # Keep it in self (child)
        for name, self_prop in self.properties.items(): 
            if name not in parent.properties: 
                result.add_property(self_prop.clone())

        return result

    def __repr__(self):
        return f"{self.__class__.__name__}(name={self.name!r}, properties={list(self.properties.keys())})"
