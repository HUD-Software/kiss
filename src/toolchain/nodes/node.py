from typing import Generic, TypeVar

T = TypeVar("T")

class Property:
    """Base class for all properties."""
    def __init__(self, name: str):
        self.name = name

    def __repr__(self):
        return f"{self.__class__.__name__}(name={self.name!r})"


class Node:
    """Base class for all nodes."""
    def __init__(self, name: str):
        self.name = name
        self.properties: dict[str, Property] = {}

    def add_property(self, prop: Property):
        self.properties[prop.name] = prop

    def get_property(self, name: str) -> Property | None:
        return self.properties.get(name)

    def __repr__(self):
        return f"{self.__class__.__name__}(name={self.name!r}, properties={list(self.properties.keys())})"



class PropertyStr(Property):
    """A property holding a single string value."""
    def __init__(self, name: str, value: str):
        super().__init__(name)
        self.value = value

    def __repr__(self):
        return f"PropertyStr(name={self.name!r}, value={self.value!r})"


class PropertyBool(Property):
    """A property holding a boolean value."""
    def __init__(self, name: str, value: bool):
        super().__init__(name)
        self.value = value

    def __repr__(self):
        return f"PropertyBool(name={self.name!r}, value={self.value!r})"



class PropertyList(Property, Generic[T]):
    def __init__(self, name: str, values: list[T]):
        super().__init__(name)
        self.values = values

    def __repr__(self):
        return (
            f"{self.__class__.__name__}("
            f"name={self.name!r}, values={self.values!r})"
        )

class PropertyStrList(PropertyList[str]):
    """A property holding a list of strings."""
    def __init__(self, name: str, values: list[str]):
        super().__init__(name, values)

    def __repr__(self):
        return f"PropertyStrList(name={self.name!r}, values={self.values!r})"

class PropertyNodeList(PropertyList[Node]):
    """A property holding a list of Nodes."""
    def __init__(self, name: str, nodes: list[Node]):
        super().__init__(name, nodes)
        self.nodes: list[Node] = nodes

    def __repr__(self):
        return f"PropertyNodeList(name={self.name!r}, nodes={self.nodes!r})"

class PropertyNodeDict(Property):
    """A property holding a dict of named Nodes (e.g. linker-specific overrides)."""
    def __init__(self, name: str, entries: dict):
        super().__init__(name)
        self.entries: dict[str, Node] = entries

    def __repr__(self):
        return f"PropertyNodeDict(name={self.name!r}, entries={self.entries!r})"
    