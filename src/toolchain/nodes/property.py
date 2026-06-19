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
        return PropertyStr(self.name, self.value, self.inheritable)
    
    def merge_with_parent(self, parent: PropertyStr) -> PropertyStr:
        return PropertyStr(self.name, self.value, self.inheritable)
    
    def __repr__(self):
        return f"PropertyStr(name={self.name!r}, value={self.value!r}, inheritable={self.inheritable!r})"


class PropertyBool(Property):
    def __init__(self, name: str, value: bool, inheritable : bool = True):
        super().__init__(name, inheritable)
        self.value = value

    def clone(self) -> PropertyBool:
        return PropertyBool(self.name, self.value, self.inheritable)
    
    def merge_with_parent(self, parent: PropertyStr) -> PropertyStr:
        return PropertyBool(self.name, self.value, self.inheritable)
    
    def __repr__(self):
        return f"PropertyBool(name={self.name!r}, value={self.value!r}, inheritable={self.inheritable!r})"


# ── String lists ──────────────────────────────────────────────────────────────

class PropertyStrList(Property):
    """List of strings. Default merge: child replaces parent (override)."""

    def __init__(self, name: str, values: list[str], inheritable : bool = True):
        super().__init__(name, inheritable)
        self.values: list[str] = list(values)

    def clone(self) -> PropertyStrList:
        return PropertyStrList(self.name, self.values.copy(), self.inheritable)
    
    def merge_with_parent(self, parent: PropertyStrList) -> PropertyStrList:
        return PropertyStrList(self.name, list(self.values), self.inheritable)
    
    def apply_modifier_prop(self, mod : PropertyStrListModifier):
        if mod.operation == StrListModifierOperation.APPEND:
            for value in mod.values:
                if value not in self.values:
                    self.values.append(value)
        elif mod.operation == StrListModifierOperation.REMOVE:
           for value in mod.values:
                if value in self.values:
                    self.values.remove(value)

    def __repr__(self):
        return f"PropertyStrList(name={self.name!r}, values={self.values}, inheritable={self.inheritable!r})"

from enum import Enum
class StrListModifierOperation(Enum):
    APPEND = "append"
    REMOVE = "remove"

class PropertyStrListModifier(PropertyStrList):
    def __init__(self, name, list_name, values,  operation: StrListModifierOperation):
        super().__init__(name, values, False)
        self.list_name = list_name
        self.operation = operation
    
    def __repr__(self):
        return (
            f"PropertyStrListModifier("
            f"name={self.name!r}, "
            f"values={self.values}, "
            f"operation={self.operation.value!r})"
        )

# ── Node lists ────────────────────────────────────────────────────────────────

class PropertyNodeList(Property):
    """List of Nodes merged by 'name' key (features, feature-rules)."""

    def __init__(self, name: str, nodes: list):
        super().__init__(name)
        self.nodes: list[PropertyDict] = list(nodes)

    def get_node(self, name: str) -> Optional[PropertyDict]:
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

        return PropertyNodeList(self.name, result, self.inheritable)

    def clone(self) -> "PropertyNodeList":  
        return PropertyNodeList(self.name, [n.clone() for n in self.nodes], self.inheritable)
    
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
    
    def clone(self) -> PropertyDict:
        cloned = PropertyDict()
        for prop in self.properties.values():
            cloned.add_property(prop.clone())
        return cloned
    
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


    def merge_with_parent(self, parent: PropertyDict) -> PropertyDict:
        """
        Merge the current node (child) with a parent node and returns a new resolved node.

        The merge follows inheritance rules:
        - Properties defined in the parent are inherited by default.
        - If the child redefines a property, it overrides or merges with the parent version.
        - Non-inheritable properties (e.g. abstract markers or internal modifiers)
        are ignored during inheritance.
        - List properties can be post-processed using explicit modifier properties
        (append/remove), allowing fine-grained inheritance control.

        The merge process is performed in three steps:

        1. Parent inheritance pass:
        - Iterate over all parent properties.
        - If the child defines the same property, merge both definitions.
        - Otherwise, clone and inherit the parent property.
        - Skip properties marked as non-inheritable.

        2. Child-only properties collection:
        - Iterate over child properties.
        - Direct properties not present in the parent are copied directly.
        - Modifier properties (e.g. PropertyStrListModifier) are NOT added directly;
            they are collected for later application.

        3. Post-processing of list modifiers:
        - Apply all collected list modifiers on the merged result.
        - This allows child nodes to:
            - append values to inherited lists
            - remove values from inherited lists
        - If the target list property does not exist yet, it is created.

        This design ensures that:
        - inheritance remains predictable and deterministic
        - child nodes can refine inherited list-based properties
        - modifier logic is decoupled from structural merging
        """
        
        result = PropertyDict()

        # For all property that are in parents
        # If in self (child), merge it
        # If not in self (child), add it
        for name, parent_prop in parent.properties.items():
            # Do not inherit property if not inheritable (e.g. PropertyStrListModifier, is_abstract)
            if not parent_prop.inheritable:
                continue

            self_prop = self.get_property(name)
            if self_prop:
                result.add_property(self_prop.merge_with_parent(parent_prop))
            else:
                result.add_property(parent_prop.clone())

        # List of all modifiers present in self (child)
        list_mod_props = {}

        # Collect child-only properties and list modifiers
        for name, self_prop in self.properties.items():
            if isinstance(self_prop, PropertyStrListModifier):
                list_mod_props.setdefault(self_prop.operation, []).append(self_prop)

            elif name not in parent.properties:
                result.add_property(self_prop.clone())

        # Apply append modifiers
        for append_mod_prop in list_mod_props.get(StrListModifierOperation.APPEND, []):
            list_prop_to_modify = result.get_property_as(
                append_mod_prop.list_name,
                PropertyStrList
            )

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

    def __repr__(self):
        return f"{self.__class__.__name__}(name={self.name!r}, properties={list(self.properties.keys())})"


