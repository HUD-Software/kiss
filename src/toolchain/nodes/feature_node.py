from __future__ import annotations
import copy
from toolchain.nodes.property import StrList, StrListModifierAdd, StrListModifierRemove, merge_str_list
from typing import Self

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

class FeatureStrList:
    def __init__(self):
        self.str_list = StrList()

    @property
    def add_modifiers(self) -> StrListModifierAdd:
        return self.str_list.add_modifiers

    @property
    def remove_modifiers(self) -> StrListModifierRemove:
        return self.str_list.remove_modifiers

    @property
    def values(self) -> set[str] :
        return self.str_list.values

    def is_user_defined_values(self) -> bool:
        return self.str_list.is_user_defined_values()
    
    def has_values(self) -> bool:
        return self.str_list.has_values()
    
    def has_modifiers(self) -> bool:
        return self.str_list.has_modifiers()
    
    def is_empty(self):
        return not self.has_values() and not self.has_modifiers()
    
    def apply_modifiers(self, feature_rules: FeatureRuleNodeList) -> FeatureStrList:
        # features : [A, B]
        # add-features: [B, C]
        # remove-features: [B]
        # become
        # features : [A, C]
        # add-features: []
        # remove-features: []
        # Ensure that only-one is respected
        values = copy.deepcopy(self.values)
        add_features = copy.deepcopy(self.add_modifiers)
        
        # Apply remove-features first to values and add-features
        for value in self.remove_modifiers.values:
            values.discard(value)
            add_features.values.discard(value)
            
        # After removing features from values and add modifiers,
        # Validate that values and add modifiers respect rules
        feature_rules.validate(values)
        feature_rules.validate(add_features.values)

        # After validation, apply add-features to values
        # Only one rule is validated for each feature to add to values
        for value_to_add in add_features.values:
            for onlyone_rule in feature_rules.feature_rules_only_one:
                if(onlyone_rule.contains(value_to_add)):
                    for value in list(values):
                        if(onlyone_rule.contains(value)):
                            values.discard(value)
            values.add(value_to_add)
        # Return the modified feature list
        result = FeatureStrList()
        result.str_list.values = values
        return result

def merge_feature_list(child: FeatureStrList, parent: FeatureStrList, feature_rules: FeatureRuleNodeList) -> FeatureStrList :
    assert isinstance(child, FeatureStrList)
    assert isinstance(parent, FeatureStrList)

    # If child have values, ignore parents
    if child.is_user_defined_values():
        return copy.deepcopy(child)
    # Child have no values, merge with parent
    else:
        # Filter the add modifiers
        # We conditionnaly add parent to the child 
        merged_add_modifiers_list = copy.deepcopy(child.add_modifiers)
        for parent_value_to_add in parent.values:
            add_in_merged = True
            # Ignore parent if we have a only-one feature rules that concerned the parent value and is also present in child values
            for onlyone_rule in feature_rules.feature_rules_only_one:
                if(onlyone_rule.contains(parent_value_to_add)):
                    for child_value in child.add_modifiers.values:
                        if(onlyone_rule.contains(child_value)):
                            add_in_merged = False
                            continue
            if add_in_merged:
                merged_add_modifiers_list.values.add(parent_value_to_add)

        #  Return the merged feature list
        result = FeatureStrList()
        result.str_list.values = copy.deepcopy(parent.values)
        result.str_list.add_modifiers = merged_add_modifiers_list
        result.str_list.remove_modifiers.values.update(child.remove_modifiers.values)
        return result

# def dispatch_feature_list(top: FeatureStrList, bottom: FeatureStrList, feature_rules: FeatureRuleNodeList):
#     assert isinstance(top, StrList)
#     assert isinstance(bottom, StrList)
#     assert not top.has_modifiers()
#     assert not bottom.has_modifiers()
#     return merge_feature_list(bottom, top, feature_rules)

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
        result = FeatureNode(self.name)
        result.flags = merge_str_list(self.flags, parent.flags)
        result.features = merge_feature_list(self.features, parent.features, feature_rules)
        result.args = copy.deepcopy(self.args if self.args else parent.args) 
        result.description = copy.deepcopy(self.description if self.description else parent.description)
        return result
    
    def apply_modifiers(self, feature_rules: FeatureRuleNodeList) -> FeatureNode:
        result = FeatureNode(self.name)
        result.flags = self.flags.apply_modifiers()
        result.features = self.features.apply_modifiers(feature_rules)
        result.args = copy.deepcopy(self.args)
        result.description = copy.deepcopy(self.description)
        return result
    
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
        result = FeatureNodeList()
        if parent:
            for parent_feature in parent.features:
                self_feature = self.get_by_name(parent_feature.name)
                if self_feature:
                    result.add_feature(self_feature.merge_with(parent_feature, feature_rules))
                else:
                    result.add_feature(copy.deepcopy(parent_feature))
        return result
    
    def apply_modifiers(self, feature_rules: FeatureRuleNodeList) -> FeatureNodeList:
        result = FeatureNodeList()
        for feature in self.features:
            result.add_feature(feature.apply_modifiers(feature_rules))
        return result

    # def dispatch(self) -> FeatureNodeList:
    #     return copy.deepcopy(self)
    

class FeatureRuleNode:
    """Represents a feature rule (only-one or incompatible)."""
    
    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description
    
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
    def __init__(self, name: str, description: str, feature_names : StrList):
        super().__init__(name, description)
        self._feature_names = feature_names

    @property
    def feature_names(self) -> StrList:
        return self._feature_names

    def contains(self, feature_name: str) -> bool:
        if self.feature_names.has_modifiers():
            raise ValueError("Only one rules must have called apply_modifiers before checking if a feature name is present in the")
        return feature_name in self.feature_names.values
    
    def merge_with(self, parent: FeatureRuleNodeOnlyOne) -> FeatureRuleNodeOnlyOne:
        return FeatureRuleNodeOnlyOne(self.name, 
                                      self.description,
                                      merge_str_list(self.feature_names, parent.feature_names))

    def apply_modifiers(self) -> FeatureRuleNodeOnlyOne:
            return  FeatureRuleNodeOnlyOne(self.name,
                                           self.description,
                                           self.feature_names.apply_modifiers())
    

class FeatureRuleNodeIncompatible(FeatureRuleNode):
    RULE_NAME = "incompatible"
    
    def __init__(self, name: str, description:str, feature: str, incompatible_with: StrList):
        super().__init__(name, description)
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

    def apply_modifiers(self) -> FeatureRuleNodeIncompatible:
        return  FeatureRuleNodeIncompatible(self.name,
                                            self.description,
                                            self.feature,
                                            self.incompatible_with.apply_modifiers())

        
class FeatureRuleNodeList:
    """Represents the 'feature-rules:' block."""
    def __init__(self):
        self._feature_rules_only_one : set[FeatureRuleNodeOnlyOne] = set()
        self._feature_rules_incompatible : set[FeatureRuleNodeIncompatible] = set()
    
    def is_empty(self) -> bool:
        return not self._feature_rules_only_one and not self._feature_rules_incompatible
    
    @property
    def feature_rules_only_one(self) -> set[FeatureRuleNodeOnlyOne]:
        return self._feature_rules_only_one
    
    @property
    def feature_rules_incompatible(self) -> set[FeatureRuleNodeIncompatible]:
        return self._feature_rules_incompatible
    
    def add_feature_rule(self, feature_rule : FeatureRuleNode):
        if isinstance(feature_rule, FeatureRuleNodeOnlyOne):
            self._feature_rules_only_one.add(feature_rule)
        elif isinstance(feature_rule, FeatureRuleNodeIncompatible):
            self._feature_rules_incompatible.add(feature_rule)
        else:
            raise TypeError("Invalid feature rule type")
    
    def get_only_one_by_name(self, name: str) -> FeatureRuleNodeOnlyOne | None:
        for rule in self.feature_rules_only_one:
            if rule.name == name:
                return rule
        return None
    
    def get_incompatible_by_name(self, name: str) -> FeatureRuleNodeIncompatible | None:
        for rule in self.feature_rules_incompatible:
            if rule.name == name:
                return rule
        return None
    
    def validate(self, list: set[str]):
        self.validate_only_one(list)
        self.validate_incompatible(list)

    def validate_only_one(self, list: set[str]):
        for rule in self.feature_rules_only_one:
            count = sum(1 for a in rule.feature_names.values if a in list)
            if count > 1:
                raise ValueError(
                    f"Feature rule '{rule.name}' allows only one of {rule.feature_names.values}, "
                    f"but found {count} in {list}"
                )

    def validate_incompatible(self, list : set[str]):
        for rule in self.feature_rules_incompatible:
            if rule.feature not in list:
                continue

            conflicts = [f for f in rule.incompatible_with.values if f in list]
            if conflicts:
                raise ValueError(
                    f"Feature '{rule.feature}' is incompatible with {conflicts} "
                    f"(rule '{rule.name}')"
                )
            
    def merge_with(self, parent: FeatureRuleNodeList):
        result = FeatureRuleNodeList()

        def merge_rules(self_rules: set, parent_rules: set):
            self_by_name = {r.name: r for r in self_rules}
            parent_by_name = {r.name: r for r in parent_rules}

            for name in self_by_name.keys() | parent_by_name.keys():
                self_rule = self_by_name.get(name)
                parent_rule = parent_by_name.get(name)

                if self_rule and parent_rule:
                    result.add_feature_rule(self_rule.merge_with(parent_rule))
                else:
                    result.add_feature_rule(copy.deepcopy(self_rule or parent_rule))

        merge_rules(self.feature_rules_only_one, parent.feature_rules_only_one)
        merge_rules(self.feature_rules_incompatible, parent.feature_rules_incompatible)

        return result
    
    def apply_modifiers(self) -> FeatureRuleNodeList:
        result = FeatureRuleNodeList()
        for rule in self.feature_rules_only_one:
            result.add_feature_rule(rule.apply_modifiers())
        for rule in self.feature_rules_incompatible:
            result.add_feature_rule(rule.apply_modifiers())
        return result

    # def dispatch(self) -> FeatureRuleNodeList:
    #     return copy.deepcopy(self)
