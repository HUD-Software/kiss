from pathlib import Path
from cmake.cmake_generator_name import CMakeGeneratorName
from project import Project
from toolchain import Toolchain

class CMakeContext:
    def __init__(self, current_directory: Path, toolchain: Toolchain, project: Project, profile_name:  str, cmake_generator_name:str):
        self._current_directory = current_directory
        self._cmake_generator_name = cmake_generator_name or CMakeGeneratorName.create(toolchain=toolchain)
        self._root_build_directory = self.resolveRootBuildDirectory(current_directory=current_directory)
        self._build_directory = self.resolveProjectBuildDirectory(current_directory=current_directory, 
                                                                  toolchain=toolchain, project=project, 
                                                                  cmake_generator_name=self._cmake_generator_name, 
                                                                  profile_name=profile_name)
        self._cmakelists_directory =  self.resolveCMakeListsDirectory(current_directory=current_directory, 
                                                                      toolchain=toolchain, 
                                                                      project=project, 
                                                                      cmake_generator_name=self._cmake_generator_name, 
                                                                      profile_name=profile_name)
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
        return CMakeContext.resolveRootBuildDirectory(current_directory=current_directory) / toolchain.target.name / toolchain.compiler.name / "cmake"
    
    @staticmethod
    def resolveProjectBuildDirectory(current_directory: Path, toolchain: Toolchain, project: Project, cmake_generator_name: CMakeGeneratorName, profile_name:  str) -> Path:
        return CMakeContext.resolveCMakeListsDirectory(current_directory=current_directory, 
                                                       toolchain=toolchain, 
                                                       project=project,
                                                       cmake_generator_name=cmake_generator_name, 
                                                       profile_name=profile_name) / "build"
    
    @staticmethod   
    def resolveCMakeListsDirectory(current_directory: Path, toolchain: Toolchain, project: Project, cmake_generator_name: CMakeGeneratorName, profile_name:  str) -> Path:
        if cmake_generator_name.is_single_profile():
            return CMakeContext.resolveCMakeBuildDirectory(current_directory=current_directory, 
                                                           toolchain=toolchain) / f"{project.name}_{project.filehash_short:08x}" / profile_name
        else:
           return CMakeContext.resolveCMakeBuildDirectory(current_directory=current_directory, 
                                                          toolchain=toolchain) / f"{project.name}_{project.filehash_short:08x}"
    
    @staticmethod   
    def resolveCMakefile(current_directory: Path, toolchain: Toolchain, project: Project, cmake_generator_name: CMakeGeneratorName, profile_name:  str) -> Path:
        return CMakeContext.resolveCMakeListsDirectory(current_directory=current_directory, 
                                                       toolchain=toolchain, 
                                                       project=project, 
                                                       cmake_generator_name=cmake_generator_name, 
                                                       profile_name=profile_name) / "CMakeLists.txt"
    
    @staticmethod
    def resolveCMakeCacheDirectory(current_directory: Path, toolchain: Toolchain, project: Project, cmake_generator_name: CMakeGeneratorName, profile_name:  str):
        return CMakeContext.resolveProjectBuildDirectory(current_directory=current_directory, 
                                                         toolchain=toolchain, 
                                                         project=project, 
                                                         cmake_generator_name=cmake_generator_name, 
                                                         profile_name=profile_name) / "CMakeCache.txt"
    
    def output_directory_for_config(self, config: str) -> str: 
        if self.cmake_generator_name.is_single_profile():
            return self.cmakelists_directory.resolve().as_posix()
        else:
            return (self.cmakelists_directory / config).resolve().as_posix()
    
    @property
    def cmake_generator_name(self) -> CMakeGeneratorName: 
        return self._cmake_generator_name


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
    
    