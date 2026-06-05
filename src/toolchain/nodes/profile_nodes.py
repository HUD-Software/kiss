from .node import PropertyDict, PropertyBool

class ProfileCompilerOverrideNode(PropertyDict):
    """Represents a compiler-specific override block inside a profile.

    msvc-compiler:
      enable-features: [OPT_LEVEL_0, WINDOWS_DLL_RUNTIME_DEBUG]
      defines: []
    """
    pass

class ProfileLinkerOverrideNode(PropertyDict):
    """Represents a linker-specific override block inside a profile.

    msvc-linker:
      enable-features: [REMOVE_DEAD_CODE]
    """
    pass


class ProfileCompilersNode(PropertyDict):
    """Represents the 'compilers:' block inside a profile.

    compilers:
      enable-features: []
      defines: [KISS_DEBUG]
      msvc-compiler:
        enable-features: [OPT_LEVEL_0]
    """
    pass


class ProfileLinkerNode(PropertyDict):
    """Represents the 'linkers:' block inside a profile.

    linkers:
      enable-features: [ENABLE_INCREMENTAL_LINK]
      msvc-linker:
        enable-features: []
    """
    pass


class ProfileProjectTypeNode(PropertyDict):
    """Represents a project-type override block inside a profile.

    dyn:
      compilers:
        enable-features: [DYNAMIC_LIBRARY_DEBUG]
      linkers:
        enable-features: []
    """
    pass

class ProfileNode(PropertyDict):
    """Represents a profile entry.

    - name: debug
      description: ...
      extends: ...
      compilers: ...
      linkers: ...
      projects: ...
    """
    @property
    def is_abstract(self) -> bool :
        prop = self.get_property_as("is_abstract", PropertyBool)
        return prop.value if prop else False

    # def merge_with_parent(self, parent: 'ProfileNode') -> 'ProfileNode':
    #     result = ProfileNode(self.name)
    #     for name, prop in self.properties.items():
    #         parent_prop = parent.get_property(name)
    #         # Add props if not in parent
    #         if not parent_prop:
    #             result.add_property(prop.clone())
    #         else:
    #             result.add_property(prop.merge_with_parent(parent_prop))
    #     return result