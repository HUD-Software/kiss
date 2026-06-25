from __future__ import annotations
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

    # def clone(self) -> ProfileNode:
    #     cloned  = ProfileNode(self.name)
    #     cloned.properties = self._properties.clone()
    #     return cloned
    
    def merge_with_parent(self, parent):
        assert type(parent) is type(self), "Type mismatch"
        merged = ProfileNode(self.name)
        merged._properties = self.properties.merge_with_parent(parent.properties)
        return merged
    
    def dispatch_globals(self) -> ProfileNode:
        dispatched = ProfileNode(self.name)
        for property in self.properties.values():
            dispatched.add_property(property.dispatch_globals())
        return dispatched

class ProfileSpecificOverrideNode(Property):
    """Represents a per-profile override inside a 'profiles:' node.
      
    profiles:
        debug: # ProfileSpecificOverrideNode
            description:
            compilers: 
            linkers:
            project-types:
        release: # ProfileSpecificOverrideNode
            description:
            compilers: 
            linkers:
            project-types:
    """
    def __init__(self, name : str):
      super().__init__(name)
      self._properties = PropertyDict()

    @property
    def properties(self) -> PropertyDict:
        return self._properties
    
    def get_property(self, name: str) -> Property | None:
        return self.properties.get_property(name)
    
    def add_property(self, property):
        self.properties.add_property(property)

    # def clone(self) -> ProfileSpecificOverrideNode:
    #     cloned  = ProfileSpecificOverrideNode(self.name)
    #     cloned._properties = self._properties.clone()
    #     return cloned
    
    def merge_with_parent(self, parent):
        assert type(parent) is type(self), "Type mismatch"
        merged = ProfileSpecificOverrideNode(self.name)
        merged._properties = self.properties.merge_with_parent(parent.properties)
        return merged

class ProfilesOverrideNode(Property):
    """Represents the 'profiles:' block.
    Contains global enable-features + per-profile overrides 'ProfileSpecificOverrideNode' nodes.

    profiles: # ProfilesOverrideNode
        debug:
            description:
            compilers: 
            linkers:
            project-types:
        release:
            description:
            compilers: 
            linkers:
            project-types:
    """
    NAME = "profiles"
    def __init__(self, name : str= NAME):
      super().__init__(name)
      self._properties = PropertyDict()

    @property
    def properties(self) -> PropertyDict:
        return self._properties
    
    def get_property(self, name: str) -> Property | None:
        return self.properties.get_property(name)
    
    def add_property(self, property):
        self.properties.add_property(property)

    # def clone(self) -> ProfilesOverrideNode:
    #     cloned  = ProfilesOverrideNode(self.name)
    #     cloned._properties = self._properties.clone()
    #     return cloned
    
    def merge_with_parent(self, parent):
        assert type(parent) is type(self), "Type mismatch"
        merged = ProfilesOverrideNode(self.name)
        merged._properties = self.properties.merge_with_parent(parent.properties)
        return merged