from __future__ import annotations
import copy
from toolchain.nodes.property import Property, PropertyDict, PropertyStr, PropertyStrList

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
        if not parent:
            return copy.deepcopy(self)
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
        if not parent:
            return copy.deepcopy(self)
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
    
    def get_property_as(self, name: str, prop_type: Type[T]) -> T | None:
        return self._properties.get_property_as(name, prop_type)
    
    def merge_with(self, parent: FeatureNodeList):
        assert False, """
        Feature rules are not is_mergeable.
        We don't allow modification of existing feature-rules"""

    def dispatch(self) -> FeatureNodeList:
        assert False, """Feature rules are not is_dispatchable."""

class FeatureRuleNodeOnlyOne(FeatureRuleNode):
    NAME = "only-one"
    def __init__(self, name: str, features: PropertyStrList):
        super().__init__(name)
        self.add_property(features)

    def features(self) -> list[str]:
        return self.get_property_as("features", PropertyStrList).values


class FeatureRuleNodeIncompatible(FeatureRuleNode):
    NAME = "incompatible"
    
    def __init__(self, name: str, feature: PropertyStr, incompatible_with: PropertyStrList):
        super().__init__(name)
        self.add_property(feature)
        self.add_property(incompatible_with)

    def feature(self) -> str:
        return self.get_property_as("feature", PropertyStr).value

    def incompatible_features(self) -> list[str]:
        return self.get_property_as("with", PropertyStrList).values
    
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

    def get_all_rules_of_type(self, rule_type: Type[T]) -> list[T]:
        """Return all rules matching the given FeatureRuleNode subclass,
        preserving declaration order."""
        return [r for r in self._feature_rules.values() if isinstance(r, rule_type)]
    
    def merge_with(self, parent: FeatureRuleNodeList):
        if not parent:
            return copy.deepcopy(self)
        result = FeatureRuleNodeList(self.name)
        # Keep self features
        for feature_rule in self.feature_rules.values():
            result.add_feature_rule(copy.deepcopy(feature_rule))

        # Add parent feature 
        for feature_rule in parent.feature_rules.values():
            if feature_rule.name not in result.feature_rules:
                result.add_feature_rule(copy.deepcopy(feature_rule))
            else:
                raise ValueError(f"Feature rule '{feature_rule.name}' already exists")
        return result

    def apply_modifiers(self) -> FeatureRuleNodeList:
        result = FeatureRuleNodeList(self.name)
        for feature in self.feature_rules.values():
            result.add_feature_rule(copy.deepcopy(feature))
        return result

    def dispatch(self) -> FeatureRuleNodeList:
        result = FeatureRuleNodeList(self.name)
        for feature in self.feature_rules.values():
            result.add_feature_rule(copy.deepcopy(feature))
        return result