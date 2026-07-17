from __future__ import annotations
import copy
from toolchain.nodes.property import Property, StrList, StrListModifier, merge_str_list

class FeatureArgsNode:
    """Represents the 'args' block inside a feature with arguments.
    args:
      min: 1
      max: ~
      separator: ","
      pattern: "*.lib"
    """
    NAME = "args"
    DEFAULT_MAX_ARGS = 512
    DEFAULT_MIN_ARGS = 1

    def __init__(self):
        self.min : int = FeatureArgsNode.DEFAULT_MIN_ARGS
        self.max : int = FeatureArgsNode.DEFAULT_MAX_ARGS
        self.separator = ","

from typing import TypeVar, Type
T = TypeVar("T", bound=Property)

class FeatureStrList:
    def __init__(self):
        self.str_list = StrList()

    def add_modifier(self, modifier :StrListModifier) : 
        self.str_list.add_modifier(modifier)

    def has_values(self) -> bool:
        return self.str_list.has_values()
    
    def has_modifiers(self) -> bool:
        return self.str_list.has_modifiers()
    
    def is_empty(self):
        return not self.has_values() and not self.has_modifiers()

def merge_feature_list(child: FeatureStrList, parent: FeatureStrList, feature_rules: FeatureRuleNodeList) -> StrList :
    assert isinstance(child, FeatureStrList)
    assert isinstance(parent, FeatureStrList)

    raise NotImplementedError

class FeatureNode:
    """Represents a single compiler feature entry.
    e.g. - name: OPT_LEVEL_0
           flags: [/Od]
           enable-features: [DEBUG_INFO]
           args: ...
    """
    def __init__(self, name: str):
        self.name = name
        self.description = ""
        self.flags = StrList()
        self.features = FeatureStrList ()
        self.args : FeatureArgsNode = None
    
    def __eq__(self, other):
        if not isinstance(other, FeatureNode):
            return NotImplemented
        return self.name == other.name

    def __hash__(self):
        return hash(self.name)
    
    def merge_with(self, parent: FeatureNode, feature_rules: FeatureRuleNodeList):
        flags = merge_str_list(self.flags, parent.flags)
        features = merge_feature_list(self.features, self.features, feature_rules)
        arg = copy.deepcopy(self.args if self.args else parent.args) 
        description = copy.deepcopy(self.description if self.description else parent.description)
        raise FeatureNode()
    
    def apply_modifiers(self) -> FeatureNode:
        raise NotImplemented
        # result = FeatureNode(self.name)
        # #result._properties = self._properties.apply_modifiers()
        # return result
    
class FeatureNodeList:
    """Represents the 'features:' block."""
    def __init__(self):
        self._features : set[FeatureNode] = set()
    
    def is_empty(self) -> bool:
        return not self._features
    
    @property
    def features(self) -> set[FeatureNode]:
        return self._features
    
    def add_feature(self, feature : FeatureNode):
        self._features.add(feature)
    
    def get_by_name(self, name: str) -> FeatureNode | None:
        for rule in self._features:
            if rule.name == name:
                return rule
        return None

    def merge_with(self, parent: FeatureNodeList, feature_rules: FeatureRuleNodeList):
        result = copy.deepcopy(self)
        if parent:
            for parent_feature in parent.features:
                self_feature = self.get_by_name(parent_feature.name)
                if self_feature:
                    result.add_feature(self_feature.merge_with(parent_feature, feature_rules))
                else:
                    result.add_feature(copy.deepcopy(parent_feature))
        return result
    
    def apply_modifiers(self) -> FeatureNodeList:
        raise NotImplemented
        # result = FeatureNodeList(self.name)
        # for feature in self.features.values():
        #     result.add_feature(feature.apply_modifiers())
        # return result

    def dispatch(self) -> FeatureNodeList:
        return copy.deepcopy(self)
    

class FeatureRuleNode:
    """Represents a feature rule (only-one or incompatible)."""
    
    def __init__(self, name: str):
        self.name = name
    
    def __eq__(self, other):
        if not isinstance(other, FeatureRuleNode):
            return NotImplemented
        return self.name == other.name

    def __hash__(self):
        return hash(self.name)
    
    def merge_with(self, parent: FeatureRuleNode):
        raise NotImplemented(f"Feature rule {self.name!r} is not mergeable with{parent.name}.")

    def dispatch(self) -> FeatureRuleNode:
        raise NotImplemented(f"Feature rule {self.name!r} are not is_dispatchable.")

class FeatureRuleNodeOnlyOne(FeatureRuleNode):  
    RULE_NAME = "only-one"
    def __init__(self, name: str, feature_names : StrList):
        super().__init__(name)
        self._feature_names = feature_names

    @property
    def feature_names(self) -> StrList:
        return self._feature_names

    def merge_with(self, parent: FeatureRuleNodeOnlyOne) -> FeatureRuleNodeOnlyOne:
        return FeatureRuleNodeOnlyOne(self.name, 
                                      merge_str_list(self.feature_names, parent.feature_names))


class FeatureRuleNodeIncompatible(FeatureRuleNode):
    RULE_NAME = "incompatible"
    
    def __init__(self, name: str, feature: str, incompatible_with: StrList):
        super().__init__(name)
        self._feature = feature
        self._with = incompatible_with
    
    @property
    def feature(self) -> str:
        return self._feature
    
    @property
    def incompatible_with(self) -> StrList:
        return self._with
    
    def merge_with(self, parent: FeatureRuleNodeIncompatible) -> FeatureRuleNodeIncompatible:
        return FeatureRuleNodeIncompatible(self.name,
                                           self.feature,
                                           merge_str_list(self.incompatible_with, parent.incompatible_with))
    
class FeatureRuleNodeList:
    """Represents the 'feature-rules:' block."""
    NAME = "feature-rules"
 
    def __init__(self):
        self._feature_rules : set[FeatureRuleNode] = set()
    
    def is_empty(self) -> bool:
        return not self._feature_rules
    
    @property
    def feature_rules(self) -> set[FeatureRuleNode]:
        return self._feature_rules
    
    def add_feature_rule(self, feature_rule : FeatureRuleNode):
        self._feature_rules.add(feature_rule)
    
    def get_by_name(self, name: str) -> FeatureRuleNode | None:
        for rule in self._feature_rules:
            if rule.name == name:
                return rule
        return None
    
    def get_all_rules_of_type(self, rule_type: Type[T]) -> list[T]:
        """Return all rules matching the given FeatureRuleNode subclass,
        preserving declaration order."""
        return [r for r in self._feature_rules if isinstance(r, rule_type)]
    
    def merge_with(self, parent: FeatureRuleNodeList):
        result = copy.deepcopy(self)
        if parent:
            for parent_feature_rule in parent.feature_rules:
                self_feature_rule = self.get_by_name(parent_feature_rule.name)
                if self_feature_rule:
                    result.add_feature_rule(self_feature_rule.merge_with(parent_feature_rule))
                else:
                    result.add_feature_rule(copy.deepcopy(parent_feature_rule))
        return result
    
    def apply_modifiers(self) -> FeatureRuleNodeList:
        return copy.deepcopy(self)

    def dispatch(self) -> FeatureRuleNodeList:
        return copy.deepcopy(self)
