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
from toolchain.nodes.compiler_nodes import CompilerNode
from toolchain.nodes.linker_nodes import LinkerNode
from toolchain.nodes.profile_nodes import ProfileNode
from toolchain.nodes.project_type_nodes import ProjectTypeNode
from toolchain.nodes.target_nodes import TargetNode
from toolchain.parsers.compiler_parser import load_compilers
from toolchain.parsers.linker_parser   import load_linkers
from toolchain.parsers.profile_parser  import load_profiles, yaml_parse_profile
from toolchain.parsers.project_type_parser  import load_project_types, yaml_parse_project_type
from toolchain.parsers.target_parser   import load_targets
from resolver.extends_resolver         import resolve_extends

@dataclass
class KissContext:
    directory:     Path
    kiss_data:     dict        = field(default_factory=dict)
    compilers:     dict[str, CompilerNode]  = field(default_factory=dict)
    linkers:       dict[str, LinkerNode]  = field(default_factory=dict)
    profiles:      dict[str, ProfileNode]  = field(default_factory=dict)
    project_types: dict[str, ProjectTypeNode]  = field(default_factory=dict)
    targets:       dict[str, TargetNode]  = field(default_factory=dict)

    # ── helpers ───────────────────────────────────────────────────────

    def has_kiss_yaml(self) -> bool:
        return bool(self.kiss_data)

    # ── Projects ───────────────────────────────────────────────────────

    def known_project(self) -> list[str]:
        """All project names declared in kiss.yaml."""
        return self.kiss_data.get("project-types", [])
        
    def project_names(self) -> list[str]:
        """All project names declared in kiss.yaml."""
        names = []
        for ptype in self.known_project_types():
            for entry in self.kiss_data.get(ptype.name, []):
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

    def known_project_types(self) -> list[ProjectTypeNode]:
        return [t for t in self.project_types.values()]

    # ── Targets ───────────────────────────────────────────────────────


    def target_names(self) -> list[str]:
        return [t.name for t in self.targets]
    
    def known_targets(self) -> list[TargetNode]:
        return [t for t in self.targets]
       
    def default_target(self) -> TargetNode | None:
        return next(iter(self.targets.values()), None)
    
    def get_target(self, name: str) -> TargetNode | None:
        return next((t for t in self.targets.values() if t.name == name), None)
    
    # ── Profiles ───────────────────────────────────────────────────────    

    def profile_names(self) -> list[str]:
        return [p.name for p in self.known_profiles()]

    def known_profiles(self) -> list[ProfileNode]:    
        return [p for p in self.profiles.values() if not p.is_abstract]
    
    def default_profile(self) -> ProfileNode | None:
        return next((p for p in self.profiles.values() if p.name == "debug"), None)
    
    def get_profile(self, name: str) -> ProfileNode | None:
        return next((p for p in self.profiles.values() if p.name == name), None)
    
    # ── Compilers ───────────────────────────────────────────────────────

    def compiler_names(self) -> list[str]:
        return [c.name for c in self.known_compilers()]

    def known_compilers(self, ignore_abstract: bool = False) -> list[CompilerNode]:
        return [ c for c in self.compilers.values() if not (c.is_abstract and ignore_abstract)]
    
    def default_compiler(self, target_name: str) -> CompilerNode | None:
        target = next((t for t in self.targets.values() if t.name == target_name), None)
        if not target:
            return None
        return target.default_compiler_name

    def get_compiler(self, name: str) -> CompilerNode | None:
        return next((c for c in self.compilers.values() if c.name == name), None)
    
    # ── Linkers ───────────────────────────────────────────────────────
    
    def linker_names(self) -> list[str]:
        return [c.name for c in self.known_compilers()]
    
    def known_linkers(self, ignore_abstract: bool = False) -> list[LinkerNode]:
        return [l for l in self.linkers.values() if not (l.is_abstract and ignore_abstract)]
    
    def default_linker(self, target_name: str) -> LinkerNode | None:
       default_compiler = self.default_compiler(target_name)
       if not default_compiler:
           return None
       compiler = next((c for c in self.compilers.values() if c.name == default_compiler), None)
       if not compiler:
           return None
       default_linker_name = compiler.default_linker_name
       if not default_linker_name:
           return None
       return next((l for l in self.linkers.values() if l.name ==  default_linker_name), None)
    
    def get_linker(self, name: str) -> LinkerNode | None:
        return next((l for l in self.linkers.values() if l.name == name), None)
    
    # ── Private ───────────────────────────────────────────────────────────────

    def _all_projects(self) -> list[ProjectTypeNode]:
        projects = []
        for ptype in self.known_project_types():
            for entry in self.kiss_data.get(ptype.name, []):
                projects.append({**entry, "_type": ptype})
        return projects


# ── Loader ────────────────────────────────────────────────────────────────────

def load_context(directory: str) -> KissContext:
    project_dir = Path(directory).resolve()
    src_dir     = Path(__file__).parent
    data_dir    = src_dir.parent / "data"

    linkers       = resolve_extends(load_linkers(str(data_dir / "linkers.yaml")))
    compilers     = resolve_extends(load_compilers(str(data_dir / "compilers.yaml")))
    project_types = resolve_extends(load_project_types(str(data_dir / "project-types.yaml")))
    targets       = load_targets(str(data_dir / "targets.yaml"))

    # Load kiss.yaml if present
    kiss_yaml = project_dir / "kiss.yaml"
    kiss_data: dict = {}
    if kiss_yaml.exists():
        with open(kiss_yaml, encoding="utf-8") as f:
            kiss_data = yaml.safe_load(f) or {}

    # Load profiles from built-in profiles.yaml, then merge with user-defined profiles from kiss.yaml.
    # If a user profile has the same name as a built-in one (e.g. 'debug'), it is merged via
    # resolve_extends — the built-in acts as parent, the user definition as child.
    # Unknown profiles (e.g. 'perf') are added as-is.
    # resolve_extends is called once on the final merged state.
    profiles = load_profiles(str(data_dir / "profiles.yaml"))
    if kiss_data.get("profiles"):
        user_profiles = {p["name"]: yaml_parse_profile(p) for p in kiss_data["profiles"]}
        for name, user_profile in user_profiles.items():
            if name in profiles:
                profiles[name] = user_profile.resolve_extends(profiles[name])
            else:
                profiles[name] = user_profile
    profiles = resolve_extends(profiles)

    # Load project types from built-in project-types.yaml, then merge with user-defined ones.
    # Same semantics as profiles: same name → resolve_extends, unknown name → add as-is.
    if kiss_data.get("project-types"):
        user_project_types = {p["name"]: yaml_parse_project_type(p) for p in kiss_data["project-types"]}
        for name, user_project_type in user_project_types.items():
            if name in project_types:
                project_types[name] = user_project_type.resolve_extends(project_types[name])
            else:
                project_types[name] = user_project_type
    project_types = resolve_extends(project_types)

    return KissContext(
        directory     = project_dir,
        kiss_data     = kiss_data,
        compilers     = compilers,
        linkers       = linkers,
        profiles      = profiles,
        project_types = project_types,
        targets       = targets,
    )