"""
feature_resolver.py
-------------------
Pass 2 of the resolution pipeline.

Given a compiler (already extends-resolved) and a set of initially
active feature names, this resolver:

1. Expands enable-features cascades
   OPT_LEVEL_0 → enable-features: [DEBUG_INFO]
   → DEBUG_INFO is automatically added

2. Propagates linker features
   A compiler feature can activate linker features via its 'linkers:' block.

3. Applies feature-rules
   - only-one  : among a group, keep only the LAST one added
                 (deepest in the activation chain wins)
   - incompatible : if both feature and any of 'with' are active → error

Raises FeatureConflictError for incompatible violations.
"""


class FeatureConflictError(Exception):
    pass


# ── Feature index ─────────────────────────────────────────────────────────────

def _build_feature_index(compiler: dict) -> dict[str, dict]:
    """Return a dict {feature_name: feature_dict} for all features in compiler."""
    return {f["name"]: f for f in compiler.get("features", [])}


def _build_linker_feature_index(linker: dict) -> dict[str, dict]:
    return {f["name"]: f for f in linker.get("features", [])}


# ── Feature-rules ─────────────────────────────────────────────────────────────

def _collect_rules(compiler: dict) -> list[dict]:
    """Collect all feature-rules from compiler (including inherited ones)."""
    return compiler.get("feature-rules", [])


def _apply_only_one(active: list[str], rules: list[dict]) -> list[str]:
    """
    For each only-one group, keep only the LAST activated feature in the group.
    Others are silently removed.
    """
    result = list(active)
    for rule in rules:
        if "only-one" not in rule:
            continue
        group = rule["features"]
        # Find all active members of this group
        active_in_group = [f for f in result if f in group]
        if len(active_in_group) <= 1:
            continue
        # Keep only the last one (highest priority = last added)
        keep = active_in_group[-1]
        for f in active_in_group:
            if f != keep:
                result.remove(f)
    return result


def _check_incompatible(active: list[str], rules: list[dict], compiler_name: str):
    """
    Raise FeatureConflictError if any incompatible pair is both active.
    """
    active_set = set(active)
    for rule in rules:
        if "incompatible" not in rule:
            continue
        feature = rule["feature"]
        conflicts = rule.get("with", [])
        if feature in active_set:
            for c in conflicts:
                if c in active_set:
                    raise FeatureConflictError(
                        f"incompatible features for compiler '{compiler_name}': "
                        f"'{feature}' is incompatible with '{c}'"
                    )


# ── Cascade expansion ─────────────────────────────────────────────────────────

def _expand_features(
    initial: list[str],
    feature_index: dict[str, dict],
    visited: set[str] | None = None,
) -> list[str]:
    """
    Recursively expand enable-features.
    Returns ordered list with no duplicates (first occurrence wins for order,
    but last activation wins for only-one resolution later).
    """
    if visited is None:
        visited = set()

    result = []
    for name in initial:
        if name in visited:
            continue
        result.append(name)
        visited.add(name)

        feature = feature_index.get(name)
        if feature and feature.get("enable-features"):
            children = _expand_features(
                feature["enable-features"], feature_index, visited
            )
            result.extend(children)

    return result


# ── Linker feature propagation ────────────────────────────────────────────────

def _collect_linker_features_from_compiler(
    active_compiler_features: list[str],
    feature_index: dict[str, dict],
    linker_name: str,
) -> list[str]:
    """
    For each active compiler feature, check if it activates linker features
    via its 'linkers:' block. Respects per-linker overrides.
    """
    linker_features = []
    for fname in active_compiler_features:
        feature = feature_index.get(fname, {})
        linkers_block = feature.get("linkers", {})
        if not linkers_block:
            continue

        # Global linker features (for all linkers)
        for lf in linkers_block.get("enable-features", []):
            if lf not in linker_features:
                linker_features.append(lf)

        # Per-linker override
        per_linker = linkers_block.get(linker_name, {})
        for lf in per_linker.get("enable-features", []):
            if lf not in linker_features:
                linker_features.append(lf)

    return linker_features


# ── Public API ────────────────────────────────────────────────────────────────

def resolve_compiler_features(
    compiler: dict,
    initial_features: list[str],
) -> list[str]:
    """
    Expand + apply only-one rules for compiler features.
    Returns final ordered list of active feature names.
    Does NOT check incompatible yet (done after linker merge).
    """
    feature_index = _build_feature_index(compiler)
    expanded      = _expand_features(initial_features, feature_index)
    rules         = _collect_rules(compiler)
    final         = _apply_only_one(expanded, rules)
    return final


def resolve_linker_features(
    linker: dict,
    initial_features: list[str],
) -> list[str]:
    """
    Expand + apply only-one rules for linker features.
    """
    feature_index = _build_linker_feature_index(linker)
    expanded      = _expand_features(initial_features, feature_index)
    rules         = linker.get("feature-rules", [])
    final         = _apply_only_one(expanded, rules)
    return final


def check_incompatible(compiler: dict, active_features: list[str]):
    """
    Check incompatible rules. Raises FeatureConflictError on violation.
    Call this AFTER all features (compiler + linker propagation) are merged.
    """
    rules = _collect_rules(compiler)
    _check_incompatible(active_features, rules, compiler["name"])


def collect_flags(
    active_features: list[str],
    feature_index: dict[str, dict],
) -> list[str]:
    """Collect all flags from active features, in order."""
    flags = []
    for fname in active_features:
        feature = feature_index.get(fname, {})
        for flag in feature.get("flags", []):
            if flag not in flags:
                flags.append(flag)
    return flags


def collect_linker_features_from_compiler(
    active_compiler_features: list[str],
    compiler: dict,
    linker_name: str,
) -> list[str]:
    """Public wrapper for linker feature propagation from compiler features."""
    feature_index = _build_feature_index(compiler)
    return _collect_linker_features_from_compiler(
        active_compiler_features, feature_index, linker_name
    )
