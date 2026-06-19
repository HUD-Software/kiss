from toolchain.nodes.compiler_nodes import CompilersOverrideNode
from toolchain.nodes.linker_nodes import LinkersOverrideNode
from toolchain.nodes.project_type_nodes import ProjectsOverrideNode

from .property import Property, PropertyDict, PropertyBool
from typing import TypeVar, Type
T = TypeVar("T", bound=Property)

class ProfileNode(Property):
    """Represents a profile entry.

    - name: debug
      description: ...
      extends: ...
      compilers: ...
      linkers: ...
      projects: ...
    """
    def __init__(self, name : str):
        super().__init__(name)
        self._properties = PropertyDict()
    
    @property
    def properties(self) -> PropertyDict:
        return self._properties
    @property
    def is_abstract(self) -> bool :
        prop = self.get_property_as("is_abstract", PropertyBool)
        return prop.value if prop else False
    
    def get_property(self, name: str) -> Property | None:
        return self.properties.get_property(name)
    
    def add_property(self, property):
        self.properties.add_property(property)

    def get_property_as(self, name: str, prop_type: Type[T]) -> T | None:
        self.properties.get_property_as(name, prop_type)

    def clone(self) -> ProfileNode:
        cloned  = ProfileNode(self.name)
        cloned.properties = self._properties.clone()
        return cloned
    
    def merge_with_parent(self, parent):
        assert type(parent) is type(self), "Type mismatch"
        merged = ProfileNode(self.name)
        merged._properties = self.properties.merge_with_parent(parent.properties)
        return merged
    
    def dispatch_globals(self) -> ProfileNode:
        dispatched = ProfileNode(self.name)
        for property_name, property in self.properties.items():
            if (property_name == CompilersOverrideNode.NAME or 
                property_name == LinkersOverrideNode.NAME or 
                property_name == ProjectsOverrideNode.NAME):
                property = property.dispatch_globals()
            dispatched.add_property(property)
        return dispatched

class ProfileSpecificOverrideNode(PropertyDict):
    pass

class ProfilesOverrideNode(PropertyDict):
    pass
