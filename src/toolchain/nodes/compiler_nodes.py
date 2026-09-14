
from __future__ import annotations
import copy
from toolchain.nodes.feature_node import FeatureNode, FeatureNodeList, FeatureRuleNodeList, FeatureStrList, merge_feature_list
from toolchain.nodes.linker_nodes import LinkersOverrideNode
from toolchain.nodes.property import PropertyDict, StrList, merge_str_list

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
        if not isinstance(other, CompilerNode):
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
        #node = node.apply_modifiers()
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
        self.linker_overrides : LinkersOverrideNode = None
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
        result.linker_overrides = self.linker_overrides.apply_modifiers() if self.linker_overrides else None
        result.feature_list = self.feature_list.apply_modifiers()
        result.feature_rule_list = self.feature_rule_list.apply_modifiers()
        return result
    
    def merge_with(self, parent: CompilerSpecificOverrideNode, compiler_feature_rules: FeatureRuleNodeList) -> CompilerSpecificOverrideNode:
        result = CompilerSpecificOverrideNode(self.name)
        result.flags = merge_str_list(parent.flags, self.flags)
        result.defines = merge_str_list(parent.defines, self.defines)
        result.features = merge_feature_list(parent.features, self.features, compiler_feature_rules)
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
      self.compilers_overrides = dict[str, CompilerSpecificOverrideNode]()

    def merge_with(self, parent: CompilersOverrideNode, compilers : dict[str, CompilerNode]):
        result = CompilersOverrideNode()
        
        # Merge common lincompilerer with the parent common lcompilerinker without feature rule list
        # We can't use feature rule list because it is bound too the compiler itself.
        # We just merge with all know compiler after and validate the merge here
        # We could wait for the dispatch step, but if we do it now, we can have better understanding of where the bad merge appears
        result.common_compiler = self.common_compiler.merge_with(parent.common_compiler, FeatureRuleNodeList())
        for compiler in compilers.values():
            features = merge_feature_list(
                self.common_compiler.features,
                parent.common_compiler.features,
                compiler.feature_rule_list
            )
            compiler.feature_rule_list.validate(features.apply_modifiers(compiler.feature_rule_list).values)

        # Merge compiler overrides
        # - Merge if present in parent and self
        # - If not present in parent, keep it
        # - Add parent that are not in self
        for compiler_override_name, compiler_override in self.compilers_overrides.items():
            if compiler_override_name in parent.compilers_overrides:
                result.compilers_overrides[compiler_override_name] = compiler_override.merge_with(parent.compilers_overrides[compiler_override_name], linkers[linker_override_name].feature_rule_list)
            else:
                result.compilers_overrides[compiler_override_name] = copy.deepcopy(compiler_override)

        for parent_compiler_override_name, parent_compiler_override in parent.compilers_overrides.items():
            if not parent_compiler_override_name in self.compilers_overrides:
                result.compilers_overrides[parent_compiler_override_name] = copy.deepcopy(parent_compiler_override)
                
        return result
    
    def apply_modifiers(self) -> CompilersOverrideNode:
        raise NotImplemented
        # result = CompilersOverrideNode(self.name)
        # result._properties = self.properties.apply_modifiers()
        # for compiler in self._compilers.values():
        #     result.add_compiler(compiler.apply_modifiers())
        # return result

    def dispatch(self, compilers: dict[str, CompilerNode]) -> CompilersOverrideNode:
        result = CompilersOverrideNode()
        result.common_compiler = copy.deepcopy(self.common_compiler)
        for compiler_override_name, linker_override in self.compilers_overrides.items():
            if compiler_override_name in compilers:
                result.compilers_overrides[compiler_override_name] = linker_override.merge_with(result.common_compiler, compilers[compiler_override_name].feature_rule_list)
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
      