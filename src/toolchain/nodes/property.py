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

# Keys that belong to a node itself and must NOT be inherited by children.


# ── Base ──────────────────────────────────────────────────────────────────────

class Property(ABC):
    """Base class. Default merge: child replaces parent."""

    def __init__(self, name: str, *, mergeable : bool = True, dispatchable : bool = True):
        self.name = name
        self.mergeable = mergeable
        self.dispatchable = dispatchable
    
    def merge_with(self, parent: Property, list_property_to_ignore: list[str] = None) -> Property:
        return copy.deepcopy(self)
    
    def dispatch(self, property: Property = None, list_property_to_ignore: list[str] = None) -> Property:
        return copy.deepcopy(self)
    
    def __repr__(self):
        return f"{self.__class__.__name__}(name={self.name!r})"

# ── Scalars ───────────────────────────────────────────────────────────────────

class PropertyStr(Property):
    def __init__(self, name: str, value: str, mergeable : bool = True, dispatchable : bool = True):
        super().__init__(name, mergeable=mergeable, dispatchable=dispatchable)
        self.value = value

    def __repr__(self):
        return f"PropertyStr(name={self.name!r}, value={self.value!r}, mergeable={self.mergeable!r}, dispatchable={self.dispatchable!r})"

    def is_empty(self) -> bool:
        return not self.value
    
    def append_to_lines_print(self, lines, ignore_empty):
        if not self.is_empty() or not ignore_empty:
            lines.append(f"{self.name}: {self.value!r}")

    def append_to_json_print(self, json, ignore_empty):
        if not self.is_empty() or not ignore_empty:
            json[self.name] = self.value

class PropertyBool(Property):
    def __init__(self, name: str, value: bool, mergeable : bool = True, dispatchable : bool = True):
        super().__init__(name, mergeable=mergeable, dispatchable=dispatchable)
        self.value = value
    
    def resolve_extends(self, parent: PropertyStr) -> PropertyStr:
        return PropertyBool(self.name, self.value, self.mergeable, self.dispatchable)
    
    def __repr__(self):
        return f"PropertyBool(name={self.name!r}, value={self.value!r}, mergeable={self.mergeable!r}, dispatchable={self.dispatchable!r})"

    def append_to_lines_print(self, lines, ignore_empty):
        lines.append(f"{self.name}: {self.value!r}")

    def append_to_json_print(self, json, ignore_empty):
        json[self.name] = self.value

class PropertyInt(Property):
    def __init__(self, name: str, value: int, mergeable : bool = True, dispatchable : bool = True):
        super().__init__(name, mergeable=mergeable, dispatchable=dispatchable)
        self.value = value
    
    def resolve_extends(self, parent: PropertyStr) -> PropertyStr:
        return PropertyBool(self.name, self.value, self.mergeable, self.dispatchable)

    def __repr__(self):
        return f"PropertyBool(name={self.name!r}, value={self.value!r}, mergeable={self.mergeable!r}, dispatchable={self.dispatchable!r})"
  
    def append_to_lines_print(self, lines, ignore_empty):
        lines.append(f"{self.name}: {self.value!r}")

    def append_to_json_print(self, json, ignore_empty):
        json[self.name] = self.value

# ── String lists ──────────────────────────────────────────────────────────────

class PropertyStrList(Property):
    """List of strings. Default merge: child replaces parent (override)."""

    def __init__(self, name: str, values: list[str], mergeable : bool = True, dispatchable : bool = True):
        super().__init__(name, mergeable=mergeable, dispatchable=dispatchable)
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
        return f"PropertyStrList(name={self.name!r}, values={self.values}, mergeable={self.mergeable!r}, dispatchable={self.dispatchable!r} )"

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
    def __init__(self, name, list_name, values,  operation: StrListModifierOperation):
        super().__init__(name)
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

        return PropertyNodeList(self.name, result, self.mergeable)

    def __repr__(self):
        return f"PropertyNodeList(name={self.name!r}, nodes={[n.name for n in self.nodes]}, mergeable={self.mergeable!r})"


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
            if isinstance(self_property, PropertyStrList):
                explicit_list_name.append(self_property.name)
        return explicit_list_name

    def _should_ignore(prop: Property, ignore_list: list[str]) -> bool:
        """Determine if a property must be kept as-is (ignored during merge/dispatch)
        because it belongs to an explicit list name."""
        if isinstance(prop, PropertyStrListModifier):
            return prop.list_name in ignore_list
        if isinstance(prop, PropertyStrList):
            return prop.name in ignore_list
        return False

    def _combine(
        self,
        other: PropertyDict,
        ignore_list: list[str],
        flag_fn,       # Callable[[Property], bool] -> True si combinable
        combine_fn,    # Callable[[Property, Property], Property]
    ) -> PropertyDict:
        """Generic merge/dispatch: combines self's properties with other's,
        driven by flag_fn (decides if a property from `other` is eligible)
        and combine_fn(self_property, other_property) -> Property."""
        result = PropertyDict()

        for self_property in self.properties.values():
            other_prop = other.get_property(self_property.name)

            # If not in parent, add it
            if other_prop is None:
                result.add_property(copy.deepcopy(self_property))
                continue

            # If not eligible for combination, skip it
            if not flag_fn(other_prop):
                continue

            # If we have a modifier that must ignore the parent
            # Ignore the merge and juste keep it unmodified
            if isinstance(self_property, PropertyStrListModifier):
                if self_property.list_name in ignore_list:
                    result.add_property(copy.deepcopy(self_property))
                    continue
            elif isinstance(self_property, PropertyStrList):
                if self_property.name in ignore_list:
                    result.add_property(copy.deepcopy(self_property))
                    continue
            result.add_property(combine_fn(self_property, other_prop))

        # Add properties that are in parent and not in self if  eligible for combination
        for other_prop in other.properties.values():
            # If already in self, skip it, it was already handled above
            if other_prop.name in self.properties:
                continue
            # If not eligible for combination, skip it
            if not flag_fn(other_prop):
                continue

            if isinstance(other_prop, PropertyStrListModifier):
                if other_prop.list_name in ignore_list:
                    continue
            elif isinstance(other_prop, PropertyStrList):
                if other_prop.name in ignore_list:
                    continue
            result.add_property(copy.deepcopy(other_prop))
        return result


    def merge_with(self, parent: PropertyDict, list_property_to_ignore: list[str] = None) -> PropertyDict:
        if list_property_to_ignore:
            list_property_to_ignore = list_property_to_ignore + self.explicit_list_name()
        else:
            list_property_to_ignore = self.explicit_list_name()
        return self._combine(
            parent,
            list_property_to_ignore,
            flag_fn=lambda prop: prop.mergeable,
            combine_fn=lambda self_prop, parent_prop: self_prop.merge_with(parent_prop),
        )


    def dispatch(self, properties: PropertyDict) -> PropertyDict:
        ignore_list = self.explicit_list_name()
        return self._combine(
            properties,
            ignore_list,
            flag_fn=lambda prop: prop.dispatchable,
            combine_fn=lambda self_prop, parent_prop: self_prop.dispatch(parent_prop, ignore_list),
        )
    

    def __repr__(self):
        return f"{self.__class__.__name__}(name={self.name!r}, properties={list(self.properties.keys())})"


