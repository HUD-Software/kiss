
from __future__ import annotations
import copy
from result import Result, Ok, Err
from toolchain.nodes.feature_node import FeatureArgsNode, FeatureNode, FeatureNodeList, FeatureRuleNodeList, FeatureStrList, ValidationError
from toolchain.nodes.linker_nodes import LinkerNode, LinkersOverrideNode
from toolchain.nodes.property import StrList

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
        self.supported_linkers = StrList()
        self.default_linker = None
        self.feature_list = CompilerFeatureNodeList()
        self.feature_rule_list = FeatureRuleNodeList()
    
    def __eq__(self, other):
        if not isinstance(other, CompilerNode):
            return NotImplemented
        return self.name == other.name

    def __hash__(self):
        return hash(self.name)

    def resolve_extends(self, parent: CompilerNode, linkers: dict[str, LinkerNode]) -> Result[CompilerNode, ValidationError]:
        result = CompilerNode(self.name)
        result.is_abstract = self.is_abstract
        result.extends = self.extends   
        result.supported_linkers = self.supported_linkers
        result.default_linker = self.default_linker

        if not parent:
            result.feature_rule_list = self.feature_rule_list.resolve_extends(FeatureRuleNodeList())
            match self.feature_list.resolve_extends(FeatureNodeList(), linkers, result.feature_rule_list):
                case Err() as err:
                    return err
                case Ok(feature_list):
                    result.feature_list = feature_list
        else:
            result.feature_rule_list = self.feature_rule_list.resolve_extends(parent.feature_rule_list)
            match self.feature_list.resolve_extends(parent.feature_list, result.feature_rule_list):
                case Err() as err:
                    return err
                case Ok(feature_list):
                    result.feature_list = feature_list
        return Ok(result)
    
    # def merge_with(self, parent: CompilerNode):
    #     if not parent:
    #         return copy.deepcopy(self)
    #     """Merge list without applying modifier or dispatching top to bottom hierarchy """
    #     assert type(parent) is type(self), "Type mismatch"
    #     result = CompilerNode(self.name)
    #     result.is_abstract = self.is_abstract
    #     result.extends = self.extends
    #     result.supported_linkers = self.supported_linkers + parent.supported_linkers
    #     result.default_linker = self.default_linker
    #     # Apply modifier during merge before merging the feature list
    #     # We want to merge feature list according the rules, we must merge feature rule with parent 
    #     # but also resolve modifier to validate
    #     result.feature_rule_list = self.feature_rule_list.merge_with(parent.feature_rule_list).apply_modifiers()
    #     result.feature_list = self.feature_list.merge_with(parent.feature_list, result.feature_rule_list)
    #     return result
    
    # def apply_modifiers(self) -> CompilerNode:
    #     """Apply list modifier"""
    #     result  = CompilerNode(self.name)
    #     result.is_abstract = self.is_abstract
    #     result.extends = self.extends
    #     result.supported_linkers = self.supported_linkers.copy()
    #     result.default_linker = self.default_linker
    #     result.feature_rule_list = self.feature_rule_list.apply_modifiers()
    #     result.feature_list = self.feature_list.apply_modifiers(result.feature_rule_list)
    #     return result
        
    # def dispatch(self) -> CompilerNode:
    #     """ 
    #     Dispatch properties from top to bottom hierarchy
    #     """
    #     result = CompilerNode(self.name)
    #     result.is_abstract = self.is_abstract
    #     result.extends = self.extends
    #     result.supported_linkers = self.supported_linkers.copy()
    #     result.default_linker = self.default_linker
    #     result.feature_rule_list = copy.deepcopy(self.feature_rule_list)
    #     result.feature_list = copy.deepcopy(self.feature_list)
    #     return result

    # def resolve_extends(self, parent: CompilerNode) -> CompilerNode:
    #     if parent:
    #         assert parent.name == self.extends
    #         node = self.merge_with(parent)
    #     else:
    #         node = copy.deepcopy(self)
    #     node = node.dispatch()
    #     node = node.apply_modifiers()
    #     return node

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
       
    # def apply_modifiers(self, compiler_feature_rules: FeatureRuleNodeList, linkers : dict[str, LinkerNode]) -> CompilerSpecificOverrideNode:
    #     result = CompilerSpecificOverrideNode(self.name)
    #     result.linker_overrides = self.linker_overrides.apply_modifiers(linkers) if self.linker_overrides else None
    #     result.flags = self.flags.apply_modifiers()
    #     result.features = self.features.apply_modifiers(compiler_feature_rules)
    #     result.defines = self.defines.apply_modifiers()
    #     return result
    
    # def merge_with(self, parent: CompilerSpecificOverrideNode, compiler_feature_rules: FeatureRuleNodeList, linkers : dict[str, LinkerNode]) -> CompilerSpecificOverrideNode:
    #     result = CompilerSpecificOverrideNode(self.name)
    #     result.flags = merge_str_list(parent.flags, self.flags)
    #     result.defines = merge_str_list(parent.defines, self.defines)
    #     result.features = merge_feature_list(parent.features, self.features, compiler_feature_rules)
    #     result.linker_overrides = merge_linkers_override_node(self.linker_overrides, parent.linker_overrides, linkers)
    #     return result
                
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

    def resolve_extends(self, parent: CompilerFeatureNodeList, linkers: dict[str, LinkerNode], feature_rules: FeatureRuleNodeList) -> Result[CompilerFeatureNodeList, ValidationError]:
        result = CompilerFeatureNodeList()
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
                match self_feature.resolve_extends(parent_feature, linkers, feature_rules):
                    case Err() as err:
                        return err
                    case Ok(feature):
                       result.add_feature(feature)

            elif parent_feature:
                # In the case the feature exist only in child
                # We create a new FeatureNode with the same name and description as the parent feature
                # Then we resolve the extends with the parent feature
                # This is to ensure that the child feature inherits the name and description from the parent feature
                # keeping same behavior as before, but without marking flags and features as override if not present in the childn the child
                self_feature = CompilerFeatureNode(parent_feature.name)
                self_feature.description = parent_feature.description
                match self_feature.resolve_extends(parent_feature, linkers, feature_rules):
                    case Err() as err:
                        return err
                    case Ok(feature):
                        result.add_feature(feature)
        return Ok(result)
    

class CompilerFeatureNode:
    def __init__(self, name: str):
        self.feature_node = FeatureNode(name)
        self.linkers = LinkersOverrideNode()

    # --- Accesseurs délégués à FeatureNode ---
    @property
    def name(self) -> str:
        return self.feature_node.name

    @name.setter
    def name(self, value: str) -> None:
        self.feature_node.name = value

    @property
    def description(self) -> str:
        return self.feature_node.description

    @description.setter
    def description(self, value: str) -> None:
        self.feature_node.description = value

    @property
    def flags(self) -> StrList:
        return self.feature_node.flags

    @flags.setter
    def flags(self, value: StrList) -> None:
        self.feature_node.flags = value

    @property
    def features(self) -> FeatureStrList:
        return self.feature_node.features

    @features.setter
    def features(self, value: FeatureStrList) -> None:
        self.feature_node.features = value

    @property
    def args(self) -> FeatureArgsNode | None:
        return self.feature_node.args

    @args.setter
    def args(self, value: FeatureArgsNode | None) -> None:
        self.feature_node.args = value

    def resolve_extends(
        self,
        parent: "CompilerFeatureNode | None",
        linkers : dict[str, LinkerNode],
        feature_rules: FeatureRuleNodeList,
    ) -> Result["CompilerFeatureNode", ValidationError]:
        parent_feature = parent.feature_node if parent is not None else None
        match self.feature_node.resolve_extends(parent_feature, feature_rules):
            case Err() as err:
                return err
            case Ok(resolved_feature):
                pass

        parent_linkers = parent.linkers if parent is not None else None
        match self.linkers.resolve_extends(parent_linkers, linkers): 
            case Err() as err:
                return err
            case Ok(resolved_linkers):
                pass

        result = CompilerFeatureNode(self.name)
        result.feature_node = resolved_feature
        result.linkers = resolved_linkers
        return Ok(result)