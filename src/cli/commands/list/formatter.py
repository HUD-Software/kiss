
from wcwidth import wcswidth
from toolchain.nodes.node import PropertyDict, PropertyBool,  PropertyNodeList, PropertyStr, PropertyStrList


# PRIVATE ──────────────────────────────────────────────────────────────────────
def _flatten_block(block: str, indent: str = "") -> list[str]:
    """
    Flatten a multi-line block into a list of indented lines.

    Each line of the input string is prefixed with the given indentation.
    This is used to integrate pre-formatted box strings into a parent layout
    while preserving visual alignment.
    """

    return [(indent + line) for line in block.split("\n")]

def _vis_len(s: str) -> int:
    """
    Return the display width of a string as formatted in a terminal.

    This accounts for Unicode characters that occupy multiple columns
    (e.g. East Asian wide characters, emojis) and combining characters,
    unlike len() which counts code points.

    Uses wcwidth/wcswidth rules for monospace terminal formatting.
    """

    return wcswidth(s)

def _box(title: str, lines: list[str]) -> list[str]:
    """
    format a bordered box around a list of text lines.

    The box width is computed using visual width (_vis_len) to properly
    handle wide Unicode characters (e.g. emojis, CJK characters).

    The title is embedded in the top border.
    Returns the box as a list of lines (not a single string) to allow
    further composition in higher-level layouts.
    """

    content_width = max((_vis_len(line) for line in lines), default=0)

    title = f" {title} "
    top_width = max(content_width, _vis_len(title))

    top = f"╭─{title}" + "─" * (top_width - _vis_len(title) + 1) + "╮"
    bottom = "╰" + "─" * (len(top) - 2) + "╯"

    out = [top]

    for line in lines:
        padding = content_width - _vis_len(line)
        out.append(f"│ {line}{' ' * padding} │")

    out.append(bottom)
    return out

def _inner_box(title: str, lines: list[str]) -> str:
    """
    format a nested (inner) box used for hierarchical compositions.

    Unlike _box, this function returns a single string instead of a list
    of lines, making it suitable for embedding inside another box after
    flattening.

    It is primarily used for recursive node formatting where intermediate
    box structures must be treated as atomic blocks.
    """

    content_width = max((_vis_len(line) for line in lines), default=0)

    title = f"{title} "
    top_width = max(content_width, _vis_len(title)) + 2

    top = f"{title}" + "─" * (top_width - _vis_len(title) + 1) + "╮"
    bottom = "╰" + "─" * (len(top) -2) + "╯"

    out = [top]

    for line in lines:
        padding = content_width - _vis_len(line)
        out.append(f"│ {line}{' ' * padding} │")

    out.append(bottom)
    return "\n".join(out)

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

def _node_to_inner_box(node: PropertyDict, ignore_empty: bool = True):
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

    title = node.name
    lines = []

    leaf_props, node_props = _split_props(node.properties)

    # LEAF PROPERTIES FIRST ─────────────────────────────
    for prop in leaf_props:
        if isinstance(prop, PropertyStr):
            if prop.value or not ignore_empty:
                lines.append(f"{prop.name}: {prop.value!r}")
        elif isinstance(prop, PropertyStrList):
            if prop.values or not ignore_empty:
                lines.append(f"{prop.name}: {prop.values}")
        elif isinstance(prop, PropertyBool):
            if prop.value or not ignore_empty:
                lines.append(f"{prop.name}: {prop.value}")

    # NODE PROPERTIES AFTER ─────────────────────────────
    for prop in node_props:
        if isinstance(prop, PropertyNodeList):
            if prop.nodes or not ignore_empty:
                for child in prop.nodes:
                    child_box = _node_to_inner_box(child, ignore_empty)
                    lines.extend(_flatten_block(child_box))
        elif isinstance(prop, PropertyDict):
            if prop.properties or not ignore_empty:
                child_box = _node_to_inner_box(prop, ignore_empty)
                lines.extend(_flatten_block(child_box))

            # if prop.properties or not ignore_empty:
            #     for _, child in prop.properties.items():
            #         child_box = _node_to_inner_box(child, ignore_empty)
            #         lines.extend(_flatten_block(child_box))
    return _inner_box(title, lines)

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
    lines = []
    
    leaf_props, node_props = _split_props(node.properties)
    
    # LEAF PROPERTIES FIRST ─────────────────────────────
    for prop in leaf_props:
        if isinstance(prop, PropertyStr):
            if prop.value or not ignore_empty:
                lines.append(f"{prop.name}: {prop.value!r}")
        elif isinstance(prop, PropertyStrList):
            if prop.values or not ignore_empty:
                lines.append(f"{prop.name}: {prop.values}")
        elif isinstance(prop, PropertyBool):
            if prop.value or not ignore_empty:
                lines.append(f"{prop.name}: {prop.value}")

    # NODE PROPERTIES AFTER ─────────────────────────────
    for prop in node_props:
        if isinstance(prop, PropertyNodeList):
            if prop.nodes or not ignore_empty:
                inner_lines = []
                for child in prop.nodes:
                    child_box = _node_to_inner_box(child, ignore_empty)
                    inner_lines.extend(_flatten_block(child_box))

                prop_box = _inner_box(prop.name, inner_lines)
                lines.extend(_flatten_block(prop_box))
        elif isinstance(prop, PropertyDict):
            if prop.properties or not ignore_empty:
                child_box = _node_to_inner_box(prop, ignore_empty)
                lines.extend(_flatten_block(child_box))
    return _box(title, lines)

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

