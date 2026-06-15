from toolchain.nodes.compiler_nodes import CompilersOverrideNode
from toolchain.nodes.linker_nodes import LinkersOverrideNode

from .property import PropertyDict, PropertyBool, PropertyStr

class ProjectTypeNode(PropertyDict):
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

    Compiler and linker overrides support the standard append/remove operations
    (e.g. 'append-defines', 'remove-enable-features') for fine-grained inheritance control.
    """
    
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
    
class ProjectSpecificOverrideNode(PropertyDict):
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
    pass

class ProjectsOverrideNode(PropertyDict):
    """Represents the 'projects:' block.
    Contains global enable-features + per-project-type overrides 'LinkerSpecificOverrideNode' nodes.

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
    pass
