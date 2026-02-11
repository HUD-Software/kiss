
import argparse
import os
from pathlib import Path
from typing import Optional, Self
from cli import KissParser
from cmake.cmake_context import CMakeContext
from cmake.fingerprint import Fingerprint
from config import Config
import console
from generate import GenerateContext
from generator import BaseGenerator
from project import  BinProject, LibProject, DynProject, Project, ProjectType
from toolchain import Toolchain

class CMakeListsGenerateContext(GenerateContext):
    def __init__(self, directory:Path, project: Project, generator_name: str, toolchain: Toolchain, config: Optional[Config]):
        super().__init__(directory=directory,project=project,generator_name=generator_name,toolchain=toolchain)
        self._config = config
        self._cmake_context = CMakeContext(current_directory=directory, toolchain=toolchain, project=project)
    
    @property
    def config(self) -> Config:
        return self._config
    
    @property
    def cmakefile(self) -> Path:
        return self._cmake_context.cmakefile
    
    @property
    def cmake_root_build_directory(self) -> Path:
        return self._cmake_context.cmake_root_build_directory

    @property
    def cmakelists_directory(self) -> Path:
        return self._cmake_context.cmakelists_directory

    @property
    def project(self) -> Project:
        return self._cmake_context.project
    
    @property
    def current_directory(self) -> Path:
        return self._cmake_context._current_directory
    
    @project.setter
    def project(self, value):
        self._cmake_context = CMakeContext(current_directory=self._cmake_context.current_directory, toolchain=self._cmake_context.toolchain, project=value)
    
    def target_output_directory_for_config(self, config: Config) -> Path:
        return self._cmake_context.target_output_directory(config)
    
    def target_output_directory(self) -> Path:
        return self.target_output_directory_for_config(self.config)
    
    @classmethod
    def create(cls, directory: Path, project_name: str, generator_name: str, toolchain: Toolchain, config: Optional[Config]) -> Self :
        project_to_generate = super().find_target_project(directory, project_name)
        if not project_to_generate:
            console.print_error(f"No project found in {str(directory)}")
            exit(1)
        generator_name = generator_name if generator_name is not None else "cmake"
        return cls(directory=directory, project=project_to_generate, generator_name=generator_name, toolchain=toolchain, config=config)



class CMakeListsGenerator(BaseGenerator):
    @classmethod
    def add_cli_argument_to_parser(cls, parser: KissParser):
        pass
    
    def __init__(self):
        super().__init__("cmake", "Generate cmake CMakeLists.txt")

    @staticmethod
    def _split_path_with_pattern(path: Path):
        parts = path.parts

        # Chercher le premier composant qui contient '*' ou '?'
        base = Path() 
        pattern = None
        rest = None
        for i, part in enumerate(parts):
            if '*' in part or '?' in part:
                pattern = str(part)
                rest = Path(*parts[i+1:]) if i + 1 < len(parts) else None
                break
            else:
                base = base / part

        
        # Si aucun wildcard
        return base, pattern, rest
    
    @staticmethod
    def _resolve_glob_source_path(base, pattern, rest):
        all_files = set()

        if "**" in pattern:
            pattern = pattern.replace("**", "**/*")
            
        # glob the pattern from base
        for f in  base.glob(pattern):
            # It's a file, add it
            if f.is_file():
                all_files.add(f'"{f.resolve().as_posix()}"')
            # It's a directory and we have rest
            # Add the rest avec the current directory and reapply the glob
            elif f.is_dir() and rest:
                src = f / rest
                base_d, pattern_d, rest_d = CMakeListsGenerator._split_path_with_pattern(src)
                all_files.update(CMakeListsGenerator._resolve_glob_source_path(base_d, pattern_d, rest_d))
        return all_files
    
    @staticmethod
    def _resolve_sources(src_list: list[Path], project_name: str): 
        all_files = set()
        for src in src_list:
            base, pattern, rest = CMakeListsGenerator._split_path_with_pattern(src)

            # We have a pattern like "**", "*" or "?"
            if pattern:
                all_files.update(CMakeListsGenerator._resolve_glob_source_path(base, pattern, rest))
           
            #  There is not pattern and it's a file, just add it
            else:
                if not src.exists():
                    console.print_error(f"Error when generating CMake file for {project_name}: file {src} not found")
                    exit(1)
                if base.is_file(): 
                    all_files.add(f'"{base.resolve().as_posix()}"')

        return list(all_files)
    
    def _generateMultiConfigProject(self, cmakelist_generate_context: CMakeListsGenerateContext):
        match cmakelist_generate_context.project.type:
            case ProjectType.bin:
                self._generateMultiConfigBinCMakeLists(cmakelist_generate_context)
            case ProjectType.lib:
                self._generateMultiConfigLibCMakeLists(cmakelist_generate_context)
            case ProjectType.dyn:
                self._generateMultiConfigDynCMakeLists(cmakelist_generate_context)       

    def _generateMultiConfigBinCMakeLists(self, cmakelist_generate_context: CMakeListsGenerateContext):
        project: BinProject = cmakelist_generate_context.project
        os.makedirs(cmakelist_generate_context.cmakelists_directory, exist_ok=True)
        # Write the CMakeLists.txt file
        with open(cmakelist_generate_context.cmakefile, "w", encoding="utf-8") as f:
            # Write CMake common
            f.write("cmake_minimum_required(VERSION 3.18)\n")
            
            # Write project description
            f.write(f"""                    
# {project.name} description
project({project.name} LANGUAGES CXX )
""")
            # Write project sources
            if project.sources:
                normalized_src = self._resolve_sources(project.sources, project.name)
                src_str:str =""
                for src in normalized_src:
                    src_str += f"\n\t{src}"
                f.write(f"add_executable({project.name} {src_str})\n")

            # Write output name
            f.write(f"""                    
# {project.name} output name
set_target_properties({project.name} PROPERTIES OUTPUT_NAME {project.name})
set_target_properties({project.name} PROPERTIES
    RUNTIME_OUTPUT_DIRECTORY_DEBUG   "{cmakelist_generate_context.target_output_directory_for_config(Config(is_release=False, is_debug_info=False)).resolve().as_posix()}"
    RUNTIME_OUTPUT_DIRECTORY_RELEASE "{cmakelist_generate_context.target_output_directory_for_config(Config(is_release=True, is_debug_info=False)).resolve().as_posix()}"
    RUNTIME_OUTPUT_DIRECTORY_RELWITHDEBINFO "{cmakelist_generate_context.target_output_directory_for_config(Config(is_release=True, is_debug_info=True)).resolve().as_posix()}"
)
""")
            # Write dependencies
            for dep_project in project.dependencies:
                dep_cmakelist_dir = CMakeContext.resolveCMakeListsDirectory(current_directory=cmakelist_generate_context.current_directory,
                                                                        platform_target=cmakelist_generate_context.platform_target,
                                                                        project=dep_project)
                dep_build_dir = CMakeContext.resolveProjectBuildDirectory(current_directory=cmakelist_generate_context.current_directory,
                                                                        platform_target=cmakelist_generate_context.platform_target,
                                                                        project=dep_project)
                f.write(f"""\n# Add {dep_project.name} dependency 
if(NOT TARGET {dep_project.name})
add_subdirectory("{dep_cmakelist_dir.resolve().as_posix()}" "{dep_build_dir.resolve().as_posix()}")
endif()
target_link_libraries({project.name} PRIVATE {dep_project.name})
target_include_directories({project.name} PRIVATE $<TARGET_PROPERTY:{dep_project.name},INTERFACE_INCLUDE_DIRECTORIES>)
""")

    def _generateMultiConfigLibCMakeLists(self, cmakelist_generate_context: CMakeListsGenerateContext):
        project: LibProject = cmakelist_generate_context.project
        os.makedirs(cmakelist_generate_context.cmakelists_directory, exist_ok=True)
        # Write the CMakeLists.txt file
        with open(cmakelist_generate_context.cmakefile, "w", encoding="utf-8") as f:
            # Write CMake common
            f.write("cmake_minimum_required(VERSION 3.18)\n")

            # Write project description
            f.write(f"""                    
# {project.name} description
project({project.name} LANGUAGES CXX )
""")
            # Write project sources
            if project.sources:
                normalized_src = self._resolve_sources(project.sources, project.name)
                src_str:str =""
                for src in normalized_src:
                    src_str += f"\n\t{src}"
                f.write(f"add_library({project.name} STATIC {src_str})\n")

            # Write project interfaces
            if project.interface_directories:
                interface_str:str =""
                for interface in project.interface_directories:
                    interface_str += f"\n\t$<BUILD_INTERFACE:{str(interface.resolve().as_posix())}> $<INSTALL_INTERFACE:{interface.name}>"
                f.write(f"target_include_directories({project.name} PUBLIC {interface_str})\n")

            # Write output name
            f.write(f"""                    
# {project.name} output name
set_target_properties({project.name} PROPERTIES OUTPUT_NAME {project.name})
set_target_properties({project.name} PROPERTIES
    ARCHIVE_OUTPUT_DIRECTORY_DEBUG   "{cmakelist_generate_context.target_output_directory_for_config(Config(is_release=False, is_debug_info=False)).resolve().as_posix()}"
    ARCHIVE_OUTPUT_DIRECTORY_RELEASE "{cmakelist_generate_context.target_output_directory_for_config(Config(is_release=True, is_debug_info=False)).resolve().as_posix()}"
    ARCHIVE_OUTPUT_DIRECTORY_RELWITHDEBINFO "{cmakelist_generate_context.target_output_directory_for_config(Config(is_release=True, is_debug_info=True)).resolve().as_posix()}"
)
""")
            # Write dependencies
            for dep_project in project.dependencies:
                dep_cmakelist_dir = CMakeContext.resolveCMakeListsDirectory(current_directory=cmakelist_generate_context.current_directory,
                                                                        platform_target=cmakelist_generate_context.platform_target,
                                                                        project=dep_project)
                dep_build_dir = CMakeContext.resolveProjectBuildDirectory(current_directory=cmakelist_generate_context.current_directory,
                                                                        platform_target=cmakelist_generate_context.platform_target,
                                                                        project=dep_project)
                f.write(f"""\n# Add {dep_project.name} dependency 
if(NOT TARGET {dep_project.name})
add_subdirectory("{dep_cmakelist_dir.resolve().as_posix()}" "{dep_build_dir.resolve().as_posix()}")
endif()
target_link_libraries({project.name} PRIVATE {dep_project.name})
target_include_directories({project.name} PRIVATE $<TARGET_PROPERTY:{dep_project.name},INTERFACE_INCLUDE_DIRECTORIES>)
""") 
                

            # Write package
            f.write(f"""
# Create alias
add_library({project.name}::{project.name} ALIAS {project.name})
include(CMakePackageConfigHelpers)
# Version file
write_basic_package_version_file(
    "${{CMAKE_CURRENT_BINARY_DIR}}/{project.name}ConfigVersion.cmake"
    VERSION 1.0.0
    COMPATIBILITY AnyNewerVersion
)

# Config file
configure_package_config_file(
    "${{CMAKE_CURRENT_LIST_DIR}}/{project.name}Config.cmake.in"
    "${{CMAKE_CURRENT_BINARY_DIR}}/{project.name}Config.cmake"
    INSTALL_DESTINATION lib/cmake/{project.name}
)
# Installation
install(TARGETS {project.name}
    EXPORT {project.name}Targets
    RUNTIME DESTINATION {project.name}
    ARCHIVE DESTINATION {project.name}
    LIBRARY DESTINATION {project.name}
)
""")
            if project.interface_directories:
                for interface in project.interface_directories:
                    f.write(f"install(DIRECTORY {str(interface.resolve().as_posix())} DESTINATION {project.name})\n")

            f.write(f"""
install(EXPORT {project.name}Targets
    FILE {project.name}Targets.cmake
    NAMESPACE {project.name}::
    DESTINATION {project.name}/cmake
)
install(FILES
    "${{CMAKE_CURRENT_BINARY_DIR}}/{project.name}Config.cmake"
    "${{CMAKE_CURRENT_BINARY_DIR}}/{project.name}ConfigVersion.cmake"
    DESTINATION {project.name}/cmake
)
""")
        
        with open(cmakelist_generate_context.cmakelists_directory / f"{project.name}Config.cmake.in", "w", encoding="utf-8") as f:
            f.write(f"""@PACKAGE_INIT@

include("${{CMAKE_CURRENT_LIST_DIR}}/{project.name}Targets.cmake")
""")
                
    def _generateMultiConfigDynCMakeLists(self, cmakelist_generate_context: CMakeListsGenerateContext):
        project: DynProject = cmakelist_generate_context.project
        os.makedirs(cmakelist_generate_context.cmakelists_directory, exist_ok=True)
        # Write the CMakeLists.txt file
        with open(cmakelist_generate_context.cmakefile, "w", encoding="utf-8") as f:
            # Write CMake common
            f.write("cmake_minimum_required(VERSION 3.18)\n")

            # Write project description
            f.write(f"""                    
# {project.name} description
project({project.name} LANGUAGES CXX )
""")
            # Write project sources
            if project.sources:
                normalized_src = self._resolve_sources(project.sources, project.name)
                src_str:str =""
                for src in normalized_src:
                    src_str += f"\n\t{src}"
                f.write(f"add_library({project.name} SHARED {src_str})\n")

            # Write project interfaces
            if project.interface_directories:
                interface_str:str =""
                for interface in project.interface_directories:
                    interface_str += f"\n\t$<BUILD_INTERFACE:{str(interface.resolve().as_posix())}> $<INSTALL_INTERFACE:{interface.name}>"
                f.write(f"target_include_directories({project.name} PUBLIC {interface_str})\n")

            # Write output name
            f.write(f"""                    
# {project.name} output name
set_target_properties({project.name} PROPERTIES OUTPUT_NAME {project.name})
target_compile_definitions({project.name} PRIVATE KISS_EXPORTS)
set_target_properties({project.name} PROPERTIES
    LIBRARY_OUTPUT_DIRECTORY_DEBUG   "{cmakelist_generate_context.target_output_directory_for_config(Config(is_release=False, is_debug_info=False)).resolve().as_posix()}"
    LIBRARY_OUTPUT_DIRECTORY_RELEASE "{cmakelist_generate_context.target_output_directory_for_config(Config(is_release=True, is_debug_info=False)).resolve().as_posix()}"
    LIBRARY_OUTPUT_DIRECTORY_RELWITHDEBINFO "{cmakelist_generate_context.target_output_directory_for_config(Config(is_release=True, is_debug_info=True)).resolve().as_posix()}"
    RUNTIME_OUTPUT_DIRECTORY_DEBUG   "{cmakelist_generate_context.target_output_directory_for_config(Config(is_release=False, is_debug_info=False)).resolve().as_posix()}"
    RUNTIME_OUTPUT_DIRECTORY_RELEASE "{cmakelist_generate_context.target_output_directory_for_config(Config(is_release=True, is_debug_info=False)).resolve().as_posix()}"
    RUNTIME_OUTPUT_DIRECTORY_RELWITHDEBINFO "{cmakelist_generate_context.target_output_directory_for_config(Config(is_release=True, is_debug_info=True)).resolve().as_posix()}"
)
""")
            # Write dependencies
            for dep_project in project.dependencies:
                dep_cmakelist_dir = CMakeContext.resolveCMakeListsDirectory(current_directory=cmakelist_generate_context.current_directory,
                                                                        platform_target=cmakelist_generate_context.platform_target,
                                                                        project=dep_project)
                dep_build_dir = CMakeContext.resolveProjectBuildDirectory(current_directory=cmakelist_generate_context.current_directory,
                                                                        platform_target=cmakelist_generate_context.platform_target,
                                                                        project=dep_project)
                f.write(f"""\n# Add {dep_project.name} dependency 
if(NOT TARGET {dep_project.name})
add_subdirectory("{dep_cmakelist_dir.resolve().as_posix()}" "{dep_build_dir.resolve().as_posix()}")
endif()
target_link_libraries({project.name} PRIVATE {dep_project.name})
target_include_directories({project.name} PRIVATE $<TARGET_PROPERTY:{dep_project.name},INTERFACE_INCLUDE_DIRECTORIES>)
""")        
                
            # Write package
            f.write(f"""
# Create alias
add_library({project.name}::{project.name} ALIAS {project.name})
include(CMakePackageConfigHelpers)
# Version file
write_basic_package_version_file(
    "${{CMAKE_CURRENT_BINARY_DIR}}/{project.name}ConfigVersion.cmake"
    VERSION 1.0.0
    COMPATIBILITY AnyNewerVersion
)

# Config file
configure_package_config_file(
    "${{CMAKE_CURRENT_LIST_DIR}}/{project.name}Config.cmake.in"
    "${{CMAKE_CURRENT_BINARY_DIR}}/{project.name}Config.cmake"
    INSTALL_DESTINATION {project.name}
)
# Installation
install(TARGETS {project.name}
    EXPORT {project.name}Targets
    RUNTIME DESTINATION {project.name}
    ARCHIVE DESTINATION {project.name}
    LIBRARY DESTINATION {project.name}
)
""")
            if project.interface_directories:
                for interface in project.interface_directories:
                    f.write(f"install(DIRECTORY {str(interface.resolve().as_posix())} DESTINATION {project.name})\n")

            f.write(f"""
install(EXPORT {project.name}Targets
    FILE {project.name}Targets.cmake
    NAMESPACE {project.name}::
    DESTINATION {project.name}/cmake
)
install(FILES
    "${{CMAKE_CURRENT_BINARY_DIR}}/{project.name}Config.cmake"
    "${{CMAKE_CURRENT_BINARY_DIR}}/{project.name}ConfigVersion.cmake"
    DESTINATION {project.name}/cmake
)
""")
        
        with open(cmakelist_generate_context.cmakelists_directory / f"{project.name}Config.cmake.in", "w", encoding="utf-8") as f:
            f.write(f"""@PACKAGE_INIT@

include("${{CMAKE_CURRENT_LIST_DIR}}/{project.name}Targets.cmake")
""")

    def _generateSingleConfigProject(self, cmakelist_generate_context: CMakeListsGenerateContext):
        match cmakelist_generate_context.project.type:
            case ProjectType.bin:
                self._generateSingleConfigBinCMakeLists(cmakelist_generate_context)
            case ProjectType.lib:
                self._generateSingleConfigLibCMakeLists(cmakelist_generate_context)
            case ProjectType.dyn:
                self._generateSingleConfigDynCMakeLists(cmakelist_generate_context)       

    def _generateSingleConfigBinCMakeLists(self, cmakelist_generate_context: CMakeListsGenerateContext):
        project: BinProject = cmakelist_generate_context.project
        os.makedirs(cmakelist_generate_context.cmakelists_directory, exist_ok=True)
        # Write the CMakeLists.txt file
        with open(cmakelist_generate_context.cmakefile, "w", encoding="utf-8") as f:
            # Write CMake common
            f.write("cmake_minimum_required(VERSION 3.18)\n")
            
            # Write project description
            f.write(f"""                    
# {project.name} description
project({project.name} LANGUAGES CXX )
""")
            # Write project sources
            if project.sources:
                normalized_src = self._resolve_sources(project.sources, project.name)
                src_str:str =""
                for src in normalized_src:
                    src_str += f"\n\t{src}"
                f.write(f"add_executable({project.name} {src_str})\n")

            # Write output name
            f.write(f"""                    
# {project.name} output name
set_target_properties({project.name} PROPERTIES OUTPUT_NAME {project.name})
set_target_properties({project.name} PROPERTIES
    RUNTIME_OUTPUT_DIRECTORY   "{cmakelist_generate_context.target_output_directory().resolve().as_posix()}"
)
""")
            # Write dependencies
            for dep_project in project.dependencies:
                dep_cmakelist_dir = CMakeContext.resolveCMakeListsDirectory(current_directory=cmakelist_generate_context.current_directory,
                                                                        toolchain=cmakelist_generate_context.toolchain,
                                                                        project=dep_project)
                dep_build_dir = CMakeContext.resolveProjectBuildDirectory(current_directory=cmakelist_generate_context.current_directory,
                                                                        toolchain=cmakelist_generate_context.toolchain,
                                                                        project=dep_project)
                f.write(f"""\n# Add {dep_project.name} dependency 
if(NOT TARGET {dep_project.name})
add_subdirectory("{dep_cmakelist_dir.resolve().as_posix()}" "{dep_build_dir.resolve().as_posix()}")
endif()
target_link_libraries({project.name} PRIVATE {dep_project.name})
target_include_directories({project.name} PRIVATE $<TARGET_PROPERTY:{dep_project.name},INTERFACE_INCLUDE_DIRECTORIES>)
""")
    
    def _generateSingleConfigLibCMakeLists(self, cmakelist_generate_context: CMakeListsGenerateContext):
        project: LibProject = cmakelist_generate_context.project
        os.makedirs(cmakelist_generate_context.cmakelists_directory, exist_ok=True)
        # Write the CMakeLists.txt file
        with open(cmakelist_generate_context.cmakefile, "w", encoding="utf-8") as f:
            # Write CMake common
            f.write("cmake_minimum_required(VERSION 3.18)\n")

            # Write project description
            f.write(f"""                    
# {project.name} description
project({project.name} LANGUAGES CXX )
""")
            # Write project sources
            if project.sources:
                normalized_src = self._resolve_sources(project.sources, project.name)
                src_str:str =""
                for src in normalized_src:
                    src_str += f"\n\t{src}"
                f.write(f"add_library({project.name} STATIC {src_str})\n")

            # Write project interfaces
            if project.interface_directories:
                interface_str:str =""
                for interface in project.interface_directories:
                    interface_str += f"\n\t$<BUILD_INTERFACE:{str(interface.resolve().as_posix())}> $<INSTALL_INTERFACE:{interface.name}>"
                f.write(f"target_include_directories({project.name} PUBLIC {interface_str})\n")

            # Write output name
            f.write(f"""                    
# {project.name} output name
set_target_properties({project.name} PROPERTIES OUTPUT_NAME {project.name})
set_target_properties({project.name} PROPERTIES
    ARCHIVE_OUTPUT_DIRECTORY "{cmakelist_generate_context.target_output_directory().resolve().as_posix()}"
)
""")
            # Write dependencies
            for dep_project in project.dependencies:
                dep_cmakelist_dir = CMakeContext.resolveCMakeListsDirectory(current_directory=cmakelist_generate_context.current_directory,
                                                                        platform_target=cmakelist_generate_context.platform_target,
                                                                        project=dep_project)
                dep_build_dir = CMakeContext.resolveProjectBuildDirectory(current_directory=cmakelist_generate_context.current_directory,
                                                                        platform_target=cmakelist_generate_context.platform_target,
                                                                        project=dep_project)
                f.write(f"""\n# Add {dep_project.name} dependency 
if(NOT TARGET {dep_project.name})
add_subdirectory("{dep_cmakelist_dir.resolve().as_posix()}" "{dep_build_dir.resolve().as_posix()}")
endif()
target_link_libraries({project.name} PRIVATE {dep_project.name})
target_include_directories({project.name} PRIVATE $<TARGET_PROPERTY:{dep_project.name},INTERFACE_INCLUDE_DIRECTORIES>)
""") 
                

            # Write package
            f.write(f"""
# Create alias
add_library({project.name}::{project.name} ALIAS {project.name})
include(CMakePackageConfigHelpers)
# Version file
write_basic_package_version_file(
    "${{CMAKE_CURRENT_BINARY_DIR}}/{project.name}ConfigVersion.cmake"
    VERSION 1.0.0
    COMPATIBILITY AnyNewerVersion
)

# Config file
configure_package_config_file(
    "${{CMAKE_CURRENT_LIST_DIR}}/{project.name}Config.cmake.in"
    "${{CMAKE_CURRENT_BINARY_DIR}}/{project.name}Config.cmake"
    INSTALL_DESTINATION lib/cmake/{project.name}
)
# Installation
install(TARGETS {project.name}
    EXPORT {project.name}Targets
    RUNTIME DESTINATION {project.name}
    ARCHIVE DESTINATION {project.name}
    LIBRARY DESTINATION {project.name}
)
""")
            if project.interface_directories:
                for interface in project.interface_directories:
                    f.write(f"install(DIRECTORY {str(interface.resolve().as_posix())} DESTINATION {project.name})\n")

            f.write(f"""
install(EXPORT {project.name}Targets
    FILE {project.name}Targets.cmake
    NAMESPACE {project.name}::
    DESTINATION {project.name}/cmake
)
install(FILES
    "${{CMAKE_CURRENT_BINARY_DIR}}/{project.name}Config.cmake"
    "${{CMAKE_CURRENT_BINARY_DIR}}/{project.name}ConfigVersion.cmake"
    DESTINATION {project.name}/cmake
)
""")
        
        with open(cmakelist_generate_context.cmakelists_directory / f"{project.name}Config.cmake.in", "w", encoding="utf-8") as f:
            f.write(f"""@PACKAGE_INIT@

include("${{CMAKE_CURRENT_LIST_DIR}}/{project.name}Targets.cmake")
""")
                
    def _generateSingleConfigDynCMakeLists(self, cmakelist_generate_context: CMakeListsGenerateContext):
        project: DynProject = cmakelist_generate_context.project
        os.makedirs(cmakelist_generate_context.cmakelists_directory, exist_ok=True)
        # Write the CMakeLists.txt file
        with open(cmakelist_generate_context.cmakefile, "w", encoding="utf-8") as f:
            # Write CMake common
            f.write("cmake_minimum_required(VERSION 3.18)\n")

            # Write project description
            f.write(f"""                    
# {project.name} description
project({project.name} LANGUAGES CXX )
""")
            # Write project sources
            if project.sources:
                normalized_src = self._resolve_sources(project.sources, project.name)
                src_str:str =""
                for src in normalized_src:
                    src_str += f"\n\t{src}"
                f.write(f"add_library({project.name} SHARED {src_str})\n")

            # Write project interfaces
            if project.interface_directories:
                interface_str:str =""
                for interface in project.interface_directories:
                    interface_str += f"\n\t$<BUILD_INTERFACE:{str(interface.resolve().as_posix())}> $<INSTALL_INTERFACE:{interface.name}>"
                f.write(f"target_include_directories({project.name} PUBLIC {interface_str})\n")

            # Write output name
            f.write(f"""                    
# {project.name} output name
set_target_properties({project.name} PROPERTIES OUTPUT_NAME {project.name})
target_compile_definitions({project.name} PRIVATE KISS_EXPORTS)
set_target_properties({project.name} PROPERTIES
    LIBRARY_OUTPUT_DIRECTORY   "{cmakelist_generate_context.target_output_directory().resolve().as_posix()}"
    RUNTIME_OUTPUT_DIRECTORY   "{cmakelist_generate_context.target_output_directory().resolve().as_posix()}"
)
""")
            # Write dependencies
            for dep_project in project.dependencies:
                dep_cmakelist_dir = CMakeContext.resolveCMakeListsDirectory(current_directory=cmakelist_generate_context.current_directory,
                                                                        platform_target=cmakelist_generate_context.platform_target,
                                                                        project=dep_project)
                dep_build_dir = CMakeContext.resolveProjectBuildDirectory(current_directory=cmakelist_generate_context.current_directory,
                                                                        platform_target=cmakelist_generate_context.platform_target,
                                                                        project=dep_project)
                f.write(f"""\n# Add {dep_project.name} dependency 
if(NOT TARGET {dep_project.name})
add_subdirectory("{dep_cmakelist_dir.resolve().as_posix()}" "{dep_build_dir.resolve().as_posix()}")
endif()
target_link_libraries({project.name} PRIVATE {dep_project.name})
target_include_directories({project.name} PRIVATE $<TARGET_PROPERTY:{dep_project.name},INTERFACE_INCLUDE_DIRECTORIES>)
""")        
                
            # Write package
            f.write(f"""
# Create alias
add_library({project.name}::{project.name} ALIAS {project.name})
include(CMakePackageConfigHelpers)
# Version file
write_basic_package_version_file(
    "${{CMAKE_CURRENT_BINARY_DIR}}/{project.name}ConfigVersion.cmake"
    VERSION 1.0.0
    COMPATIBILITY AnyNewerVersion
)

# Config file
configure_package_config_file(
    "${{CMAKE_CURRENT_LIST_DIR}}/{project.name}Config.cmake.in"
    "${{CMAKE_CURRENT_BINARY_DIR}}/{project.name}Config.cmake"
    INSTALL_DESTINATION {project.name}
)
# Installation
install(TARGETS {project.name}
    EXPORT {project.name}Targets
    RUNTIME DESTINATION {project.name}
    ARCHIVE DESTINATION {project.name}
    LIBRARY DESTINATION {project.name}
)
""")
            if project.interface_directories:
                for interface in project.interface_directories:
                    f.write(f"install(DIRECTORY {str(interface.resolve().as_posix())} DESTINATION {project.name})\n")

            f.write(f"""
install(EXPORT {project.name}Targets
    FILE {project.name}Targets.cmake
    NAMESPACE {project.name}::
    DESTINATION {project.name}/cmake
)
install(FILES
    "${{CMAKE_CURRENT_BINARY_DIR}}/{project.name}Config.cmake"
    "${{CMAKE_CURRENT_BINARY_DIR}}/{project.name}ConfigVersion.cmake"
    DESTINATION {project.name}/cmake
)
""")
        
        with open(cmakelist_generate_context.cmakelists_directory / f"{project.name}Config.cmake.in", "w", encoding="utf-8") as f:
            f.write(f"""@PACKAGE_INIT@

include("${{CMAKE_CURRENT_LIST_DIR}}/{project.name}Targets.cmake")
""")


    def generate_project(self, cmakelist_generate_context: CMakeListsGenerateContext) -> list[Project]:
        # Create the finger print and load it
        fingerprint = Fingerprint(cmakelist_generate_context.cmake_root_build_directory)
        fingerprint.load_or_create()

        # List flatten projet to generate
        project_list_to_generate = cmakelist_generate_context.project.topological_sort_projects()

        # Create a CMakeContext list that keep the same order as the topoligical sort
        # Example:
        # project_list_to_generate is  A < B < C < D < E
        # if A, C, E are unfresh (order is the same as project_list_to_generate)
        # unfreshlist is A < C < E 
        unfreshlist : list[Project] = list()
        unfreshflags: list[bool] = [False] * len(project_list_to_generate)
        for i, project in enumerate(project_list_to_generate):
            # If the project is not fresh anymore add it to refresh
            if not (fingerprint.is_fresh_file(CMakeContext.resolveCMakefile(current_directory=cmakelist_generate_context.directory, toolchain=cmakelist_generate_context.toolchain, project=project)) and fingerprint.is_fresh_file(project.file)):
                unfreshflags[i] = True
            else:
                # If one of the dependency of this project is unfresh, we also mark it as unfresh
                for deps_project in project.dependencies:
                    for unfresh_project in unfreshlist:
                        if unfresh_project is deps_project:
                            unfreshflags[i] = True
                            break
            if unfreshflags[i] == True:
                unfreshlist.append(project)

        # Generate all unfresh project in order
        if unfreshlist:
            console.print_step("⚙️  Generate CMakeLists.txt...")
            for project in unfreshlist:
                console.print_tips(f"  📝 {project.name}")
                cmakelist_generate_context.project = project
                is_multi_config = cmakelist_generate_context.toolchain.target.name == "x86_64-pc-windows-msvc"
                if is_multi_config:
                    self._generateMultiConfigProject(cmakelist_generate_context)
                else:
                    self._generateSingleConfigProject(cmakelist_generate_context)
                fingerprint.update_file(cmakelist_generate_context.cmakefile)
                fingerprint.update_file(project.file)
            fingerprint.save()
        else:
            console.print_step(f"✔️  All CMakeLists.txt are up-to-date")
        return unfreshlist

    def generate(self, cli_args: argparse.Namespace)-> list[CMakeContext]:
        cmakelist_generate_context = CMakeListsGenerateContext.from_cli_args(cli_args)
        return self.generate_project(cmakelist_generate_context=cmakelist_generate_context)