"""
profile_resolver.py
-------------------
Pass 3 (and final) of the resolution pipeline.

Combines:
  target    → global linker features (TARGET_X64 / TARGET_X86)
  profile   → compiler features (global + compiler-specific)
            → linker features   (global + linker-specific)
            → project overrides (per project-type)
  project   → project-type compiler/linker features
  compiler  → feature cascade expansion + only-one resolution
  linker    → feature cascade expansion + only-one resolution

Then checks incompatible rules and collects the final flags.

Entry point: resolve(...)
"""

from resolver.extends_resolver import resolve_extends
from resolver.feature_resolver import (
    resolve_compiler_features,
    resolve_linker_features,
    check_incompatible,
    collect_flags,
    collect_linker_features_from_compiler,
    FeatureConflictError,
)
from resolver.resolved import ResolvedFlags


# ── Helpers ───────────────────────────────────────────────────────────────────

def _find(nodes: list[dict], name: str) -> dict | None:
    return next((n for n in nodes if n["name"] == name), None)


def _merge_features(*feature_lists) -> list[str]:
    """Merge multiple feature lists, preserving order, no duplicates."""
    seen = []
    for lst in feature_lists:
        for f in (lst or []):
            if f not in seen:
                seen.append(f)
    return seen


def _collect_defines(*define_lists) -> list[str]:
    seen = []
    for lst in define_lists:
        for d in (lst or []):
            if d not in seen:
                seen.append(d)
    return seen


# ── Feature collection per layer ──────────────────────────────────────────────

def _features_from_profile_compilers(profile: dict, compiler_name: str, compiler_abstract: str) -> tuple[list, list]:
    """
    Extract compiler features and defines from profile.compilers block.
    Returns (features, defines).
    Merges: global + compiler-specific (by name and by abstract parent).
    """
    block = profile.get("compilers", {})
    features = list(block.get("enable-features", []))
    defines  = list(block.get("defines", []))

    # compiler-specific override (match by compiler name or abstract parent)
    for key in (compiler_name, compiler_abstract):
        if key and key in block and isinstance(block[key], dict):
            features = _merge_features(features, block[key].get("enable-features", []))
            defines  = _collect_defines(defines, block[key].get("defines", []))

    return features, defines


def _features_from_profile_linkers(profile: dict, linker_name: str, linker_abstract: str) -> list[str]:
    """Extract linker features from profile.linkers block."""
    block = profile.get("linkers", {})
    features = list(block.get("enable-features", []))

    for key in (linker_name, linker_abstract):
        if key and key in block and isinstance(block[key], dict):
            features = _merge_features(features, block[key].get("enable-features", []))

    return features


def _features_from_profile_project(
    profile: dict,
    project_type: str,
    compiler_name: str,
    compiler_abstract: str,
    linker_name: str,
) -> tuple[list, list, list]:
    """
    Extract compiler features, defines and linker features
    from profile.project-types.<project_type> block.
    Returns (compiler_features, defines, linker_features).
    """
    projects_block = profile.get("project-types", {})
    proj_block = projects_block.get(project_type, {})
    if not proj_block:
        return [], [], []

    # compiler side
    comp_block = proj_block.get("compilers", {})
    c_features = list(comp_block.get("enable-features", []))
    c_defines  = list(comp_block.get("defines", []))
    for key in (compiler_name, compiler_abstract):
        if key and key in comp_block and isinstance(comp_block[key], dict):
            c_features = _merge_features(c_features, comp_block[key].get("enable-features", []))
            c_defines  = _collect_defines(c_defines, comp_block[key].get("defines", []))

    # linker side
    link_block = proj_block.get("linkers", {})
    l_features = list(link_block.get("enable-features", []))
    for key in (linker_name,):
        if key and key in link_block and isinstance(link_block[key], dict):
            l_features = _merge_features(l_features, link_block[key].get("enable-features", []))

    return c_features, c_defines, l_features


def _features_from_project_type(project_type_def: dict, compiler_name: str, linker_name: str) -> tuple[list, list, list]:
    """
    Extract compiler features, defines and linker features from project-types.yaml definition.
    Returns (compiler_features, defines, linker_features).
    """
    if not project_type_def:
        return [], [], []

    comp_block = project_type_def.get("compilers", {})
    c_features = list(comp_block.get("enable-features", []))
    c_defines  = list(comp_block.get("defines", []))

    link_block = project_type_def.get("linkers", {})
    l_features = list(link_block.get("enable-features", []))

    return c_features, c_defines, l_features


def _features_from_target(target: dict, linker_name: str) -> list[str]:
    """Extract linker features from targets.yaml (e.g. TARGET_X64)."""
    block = target.get("linkers", {})
    return list(block.get("enable-features", []))


def _target_compiler_feature_overrides(
    target: dict,
    compiler_name: str,
    active_compiler_features: list[str],
) -> list[str]:
    """
    Apply per-compiler feature overrides defined in targets.yaml.
    e.g. i686 target overrides ASAN feature for clangcl to add LINK:msvcrt.lib
    Returns additional linker features to activate.
    """
    comp_overrides = target.get("compilers", {})
    compiler_block = comp_overrides.get(compiler_name, {})
    if not compiler_block:
        return []

    extra_linker = []
    for feat_override in compiler_block.get("features", []):
        if feat_override["name"] in active_compiler_features:
            linkers_block = feat_override.get("linkers", {})
            extra_linker.extend(linkers_block.get("enable-features", []))

    return extra_linker


# ── Abstract parent lookup ────────────────────────────────────────────────────

def _abstract_parent(node: dict, all_nodes: list[dict]) -> str | None:
    """
    Return the name of the first abstract ancestor of a node.
    Used to match compiler/linker-specific blocks in profiles.
    e.g. cl → msvc-compiler, lld-link → msvc-linker
    """
    extends = node.get("extends")
    if not extends:
        return None
    parent = _find(all_nodes, extends)
    if not parent:
        return None
    if parent.get("is_abstract"):
        return parent["name"]
    return _abstract_parent(parent, all_nodes)


# ── Main entry point ──────────────────────────────────────────────────────────

def resolve(
    project:      dict,
    profile_name: str,
    compiler_name: str,
    target_name:  str,
    # Resolved (extends-merged) data
    compilers:    list[dict],
    linkers:      list[dict],
    profiles:     list[dict],
    project_types: list[dict],
    targets:      list[dict],
) -> ResolvedFlags:
    """
    Full resolution pipeline for one project.

    Returns a ResolvedFlags with all compiler/linker flags ready for the generator.
    """

    project_type = project.get("_type", "bin")

    # ── 1. Find nodes ─────────────────────────────────────────────────────────
    compiler = _find(compilers, compiler_name)
    if not compiler:
        raise ValueError(f"Compiler '{compiler_name}' not found")

    linker_name = compiler.get("default-linker", "link")
    linker = _find(linkers, linker_name)
    if not linker:
        raise ValueError(f"Linker '{linker_name}' not found")

    profile = _find(profiles, profile_name)
    if not profile:
        raise ValueError(f"Profile '{profile_name}' not found")

    target = _find(targets, target_name)
    if not target:
        raise ValueError(f"Target '{target_name}' not found")

    project_type_def = _find(project_types, project_type) or {}

    # Abstract parents (for profile compiler/linker block matching)
    compiler_abstract = _abstract_parent(compiler, compilers)
    linker_abstract   = _abstract_parent(linker, linkers)

    # ── 2. Collect raw feature lists (ordered by priority, lowest last) ───────

    # Compiler features
    pf_comp, pf_defines   = _features_from_profile_compilers(profile, compiler_name, compiler_abstract)
    pp_comp, pp_def, pp_link = _features_from_profile_project(profile, project_type, compiler_name, compiler_abstract, linker_name)
    pt_comp, pt_def, pt_link = _features_from_project_type(project_type_def, compiler_name, linker_name)

    raw_compiler_features = _merge_features(pf_comp, pt_comp, pp_comp)
    raw_defines           = _collect_defines(pf_defines, pt_def, pp_def)

    # Linker features
    tgt_link  = _features_from_target(target, linker_name)
    pf_link   = _features_from_profile_linkers(profile, linker_name, linker_abstract)

    raw_linker_features = _merge_features(tgt_link, pf_link, pt_link, pp_link)

    # ── 3. Expand compiler features (cascade + only-one) ─────────────────────
    active_compiler = resolve_compiler_features(compiler, raw_compiler_features)

    # ── 4. Propagate linker features triggered by compiler features ───────────
    propagated_linker = collect_linker_features_from_compiler(
        active_compiler, compiler, linker_name
    )

    # ── 5. Apply target-level compiler overrides (e.g. i686 + ASAN + clangcl) -
    target_extra_linker = _target_compiler_feature_overrides(
        target, compiler_name, active_compiler
    )

    # ── 6. Expand linker features (cascade + only-one) ────────────────────────
    all_raw_linker = _merge_features(
        raw_linker_features, propagated_linker, target_extra_linker
    )
    active_linker = resolve_linker_features(linker, all_raw_linker)

    # ── 7. Check incompatible rules ───────────────────────────────────────────
    check_incompatible(compiler, active_compiler)

    # ── 8. Collect flags ──────────────────────────────────────────────────────
    compiler_feature_index = {f["name"]: f for f in compiler.get("features", [])}
    linker_feature_index   = {f["name"]: f for f in linker.get("features", [])}

    compiler_flags = collect_flags(active_compiler, compiler_feature_index)
    linker_flags   = collect_flags(active_linker,   linker_feature_index)

    return ResolvedFlags(
        project_name             = project["name"],
        project_type             = project_type,
        profile                  = profile_name,
        compiler                 = compiler_name,
        linker                   = linker_name,
        compiler_flags           = compiler_flags,
        defines                  = raw_defines,
        linker_flags             = linker_flags,
        active_compiler_features = active_compiler,
        active_linker_features   = active_linker,
    )
