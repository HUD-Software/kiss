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

    def __init__(self, title: str):
        self.title = title
        self.lines = list[str]()
        self.inner_box = list[Box]()
    @staticmethod
    def _title_str(box: Box) -> str:
        return f"{box.title} "
    
    def to_boxed_strings(self) -> list[str]:
        # 1. Render all content lines (inner boxes are fully rendered first)
        content_lines: list[str] = []
        for line in self.lines:
            content_lines.append(line)
        for inner_box in self.inner_box:
            for line in inner_box.to_boxed_strings():
                content_lines.append(line)

        # 2. Compute widths
        title = f"{self.title} "
        inner_width = max((_vis_len(line) for line in content_lines), default=0)
        inner_width = max(inner_width, _vis_len(title))
        box_width = inner_width + _vis_len(Box.TOP_LEFT_ANGLE) + _vis_len(Box.TOP_RIGHT_ANGLE)

        # 3. Build top and bottom borders
        dashes = box_width - _vis_len(title)
        top    = f"{Box.TOP_LEFT_ANGLE}{title}" + "─" * dashes + Box.TOP_RIGHT_ANGLE
        bottom = f"{Box.BOTTOM_LEFT_ANGLE}" + "─" * box_width + Box.BOTTOM_RIGHT_ANGLE

        # 4. Assemble with padding
        out = [top]
        for line in content_lines:
            padding = max(0, inner_width - _vis_len(line))
            out.append(f"{Box.LEFT_BORDER}{line}{' ' * padding}{Box.RIGHT_BORDER}")
        out.append(bottom)
        return out


def _split_props(properties):
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


def _node_to_box(title: str, node, ignore_empty: bool = True) -> Box:
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

    leaf_props, node_props = _split_props(node.properties)

    # LEAF PROPERTIES FIRST ─────────────────────────────
    for prop in leaf_props:
        if isinstance(prop, PropertyStr):
            if prop.value or not ignore_empty:
                box.lines.append(f"{prop.name}: {prop.value!r}")
        elif isinstance(prop, PropertyStrList):
            if prop.values or not ignore_empty:
                box.lines.append(f"{prop.name}: {prop.values}")
        elif isinstance(prop, PropertyBool):
            if prop.value or not ignore_empty:
                box.lines.append(f"{prop.name}: {prop.value}")

    # NODE PROPERTIES AFTER ─────────────────────────────
    for prop in node_props:
        if isinstance(prop, FeatureArgsNode):
            if prop.properties or not ignore_empty:
                child_box = _node_to_box(prop.name, prop,  ignore_empty)
                box.inner_box.append(child_box)
        elif isinstance(prop, LinkersOverrideNode):
            if prop.properties or not ignore_empty:
                child_box = _node_to_box(prop.name, prop,  ignore_empty)
                box.inner_box.append(child_box)
        elif isinstance(prop, LinkerSpecificOverrideNode):
            if prop.properties or not ignore_empty:
                child_box = _node_to_box(prop.name, prop,  ignore_empty)
                box.inner_box.append(child_box)

    # for inner_box in box.inner_box:
    #     box.lines.extend(inner_box.lines)
    return box

# PUBLIC ──────────────────────────────────────────────────────────────────────

def format_node_to_boxed_lines(node, ignore_empty:bool = True, is_default: bool = False) -> list[str]:
    """
    Format a Node into a hierarchical boxed representation.

    This function builds a full visual layout composed of nested ASCII boxes.

    Properties are split into:
    - leaf properties: scalar values formatted directly inside the box
    - node properties: structured values formatted as nested inner boxes

    Node properties are recursively formatted and embedded as boxed blocks,
    ensuring visual hierarchy is preserved in terminal output.
    """

    title = node.name + (" (default)" if is_default else "")
    box = Box(title)

    leaf_props, node_props = _split_props(node.properties)
    
    # LEAF PROPERTIES FIRST ─────────────────────────────
    for prop in leaf_props:
        if isinstance(prop, PropertyStr):
            if prop.value or not ignore_empty:
                box.lines.append(f"{prop.name}: {prop.value!r}")
        elif isinstance(prop, PropertyStrList):
            if prop.values or not ignore_empty:
                box.lines.append(f"{prop.name}: {prop.values}")
        elif isinstance(prop, PropertyBool):
            if prop.value or not ignore_empty:
                box.lines.append(f"{prop.name}: {prop.value}")

    # NODE PROPERTIES AFTER ─────────────────────────────
    for prop in node_props:
        if isinstance(prop,FeatureNodeList):
            if prop.features or not ignore_empty:
                features_box = Box(FeatureNodeList.NAME)
                for feature in prop.features.values():
                    feature_box = _node_to_box(feature.name, feature,  ignore_empty)
                    features_box.inner_box.append(feature_box)
                box.inner_box.append(features_box)
        elif isinstance(prop, FeatureRuleNodeList):
            if prop.feature_rules or not ignore_empty:
                feature_rules_box = Box(FeatureRuleNodeList.NAME)
                for feature_rule in prop.feature_rules.values():
                    feature_rule_box = _node_to_box(feature_rule.name, feature_rule,  ignore_empty)
                    feature_rules_box.inner_box.append(feature_rule_box)
                box.inner_box.append(feature_rules_box)

    # for inner_box in box.inner_box:
    #     line = inner_box.to_boxed_string()
    #     for inner_box in box.inner_box:
    #         box.lines.extend(inner_box)
    #     box.lines.extend()
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

    leaf_props, node_props = _split_props(node.properties)

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

