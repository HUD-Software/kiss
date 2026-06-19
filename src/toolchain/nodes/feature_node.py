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

    def clone(self) -> FeatureArgsNode:
        cloned  = FeatureArgsNode(self.name)
        cloned._properties = self._properties.clone()
        return cloned
    
    def merge_with_parent(self, parent) -> FeatureArgsNode:
        merged = FeatureArgsNode(self.name)
        merged._properties = self._properties.merge_with_parent(parent._properties)
        return merged


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
        return self._properties.get(name)

    def dispatch_globals(self) -> FeatureNode:
        return self.clone()
    
    def clone(self) -> FeatureNode:
        cloned  = FeatureNode(self.name)
        cloned._properties = self._properties.clone()
        return cloned
    
    def merge_with_parent(self, parent) -> FeatureNode:
        merged = FeatureNode(self.name)
        merged._properties = self._properties.merge_with_parent(parent._properties)
        return merged

class FeatureNodeList(Property):
    """Represents the 'features:' block."""
    NAME = "features"

    def __init__(self, name:str=NAME):
        super().__init__(name)
        self._features = PropertyDict()
    
    @property
    def features(self) -> PropertyDict:
        return self._features
    
    def add_feature(self, feature : FeatureNode):
        self._features.add_property(feature)

    def clone(self) -> FeatureNodeList:
        cloned  = FeatureNodeList(self.name)
        cloned._features = self._features.clone()
        return cloned
    
    def merge_with_parent(self, parent):
        merged = FeatureNodeList(self.name)
        merged._features = self._features.merge_with_parent(parent._features)
        return merged
    
    def dispatch_globals(self) -> FeatureNodeList:
        dispatched = FeatureNodeList()
        for feature in self._features.values():
            dispatched.add_feature(feature.dispatch_globals())
        return dispatched


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
    
    def dispatch_globals(self) -> FeatureRuleNode:
        return self.clone()
    
    def clone(self) -> FeatureRuleNode:
        cloned  = FeatureRuleNode(self.name)
        cloned._properties = self._properties.clone()
        return cloned
    
    def merge_with_parent(self, parent) -> FeatureRuleNode:
        merged = FeatureRuleNode(self.name)
        merged._properties = self._properties.merge_with_parent(parent._properties)
        return merged
    

class FeatureRuleNodeList(Property):
    """Represents the 'feature-rules:' block."""
    NAME = "feature-rules"

    def __init__(self, name:str=NAME):
        super().__init__(name)
        self._feature_rules = PropertyDict()

    @property
    def feature_rules(self) -> PropertyDict:
        return self._feature_rules
    
    def add_feature_rule(self, feature : FeatureRuleNode):
        self._feature_rules.add_property(feature)

    def clone(self) -> FeatureRuleNodeList:
        cloned  = FeatureRuleNodeList(self.name)
        cloned._feature_rules = self._feature_rules.clone()
        return cloned
    
    def merge_with_parent(self, parent):
        merged = FeatureRuleNodeList(self.name)
        merged._feature_rules = self._feature_rules.merge_with_parent(parent._feature_rules)
        return merged
    
    def dispatch_globals(self) -> FeatureRuleNodeList:
        dispatched = FeatureRuleNodeList()
        for feature in self._feature_rules.values():
            dispatched.add_feature_rule(feature.dispatch_globals())
        return dispatched