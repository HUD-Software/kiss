from collections import deque
from pathlib import Path
from typing import Self
from cmake.fingerprint import Fingerprint
from platform_target import PlatformTarget
from project import Project
import hashlib

class CMakeContext:
    project_directory: Path
    cmakelists_directory : Path
    build_directory : Path

    def __init__(self, project_directory: Path, platform_target: PlatformTarget, project: Project):
        self._project_directory = project_directory
        self._build_directory = self.resolveBuildDirectory(project_directory=project_directory, platform_target=platform_target)
        h = int.from_bytes(hashlib.sha256(str(project.file).encode()).digest()[:4], "little" )& 0xFFFFFFFF
        self._cmakelists_directory =  self.build_directory / f"{project.name}_{h:08x}"
        self._project = project
        self._platform_target = platform_target
        self._cmakefile = self.cmakelists_directory / "CMakeLists.txt"
        self._dependencies_context : list[Self] = []
    
    @staticmethod
    def resolveBuildDirectory(project_directory: Path, platform_target: PlatformTarget) -> Path:
        return  project_directory / "build" / platform_target.name / "cmake"

    @property
    def project_directory(self) -> Path:
        return self._project_directory
    
    @property
    def build_directory(self) -> Path:
        return self._build_directory
    
    @property
    def cmakelists_directory(self) -> Path:
        return self._cmakelists_directory
    
    @property
    def cmakefile(self) -> Path:
        return self._cmakefile
    
    @property
    def project(self) -> Path:
        return self._project
    
    @property
    def platform_target(self) -> PlatformTarget:
        return self._platform_target
    
    @property
    def dependencies_context(self) -> list[Self]:
        return self._dependencies_context