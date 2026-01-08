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
    fingerprint : Fingerprint

    def __init__(self, project_directory: Path, platform_target: PlatformTarget, project: Project, fingerprint:Fingerprint):
        self._project_directory = project_directory
        self._build_directory = self.project_directory / "build" / platform_target.name / "cmake"
        h = int.from_bytes(hashlib.sha256(str(project.file).encode()).digest()[:4], "little" )& 0xFFFFFFFF
        self._cmakelists_directory =  self.build_directory / f"{project.name}_{h:08x}"
        self._project = project
        self._platform_target = platform_target
        self._cmakefile = self.cmakelists_directory / "CMakeLists.txt"
        if fingerprint is None:
            self._fingerprint = Fingerprint(self._build_directory)
        else:
            self._fingerprint = fingerprint

        self._dependencies_context : list[Self] = []

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
    def fingerprint(self) -> Fingerprint:
        return self._fingerprint

    @property
    def dependencies_context(self) -> list[Self]:
        return self._dependencies_context
    
    def flatten_leaf_to_root(self) -> list[Self]:
        flat_list = []

        def dfs(node):
            for child in node.dependencies_context:
                dfs(child)
            flat_list.append(node)

        dfs(self)
        return flat_list
    
    def flatten_root_to_leaf(self) -> list[Self]:
        queue = deque([self])
        flat_list = []

        while queue:
            node = queue.popleft()
            flat_list.append(node)
            queue.extend(node.dependencies_context)

        return flat_list
    
    