from pathlib import Path
import console
import semver
from semver import Version

PROJECT_FILE_NAME = "kiss.yaml"

class Project:
    def __init__(self, path: Path, name: str, description :str, version: Version):
        self.path_ = path
        self.name_ = name
        self.description_ = description
        self.version_ = version

        @property
        def path(self):
            return self.path_
        
        @property
        def name(self):
            return self.name_
        
        @property
        def description(self): 
            return self.description_
        
        @property
        def version(self):
            return self.version_

class BinProject(Project):
    def __init__(self, path: Path, name: str, description :str, version: Version, sources: list[Path] = []):
        super().__init__(path, name, description, version)
        self.sources_ = sources

    @property
    def sources(self) -> list[Path]:
        return self.sources_
    
class ProjectYAMLLoader:
    @staticmethod
    def load_projects_from_yaml(file: Path) -> list[Project] | None:
        import yaml
        VALID_ROOT = ["bin", "dyn", "lib", "workspace"]
        with file.open() as f:
            data = yaml.safe_load(f)
        if not data:
            console.print_error(f"  | Error: Project file is empty: {file}")
            return None
        
        projects: list[Project] = []
        for key, value in data.items():
            if key not in VALID_ROOT:
                console.print_error (f"⚠️  Error: invalid project type '{key}' in {file}")
                return None

            for item in value:
                if isinstance(item, dict):
                    name = item.get("name")
                    if not name:
                        console.print_error(f"⚠️  Error: Project name is missing in {file} under '{key}'")
                        return None
                    version = item.get("version")
                    if not version:
                        console.print_error(f"⚠️  Error: Project name is missing in {file} under '{key}'")
                        return None
                    try:
                        version = semver.VersionInfo.parse(version)
                    except Exception as e:
                        console.print_error(f"⚠️  Error: Invalid version format in {file} under '{key}': {e}")
                        return None

                    description = item.get("description", "")
                     
                    
                    project_path = file.parent / item.get("path", "")

                    match key:
                        case "bin":
                            sources = [file.parent / src for src in item.get("sources", [])]
                            projects.append(BinProject(path=project_path, name=name, description=description, sources=sources, version=version))
        return projects

class ProjectRegistry:
    def __init__(self):
        self.registry_: dict[Path, Project] = {}

    def register_project(self, project: Project):
        self.registry_[project.path] = project

    def is_file_loaded(self, filepath:Path) -> bool:
        return filepath in self.registry_
    
    def load_projects_in_directory(self, path: Path, recursive: bool = False):
        pattern = f"**/{PROJECT_FILE_NAME}" if recursive else PROJECT_FILE_NAME

        # Load modules
        for file in path.glob(pattern):
            if self.is_file_loaded(file):
                continue
            ProjectYAMLLoader.load_projects_from_yaml(file)


