

from .node import PropertyDict, PropertyBool

class LinkerFeatureArgsNode(PropertyDict):
    """Represents the 'args' block inside a linker feature with arguments.

    args:
      min: 1
      max: ~
      separator: ","
      pattern: "*.lib"
    """
    pass


class LinkerFeatureNode(PropertyDict):
    """Represents a single linker feature entry.

    - name: LINK
      description: Link with library
      args: ...
      flags: [/link {args}]
    """
    pass

class LinkerFeatureRuleNode(PropertyDict):
    """Represents a feature rule (only-one or incompatible)."""
    pass


class LinkerNode(PropertyDict):
    """Represents a linker entry (abstract or concrete).
    e.g. msvc-linker, link, lld-link
    """

    @property
    def is_abstract(self) -> bool :
        prop = self.get_property_as("is_abstract", PropertyBool)
        return prop.value if prop else False

    # def merge_with_parent(self, parent: 'LinkerNode') -> 'LinkerNode':
    #     result = LinkerNode(self.name)
    #     for name, prop in self.properties.items():
    #         parent_prop = parent.get_property(name)
    #         # Add props if not in parent
    #         if not parent_prop:
    #             result.add_property(prop.clone())
    #         else:
    #             result.add_property(prop.merge_with_parent(parent_prop))
    #     return result