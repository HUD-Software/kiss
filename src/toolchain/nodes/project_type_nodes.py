from __future__ import annotations
import copy
from toolchain.nodes.compiler_nodes import CompilersOverrideNode
from toolchain.nodes.linker_nodes import LinkersOverrideNode
from .property import Property, PropertyDict, PropertyBool, PropertyStr

from typing import TypeVar, Type
T = TypeVar("T", bound=Property)

class ProjectTypeNode(Property):
    """Represents a project type definition in project-types.yaml.

    A project type describes the nature of a build output (e.g. 'bin', 'lib', 'dyn', 'test')
    and can be abstract or concrete. Concrete types can extend another via 'extends',
    inheriting and overriding its compiler/linker configuration.

    Key attributes:
    - is_abstract: if True, this node is a base template and cannot be used directly
    - icon: emoji or symbol used for display purposes (e.g. 🚀 for bin, 📦 for lib)
    - description: human-readable label for the project type
    - compilers: compiler-side overrides applied when building this project type,
                 including features to enable and preprocessor defines — can be
                 specified globally or per compiler (e.g. under 'msvc-compiler')
    - linkers: linker-side overrides applied when building this project type,
               including features to enable — can be specified globally or per linker

    Compiler and linker overrides support the standard add/remove-enable/disable operations
    (e.g. 'add-defines', 'remove-features') for fine-grained inheritance control.
    """
    def __init__(self, name : str):
        super().__init__(name)
        self._properties = PropertyDict()
        self.linkers: LinkersOverrideNode = None
        self.compilers : CompilersOverrideNode = None
    
    @property
    def properties(self) -> PropertyDict:
        return self._properties
    
    @property
    def is_abstract(self) -> bool :
        prop = self.get_property_as("is_abstract", PropertyBool)
        return prop.value if prop else False
    
    @property
    def icon(self) -> str:
        prop = self.get_property_as("icon", PropertyStr)
        return prop.value if prop else ""

    @property
    def description(self) -> str:
        prop = self.get_property_as("description", PropertyStr)
        return prop.value if prop else ""
    
    def get_property(self, name: str) -> Property | None:
        return self.properties.get_property(name)
    
    def add_property(self, property):
        self.properties.add_property(property)
    
    def get_property_as(self, name: str, prop_type: Type[T]) -> T | None:
        return self.properties.get_property_as(name, prop_type)
    
    def merge_with(self, parent: ProjectTypeNode):
        if not parent:
            return copy.deepcopy(self)
        """Merge list without applying modifier or dispatching top to bottom hierarchy """
        assert type(parent) is type(self), "Type mismatch"
        result = ProjectTypeNode(self.name)
        result._properties = self.properties.merge_with(parent.properties)
        explicit_list_names = self.properties.explicit_list_names()
        result.linkers = self.linkers.merge_with(parent.linkers, explicit_list_names) if self.linkers else None
        result.compilers = self.compilers.merge_with(parent.compilers, explicit_list_names) if self.compilers else None
        return result
    
    def apply_modifiers(self) -> ProjectTypeNode:
        """Apply list modifier"""
        result  = ProjectTypeNode(self.name)
        result._properties = self.properties.apply_modifiers()
        result.linkers = self.linkers.apply_modifiers() if self.linkers else None
        result.compilers = self.compilers.apply_modifiers() if self.compilers else None
        return result
    
    def dispatch(self) -> ProjectTypeNode:
        """ 
        Dispatch properties from top to bottom hierarchy
        """
        result = ProjectTypeNode(self.name)
        result._properties = copy.deepcopy(self.properties)
        result.linkers = self.linkers.dispatch(result._properties) if self.linkers else None
        result.compilers = self.compilers.dispatch(result._properties) if self.compilers else None
        return result

class ProjectTypeSpecificOverrideNode(Property):
    """Represents a per-project-type override inside a 'project-types:' node.
      
    project-types:
        dyn: # ProjectTypeSpecificOverrideNode
            compilers:
            enable-features: []
            defines: []
            msvc-compiler:
                enable-features: []
            linkers:
                enable-features: []
        lib: # ProjectTypeSpecificOverrideNode
            compilers:
            enable-features: []
            defines: []
            msvc-compiler:
                enable-features: []
            linkers:
                enable-features: []
    """
    def __init__(self, name : str):
      super().__init__(name)
      self._properties = PropertyDict()
      self.compilers : CompilersOverrideNode = None
      self.linkers : LinkersOverrideNode = None

    @property
    def properties(self) -> PropertyDict:
        return self._properties

    def get_property(self, name: str) -> Property | None:
        return self.properties.get_property(name)
    
    def add_property(self, property):
        self.properties.add_property(property)

    def apply_modifiers(self) -> ProjectTypeSpecificOverrideNode:
        result = ProjectTypeSpecificOverrideNode(self.name)
        result._properties = self.properties.apply_modifiers()
        result.linkers = self.linkers.apply_modifiers() if self.linkers else None
        result.compilers = self.compilers.apply_modifiers() if self.compilers else None
        return result
    
    def merge_with(self, other: ProjectTypeSpecificOverrideNode, parent_list_name_to_ignore: set[str] = None) -> ProjectTypeSpecificOverrideNode:
        if not other:
            return copy.deepcopy(self)
        assert self.name == other.name, "Name mismatch"
        result = ProjectTypeSpecificOverrideNode(self.name)
        result._properties = self.properties.merge_with(other.properties, parent_list_name_to_ignore)
        result.compilers = self.compilers.merge_with(other.compilers, parent_list_name_to_ignore) if self.compilers else None
        result.linkers = self.linkers.merge_with(other.linkers, parent_list_name_to_ignore) if self.linkers else None
        return result
    
    def dispatch(self, properties : PropertyDict) -> ProjectTypeSpecificOverrideNode:
        result = ProjectTypeSpecificOverrideNode(self.name)
        result._properties = self.properties.dispatch(properties)
        result.linkers = self.linkers.dispatch(result._properties) if self.linkers else None
        result.compilers = self.compilers.dispatch(result._properties) if self.compilers else None
        return result

class ProjectTypesOverrideNode(Property):
    """Represents the 'project-types:' block.
    Contains global enable-features + per-project-type overrides 'ProjectTypeSpecificOverrideNode' nodes.

    project-types: # ProjectTypesOverrideNode
        dyn:
            compilers:
            enable-features: []
            defines: []
            msvc-compiler:
                enable-features: []
            linkers:
            enable-features: []
        lib:
            compilers:
            enable-features: []
            defines: []
            msvc-compiler:
                enable-features: []
            linkers:
            enable-features: []
    """
    NAME = "project-types"
    def __init__(self, name : str= NAME):
      super().__init__(name)
      self._properties = PropertyDict()
      self._project_types = dict[str, ProjectTypeSpecificOverrideNode]()

    @property
    def properties(self) -> PropertyDict:
        return self._properties
    
    def get_property(self, name: str) -> Property | None:
        return self.properties.get_property(name)
    
    def add_property(self, property):
        self.properties.add_property(property)

    def add_project_type(self, project_type:ProjectTypeSpecificOverrideNode):
        self._project_types[project_type.name] = project_type

    def merge_with(self, other: ProjectTypesOverrideNode, parent_list_name_to_ignore: set[str] = None) -> ProjectTypesOverrideNode:
        if not other:
            return copy.deepcopy(self)
        assert type(other) is type(self), "Type mismatch"
        result = ProjectTypesOverrideNode(self.name)
        result._properties = self.properties.merge_with(other.properties, parent_list_name_to_ignore)
        
        if parent_list_name_to_ignore:
            parent_list_name_to_ignore.update(self.properties.explicit_list_names())
        else :
            parent_list_name_to_ignore = self.properties.explicit_list_names()

        for project_type in self._project_types.values():
            other_project_type = other._project_types.get(project_type.name)
            if other_project_type: # project type in both
                result.add_project_type(project_type.merge_with(other_project_type, parent_list_name_to_ignore))
            else: # project type only in self
                result.add_project_type(copy.deepcopy(project_type))
        
        for project_type_name, other_project_type in other._project_types.items():
            if project_type_name not in self._project_types: # Only in parents
                self_linker = ProjectTypeSpecificOverrideNode(other_project_type.name)
                result.add_project_type(self_linker.merge_with(other_project_type, parent_list_name_to_ignore))

        return result
    
    def apply_modifiers(self) -> ProjectTypesOverrideNode:
        result = ProjectTypesOverrideNode(self.name)
        result._properties = self.properties.apply_modifiers()
        for project_type in self._project_types.values():
            result.add_project_type(project_type.apply_modifiers())
        return result

    def dispatch(self, properties: PropertyDict) -> ProjectTypesOverrideNode:
        result = ProjectTypesOverrideNode(self.name)
        result._properties = self.properties.dispatch(properties)
        for project_type in self._project_types.values():
            result.add_project_type(project_type.dispatch(result.properties))
        return result