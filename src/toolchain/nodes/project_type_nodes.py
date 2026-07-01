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
        self._linkers: LinkersOverrideNode = None
        self._compilers : CompilersOverrideNode = None
    
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
    
    def get_property(self, name: str) -> Property | None:
        return self.properties.get_property(name)
    
    def add_property(self, property):
        self.properties.add_property(property)
    
    def get_property_as(self, name: str, prop_type: Type[T]) -> T | None:
        return self.properties.get_property_as(name, prop_type)
    
    def apply_modifiers(self) -> ProjectTypeNode:
        result = ProjectTypeNode(self.name)
        result._properties = self.properties.apply_modifiers()
        result._linkers = self.linkers.apply_modifiers() if self.linkers else None
        result.compilers = self.compilers.apply_modifiers() if self.compilers else None
        return result
    

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
