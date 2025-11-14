import os
from pathlib import Path
from kiss_parser import KissParser
from platform_target import PlatformTarget
from project.project import Project


class CMakeDirectories:
    project_directory: Path
    cmakelists_directory : Path
    build_directory : Path

    def __init__(self, project_directory: Path, platform_target: PlatformTarget, project: Project):
        self._project_directory = project_directory
        self._build_directory = self.project_directory / "build" / platform_target.name / "cmake"
        self._cmakelists_directory =  self.build_directory / project.name

    @property
    def project_directory(self) -> Path:
        return self._project_directory
    
    @property
    def build_directory(self) -> Path:
        return self._build_directory
    
    @property
    def cmakelists_directory(self) -> Path:
        return self._cmakelists_directory