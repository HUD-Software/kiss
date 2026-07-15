
from __future__ import annotations
import copy
from toolchain.nodes.feature_node import FeatureNode, FeatureNodeList, FeatureRuleNodeList
from toolchain.nodes.linker_nodes import LinkersOverrideNode
from toolchain.nodes.property import Property, PropertyBool, PropertyDict, PropertyStr, PropertyStrList
from typing import TypeVar, Type
T = TypeVar("T", bound=Property)

class CompilerNode(Property):
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
        super().__init__(name)
        self._properties = PropertyDict()
        self.feature_list = FeatureNodeList()
        self.feature_rule_list = FeatureRuleNodeList()
        
    @property
    def properties(self) -> PropertyDict:
        return self._properties
    
    @property
    def supported_linkers(self) -> list[str]:
        prop = self.get_property_as("supported_linkers", PropertyStrList)
        return prop.values if prop else None
    
    @property
    def is_abstract(self) -> bool :
        prop = self.get_property_as("is_abstract", PropertyBool)
        return prop.value if prop else False
    
    @property
    def default_linker_name(self) -> str | None:
        prop = self.get_property_as("default-linker", PropertyStr)
        return prop.value if prop else None
    
    def get_property(self, name: str) -> Property | None:
        return self.properties.get_property(name)
    
    def add_property(self, property):
        self.properties.add_property(property)
    
    def get_property_as(self, name: str, prop_type: Type[T]) -> T | None:
        return self.properties.get_property_as(name, prop_type)

    def merge_with(self, parent: CompilerNode):
        if not parent:
            return copy.deepcopy(self)
        """Merge list without applying modifier or dispatching top to bottom hierarchy """
        assert type(parent) is type(self), "Type mismatch"
        merged = CompilerNode(self.name)
        merged._properties = self.properties.merge_with(parent.properties)
        merged.feature_rule_list = self.feature_rule_list.merge_with(parent.feature_rule_list)
        merged.feature_list = self.feature_list.merge_with(parent.feature_list, merged.feature_rule_list)

        return merged
    
    def apply_modifiers(self) -> CompilerNode:
        """Apply list modifier"""
        applied  = CompilerNode(self.name)
        applied._properties = self.properties.apply_modifiers()
        applied.feature_list = self.feature_list.apply_modifiers()
        applied.feature_rule_list = copy.deepcopy(self.feature_rule_list)
        return applied
        
    def dispatch(self) -> CompilerNode:
        """ 
        Dispatch properties from top to bottom hierarchy
        """
        dispatched = CompilerNode(self.name)
        dispatched._properties = copy.deepcopy(self.properties)
        dispatched.feature_list = self.feature_list.dispatch()
        dispatched.feature_rule_list = copy.deepcopy(self.feature_rule_list)
        return dispatched

class CompilerSpecificOverrideNode(Property):
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
        super().__init__(name)
        self._properties = PropertyDict()
        self.linkers : LinkersOverrideNode = None
        self.feature_list = FeatureNodeList()
        self.feature_rule_list = FeatureRuleNodeList()

    @property
    def properties(self) -> PropertyDict:
        return self._properties
    
    def get_property(self, name: str) -> Property | None:
        return self.properties.get_property(name)
    
    def add_property(self, property):
        self.properties.add_property(property)

    def apply_modifiers(self) -> CompilerSpecificOverrideNode:
        result = CompilerSpecificOverrideNode(self.name)
        result._properties = self.properties.apply_modifiers()
        result.linkers = self.linkers.apply_modifiers() if self.linkers else None
        result.feature_list = self.feature_list.apply_modifiers()
        result.feature_rule_list = self.feature_rule_list.apply_modifiers()
        return result
    
    def merge_with(self, other: CompilerSpecificOverrideNode, parent_list_name_to_ignore: set[str]) -> CompilerSpecificOverrideNode:
        if not other:
            return copy.deepcopy(self)
        assert self.name == other.name, "Name mismatch"
        result = CompilerSpecificOverrideNode(self.name)
        result._properties = self.properties.merge_with(other.properties, parent_list_name_to_ignore)
        result.linkers = self.linkers.merge_with(other.linkers) if self.linkers else None
        result.feature_rule_list = self.feature_rule_list.merge_with(other.feature_rule_list)
        result.feature_list = self.feature_list.merge_with(other.feature_list, result.feature_rule_list)
        return result
    
    def dispatch(self, top : PropertyDict) -> CompilerSpecificOverrideNode:
        result = CompilerSpecificOverrideNode(self.name)
        result._properties = self.properties.dispatch(top)
        result.linkers = self.linkers.dispatch(top) if self.linkers else None
        result.feature_list = self.feature_list.dispatch()
        result.feature_rule_list = self.feature_rule_list.dispatch()
        return result
    
   
class CompilersOverrideNode(Property):
    """Represents the 'compilers:' block.
    Contains global enable-features + per-compiler overrides 'CompilerSpecificOverrideNode' nodes.

    compilers: # CompilersOverrideNode
      gcc : 
        enable-features: []
        defines: []
      ...
    """
    NAME = "compilers"
    def __init__(self, name : str= NAME):
      super().__init__(name)
      self._properties = PropertyDict()
      self._compilers = dict[str, CompilerSpecificOverrideNode]()

    @property
    def properties(self) -> PropertyDict:
        return self._properties

    def get_property(self, name: str) -> Property | None:
        return self.properties.get_property(name)
    
    def add_property(self, property):
        self.properties.add_property(property)
    
    def add_compiler(self, compiler:CompilerSpecificOverrideNode):
        self._compilers[compiler.name] = compiler

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

class CompilerFeatureNode(FeatureNode):

    def __init__(self, name:str):
        super().__init__(name)
        self.linkers : LinkersOverrideNode = None

    def merge_with(self, other: CompilerFeatureNode):
        if not other:
            return copy.deepcopy(self)
        merged = CompilerFeatureNode(self.name)
        merged._properties = self.properties.merge_with(other.properties)
        if other.linkers:
            if self.linkers:
                merged.linkers = self.linkers.merge_with(other.linkers)
            else:
                merged.linkers = copy.deepcopy(other.linkers)
        return merged
    
    def apply_modifiers(self) -> FeatureNodeList:
        result = CompilerFeatureNode(self.name)
        result._properties = self.properties.apply_modifiers()
        if self.linkers:
            result.linkers = self.linkers.apply_modifiers()
        return result

    def dispatch(self) -> CompilerFeatureNode:
        result = CompilerFeatureNode(self.name)
        result._properties = copy.deepcopy(self.properties)
        if self.linkers:
            result.linkers = self.linkers.dispatch(result.properties)
        return result