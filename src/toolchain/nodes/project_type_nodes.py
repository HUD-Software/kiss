from __future__ import annotations
from toolchain.nodes.compiler_nodes import CompilersOverrideNode
from toolchain.nodes.linker_nodes import LinkersOverrideNode
from .property import Property, PropertyDict, PropertyBool, PropertyStr

from typing import TypeVar, Type
T = TypeVar("T", bound=Property)

class ProjectTypeNode(Property):
    """Represents a project type definition in projects.yaml.

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
    
    @property
    def compilers(self) -> CompilersOverrideNode:
        self.get_property_as("compilers", CompilersOverrideNode)
    
    @property
    def linkers(self) -> LinkersOverrideNode:
        self.get_property_as("linkers", LinkersOverrideNode)


    def get_property(self, name: str) -> Property | None:
        return self.properties.get_property(name)
    
    def add_property(self, property):
        self.properties.add_property(property)
    
    def get_property_as(self, name: str, prop_type: Type[T]) -> T | None:
        return self.properties.get_property_as(name, prop_type)
    
    # def clone(self) -> ProjectTypeNode:
    #     cloned  = ProjectTypeNode(self.name)
    #     cloned.properties = self._properties.clone()
    #     return cloned
    
    def resolve_extends(self, parent):
        assert type(parent) is type(self), "Type mismatch"
        merged = ProjectTypeNode(self.name)
        merged._properties = self.properties.resolve_extends(parent.properties)
        return merged
    
    def dispatch_globals(self) -> ProjectTypeNode:
        dispatched = ProjectTypeNode(self.name)
        for property in self.properties.values():
            dispatched.add_property(property.dispatch_globals())
        return dispatched
    
class ProjectSpecificOverrideNode(Property):
    """Represents a per-project-type override inside a 'projects:' node.
      
    projects:
        dyn: # ProjectSpecificOverrideNode
            compilers:
            enable-features: []
            defines: []
            msvc-compiler:
                enable-features: []
            linkers:
            enable-features: []
        lib: # ProjectSpecificOverrideNode
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

    @property
    def properties(self) -> PropertyDict:
        return self._properties
    
    def get_property(self, name: str) -> Property | None:
        return self.properties.get_property(name)
    
    def add_property(self, property):
        self.properties.add_property(property)

    # def clone(self) -> ProjectSpecificOverrideNode:
    #     cloned  = ProjectSpecificOverrideNode(self.name)
    #     cloned._properties = self._properties.clone()
    #     return cloned
    
    def resolve_extends(self, parent):
        assert type(parent) is type(self), "Type mismatch"
        merged = ProjectSpecificOverrideNode(self.name)
        merged._properties = self.properties.resolve_extends(parent.properties)
        return merged


class ProjectsOverrideNode(Property):
    """Represents the 'projects:' block.
    Contains global enable-features + per-project-type overrides 'ProjectSpecificOverrideNode' nodes.

    projects: # ProjectsOverrideNode
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
    NAME = "projects"
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

    # def clone(self) -> ProjectsOverrideNode:
    #     cloned  = ProjectsOverrideNode(self.name)
    #     cloned._properties = self._properties.clone()
    #     return cloned
    
    def resolve_extends(self, parent):
        assert type(parent) is type(self), "Type mismatch"
        merged = ProjectsOverrideNode(self.name)
        merged._properties = self.properties.resolve_extends(parent.properties)
        return merged
