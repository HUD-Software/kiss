from pathlib import Path
from config import Config
from project import Project
from toolchain import Toolchain

class CMakeContext:
    def __init__(self, current_directory: Path, toolchain: Toolchain, project: Project):
        self._current_directory = current_directory
        self._root_build_directory = self.resolveRootBuildDirectory(current_directory=current_directory)
        self._build_directory = self.resolveProjectBuildDirectory(current_directory=current_directory, toolchain=toolchain, project=project)
        self._cmakelists_directory =  self.resolveCMakeListsDirectory(current_directory=current_directory, toolchain=toolchain, project=project)
        self._project = project
        self._toolchain = toolchain
        self._cmakefile = self._cmakelists_directory / "CMakeLists.txt"
        self._cmakecache = self._build_directory / "CMakeCache.txt"
        self._install_directory = self._root_build_directory / "install"
    
    @staticmethod
    def resolveRootBuildDirectory(current_directory: Path) -> Path:
        return  current_directory / "build"
        
    @staticmethod
    def resolveCMakeBuildDirectory(current_directory: Path, toolchain: Toolchain) -> Path:
        return CMakeContext.resolveRootBuildDirectory(current_directory=current_directory) / toolchain.target.name / "cmake"
    
    @staticmethod
    def resolveProjectBuildDirectory(current_directory: Path, toolchain: Toolchain, project: Project) -> Path:
        return CMakeContext.resolveCMakeBuildDirectory(current_directory=current_directory, toolchain=toolchain) / f"{project.name}_{project.filehash_short:08x}" / "build"
    
    @staticmethod   
    def resolveCMakeListsDirectory(current_directory: Path, toolchain: Toolchain, project: Project) -> Path:
        return CMakeContext.resolveCMakeBuildDirectory(current_directory=current_directory, toolchain=toolchain) / f"{project.name}_{project.filehash_short:08x}"
    
    @staticmethod   
    def resolveCMakefile(current_directory: Path, toolchain: Toolchain, project: Project) -> Path:
        return CMakeContext.resolveCMakeListsDirectory(current_directory=current_directory, toolchain=toolchain, project=project) / "CMakeLists.txt"
    
    @staticmethod
    def resolveCMakeCacheDirectory(current_directory: Path, toolchain: Toolchain, project: Project):
        return CMakeContext.resolveProjectBuildDirectory(current_directory=current_directory, toolchain=toolchain, project=project) / "CMakeCache.txt"
    
    @property
    def cmake_root_build_directory(self) -> Path:
        return self._root_build_directory
    
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
    def toolchain(self) -> Toolchain:
        return self._toolchain

    def target_output_directory(self, config: Config) -> Path:
        if config.is_release:
            if config.is_debug_info:
                return self.cmakelists_directory / "relwithdebinfo"
            else:
                return self.cmakelists_directory / "release"
        else:    
            return self.cmakelists_directory / "debug"