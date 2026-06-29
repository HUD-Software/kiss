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
from abc import ABC, abstractmethod


# Keys that belong to a node itself and must NOT be inherited by children.


# ── Base ──────────────────────────────────────────────────────────────────────

class Property(ABC):
    """Base class. Default merge: child replaces parent."""

    def __init__(self, name: str, inheritable : bool = True):
        self.name = name
        self.inheritable = inheritable
    
    def merge_with(self, parent: Property) -> Property:
        return copy.deepcopy(self)
    
    # @abstractmethod
    # def clone(self) -> Property:
    #     pass

    def append_to_lines_print(self, lines, ignore_empty):
        pass

    def dispatch(self) -> Property:
        return copy.deepcopy(self)
    
    def __repr__(self):
        return f"{self.__class__.__name__}(name={self.name!r})"

# ── Scalars ───────────────────────────────────────────────────────────────────

class PropertyStr(Property):
    def __init__(self, name: str, value: str, inheritable : bool = True):
        super().__init__(name, inheritable)
        self.value = value

    def __repr__(self):
        return f"PropertyStr(name={self.name!r}, value={self.value!r}, inheritable={self.inheritable!r})"

    def is_empty(self) -> bool:
        return not self.value
    
    def append_to_lines_print(self, lines, ignore_empty):
        if not self.is_empty() or not ignore_empty:
            lines.append(f"{self.name}: {self.value!r}")

    def append_to_json_print(self, json, ignore_empty):
        if not self.is_empty() or not ignore_empty:
            json[self.name] = self.value

class PropertyBool(Property):
    def __init__(self, name: str, value: bool, inheritable : bool = True):
        super().__init__(name, inheritable)
        self.value = value
    
    def resolve_extends(self, parent: PropertyStr) -> PropertyStr:
        return PropertyBool(self.name, self.value, self.inheritable)
    
    def __repr__(self):
        return f"PropertyBool(name={self.name!r}, value={self.value!r}, inheritable={self.inheritable!r})"

    def is_empty(self) -> bool:
        return not self.value
    
    def append_to_lines_print(self, lines, ignore_empty):
        if not self.is_empty() or not ignore_empty:
            lines.append(f"{self.name}: {self.value!r}")

    def append_to_json_print(self, json, ignore_empty):
        if not self.is_empty() or not ignore_empty:
            json[self.name] = self.value

# ── String lists ──────────────────────────────────────────────────────────────

class PropertyStrList(Property):
    """List of strings. Default merge: child replaces parent (override)."""

    def __init__(self, name: str, values: list[str], inheritable : bool = True):
        super().__init__(name, inheritable)
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
        return f"PropertyStrList(name={self.name!r}, values={self.values}, inheritable={self.inheritable!r})"

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

class PropertyStrListModifier(PropertyStrList):
    def __init__(self, name, list_name, values,  operation: StrListModifierOperation):
        super().__init__(name, values)
        self.list_name = list_name
        self.operation = operation
    
    def __repr__(self):
        return (
            f"PropertyStrListModifier("
            f"name={self.name!r}, "
            f"values={self.values}, "
            f"operation={self.operation.value!r})"
        )
    
    def merge_with(self, other:StrListModifierOperation) -> MergeResult:
        assert self.operation == other.operation, "Not the same operation"
        assert self.list_name == other.list_name, "Not the same list"
        # Merged list in order, first other, then self
        # We want to keep read order the same as in the file from top to bottom
        prefix = []
        for value in other.values:
            if value not in self.values and value not in prefix:
                prefix.append(value)
        values = prefix + self.values
        return PropertyStrListModifier(self.name, self.list_name, values ,self.operation)
    
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

        return PropertyNodeList(self.name, result, self.inheritable)

    def __repr__(self):
        return f"PropertyNodeList(name={self.name!r}, nodes={[n.name for n in self.nodes]}, inheritable={self.inheritable!r})"


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
        Apply modifier add/remove-enable/disable
        Remove then from properties
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
    
    def explicit_list_name(self) -> list[str]:
        explicit_list_name = list[str]()
        for self_property in self.properties.values():
            if isinstance(self_property, PropertyStrListModifier):
                explicitly_present_list : PropertyStrList = self.properties.get(self_property.list_name)
                if explicitly_present_list:
                    explicit_list_name.append(self_property.list_name)
        return explicit_list_name

    def merge_with(self, parent: PropertyDict, parent_list_property_to_ignore : list[str] = None) -> PropertyDict:
        result = PropertyDict()

        if not parent_list_property_to_ignore:
            parent_list_property_to_ignore = self.explicit_list_name()

        # For all property that are in self
        for self_property in self.properties.values():
            parent_prop = parent.get_property(self_property.name)

            # if in parent, merge it if inheritable
            if parent_prop:
                if parent_prop.inheritable:
                    # If we have a modifier that must ignore the parent
                    # Ignore the merge and juste keep it unmodified
                    if isinstance(self_property, PropertyStrListModifier):
                        if self_property.list_name in parent_list_property_to_ignore:
                            result.add_property(copy.deepcopy(self_property))
                            continue
                    elif isinstance(self_property, PropertyStrList):
                        if self_property.name in parent_list_property_to_ignore:
                            result.add_property(copy.deepcopy(self_property))
                            continue
                    result.add_property(self_property.merge_with(parent_prop))
            # if not in parent, add it
            else:
                result.add_property(copy.deepcopy(self_property))

        # Add properties that are in parent and not in self if inheritable
        for parent_prop in parent.properties.values():
            if parent_prop.name not in self.properties and parent_prop.inheritable:
                if isinstance(parent_prop, PropertyStrListModifier):
                    if parent_prop.list_name in parent_list_property_to_ignore:
                        continue
                elif isinstance(parent_prop, PropertyStrList):
                    if parent_prop.name in parent_list_property_to_ignore:
                        continue
                result.add_property(copy.deepcopy(parent_prop))

        return result

    def __repr__(self):
        return f"{self.__class__.__name__}(name={self.name!r}, properties={list(self.properties.keys())})"


