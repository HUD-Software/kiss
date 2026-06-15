from .property import PropertyDict, PropertyBool

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


class ProfileSpecificOverrideNode(PropertyDict):
    pass

class ProfilesOverrideNode(PropertyDict):
    pass
