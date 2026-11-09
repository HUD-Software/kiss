from __future__ import annotations
import copy
from dataclasses import dataclass
from result import Err, Ok, Result
from toolchain.nodes.property import StrList, StrListModifierAdd, StrListModifierRemove, resolve_extends_str_list
from typing import Self


@dataclass(frozen=True, slots=True)
class OnlyOneViolation:
    rule_name: str
    allowed: list[str]
    found: list[str]
    list : list[str]

    def __str__(self) -> str:
        return (
            f"Feature rule '{self.rule_name}' allows only one of {self.allowed}, "
            f"but found ({len(self.found)}){self.found} in {self.list}"
        )


@dataclass(frozen=True, slots=True)
class IncompatibleViolation:
    rule_name: str
    feature: str
    conflicts: list[str]

    def __str__(self) -> str:
        return (
            f"Feature '{self.feature}' is incompatible with {self.conflicts} "
            f"(rule '{self.rule_name}')"
        )


type ValidationError = OnlyOneViolation | IncompatibleViolation


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
    
    def apply_remove(self):
        result = FeatureStrList()
        result.str_list = self.str_list.apply_remove()
        return result

    @property
    def values(self) -> set[str] :
        return self.str_list.values
    
    @property
    def override(self) ->  bool:
        return self.str_list.override
    
    @property
    def remove_modifiers(self) -> StrListModifierRemove :
        return self.str_list.remove_modifiers
    
    # def is_user_defined_values(self) -> bool:
    #     return self.str_list.is_user_defined_values()
    
    # def has_values(self) -> bool:
    #     return self.str_list.has_values()
    
    # def has_modifiers(self) -> bool:
    #     return self.str_list.has_modifiers()
    
    # def is_empty(self):
    #     return not self.has_values() and not self.has_modifiers()
    
    # def apply_remove(self) : 
    #         result = StrList()
    #         if self.remove_modifiers.is_empty():
    #             return copy.deepcopy(self)
    #         else:
    #             for value_to_remove in self.remove_modifiers.values:
    #                 if value_to_remove not in result.values:
    #                     result.values.add(value_to_remove)
    #                 if value_to_remove not in result.add_modifiers.values:
    #                     result.add_modifiers.values.add(value_to_remove)
    #         return result
    
    # def apply_modifiers(self, feature_rules: FeatureRuleNodeList) -> FeatureStrList:
    #     # features : [A, B]
    #     # add-features: [B, C]
    #     # remove-features: [B]
    #     # become
    #     # features : [A, C]
    #     # add-features: []
    #     # remove-features: []
    #     # Ensure that only-one is respected
    #     values = copy.deepcopy(self.values)
    #     add_features = copy.deepcopy(self.add_modifiers)
        
    #     # Apply remove-features first to values and add-features
    #     for value in self.remove_modifiers.values:
    #         values.discard(value)
    #         add_features.values.discard(value)
            
    #     # After removing features from values and add modifiers,
    #     # Validate that values and add modifiers respect rules
    #     feature_rules.validate(values)
    #     feature_rules.validate(add_features.values)

    #     # After validation, apply add-features to values
    #     # Only one rule is validated for each feature to add to values
    #     for value_to_add in add_features.values:
    #         for onlyone_rule in feature_rules.feature_rules_only_one:
    #             if(onlyone_rule.contains(value_to_add)):
    #                 for value in list(values):
    #                     if(onlyone_rule.contains(value)):
    #                         values.discard(value)
    #         values.add(value_to_add)

    #     # Validate that adding don't break incompatible rules
    #     feature_rules.validate_incompatible(values)

    #     # Return the modified feature list
    #     result = FeatureStrList()
    #     result.str_list.values = values
    #     return result

def resolve_extends_feature_list(child: FeatureStrList, parent: FeatureStrList, feature_rules: FeatureRuleNodeList) -> Result[FeatureStrList, ValidationError]:
    assert isinstance(child, FeatureStrList)
    assert isinstance(parent, FeatureStrList)

    # Add all child values and add modifiers in add modifiers if not removed
    result = FeatureStrList()
    result.str_list.override = child.str_list.override

    # Add child value if not removed
    for value in child.str_list.values:
        if value not in child.str_list.remove_modifiers.values:
            # Add the value only if not already present
            result.str_list.values.add(value)
    # Validate after all insertion of childs
    match feature_rules.validate_only_one(result.str_list.values):
        case Err() as err:
            return err
                        
    # If the child do not override the value add parents values
    if not child.str_list.override:

        def can_add_parent_value(parent_value, child_list, only_one):
            # Parent value is concerned by the rule
            if only_one.contains(parent_value):
                # Parent value is concerned by the rule
                # If at least one value in this rule is in the child list
                # don't add to the parent
                for child_value in child_list:
                    if only_one.contains(child_value):
                        return False

            # Parent value is not concerned by the rule
            # or
            # The child list does not contains any value in the only one rule
            return True
            
            
        # If Child do not override value, add parent values if not in only_one rule
        for parent_value in parent.str_list.values:
            if parent_value not in child.str_list.remove_modifiers.values:
                can_add = True
                for only_one in feature_rules.feature_rules_only_one:
                    if not can_add_parent_value(parent_value, result.str_list.values, only_one):
                        can_add = False
                        break
                if can_add:
                    result.str_list.values.add(parent_value)

    # Validate incompatible values
    match feature_rules.validate_incompatible(result.str_list.values):
        case Err() as err:
            return err
    
    return Ok(result)

# def merge_feature_list(child: FeatureStrList, parent: FeatureStrList, feature_rules: FeatureRuleNodeList) -> FeatureStrList :
#     assert isinstance(child, FeatureStrList)
#     assert isinstance(parent, FeatureStrList)

#     # If child have user defined, ignore parents
#     if child.has_values():
#         return copy.deepcopy(child)
#     # Child have no values, merge with parent
#     else:
#         # Filter the add modifiers
#         # We conditionnaly add parent to the child 
#         merged_add_modifiers_list = copy.deepcopy(child.add_modifiers)
#         for parent_value_to_add in parent.add_modifiers.values:
#             add_in_merged = True
#             # Ignore parent if we have a only-one feature rules that concerned the parent value and is also present in child values
#             for onlyone_rule in feature_rules.feature_rules_only_one:
#                 if(onlyone_rule.contains(parent_value_to_add)):
#                     for child_value in child.add_modifiers.values:
#                         if(onlyone_rule.contains(child_value)):
#                             add_in_merged = False
#                             continue
#             if add_in_merged:
#                 merged_add_modifiers_list.values.add(parent_value_to_add)

#         #  Return the merged feature list
#         result = FeatureStrList()
#         result.str_list.values = copy.deepcopy(parent.values)
#         result.str_list.add_modifiers = merged_add_modifiers_list
#         result.str_list.remove_modifiers.values.update(child.remove_modifiers.values)

#         # Validate that the result respect feature rules
#         feature_rules.validate(result.apply_modifiers(feature_rules).values)
        
#         return result

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
        self.features = FeatureStrList()
        self.args : FeatureArgsNode = None
    
    def __eq__(self, other):
        if not isinstance(other, FeatureNode):
            return NotImplemented
        return self.name == other.name

    def __hash__(self):
        return hash(self.name)

    def resolve_extends(self, parent: FeatureNode, feature_rules: FeatureRuleNodeList):
        result = FeatureNode(self.name)
        result.description = self.description
        if parent:
            result.flags = resolve_extends_str_list(self.flags, parent.flags)
            result.features = resolve_extends_feature_list(self.features, parent.features, feature_rules).unwrap()
        else:
            result.flags = resolve_extends_str_list(self.flags, StrList())
            result.features = resolve_extends_feature_list(self.features, FeatureStrList(), feature_rules).unwrap()
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

    def resolve_extends(self, parent: FeatureNodeList, feature_rules: FeatureRuleNodeList):
        result = FeatureNodeList()
        parent_features = parent.features if parent else set()
        self_by_name = {r.name: r for r in self.features}
        parent_by_name = {r.name: r for r in parent_features}

        for name in self_by_name.keys() | parent_by_name.keys():
            self_feature = self_by_name.get(name)
            parent_feature = parent_by_name.get(name)

            if self_feature:
                # In the case the feature exist in child
                # We extends the child with the parent feature
                # if the parent feature doesn't exist, feature resolve_extends handle this case
                result.add_feature(self_feature.resolve_extends(parent_feature, feature_rules))
            elif parent_feature:
                # In the case the feature exist only in child
                # We create a new FeatureNode with the same name and description as the parent feature
                # Then we resolve the extends with the parent feature
                # This is to ensure that the child feature inherits the name and description from the parent feature
                # keeping same behavior as before, but without marking flags and features as override if not present in the childn the child
                self_feature = FeatureNode(parent_feature.name)
                self_feature.description = parent_feature.description
                result.add_feature(self_feature.resolve_extends(parent_feature, feature_rules))
        return result    

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
        self.feature_names = feature_names

    def contains(self, feature_name: str) -> bool:
        return feature_name in self.feature_names.values

    def resolve_extends(self, parent: FeatureRuleNodeOnlyOne) :
        if parent:
            assert parent.name == self.name
            description = self.description if self.description else parent.description
            return FeatureRuleNodeOnlyOne(self.name, 
                                        description,
                                        resolve_extends_str_list(self.feature_names, parent.feature_names))
        else:
            return FeatureRuleNodeOnlyOne(self.name, 
                                          self.description,
                                          resolve_extends_str_list(self.feature_names, StrList()))
    
    # def merge_with(self, parent: FeatureRuleNodeOnlyOne) -> FeatureRuleNodeOnlyOne:
    #     return FeatureRuleNodeOnlyOne(self.name, 
    #                                   self.description,
    #                                   merge_str_list(self.feature_names, parent.feature_names))

    # def apply_modifiers(self) -> FeatureRuleNodeOnlyOne:
    #         return  FeatureRuleNodeOnlyOne(self.name,
    #                                        self.description,
    #                                        self.feature_names.apply_modifiers())
    

class FeatureRuleNodeIncompatible(FeatureRuleNode):
    RULE_NAME = "incompatible"
    
    def __init__(self, name: str, description:str, feature: str, incompatible_with: StrList):
        super().__init__(name, description)
        self.feature = feature
        self.incompatible_with = incompatible_with
      
    def resolve_extends(self, parent: FeatureRuleNodeIncompatible) :
        if parent:
            assert parent.name == self.name
            if self.feature:
                assert parent.feature == self.feature 
            description = self.description if self.description else parent.description
            return FeatureRuleNodeIncompatible(self.name, 
                                               description,
                                               self.feature,
                                               resolve_extends_str_list(self.incompatible_with, parent.incompatible_with))
        else:
            return FeatureRuleNodeIncompatible(self.name, 
                                               self.description,
                                               self.feature,
                                               resolve_extends_str_list(self.incompatible_with, StrList()))
        
    # def merge_with(self, parent: FeatureRuleNodeIncompatible) -> FeatureRuleNodeIncompatible:
    #     return FeatureRuleNodeIncompatible(self.name,
    #                                        self.feature,
    #                                        merge_str_list(self.incompatible_with, parent.incompatible_with))

    # def apply_modifiers(self) -> FeatureRuleNodeIncompatible:
    #     return  FeatureRuleNodeIncompatible(self.name,
    #                                         self.description,
    #                                         self.feature,
    #                                         self.incompatible_with.apply_modifiers())


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
    
    def validate(self, selected: set[str]) -> Result[None, ValidationError]:
        match self.validate_only_one(selected):
            case Err() as err:
                return err
        return self.validate_incompatible(selected)

    def validate_only_one(self, selected: set[str]) -> Result[None, ValidationError]:
        for rule in self.feature_rules_only_one:
            found = [f for f in rule.feature_names.values if f in selected]
            if len(found) > 1:
                return Err(OnlyOneViolation(rule.name, list(rule.feature_names.values), found, list(selected)))
        return Ok(None)

    def validate_incompatible(self, selected: set[str]) -> Result[None, ValidationError]:
        for rule in self.feature_rules_incompatible:
            if rule.feature not in selected:
                continue
            conflicts = [f for f in rule.incompatible_with.values if f in selected]
            if conflicts:
                return Err(IncompatibleViolation(rule.name, rule.feature, conflicts))
        return Ok(None)

    def resolve_extends(self, parent: FeatureRuleNodeList):
        result = FeatureRuleNodeList()
        def merge_rules(self_rules: set, parent_rules: set):
            self_by_name = {r.name: r for r in self_rules}
            parent_by_name = {r.name: r for r in parent_rules}

            for name in self_by_name.keys() | parent_by_name.keys():
                self_rule = self_by_name.get(name)
                parent_rule = parent_by_name.get(name)

                if self_rule:
                    result.add_feature_rule(self_rule.resolve_extends(parent_rule))
                elif parent_rule:
                    result.add_feature_rule(copy.deepcopy(parent_rule))
        if parent:
            merge_rules(self.feature_rules_only_one, parent.feature_rules_only_one)
            merge_rules(self.feature_rules_incompatible, parent.feature_rules_incompatible)
        else:
            merge_rules(self.feature_rules_only_one, set())
            merge_rules(self.feature_rules_incompatible, set())
        return result
    
    # def merge_with(self, parent: FeatureRuleNodeList):
    #     result = FeatureRuleNodeList()

    #     def merge_rules(self_rules: set, parent_rules: set):
    #         self_by_name = {r.name: r for r in self_rules}
    #         parent_by_name = {r.name: r for r in parent_rules}

    #         for name in self_by_name.keys() | parent_by_name.keys():
    #             self_rule = self_by_name.get(name)
    #             parent_rule = parent_by_name.get(name)

    #             if self_rule and parent_rule:
    #                 result.add_feature_rule(self_rule.merge_with(parent_rule))
    #             else:
    #                 result.add_feature_rule(copy.deepcopy(self_rule or parent_rule))

    #     merge_rules(self.feature_rules_only_one, parent.feature_rules_only_one)
    #     merge_rules(self.feature_rules_incompatible, parent.feature_rules_incompatible)

    #     return result
    
    # def apply_modifiers(self) -> FeatureRuleNodeList:
    #     result = FeatureRuleNodeList()
    #     for rule in self.feature_rules_only_one:
    #         result.add_feature_rule(rule.apply_modifiers())
    #     for rule in self.feature_rules_incompatible:
    #         result.add_feature_rule(rule.apply_modifiers())
    #     return result

    # def dispatch(self) -> FeatureRuleNodeList:
    #     return copy.deepcopy(self)
