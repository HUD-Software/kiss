"""
context.py
----------
Global Kiss context loaded once from --directory.
Holds all parsed toolchain data + kiss.yaml content.
Passed to every command via typer's context mechanism.
"""

import yaml
from dataclasses import dataclass, field
from pathlib import Path
from resolver.extends_resolver import resolve_extends


def _load_yaml(path: str) -> list[dict]:
    with open(path) as f:
        data = yaml.safe_load(f) or {}
    return list(data.values())[0] if data else []


@dataclass
class KissContext:
    directory:     Path
    kiss_data:     dict        = field(default_factory=dict)
    compilers:     list[dict]  = field(default_factory=list)
    linkers:       list[dict]  = field(default_factory=list)
    profiles:      list[dict]  = field(default_factory=list)
    project_types: list[dict]  = field(default_factory=list)
    targets:       list[dict]  = field(default_factory=list)

    # ── helpers ───────────────────────────────────────────────────────

    def has_kiss_yaml(self) -> bool:
        return bool(self.kiss_data)

    # ── Projects ───────────────────────────────────────────────────────

    def known_project(self) -> list[str]:
        """All project names declared in kiss.yaml."""
        return self.kiss_data.get("projects", [])
        
    def project_names(self) -> list[str]:
        """All project names declared in kiss.yaml."""
        names = []
        for ptype in self.known_project_types():
            for entry in self.kiss_data.get(ptype, []):
                names.append(entry["name"])
        return names

    def get_project(self, name: str | None) -> dict:
        """
        Resolve project by name (or auto-select if only one).
        Returns the project dict with '_type' injected.
        """
        import typer
        all_projects = self._all_projects()

        if name:
            matches = [p for p in all_projects if p["name"] == name]
            if not matches:
                typer.echo(f"error: project '{name}' not found. Available: {self.project_names()}", err=True)
                raise typer.Exit(1)
            return matches[0]

        if len(all_projects) == 1:
            return all_projects[0]

        if not all_projects:
            typer.echo("error: no projects defined in kiss.yaml", err=True)
            raise typer.Exit(1)

        names = ", ".join(p["name"] for p in all_projects)
        typer.echo(f"error: multiple projects found, specify one: {names}", err=True)
        raise typer.Exit(1)

    def known_project_types(self) -> list[str]:
        """Built-in + custom project types from projects.yaml + kiss.yaml."""
        builtin = [p["name"] for p in self.project_types]
        custom  = [p["name"] for p in self.kiss_data.get("projects", [])]
        return list(dict.fromkeys(builtin + custom))  # deduplicated, ordered

    # ── Targets ───────────────────────────────────────────────────────


    def target_names(self) -> list[str]:
        return [t["name"] for t in self.targets]
    
    def known_targets(self) -> list[dict]:
        return [t for t in self.targets]
       
    def default_target(self) -> dict | None:
        return self.targets[0] if self.targets else None
    
   
    
    # ── Profiles ───────────────────────────────────────────────────────    

    def profile_names(self) -> list[str]:
        return [p["name"] for p in self.profiles if not p.get("is_abstract")]

    def known_profiles(self) -> list[dict]:
        return [p for p in self.profiles if not p.get("is_abstract")]
    
    def default_profile(self) -> dict | None:
        return next((p for p in self.profiles if p.get("is_default")), None)
    
    # ── Compilers ───────────────────────────────────────────────────────

    def compiler_names(self) -> list[str]:
        return [c["name"] for c in self.compilers if not c.get("is_abstract")]

    def known_compilers(self) -> list[dict]:
        return [c for c in self.compilers if not c.get("is_abstract")]
    
    def default_compiler(self, target_name: str) -> str | None:
        target = next((t for t in self.targets if t["name"] == target_name), None)
        if not target:
            return None
        return target.get("default-compiler") or (
            target.get("supported-compilers", [None])[0]
        )

    # ── Linkers ───────────────────────────────────────────────────────
    
    def linker_names(self) -> list[str]:
        return [l["name"] for l in self.linkers if not l.get("is_abstract")]
    
    def known_linkers(self) -> list[dict]:
        return [l for l in self.linkers if not l.get("is_abstract")]
    
    def default_linker(self, target_name: str) -> dict | None:
       default_compiler = self.default_compiler(target_name)
       if not default_compiler:
           return None
       compiler = next((c for c in self.compilers if c["name"] == default_compiler), None)
       if not compiler:
           return None
       default_linker_name = compiler.get("default-linker")
       if not default_linker_name:
           return None
       return next((l for l in self.linkers if l["name"] ==  default_linker_name), None)
    
    # ── Private ───────────────────────────────────────────────────────────────

    def _all_projects(self) -> list[dict]:
        projects = []
        for ptype in self.known_project_types():
            for entry in self.kiss_data.get(ptype, []):
                projects.append({**entry, "_type": ptype})
        return projects


# ── Loader ────────────────────────────────────────────────────────────────────

def load_context(directory: str) -> KissContext:
    """
    Load all toolchain YAML files + kiss.yaml from directory.
    kiss.yaml is optional (needed only for build/run/generate).
    """
    project_dir = Path(directory).resolve()

    # Locate data/ directory relative to this file (src/context.py → data/)
    src_dir  = Path(__file__).parent
    data_dir = src_dir.parent / "data"

    compilers     = resolve_extends(_load_yaml(str(data_dir / "compilers.yaml")))
    linkers       = resolve_extends(_load_yaml(str(data_dir / "linkers.yaml")))
    project_types = _load_yaml(str(data_dir / "projects.yaml"))
    targets       = _load_yaml(str(data_dir / "targets.yaml"))

    # Load kiss.yaml if present
    kiss_yaml = project_dir / "kiss.yaml"
    kiss_data: dict = {}
    if kiss_yaml.exists():
        with open(kiss_yaml) as f:
            kiss_data = yaml.safe_load(f) or {}

    # Merge profiles: built-in + custom from kiss.yaml
    profiles = resolve_extends(_load_yaml(str(data_dir / "profiles.yaml")))
    for p in kiss_data.get("profiles", []):
        profiles.append(p)
    if kiss_data.get("profiles"):
        profiles = resolve_extends(profiles)

    # Merge project types: built-in + custom from kiss.yaml
    for pt in kiss_data.get("projects", []):
        project_types.append(pt)

    return KissContext(
        directory     = project_dir,
        kiss_data     = kiss_data,
        compilers     = compilers,
        linkers       = linkers,
        profiles      = profiles,
        project_types = project_types,
        targets       = targets,
    )
