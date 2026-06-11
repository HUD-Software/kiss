
from toolchain.nodes.feature_node import FeatureNode, FeatureRuleNode
from toolchain.nodes.property import PropertyBool, PropertyDict

class LinkerNode(PropertyDict):
    """Represents a linker entry (abstract or concrete).
    e.g. msvc-linker, link, lld-link
    """

    @property
    def is_abstract(self) -> bool :
        prop = self.get_property_as("is_abstract", PropertyBool)
        return prop.value if prop else False