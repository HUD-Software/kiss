
from __future__ import annotations
import copy
from toolchain.nodes.feature_node import FeatureNode, FeatureNodeList, FeatureRuleNodeList, FeatureStrList
from toolchain.nodes.linker_nodes import LinkersOverrideNode
from toolchain.nodes.property import Property,  PropertyDict, StrList

class CompilerNode:
    """Represents a compiler definition in compilers.yaml.

    A compiler node can be abstract (base template, e.g. 'msvc-compiler') or concrete
    (e.g. 'cl', 'clangcl'). Concrete compilers can extend an abstract one via 'extends',
    inheriting its features and feature-rules while adding or overriding their own.

    Key attributes:
    - supported_linkers: list of linker names compatible with this compiler
    - default_linker: preferred linker when multiple supported linkers are available
    - is_abstract: if True, this node is a base template and cannot be used directly
    - features: compiler flags grouped by named capability (e.g. OPT_LEVEL_2, ASAN)
    - feature_rules: constraints between features (only-one and incompatible)

    Features can cascade to the linker layer via their 'linkers' sub-key,
    enabling linker-specific features when a given compiler feature is activated.
    """
    def __init__(self, name : str):
        self.name = name
        self.is_abstract = False
        self.extends = None
        self.supported_linkers = list[str]()
        self.default_linker = None
        self.feature_list = FeatureNodeList()
        self.feature_rule_list = FeatureRuleNodeList()
    
    def __eq__(self, other):
        if not isinstance(other, FeatureNode):
            return NotImplemented
        return self.name == other.name

    def __hash__(self):
        return hash(self.name)
    
    def merge_with(self, parent: CompilerNode):
        if not parent:
            return copy.deepcopy(self)
        """Merge list without applying modifier or dispatching top to bottom hierarchy """
        assert type(parent) is type(self), "Type mismatch"
        result = CompilerNode(self.name)
        result.is_abstract = self.is_abstract
        result.extends = self.extends
        result.supported_linkers = self.supported_linkers + parent.supported_linkers
        result.default_linker = self.default_linker
        # Apply modifier during merge before merging the feature list
        # We want to merge feature list according the rules, we must merge feature rule with parent 
        # but also resolve modifier to validate
        result.feature_rule_list = self.feature_rule_list.merge_with(parent.feature_rule_list).apply_modifiers()
        result.feature_list = self.feature_list.merge_with(parent.feature_list, result.feature_rule_list)
        return result
    
    def apply_modifiers(self) -> CompilerNode:
        """Apply list modifier"""
        result  = CompilerNode(self.name)
        result.is_abstract = self.is_abstract
        result.extends = self.extends
        result.supported_linkers = self.supported_linkers.copy()
        result.default_linker = self.default_linker
        result.feature_rule_list = self.feature_rule_list.apply_modifiers()
        result.feature_list = self.feature_list.apply_modifiers(result.feature_rule_list)
        return result
        
    def dispatch(self) -> CompilerNode:
        """ 
        Dispatch properties from top to bottom hierarchy
        """
        result = CompilerNode(self.name)
        result.is_abstract = self.is_abstract
        result.extends = self.extends
        result.supported_linkers = self.supported_linkers.copy()
        result.default_linker = self.default_linker
        result.feature_rule_list = copy.deepcopy(self.feature_rule_list)
        result.feature_list = copy.deepcopy(self.feature_list)
        return result

    def resolve_extends(self, parent: CompilerNode) -> CompilerNode:
        if parent:
            assert parent.name == self.extends
            node = self.merge_with(parent)
        else:
            node = self
        node = node.dispatch()
        node = node.apply_modifiers()
        return node

class CompilerSpecificOverrideNode:
    """Represents a per-compiler override inside a 'compilers:' node.

    compilers:
      gcc : # CompilerSpecificOverrideNode
        enable-features: []
        defines: []
        features:
          - name: ASAN
            linkers:
      ...
    """
    def __init__(self, name : str):
        self.name = name
        self.linkers : LinkersOverrideNode = None
        self.flags = StrList()
        self.features = FeatureStrList ()
        self.defines = StrList()

    def __eq__(self, other):
        if not isinstance(other, CompilerSpecificOverrideNode):
            return NotImplemented
        return self.name == other.name

    def __hash__(self):
        return hash(self.name)
       
    def apply_modifiers(self) -> CompilerSpecificOverrideNode:
        result = CompilerSpecificOverrideNode(self.name)
        result.linkers = self.linkers.apply_modifiers() if self.linkers else None
        result.feature_list = self.feature_list.apply_modifiers()
        result.feature_rule_list = self.feature_rule_list.apply_modifiers()
        return result
    
    def merge_with(self, other: CompilerSpecificOverrideNode, parent_list_name_to_ignore: set[str]) -> CompilerSpecificOverrideNode:
        if not other:
            return copy.deepcopy(self)
        assert self.name == other.name, "Name mismatch"
        result = CompilerSpecificOverrideNode(self.name)
        result.linkers = self.linkers.merge_with(other.linkers) if self.linkers else None
        result.feature_list = self.feature_list.merge_with(other.feature_list)
        result.feature_rule_list = self.feature_rule_list.merge_with(other.feature_rule_list)
        return result
    
    def dispatch(self, top : PropertyDict) -> CompilerSpecificOverrideNode:
        result = CompilerSpecificOverrideNode(self.name)
        result._properties = self.properties.dispatch(top)
        result.linkers = self.linkers.dispatch(top) if self.linkers else None
        result.feature_list = self.feature_list.dispatch()
        result.feature_rule_list = self.feature_rule_list.dispatch()
        return result
   
class CompilersOverrideNode:
    """Represents the 'compilers:' block.
    Contains global enable-features + per-compiler overrides 'CompilerSpecificOverrideNode' nodes.

    compilers: # CompilersOverrideNode
      gcc : 
        enable-features: []
        defines: []
      ...
    """
    def __init__(self):
      self.common_compiler = CompilerSpecificOverrideNode("")
      self.compilers = set[CompilerSpecificOverrideNode]()

    def merge_with(self, parent: CompilersOverrideNode, parent_list_name_to_ignore: set[str] = None):
        if not parent:
            return copy.deepcopy(self)
        result = CompilersOverrideNode(self.name)
        result._properties = self.properties.merge_with(parent.properties, parent_list_name_to_ignore)
        
        if parent_list_name_to_ignore:
            parent_list_name_to_ignore.update(self.properties.explicit_list_names())
        else :
            parent_list_name_to_ignore = self.properties.explicit_list_names()

        for compiler in self._compilers.values():
            parent_compiler = parent._compilers.get(compiler.name)
            if parent_compiler: # compiler in both
                result.add_compiler(compiler.merge_with(parent_compiler, parent_list_name_to_ignore))
            else: # compiler only in self
                result.add_compiler(copy.deepcopy(compiler))
        
        for compiler_name, parent_compiler in parent._compilers.items():
            if compiler_name not in self._compilers: # Only in parents
                self_compiler = CompilerSpecificOverrideNode(parent_compiler.name)
                result.add_compiler(self_compiler.merge_with(parent_compiler, parent_list_name_to_ignore))

        return result
    
    def apply_modifiers(self) -> CompilersOverrideNode:
        result = CompilersOverrideNode(self.name)
        result._properties = self.properties.apply_modifiers()
        for compiler in self._compilers.values():
            result.add_compiler(compiler.apply_modifiers())
        return result

    def dispatch(self, top: PropertyDict) -> CompilersOverrideNode:
        result = CompilersOverrideNode(self.name)
        result._properties = self.properties.dispatch(top)
        for compiler in self._compilers.values():
            result.add_compiler(compiler.dispatch(result.properties))
        return result

class CompilerFeatureNodeList:
    """Represents the 'features:' block."""
    def __init__(self):
        self._features : set[CompilerFeatureNode] = set()
    
    def is_empty(self) -> bool:
        return not self._features
    
    @property
    def features(self) -> set[CompilerFeatureNode]:
        return self._features
    
    def add_feature(self, feature : CompilerFeatureNode):
        self._features.add(feature)
    
    def get_by_name(self, name: str) -> CompilerFeatureNode | None:
        for rule in self._features:
            if rule.name == name:
                return rule
        return None

    def merge_with(self, parent: CompilerFeatureNodeList, feature_rules: FeatureRuleNodeList):
        result = CompilerFeatureNodeList()
        if parent:
            for parent_feature in parent.features:
                self_feature = self.get_by_name(parent_feature.name)
                if self_feature:
                    result.add_feature(self_feature.merge_with(parent_feature, feature_rules))
                else:
                    result.add_feature(copy.deepcopy(parent_feature))
        return result
    
    def apply_modifiers(self, feature_rules: FeatureRuleNodeList) -> CompilerFeatureNodeList:
        result = CompilerFeatureNodeList()
        for feature in self.features:
            result.add_feature(feature.apply_modifiers(feature_rules))
        return result

    # def dispatch(self, feature_rules: FeatureRuleNodeList) -> CompilerFeatureNodeList:
    #     result = CompilerFeatureNodeList()
    #     for feature in self.features:
    #         result.add_feature(feature.dispatch(feature_rules))
    #     return result

class CompilerFeatureNode(FeatureNode):
    def __init__(self, name:str):
        super().__init__(name)
        self.linkers = LinkersOverrideNode()

    @classmethod
    def from_feature_node(cls, feature: FeatureNode) -> CompilerFeatureNode:
        obj = cls(feature.name)
        obj.flags = copy.deepcopy(feature.flags)
        obj.features = copy.deepcopy(feature.features)
        obj.args = copy.deepcopy(feature.args)
        obj.description = copy.deepcopy(feature.description)
        return obj
    
    def merge_with(self, other: CompilerFeatureNode, feature_rules: FeatureRuleNodeList):
        s : FeatureNode = super().apply_modifiers(feature_rules)
        result = CompilerFeatureNode.from_feature_node(s)
        result.linkers = self.linkers.merge_with(other.linkers)
        return result
    
    def apply_modifiers(self, feature_rules: FeatureRuleNodeList) -> CompilerFeatureNode:
        s : FeatureNode = super().apply_modifiers(feature_rules)
        result = CompilerFeatureNode.from_feature_node(s)
        result.linkers = copy.deepcopy(self.linkers)
        return result

    # def dispatch(self, feature_rules: FeatureRuleNodeList) -> CompilerFeatureNode:
    #     result = CompilerFeatureNode.from_feature_node(self)
    #     result.linkers = self.linkers.dispatch(feature_rules)
    #     return result
      