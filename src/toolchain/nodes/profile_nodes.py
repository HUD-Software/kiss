from __future__ import annotations
import copy
from toolchain.nodes.compiler_nodes import CompilersOverrideNode
from toolchain.nodes.linker_nodes import LinkersOverrideNode
from toolchain.nodes.project_type_nodes import ProjectTypesOverrideNode

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
      project-types: ...
    """
    def __init__(self, name : str):
        super().__init__(name)
        self._properties = PropertyDict()
        self._compilers : CompilersOverrideNode = None
        self._linkers : LinkersOverrideNode = None
        self._project_types : ProjectTypesOverrideNode = None
    
    @property
    def properties(self) -> PropertyDict:
        return self._properties
    @property
    def is_abstract(self) -> bool :
        prop = self.get_property_as("is_abstract", PropertyBool)
        return prop.value if prop else False

    @property
    def linkers(self) -> LinkersOverrideNode:
        return self._linkers
    
    @linkers.setter
    def linkers(self, value):
        self._linkers = value

    @property
    def compilers(self) -> CompilersOverrideNode:
        return self._compilers
    
    @compilers.setter
    def compilers(self, value):
        self._compilers = value

    @property
    def project_types(self) -> ProjectTypesOverrideNode:
        return self._project_types
    
    @project_types.setter
    def project_types(self, value):
        self._project_types = value

    def get_property(self, name: str) -> Property | None:
        return self.properties.get_property(name)
    
    def add_property(self, property):
        self.properties.add_property(property)

    def get_property_as(self, name: str, prop_type: Type[T]) -> T | None:
        self.properties.get_property_as(name, prop_type)

    def merge_with(self, parent: ProfileNode):
        """Merge list without applying modifier or dispatching top to bottom hierarchy """
        assert type(parent) is type(self), "Type mismatch"
        result = ProfileNode(self.name)
        result._properties = self.properties.merge_with(parent.properties)
        list_property_to_ignore = result._properties .explicit_list_name() 

        result.linkers = self.linkers.merge_with(parent.linkers, list_property_to_ignore)
        result.compilers = self.compilers.merge_with(parent.compilers, list_property_to_ignore)
        result.project_types = self.project_types.merge_with(parent.project_types, list_property_to_ignore)
        return result
    
    def apply_modifiers(self) -> ProfileNode:
        """Apply list modifier"""
        result  = ProfileNode(self.name)
        result._properties = self.properties.apply_modifiers()
        result.linkers = self.linkers.apply_modifiers()
        result.compilers = self.compilers.apply_modifiers()
        result.project_types = self.project_types.apply_modifiers()
        return result
    
    def dispatch(self) -> ProfileNode:
        """ 
        Dispatch properties from top to bottom hierarchy
        """
        result = ProfileNode(self.name)
        result._properties = copy.deepcopy(self.properties)
        result.linkers = self.linkers.dispatch(result._properties)
        result.compilers = self.compilers.dispatch(result._properties)
        result.project_types = self.project_types.dispatch(result._properties)
        return result
    
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