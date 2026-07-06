"""
node.py
-------
Base classes for all Kiss nodes and properties.

Property.resolve_extends(parent)
------------------------------------
Every Property subclass decides how it combines with its parent's value.
The child (self) drives the merge — it knows what it wants from the parent.

Default behaviors:
  Property / PropertyStr / PropertyBool  → child replaces parent
  PropertyStrList                        → child replaces parent (override)
  PropertyNodeList                       → merged by 'name' key
  PropertyNodeDict                       → merged by dict key

Multiple ops on the same property key
---------------------------------------
A Node stores properties as an ordered list (not a dict) so that
multiple operations on the same key (e.g. add-flags then remove-flags)
are applied in declaration order. Node.get_property() returns the last one.
"""
from __future__ import annotations
from abc import ABC
from unittest import result

# Keys that belong to a node itself and must NOT be inherited by children.


# ── Base ──────────────────────────────────────────────────────────────────────

class Property(ABC):
    """Base class. Default merge: child replaces parent."""

    def __init__(self, name: str, *, is_mergeable : bool = True, is_dispatchable : bool = True):
        self.name = name
        self.is_mergeable = is_mergeable
        self.is_dispatchable = is_dispatchable
    
    def merge_with(self, parent: Property, parent_list_name_to_ignore: set[str] = None) -> Property:
        return copy.deepcopy(self)
    
    def dispatch(self, top: Property = None) -> Property:
        return copy.deepcopy(self)
    
    def __repr__(self):
        return f"{self.__class__.__name__}(name={self.name!r})"

# ── Scalars ───────────────────────────────────────────────────────────────────

class PropertyStr(Property):
    def __init__(self, name: str, value: str, is_mergeable : bool = True, is_dispatchable : bool = True):
        super().__init__(name, is_mergeable=is_mergeable, is_dispatchable=is_dispatchable)
        self.value = value

    def __repr__(self):
        return f"PropertyStr(name={self.name!r}, value={self.value!r}, is_mergeable={self.is_mergeable!r}, is_dispatchable={self.is_dispatchable!r})"

    def is_empty(self) -> bool:
        return not self.value
    
    def append_to_lines_print(self, lines, ignore_empty):
        if not self.is_empty() or not ignore_empty:
            lines.append(f"{self.name}: {self.value!r}")

    def append_to_json_print(self, json, ignore_empty):
        if not self.is_empty() or not ignore_empty:
            json[self.name] = self.value

class PropertyBool(Property):
    def __init__(self, name: str, value: bool, is_mergeable : bool = True, is_dispatchable : bool = True):
        super().__init__(name, is_mergeable=is_mergeable, is_dispatchable=is_dispatchable)
        self.value = value
    
    def resolve_extends(self, parent: PropertyStr) -> PropertyStr:
        return PropertyBool(self.name, self.value, self.is_mergeable, self.is_dispatchable)
    
    def __repr__(self):
        return f"PropertyBool(name={self.name!r}, value={self.value!r}, is_mergeable={self.is_mergeable!r}, is_dispatchable={self.is_dispatchable!r})"

    def append_to_lines_print(self, lines, ignore_empty):
        lines.append(f"{self.name}: {self.value!r}")

    def append_to_json_print(self, json, ignore_empty):
        json[self.name] = self.value

class PropertyInt(Property):
    def __init__(self, name: str, value: int, is_mergeable : bool = True, is_dispatchable : bool = True):
        super().__init__(name, is_mergeable=is_mergeable, is_dispatchable=is_dispatchable)
        self.value = value
    
    def resolve_extends(self, parent: PropertyStr) -> PropertyStr:
        return PropertyBool(self.name, self.value, self.is_mergeable, self.is_dispatchable)

    def __repr__(self):
        return f"PropertyBool(name={self.name!r}, value={self.value!r}, is_mergeable={self.is_mergeable!r}, is_dispatchable={self.is_dispatchable!r})"
  
    def append_to_lines_print(self, lines, ignore_empty):
        lines.append(f"{self.name}: {self.value!r}")

    def append_to_json_print(self, json, ignore_empty):
        json[self.name] = self.value

# ── String lists ──────────────────────────────────────────────────────────────

class PropertyStrList(Property):
    """List of strings. Default merge: child replaces parent (override)."""

    def __init__(self, name: str, values: list[str], is_mergeable : bool = True, is_dispatchable : bool = True):
        super().__init__(name, is_mergeable=is_mergeable, is_dispatchable=is_dispatchable)
        self.values: list[str] = list(values)

    def apply_modifier_prop(self, mod : PropertyStrListModifier):
        if mod.operation == StrListModifierOperation.ADD or mod.operation == StrListModifierOperation.ENABLE:
            for value in mod.values:
                if value not in self.values:
                    self.values.append(value)
        elif mod.operation == StrListModifierOperation.REMOVE or mod.operation == StrListModifierOperation.DISABLE:
           for value in mod.values:
                if value in self.values:
                    self.values.remove(value)

    def __repr__(self):
        return f"PropertyStrList(name={self.name!r}, values={self.values}, is_mergeable={self.is_mergeable!r}, is_dispatchable={self.is_dispatchable!r} )"

    def is_empty(self) -> bool:
        return not self.values
    
    def append_to_lines_print(self, lines, ignore_empty):
        if not self.is_empty() or not ignore_empty:
            lines.append(f"{self.name}: {self.values!r}")

    def append_to_json_print(self, json, ignore_empty):
        if not self.is_empty() or not ignore_empty:
            json[self.name] = self.values

import copy
from enum import Enum
class StrListModifierOperation(Enum):
    ENABLE = "enable"
    DISABLE = "disable"
    ADD = "add"
    REMOVE = "remove"

class PropertyStrListModifier(Property):
    def __init__(self, list_name, values,  operation: StrListModifierOperation):
        super().__init__(f"{operation.value}-{list_name}")
        self.values: list[str] = list(values)
        self.list_name = list_name
        self.operation = operation
    
    def __repr__(self):
        return (
            f"PropertyStrListModifier("
            f"name={self.name!r}, "
            f"values={self.values}, "
            f"operation={self.operation.value!r})"
        )
    
    def is_empty(self) -> bool:
        return not self.values
    
    def append_to_lines_print(self, lines, ignore_empty):
        if not self.is_empty() or not ignore_empty:
            lines.append(f"{self.name}: {self.values!r}")

    def append_to_json_print(self, json, ignore_empty):
        if not self.is_empty() or not ignore_empty:
            json[self.name] = self.values

    def merge_with(self, other:StrListModifierOperation, list_property_to_ignore: list[str] = None) -> PropertyStrListModifier:
        assert self.operation == other.operation, "Not the same operation"
        assert self.list_name == other.list_name, "Not the same list"
        # Merged list in order, first other, then self
        # We want to keep read order the same as in the file from top to bottom
        prefix = []
        for value in other.values:
            if value not in self.values and value not in prefix:
                prefix.append(value)
        values = prefix + self.values
        return PropertyStrListModifier(self.list_name, values ,self.operation)
    
    def dispatch(self, other: StrListModifierOperation, list_property_to_ignore: list[str] = None) -> Property:
        assert self.operation == other.operation, "Not the same operation"
        assert self.list_name == other.list_name, "Not the same list"
        # Merged list in order, first other, then self
        # We want to keep read order the same as in the file from top to bottom
        prefix = []
        for value in other.values:
            if value not in self.values and value not in prefix:
                prefix.append(value)
        values = prefix + self.values
        return PropertyStrListModifier(self.list_name, values ,self.operation)
    
# ── Node lists ────────────────────────────────────────────────────────────────

class PropertyNodeList(Property):
    """List of Nodes merged by 'name' key (features, feature-rules)."""

    def __init__(self, name: str, nodes: list):
        super().__init__(name)
        self.nodes: list[PropertyDict] = list(nodes)

    def get_node(self, name: str) -> Optional[PropertyDict]:
        return next((n for n in self.nodes if n.name == name), None)
    
    def resolve_extends(self, parent: PropertyNodeList) -> PropertyNodeList:
        result = []
        # Check all parents nodes
        # If not in self, add it
        # if in self, merge it
        for parent_node in parent.nodes:
            self_node = self.get_node(parent_node.name)
            if not self_node:
                result.append(parent_node.clone())
            else:
                result.append(self_node.resolve_extends(parent_node))
        # Add all self node that are not in parent
        for self_node in self.nodes: 
            parent_node = parent.get_node(self_node.name)
            if not parent_node:
                result.append(self_node.clone())

        return PropertyNodeList(self.name, result, self.is_mergeable)

    def __repr__(self):
        return f"PropertyNodeList(name={self.name!r}, nodes={[n.name for n in self.nodes]}, is_mergeable={self.is_mergeable!r})"


# ── PropertyDict ──────────────────────────────────────────────────────────────────────
from typing import Optional, TypeVar, Type
T = TypeVar("T", bound=Property)

class PropertyDict:
    """
    Base class for all Kiss nodes.
    get_property() returns the last property with the given name.
    """

    def __init__(self):
        self.properties: dict[str, Property] = {}
    
    def items(self):
        return self.properties.items()
    
    def values(self):
        return self.properties.values()
    
    def __contains__(self, name: str) -> bool:
        return name in self.properties
    
    def add_property(self, prop: Property): 
        if prop.name in self.properties:
            raise ValueError(f"Duplicate property '{prop.name}'")
        self.properties[prop.name] = prop

    def add_or_merge_property(self, prop: Property, list_property_to_ignore: list[str] = None):
        if prop.name in self.properties:
            existing_prop = self.properties[prop.name]
            merged_prop = existing_prop.merge_with(prop, list_property_to_ignore)
            self.properties[prop.name] = merged_prop
        else:
            self.properties[prop.name] = prop

    def remove_property(self, name: Property):
        self.properties.pop(name)

    def get_property(self, name: str) -> Property | None:
        return self.properties.get(name)

    def get_property_as(self, name: str, prop_type: Type[T]) -> T | None:
        """Return the last property with this name if it matches prop_type, else None."""
        prop = self.get_property(name)
        if isinstance(prop, prop_type):
            return prop
        return None

    def apply_modifiers(self) -> PropertyDict:
        """
        Resolve modifier properties (add-f:[...] / remove-f:[...]) against their
        target list, then drop the modifiers from the result.

        Modifiers are applied in two phases, ADD before REMOVE, so that an
        element added and removed in the same node consistently ends up removed
        regardless of declaration order.
        """
        result = PropertyDict()
        
        # List of all modifiers present in self (child)
        list_mod_props = {}

        # Collect list modifiers
        for self_prop in self.properties.values():
            if isinstance(self_prop, PropertyStrListModifier):
                list_mod_props.setdefault(self_prop.operation, []).append(self_prop)
            else:
                result.add_property(copy.deepcopy(self_prop))

        # Apply append modifiers
        for append_mod_prop in list_mod_props.get(StrListModifierOperation.ADD, []):
            list_prop_to_modify = result.get_property_as(
                append_mod_prop.list_name,
                PropertyStrList
            )

            # Create the list if not exist
            if not list_prop_to_modify:
                list_prop_to_modify = PropertyStrList(append_mod_prop.list_name, [])
                result.add_property(list_prop_to_modify)

            list_prop_to_modify.apply_modifier_prop(append_mod_prop)

        # Apply remove modifiers
        for remove_mod_prop in list_mod_props.get(StrListModifierOperation.REMOVE, []):
            list_prop_to_modify = result.get_property_as(
                remove_mod_prop.list_name,
                PropertyStrList
            )

            if not list_prop_to_modify:
                list_prop_to_modify = PropertyStrList(remove_mod_prop.list_name, [])
                result.add_property(list_prop_to_modify)

            list_prop_to_modify.apply_modifier_prop(remove_mod_prop)

        return result
    
    def explicit_list_names(self) -> set[str]:
        explicit_list_names = set[str]()
        for self_property in self.properties.values():
            if isinstance(self_property, PropertyStrList):
                explicit_list_names.add(self_property.name)
        return explicit_list_names

    def merge_with(self, parent: PropertyDict, parent_list_name_to_ignore: set[str] = None) -> PropertyDict:
        """
        Merge this PropertyDict with a parent one, extending the parent with self (child).

        Rules:
        - If self (child) has an explicit list (e.g. `features:[...]`), any parent list
        or modifier related to that same list is ignored entirely.
        - Additional list names to ignore can optionally be passed via
        `parent_list_name_to_ignore`. This is mainly used when self (child) has a
        "global" explicit list that must override everything below it, including
        lists nested deeper in the hierarchy.

        Example:
            parent:
                compilers:
                features: [F_P]
            child:
                extends: parent
                features: [F_C]
                compilers:
                ...

        Here, child's `compilers:` should end up with [F_C], not [F_P], even though
        the explicit list isn't declared directly under `compilers:`. To achieve this,
        we pass [F_C] (child's own explicit list name) as `parent_list_name_to_ignore`,
        so that F_P is discarded when merging compilers.

        :param parent: the parent PropertyDict to merge into self
        :param parent_list_name_to_ignore: extra list names whose parent values must be
            discarded, even if not explicitly overridden at this level
        :return: a new PropertyDict resulting from the merge (parent + self, self wins)
        """
        result = PropertyDict()

        override_list_names = self.explicit_list_names()

        for p in parent.properties.values():
            if p.is_mergeable:
                overrided_name = p.list_name if isinstance(p, PropertyStrListModifier) else p.name
                if parent_list_name_to_ignore and overrided_name in parent_list_name_to_ignore:
                    continue
                if overrided_name not in override_list_names:
                    s = self.get_property(p.name)
                    if s:
                        result.add_property(s.merge_with(p))
                    else:
                        result.add_property(copy.deepcopy(p))

        for b in self.properties.values():
            if b.name not in result.properties:
                result.add_property(copy.deepcopy(b))

        return result
    
    def dispatch(self, top: PropertyDict) -> PropertyDict:
        """
        Dispatch (propagate) top-level properties down into self.

        This is the structural mirror of `merge_with`: instead of the child
        extending the parent, here the top-level properties are pushed down
        into self, unless self already declares an explicit list for that name
        (self wins, same rule as `merge_with`'s `override_list_names`).

        :param top: the top-level PropertyDict whose properties are propagated down
        :return: a new PropertyDict resulting from the dispatch (top + self, self wins)
        """
        result = PropertyDict()

        override_list_names = self.explicit_list_names()

        for t in top.properties.values():
            if t.is_dispatchable:
                overrided_name = t.list_name if isinstance(t, PropertyStrListModifier) else t.name
                if overrided_name not in override_list_names:
                    s = self.get_property(t.name)
                    if s:
                        result.add_property(s.dispatch(t))
                    else:
                        result.add_property(copy.deepcopy(t))

        for s in self.properties.values():
            if s.name not in result.properties:
                result.add_property(copy.deepcopy(s))

        return result

    def __repr__(self):
        return f"{self.__class__.__name__}(name={self.name!r}, properties={list(self.properties.keys())})"


