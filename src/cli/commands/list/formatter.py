from __future__ import annotations
import copy
from wcwidth import wcswidth
from toolchain.nodes.compiler_nodes import CompilerFeatureNode, CompilerNode, CompilerSpecificOverrideNode, CompilersOverrideNode
from toolchain.nodes.feature_node import FeatureArgsNode, FeatureNode, FeatureNodeList, FeatureRuleNode, FeatureRuleNodeList
from toolchain.nodes.linker_nodes import LinkerNode, LinkerSpecificOverrideNode, LinkersOverrideNode
from toolchain.nodes.project_type_nodes import ProjectTypeNode
from toolchain.nodes.property import Property, PropertyDict, PropertyBool,  PropertyNodeList, PropertyStr, PropertyStrList


# PRIVATE ──────────────────────────────────────────────────────────────────────
def _vis_len(s: str) -> int:
    """
    Return the display width of a string as formatted in a terminal.

    This accounts for Unicode characters that occupy multiple columns
    (e.g. East Asian wide characters, emojis) and combining characters,
    unlike len() which counts code points.

    Uses wcwidth/wcswidth rules for monospace terminal formatting.
    """

    return wcswidth(s)

_BOX_CONVERTERS: dict[type, callable] = {}

def register_box(cls):
    def decorator(func):
        _BOX_CONVERTERS[cls] = func
        return func
    return decorator

def to_box(obj, ignore_empty: bool = True):
    obj_type = type(obj)

    if obj_type in _BOX_CONVERTERS:
        return _BOX_CONVERTERS[obj_type](obj, ignore_empty)

    raise TypeError(f"No box converter for {obj_type}")

@register_box(LinkerSpecificOverrideNode)
def _(linker_node: LinkerSpecificOverrideNode, ignore_empty: bool):
    box = Box(linker_node.name)
    for properties in linker_node.properties.values():
        properties.append_to_lines_print(box.lines, ignore_empty)
    return box

@register_box(LinkersOverrideNode)
def _(linkers_node: LinkersOverrideNode, ignore_empty: bool):
    box = Box(LinkersOverrideNode.NAME)
    for properties in linkers_node.properties.values():
        properties.append_to_lines_print(box.lines, ignore_empty)
    for linker in linkers_node._linkers.values():
        linker_box = to_box(linker, ignore_empty)
        box.inner_boxes.append(linker_box)
    return box

@register_box(FeatureNode)
def _(feature_node: FeatureNode, ignore_empty: bool):
    box = Box(feature_node.name)
    for properties in feature_node.properties.values():
        properties.append_to_lines_print(box.lines, ignore_empty)
    return box

@register_box(CompilerFeatureNode)
def _(feature_node: CompilerFeatureNode, ignore_empty: bool):
    box = Box(feature_node.name)
    for properties in feature_node.properties.values():
        properties.append_to_lines_print(box.lines, ignore_empty)
    if feature_node.linkers:
        linkers_box = to_box(feature_node.linkers, ignore_empty)
        box.inner_boxes.append(linkers_box)
    return box

@register_box(FeatureNodeList)
def _(feature_list: FeatureNodeList, ignore_empty: bool):
    box = Box(FeatureNodeList.NAME)
    for feature in feature_list.features.values():
        feature_box = to_box(feature, ignore_empty)
        box.inner_boxes.append(feature_box)
    return box

@register_box(FeatureRuleNode)
def _(feature_rule_node: FeatureRuleNode, ignore_empty: bool):
    box = Box(feature_rule_node.name)
    for properties in feature_rule_node.properties.values():
        properties.append_to_lines_print(box.lines, ignore_empty)
    return box

@register_box(FeatureRuleNodeList)
def _(feature_rule_list: FeatureRuleNodeList, ignore_empty: bool):
    box = Box(FeatureRuleNodeList.NAME)
    for feature_rule in feature_rule_list.feature_rules.values():
        feature_rule_box = to_box(feature_rule, ignore_empty)
        box.inner_boxes.append(feature_rule_box)
    return box

@register_box(CompilerSpecificOverrideNode)
def _(node: CompilerSpecificOverrideNode, ignore_empty: bool):
    box = Box(node.name)
    for properties in node.properties.values():
        properties.append_to_lines_print(box.lines, ignore_empty)
    return box

@register_box(CompilersOverrideNode)
def _(node: CompilersOverrideNode, ignore_empty: bool):
    box = Box(CompilersOverrideNode.NAME)
    for properties in node.properties.values():
        properties.append_to_lines_print(box.lines, ignore_empty)
    for compiler in node._compilers.values():
        compiler_box = to_box(compiler, ignore_empty)
        box.inner_boxes.append(compiler_box)
    return box

@register_box(ProjectTypeNode)
def _(node: ProjectTypeNode, ignore_empty: bool):
    box = Box(node.name)
    for properties in node.properties.values():
        properties.append_to_lines_print(box.lines, ignore_empty)
    compiler_overrides = to_box(node._compilers)
    linker_overrides = to_box(node._linkers)
    box.inner_boxes.append(compiler_overrides)
    box.inner_boxes.append(linker_overrides)
    return box

@register_box(CompilerNode)
def _(node: CompilerNode, ignore_empty: bool):
    box = Box(node.name)
    for prop in node.properties.values():
        prop.append_to_lines_print(box.lines, ignore_empty)
    feature_list_box = to_box(node.feature_list, ignore_empty)
    feature_rule_list_box = to_box(node.feature_rule_list, ignore_empty)
    box.inner_boxes.append(feature_list_box)
    box.inner_boxes.append(feature_rule_list_box)
    return box

@register_box(LinkerNode)
def _(node: LinkerNode, ignore_empty: bool):
    box = Box(node.name)
    for prop in node.properties.values():
        prop.append_to_lines_print(box.lines, ignore_empty)
    feature_list_box = to_box(node.feature_list, ignore_empty)
    feature_rule_list_box = to_box(node.feature_rule_list, ignore_empty)
    box.inner_boxes.append(feature_list_box)
    box.inner_boxes.append(feature_rule_list_box)
    return box

class Box:
    LEFT_BORDER = "│ "
    RIGHT_BORDER = " │"
    TOP_LEFT_ANGLE = "╭"
    TOP_RIGHT_ANGLE = "╮"
    BOTTOM_LEFT_ANGLE = "╰"
    BOTTOM_RIGHT_ANGLE = "╯"
    DASH = "─"

    def __init__(self, title: str):
        self.title = title
        self.lines = list[str]()
        self.inner_boxes = list[Box]()
        
    @staticmethod
    def _title_str(box: Box) -> str:
        return f"{box.title} "
    
    def is_empty(self) -> bool:
        # Empty if no line or not inner box or inner box are all empty 
        return (
        not self.lines
        and all(box.is_empty() for box in self.inner_boxes)
    )
    
    def to_boxed_strings(self) -> list[str]:
        if self.is_empty():
            return []
        
        # 1. Render all content lines (inner boxes are fully rendered first)
        content_lines: list[str] = []
        for line in self.lines:
            content_lines.append(line)
        for inner_boxes in self.inner_boxes:
            for line in inner_boxes.to_boxed_strings():
                content_lines.append(line)

        # 2. Compute widths
        title = f"{self.title} "
        inner_width = max((_vis_len(line) for line in content_lines), default=0)
        inner_width = max(inner_width, _vis_len(title))
        box_width = inner_width + _vis_len(Box.TOP_LEFT_ANGLE) + _vis_len(Box.TOP_RIGHT_ANGLE)

        # 3. Build top and bottom borders
        dashes = box_width - _vis_len(title)
        top    = f"{Box.TOP_LEFT_ANGLE}{title}" + Box.DASH * dashes + Box.TOP_RIGHT_ANGLE
        bottom = f"{Box.BOTTOM_LEFT_ANGLE}" + Box.DASH * box_width + Box.BOTTOM_RIGHT_ANGLE

        # 4. Assemble with padding
        out = [top]
        for line in content_lines:
            padding = max(0, inner_width - _vis_len(line))
            out.append(f"{Box.LEFT_BORDER}{line}{' ' * padding}{Box.RIGHT_BORDER}")
        out.append(bottom)
        return out
    
    @staticmethod
    def properties_to_box(title: str, properties: PropertyDict, ignore_empty: bool = True) -> Box | None:
        """
        Recursively format a Node into a nested inner-box structure.

        Properties are split into:
        - leaf properties: simple scalar values (str, bool, lists)
        - node properties: hierarchical structures requiring recursion

        Leaf properties are formatted first to improve readability, followed
        by nested structures.

        Node-based properties are recursively formatted as inner boxes and
        flattened into the current layout.
        """
        box = Box(title)

        leaf_props, node_props = split_props(properties)

        # LEAF PROPERTIES FIRST ─────────────────────────────
        for prop in leaf_props:
            prop.append_to_lines_print(box.lines, ignore_empty)

        # NODE PROPERTIES AFTER ─────────────────────────────
        for prop in node_props:
            if prop.properties or not ignore_empty:
                if isinstance(prop, CompilerFeatureNode):
                    properties = copy.deepcopy(prop.properties)
                    if prop.linkers:
                        properties.add_property(prop.linkers)
                    child_box = Box.properties_to_box(prop.name, properties, ignore_empty)
                elif isinstance(prop, LinkersOverrideNode):
                    properties = copy.deepcopy(prop.properties)
                    for linker in prop._linkers.values():
                        properties.add_property(linker)
                    child_box = Box.properties_to_box(prop.name, properties, ignore_empty)
                else:
                    child_box = Box.properties_to_box(prop.name, prop.properties, ignore_empty)
                box.inner_boxes.append(child_box)
        return box


def split_props(properties: PropertyDict):
    """
    Split node properties into two categories:

    - leaf properties: simple scalar or flat values (string, bool, lists of strings)
    - node properties: structured values containing nested nodes or dict-like structures

    This separation is used to control format order, ensuring that
    simple properties are displayed before hierarchical / nested properties.
    """

    leaf = []
    nodes = []

    for prop in properties.values():
        if isinstance(prop, (PropertyStr, PropertyStrList, PropertyBool)):
            leaf.append(prop)
        else:
            nodes.append(prop)

    return leaf, nodes

def format_properties_to_boxed_lines(node, ignore_empty:bool = True) -> list[str]:
    """
    Format a Node into a hierarchical boxed representation.

    This function builds a full visual layout composed of nested ASCII boxes.

    Properties are split into:
    - leaf properties: scalar values formatted directly inside the box
    - node properties: structured values formatted as nested inner boxes

    Node properties are recursively formatted and embedded as boxed blocks,
    ensuring visual hierarchy is preserved in terminal output.
    """
    box = to_box(node, ignore_empty)
    return box.to_boxed_strings()


def properties_to_lines(lines: list[str], title: str, properties: PropertyDict, indent: int, ignore_empty:bool = True):
    leaf_props, node_props = split_props(properties)
    
    lines.append(f"{' ' * indent}{title}")
    
    for prop in leaf_props:
        inner_lines = list[str]()
        prop.append_to_lines_print(inner_lines, ignore_empty)
        for inner_line in inner_lines:
            lines.append(f"{' ' * (indent+1)}{inner_line}")
    
    for prop in node_props:
        if prop.properties or not ignore_empty:
            inner_lines = list[str]()
            properties_to_lines(lines=inner_lines, title=prop.name, properties=prop.properties, indent=indent+1, ignore_empty=ignore_empty)
            for inner_line in inner_lines:
                lines.append(inner_line)

def format_properties_to_lines(title: str, properties: PropertyDict, ignore_empty:bool = True) -> list[str]:
    """
    Format a Node into a plain indented tree representation.

    This format is designed for debugging and pipeline-friendly output,
    where structure is represented using indentation instead of boxes.

    Properties are split into:
    - leaf properties: displayed inline under the node header
    - node properties: recursively expanded as nested indented sections

    NodeDict and NodeList are formatted as hierarchical branches.
    """
    lines = list[str]()
    properties_to_lines(lines, title, properties, 0, ignore_empty)
    return lines

def properties_to_json(result: dict, title: str, properties: PropertyDict, ignore_empty:bool = True):
    leaf_props, node_props = split_props(properties)

    result_value = {}
    for prop in leaf_props:
        prop.append_to_json_print(result_value, ignore_empty)

    for prop in node_props:
            if prop.properties or not ignore_empty:
                properties_to_json(result_value, prop.name, prop.properties, ignore_empty)
    result[title] = result_value
    return result

def format_properties_to_json(title: str, properties: PropertyDict, ignore_empty:bool = True) -> dict:
    """
    Format a Node into a JSON-compatible dictionary.

    The resulting structure preserves both:
    - scalar properties (stored directly as key/value pairs)
    - hierarchical properties (stored as nested objects or arrays)

    NodeList becomes JSON arrays, while NodeDict becomes JSON objects.

    This function is intended for machine consumption (serialization,
    tooling, configuration exchange) rather than visual formatting.
    """
    result = {}
    properties_to_json(result, title , properties, ignore_empty)
    return result

