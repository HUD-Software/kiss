from __future__ import annotations
from toolchain.nodes.property import Property, PropertyDict

class FeatureArgsNode(Property):
    """Represents the 'args' block inside a feature with arguments.
    args:
      min: 1
      max: ~
      separator: ","
      pattern: "*.lib"
    """
    NAME = "args"

    def __init__(self, name:str =NAME):
        super().__init__(name)
        self._properties = PropertyDict()
    
    @property
    def properties(self) -> PropertyDict:
        return self._properties

    def add_property(self, property: Property):
        self._properties.add_property(property)

from typing import TypeVar, Type
T = TypeVar("T", bound=Property)

class FeatureNode(Property):
    """Represents a single compiler feature entry.
    e.g. - name: OPT_LEVEL_0
           flags: [/Od]
           enable-features: [DEBUG_INFO]
           args: ...
    """
    def __init__(self, name:str):
        super().__init__(name)
        self._properties = PropertyDict()
    
    @property
    def properties(self) -> PropertyDict:
        return self._properties
    
    def add_property(self, property: Property):
        self._properties.add_property(property)

    def get_property(self, name: str) -> Property | None:
        return self._properties.get_property(name)
    
    def get_property_as(self, name: str, prop_type: Type[T]) -> T | None:
        return self._properties.get_property_as(name, prop_type)
    
    def merge_with(self, parent: FeatureNode):
        merged = FeatureNode(self.name)
        merged._properties = self._properties.merge_with(parent._properties)
        return merged
    
    def apply_modifiers(self) -> FeatureNode:
        result = FeatureNode(self.name)
        result._properties = self._properties.apply_modifiers()
        return result
    
class FeatureNodeList(Property):
    """Represents the 'features:' block."""
    NAME = "features"

    def __init__(self, name:str=NAME):
        super().__init__(name)
        self._features = PropertyDict()
    
    @property
    def properties(self) -> PropertyDict:
        return self._features
    
    @property
    def features(self) -> PropertyDict:
        return self.properties
    
    def add_feature(self, feature : FeatureNode):
        self._features.add_property(feature)
    
    def merge_with(self, parent: FeatureNodeList):
        merged = FeatureNodeList(self.name)
        merged._features = self._features.merge_with(parent._features)
        return merged
    
    def apply_modifiers(self) -> FeatureNodeList:
        result = FeatureNodeList(self.name)
        for feature in self.features.values():
            result.add_feature(feature.apply_modifiers())
        return result

    def dispatch(self) -> FeatureNodeList:
        result = FeatureNodeList(self.name)
        for feature in self.features.values():
            result.add_feature(feature.dispatch())
        return result

class FeatureRuleNode(Property):
    """Represents a feature rule (only-one or incompatible)."""
    
    def __init__(self, name:str):
        super().__init__(name)
        self._properties = PropertyDict()
    
    @property
    def properties(self) -> PropertyDict:
        return self._properties
    
    def add_property(self, property: Property):
        self._properties.add_property(property)

    def get_property(self, name: str) -> Property | None:
        return self._properties.get(name)
    
    def merge_with(self, parent: FeatureNodeList):
        assert False, """
        Feature rules are not mergeable.
        We don't allow modification of existing feature-rules"""

    def dispatch(self) -> FeatureNodeList:
        assert False, """Feature rules are not dispatchable."""

class FeatureRuleNodeList(Property):
    """Represents the 'feature-rules:' block."""
    NAME = "feature-rules"

    def __init__(self, name:str=NAME):
        super().__init__(name)
        self._feature_rules = PropertyDict()

    @property
    def properties(self) -> PropertyDict:
        return self._feature_rules

    @property
    def feature_rules(self) -> PropertyDict:
        return self.properties
    
    def add_feature_rule(self, feature : FeatureRuleNode):
        self._feature_rules.add_property(feature)
