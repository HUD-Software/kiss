from __future__ import annotations
from wcwidth import wcswidth
from toolchain.nodes.feature_node import FeatureArgsNode, FeatureNodeList, FeatureRuleNodeList
from toolchain.nodes.linker_nodes import LinkerSpecificOverrideNode, LinkersOverrideNode
from toolchain.nodes.property import PropertyDict, PropertyBool,  PropertyNodeList, PropertyStr, PropertyStrList


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
    def properties_to_box(title: str, properties, ignore_empty: bool = True) -> Box | None:
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
            prop.append_to_boxed_print(box, ignore_empty)

        # NODE PROPERTIES AFTER ─────────────────────────────
        for prop in node_props:
            if prop.properties or not ignore_empty:
                child_box = Box.properties_to_box(prop.name, prop.properties,  ignore_empty)
                box.inner_boxes.append(child_box)
        return box

def split_props(properties):
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

def format_node_to_boxed_lines(title, properties, ignore_empty:bool = True, is_default: bool = False) -> list[str]:
    """
    Format a Node into a hierarchical boxed representation.

    This function builds a full visual layout composed of nested ASCII boxes.

    Properties are split into:
    - leaf properties: scalar values formatted directly inside the box
    - node properties: structured values formatted as nested inner boxes

    Node properties are recursively formatted and embedded as boxed blocks,
    ensuring visual hierarchy is preserved in terminal output.
    """

    title = title + (" (default)" if is_default else "")
    box = Box.properties_to_box(title, properties, ignore_empty)
    return box.to_boxed_strings()

def format_node_to_lines(node: PropertyDict, ignore_empty:bool = True, indent: int = 0) -> list[str]:
    """
    Format a Node into a plain indented tree representation.

    This format is designed for debugging and pipeline-friendly output,
    where structure is represented using indentation instead of boxes.

    Properties are split into:
    - leaf properties: displayed inline under the node header
    - node properties: recursively expanded as nested indented sections

    NodeDict and NodeList are formatted as hierarchical branches.
    """
     
    prefix = "  " * indent
    lines = []

    leaf_props, node_props = split_props(node.properties)

    #  NODE HEADER ─────────────────────────────
    lines.append(f"{prefix}{node.name}")

    # LEAF PROPS FIRST ─────────────────────────
    for prop in leaf_props:
        if isinstance(prop, PropertyStr):
            if prop.value or not ignore_empty:
                lines.append(f"{prefix}  {prop.name}: {prop.value!r}")
        elif isinstance(prop, PropertyStrList):
            if prop.values or not ignore_empty:
                lines.append(f"{prefix}  {prop.name}: {prop.values}")
        elif isinstance(prop, PropertyBool):
            if prop.value or not ignore_empty:
                lines.append(f"{prefix}  {prop.name}: {prop.value}")

    # NODE PROPS AFTER ────────────────────────
    for prop in node_props:
        if isinstance(prop, PropertyNodeList):
            if prop.nodes or not ignore_empty:
                lines.append(f"{prefix}  {prop.name}:")

                for child in prop.nodes:
                    lines.extend(format_node_to_lines(child, ignore_empty, indent + 2))
        elif isinstance(prop, PropertyDict):
            if prop.properties or not ignore_empty:
                lines.append(f"{prefix}  {prop.name}:")

                for key, child in prop.properties.items():
                    lines.append(f"{prefix}    {key}:")
                    lines.extend(format_node_to_lines(child, ignore_empty, indent + 3))

    return lines

def format_node_to_json(node: PropertyDict, ignore_empty:bool = True) -> dict:
    """
    Format a Node into a JSON-compatible dictionary.

    The resulting structure preserves both:
    - scalar properties (stored directly as key/value pairs)
    - hierarchical properties (stored as nested objects or arrays)

    NodeList becomes JSON arrays, while NodeDict becomes JSON objects.

    This function is intended for machine consumption (serialization,
    tooling, configuration exchange) rather than visual formatting.
    """
    result = {
        "name": node.name,
    }

    for prop_name, prop in node.properties.items():
        if isinstance(prop, PropertyStr):
            if prop.value or not ignore_empty:
                result[prop_name] = prop.value
        elif isinstance(prop, PropertyStrList):
            if prop.values or not ignore_empty:
                result[prop_name] = prop.values
        elif isinstance(prop, PropertyBool):
            if prop.value or not ignore_empty:
                result[prop_name] = prop.value
        elif isinstance(prop, PropertyNodeList):
            if prop.nodes or not ignore_empty:
                result[prop_name] = []
                for node in prop.nodes:
                    result[prop_name].append(format_node_to_json(node))
        elif isinstance(prop, PropertyDict):
            if prop.properties or not ignore_empty:
                result[prop_name] = {}
                for node_name, node in prop.properties.items():
                    result[prop_name][node_name] = format_node_to_json(node)

    return result

