
from __future__ import annotations
import copy
from toolchain.nodes.feature_node import FeatureNode, FeatureNodeList, FeatureRuleNodeList, FeatureStrList, merge_feature_list
from toolchain.nodes.linker_nodes import LinkerNode, LinkersOverrideNode, merge_linkers_override_node
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
            node = copy.deepcopy(self)
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
       
    def apply_modifiers(self, compiler_feature_rules: FeatureRuleNodeList, linkers : dict[str, LinkerNode]) -> CompilerSpecificOverrideNode:
        result = CompilerSpecificOverrideNode(self.name)
        result.linker_overrides = self.linker_overrides.apply_modifiers(linkers) if self.linker_overrides else None
        result.flags = self.flags.apply_modifiers()
        result.features = self.features.apply_modifiers(compiler_feature_rules)
        result.defines = self.defines.apply_modifiers()
        return result
    
    def merge_with(self, parent: CompilerSpecificOverrideNode, compiler_feature_rules: FeatureRuleNodeList, linkers : dict[str, LinkerNode]) -> CompilerSpecificOverrideNode:
        result = CompilerSpecificOverrideNode(self.name)
        result.flags = merge_str_list(parent.flags, self.flags)
        result.defines = merge_str_list(parent.defines, self.defines)
        result.features = merge_feature_list(parent.features, self.features, compiler_feature_rules)
        result.linker_overrides = merge_linkers_override_node(self.linker_overrides, parent.linker_overrides, linkers)
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
      self.compiler_overrides = dict[str, CompilerSpecificOverrideNode]()

    def merge_with(self, parent: CompilersOverrideNode, linkers: dict[str, LinkerNode], compilers: dict[str, CompilerNode]):
        result = CompilersOverrideNode()
        
        # Merge common compiler with the parent common compiler without feature rule list
        # We can't use feature rule list because it is bound too the compiler itself.
        # We just merge with all know compiler after and validate the merge here
        # We could wait for the dispatch step, but if we do it now, we can have better understanding of where the bad merge appears
        result.common_compiler = self.common_compiler.merge_with(parent.common_compiler, FeatureRuleNodeList(), linkers)
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
        for compiler_override_name, compiler_override in self.compiler_overrides.items():
            if compiler_override_name in parent.compiler_overrides:
                result.compiler_overrides[compiler_override_name] = compiler_override.merge_with(parent.compiler_overrides[compiler_override_name], compilers[compiler_override_name].feature_rule_list)
            else:
                result.compiler_overrides[compiler_override_name] = copy.deepcopy(compiler_override)

        for parent_compiler_override_name, parent_compiler_override in parent.compiler_overrides.items():
            if not parent_compiler_override_name in self.compiler_overrides:
                result.compiler_overrides[parent_compiler_override_name] = copy.deepcopy(parent_compiler_override)
                
        return result
    
    def apply_modifiers(self, linkers: dict[str, LinkerNode], compilers: dict[str, CompilerNode]) -> CompilersOverrideNode:
        result = CompilersOverrideNode()
        # Apply modifier on common compiler without feature rule list
        # We can't use feature rule list because it is bound too the compiler itself
        # We just apply modifiers with all know compiler after and validate the apply modifiers
        result.common_compiler = self.common_compiler.apply_modifiers(FeatureRuleNodeList(), linkers )
        for compiler in compilers.values():
            result.common_compiler.apply_modifiers(compiler.feature_rule_list, linkers)

        # Apply modifiers for all compiler overrides
        for compiler_override_name, compiler_override in self.compiler_overrides.items():
            result.compiler_overrides[compiler_override_name] = compiler_override.apply_modifiers(compilers[compiler_override_name].feature_rule_list, linkers)
        return result

    def dispatch(self, linkers: dict[str, LinkerNode], compilers: dict[str, CompilerNode]) -> CompilersOverrideNode:
        result = CompilersOverrideNode()
        result.common_compiler = copy.deepcopy(self.common_compiler)
        for compiler_override_name, compiler_override in self.compiler_overrides.items():
            if compiler_override_name in compilers:
                result.compiler_overrides[compiler_override_name] = compiler_override.merge_with(result.common_compiler, compilers[compiler_override_name].feature_rule_list, linkers)
        return result

def merge_compiler_overrides_node(child: CompilersOverrideNode, parent: CompilersOverrideNode, linkers: dict[str, LinkerNode], compilers: dict[str, CompilerNode] ):
    if child and parent:
        return child.merge_with(parent, linkers, compilers)
    elif child:
        return copy.deepcopy(child)
    elif parent:
        return copy.deepcopy(parent)
    
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
