from .property import PropertyDict, PropertyBool, PropertyNodeList, PropertyStr

class ProjectTypeCompilerNode(PropertyDict):
    """Represents the 'compilers:' block inside a project type.

    compilers:
      enable-features: []
      defines: [KISS_BIN]
      ...
    """
    pass

class ProjectTypeCompilerOverrideNode(PropertyDict):
    """Represents the linker override block inside 'compilers:' block inside a project type.

    compilers:
      enable-features: []
      defines: [KISS_BIN]
      ...
    """
    pass


class ProjectTypeLinkerNode(PropertyDict):
    """Represents the 'linkers:' block inside a project type.

    linkers:
      enable-features: []
      ...
    """
    pass

class ProjectTypeLinkerOverrideNode(PropertyDict):
    """Represents the 'linkers:' block inside a project type.

    compilers:
      enable-features: []
      defines: [KISS_BIN]
      ...
    """
    pass

class ProjectTypeNode(PropertyDict):
    """Represents a project type entry (bin, lib, dyn or custom).

    - name: my_bin
      description: Executable binary
      extends: ...
      compilers: ...
      linkers: ...
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
    def compilers(self) -> list[ProjectTypeCompilerNode]:
        prop = self.get_property_as("compilers", PropertyNodeList)
        if prop.nodes:
            return [c for c in prop.nodes]
        return []
    
    # def merge_with_parent(self, parent: 'ProjectTypeNode') -> 'ProjectTypeNode':
    #     result = ProjectTypeNode(self.name)
    #     for name, prop in self.properties.items():
    #         parent_prop = parent.get_property(name)
    #         # Add props if not in parent
    #         if not parent_prop:
    #             result.add_property(prop.clone())
    #         else:
    #             result.add_property(prop.merge_with_parent(parent_prop))
    #     return result