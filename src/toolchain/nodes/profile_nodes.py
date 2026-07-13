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
        self.compilers : CompilersOverrideNode = None
        self.linkers : LinkersOverrideNode = None
        self.project_types : ProjectTypesOverrideNode = None
    
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

    def merge_with(self, parent: ProfileNode):
        """Merge list without applying modifier or dispatching top to bottom hierarchy """
        assert type(parent) is type(self), "Type mismatch"
        result = ProfileNode(self.name)
        result._properties = self.properties.merge_with(parent.properties)
        explicit_list_names = self.properties.explicit_list_names()
        result.linkers = self.linkers.merge_with(parent.linkers, explicit_list_names) if self.linkers else None
        result.compilers = self.compilers.merge_with(parent.compilers, explicit_list_names) if self.compilers else None
        result.project_types = self.project_types.merge_with(parent.project_types, explicit_list_names) if self.project_types else None
        return result
    
    def apply_modifiers(self) -> ProfileNode:
        """Apply list modifier"""
        result  = ProfileNode(self.name)
        result._properties = self.properties.apply_modifiers()
        result.linkers = self.linkers.apply_modifiers() if self.linkers else None
        result.compilers = self.compilers.apply_modifiers() if self.compilers else None
        result.project_types = self.project_types.apply_modifiers() if self.project_types else None
        return result
    
    def dispatch(self) -> ProfileNode:
        """ 
        Dispatch properties from top to bottom hierarchy
        """
        result = ProfileNode(self.name)
        result._properties = copy.deepcopy(self.properties)
        result.linkers = self.linkers.dispatch(result._properties) if self.linkers else None
        result.compilers = self.compilers.dispatch(result._properties) if self.compilers else None
        result.project_types = self.project_types.dispatch(result._properties) if self.project_types else None
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
      self.compilers : CompilersOverrideNode = None
      self.linkers : LinkersOverrideNode = None
      self.project_types : ProjectTypesOverrideNode = None

    @property
    def properties(self) -> PropertyDict:
        return self._properties
    
    def get_property(self, name: str) -> Property | None:
        return self.properties.get_property(name)
    
    def add_property(self, property):
        self.properties.add_property(property)

    def apply_modifiers(self) -> ProfileSpecificOverrideNode:
        result = ProfileSpecificOverrideNode(self.name)
        result._properties = self.properties.apply_modifiers()
        result.linkers = self.linkers.apply_modifiers() if self.linkers else None
        result.compilers = self.compilers.apply_modifiers() if self.compilers else None
        result.project_types = self.project_types.apply_modifiers() if self.project_types else None
        return result
    
    def merge_with(self, other: ProfileSpecificOverrideNode, parent_list_name_to_ignore: set[str] = None) -> ProfileSpecificOverrideNode:
        assert self.name == other.name, "Name mismatch"
        result = ProfileSpecificOverrideNode(self.name)
        result._properties = self.properties.merge_with(other.properties, parent_list_name_to_ignore)
        result.compilers = self.compilers.merge_with(other.compilers, parent_list_name_to_ignore) if self.compilers else None
        result.linkers = self.linkers.merge_with(other.linkers, parent_list_name_to_ignore) if self.linkers else None
        result.project_types = self.project_types.merge_with(other.project_types, parent_list_name_to_ignore) if self.project_types else None
        return result
    
    def dispatch(self, properties : PropertyDict) -> ProfileSpecificOverrideNode:
        result = ProfileSpecificOverrideNode(self.name)
        result._properties = self.properties.dispatch(properties)
        result.linkers = self.linkers.dispatch(result._properties) if self.linkers else None
        result.compilers = self.compilers.dispatch(result._properties) if self.compilers else None
        result.project_types = self.project_types.dispatch(result._properties) if self.project_types else None
        return result
    
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
      self._profiles = dict[str, ProfileSpecificOverrideNode]()

    @property
    def properties(self) -> PropertyDict:
        return self._properties

    def get_property(self, name: str) -> Property | None:
        return self.properties.get_property(name)
    
    def add_property(self, property):
        self.properties.add_property(property)

    def add_profile(self, profile:ProfileSpecificOverrideNode):
        self._profiles[profile.name] = profile

    def merge_with(self, other: ProfilesOverrideNode, parent_list_name_to_ignore: set[str] = None) -> ProfilesOverrideNode:
        assert type(other) is type(self), "Type mismatch"
        result = ProfilesOverrideNode(self.name)
        result._properties = self.properties.merge_with(other.properties, parent_list_name_to_ignore)
        
        if parent_list_name_to_ignore:
            parent_list_name_to_ignore.update(self.properties.explicit_list_names())
        else :
            parent_list_name_to_ignore = self.properties.explicit_list_names()

        for profile in self._profiles.values():
            other_profile = other._profiles.get(profile.name)
            if other_profile: # project type in both
                result.add_project_type(profile.merge_with(other_profile, parent_list_name_to_ignore))
            else: # project type only in self
                result.add_project_type(copy.deepcopy(profile))
        
        for profile_name, other_profile in other._profiles.items():
            if profile_name not in self._profiles: # Only in parents
                self_linker = ProfilesOverrideNode(other_profile.name)
                result.add_project_type(self_linker.merge_with(other_profile, parent_list_name_to_ignore))

        return result
    
    def apply_modifiers(self) -> ProfilesOverrideNode:
        result = ProfilesOverrideNode(self.name)
        result._properties = self.properties.apply_modifiers()
        for project_type in self._profiles.values():
            result.add_project_type(project_type.apply_modifiers())
        return result

    def dispatch(self, properties: PropertyDict) -> ProfilesOverrideNode:
        result = ProfilesOverrideNode(self.name)
        result._properties = self.properties.dispatch(properties)
        for project_type in self._profiles.values():
            result.add_project_type(project_type.dispatch(result.properties))
        return result
    