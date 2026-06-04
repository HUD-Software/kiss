"""
resolver/__init__.py
Public API for the resolution pipeline.
"""

import os
import yaml

from resolver.extends_resolver import resolve_extends
from resolver.profile_resolver import resolve
from resolver.resolved import ResolvedFlags


def _load_yaml(path: str) -> list[dict]:
    with open(path, encoding="utf-8") as f:
        data = yaml.safe_load(f) or {}
    return list(data.values())[0] if data else []


def _load_all(data_dir: str, kiss_data: dict | None = None) -> dict:
    compilers     = resolve_extends(_load_yaml(os.path.join(data_dir, "compilers.yaml")))
    linkers       = resolve_extends(_load_yaml(os.path.join(data_dir, "linkers.yaml")))
    profiles      = resolve_extends(_load_yaml(os.path.join(data_dir, "profiles.yaml")))
    project_types = _load_yaml(os.path.join(data_dir, "projects.yaml"))
    targets       = _load_yaml(os.path.join(data_dir, "targets.yaml"))

    if kiss_data:
        for p in kiss_data.get("profiles", []):
            profiles.append(p)
        profiles = resolve_extends(profiles)
        for pt in kiss_data.get("projects", []):
            project_types.append(pt)

    return dict(
        compilers=compilers,
        linkers=linkers,
        profiles=profiles,
        project_types=project_types,
        targets=targets,
    )


def resolve_project(
    project:       dict,
    profile_name:  str,
    compiler_name: str,
    target_name:   str,
    data_dir:      str,
    kiss_data:     dict | None = None,
) -> ResolvedFlags:
    toolchain = _load_all(data_dir, kiss_data)
    return resolve(
        project        = project,
        profile_name   = profile_name,
        compiler_name  = compiler_name,
        target_name    = target_name,
        **toolchain,
    )
