from pathlib import Path
from typing import Self
import console
from platform_target import PlatformTarget
from project import Project

class CMakeContext:
    def __init__(self, current_directory: Path, platform_target: PlatformTarget, project: Project):
        self._current_directory = current_directory
        root_build_directory = self.resolveRootBuildDirectory(current_directory=current_directory, platform_target=platform_target)
        self._build_directory = self.resolveBuildDirectory(current_directory=current_directory, platform_target=platform_target, project=project)
        self._cmakelists_directory =  self.resolveCMakeListsDirectory(current_directory=current_directory, platform_target=platform_target, project=project)
        self._project = project
        self._platform_target = platform_target
        self._cmakefile = self.resolveCMakefile(current_directory=current_directory, platform_target=platform_target, project=project)
        self._cmakecache = self._build_directory / "CMakeCache.txt"
        self._install_directory = root_build_directory / "install"
        self._dependencies_context : list[Self] = []
    
    @staticmethod
    def resolveRootBuildDirectory(current_directory: Path, platform_target: PlatformTarget) -> Path:
        return  current_directory / "build" / platform_target.name / "cmake"
    
    @staticmethod
    def resolveBuildDirectory(current_directory: Path, platform_target: PlatformTarget, project: Project) -> Path:
        return  CMakeContext.resolveRootBuildDirectory(current_directory=current_directory, platform_target=platform_target) / f"{project.name}_{project.filehash_short:08x}" / "build"
    
    @staticmethod   
    def resolveCMakeListsDirectory(current_directory: Path, platform_target: PlatformTarget, project: Project) -> Path:
        return CMakeContext.resolveRootBuildDirectory(current_directory=current_directory, platform_target=platform_target) / f"{project.name}_{project.filehash_short:08x}"
    
    @staticmethod   
    def resolveCMakefile(current_directory: Path, platform_target: PlatformTarget, project: Project) -> Path:
        return CMakeContext.resolveCMakeListsDirectory(current_directory=current_directory, platform_target=platform_target, project=project) / "CMakeLists.txt"
    
    @property
    def current_directory(self) -> Path:
        return self._current_directory
    
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
    def cmakecache(self) -> Path:
        return self._cmakecache
    
    @property
    def install_directory(self) -> Path:
        return self._install_directory
    
    @property
    def project(self) -> Path:
        return self._project
    
    @property
    def platform_target(self) -> PlatformTarget:
        return self._platform_target
    
    @property
    def dependencies_context(self) -> list[Self]:
        return self._dependencies_context
