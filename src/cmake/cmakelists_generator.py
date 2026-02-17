
import argparse
import os
from pathlib import Path
from typing import Self
import asan
from cli import KissParser
from cmake.cmake_context import CMakeContext
from cmake.cmake_generator_name import CMakeGeneratorName
from cmake.fingerprint import Fingerprint
import console
from generate import GenerateContext
from generator import BaseGenerator
from project import  BinProject, LibProject, Project, ProjectType
from toolchain import Toolchain

class CMakeListsGenerateContext(GenerateContext):
    def __init__(self, directory:Path, project: Project, generator_name: str, toolchain: Toolchain, profile: str):
        super().__init__(directory=directory,project=project,generator_name=generator_name,toolchain=toolchain, profile=profile)
        self._cmake_context = CMakeContext(current_directory=directory, toolchain=toolchain, project=project)
        self._cmake_generator_name = CMakeGeneratorName.create(toolchain=toolchain)
    
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
    
    @property
    def toolchain(self) -> Toolchain:
        return self._cmake_context.toolchain
    
    @property
    def cmake_generator_name(self) -> CMakeGeneratorName: 
        return self._cmake_generator_name

    @project.setter
    def project(self, value):
        self._cmake_context = CMakeContext(current_directory=self._cmake_context.current_directory, toolchain=self._cmake_context.toolchain, project=value)
    
    @classmethod
    def create(cls, directory: Path, project_name: str, generator_name: str, toolchain: Toolchain, profile: str) -> Self :
        project_to_generate = super().find_target_project(directory, project_name)
        if not project_to_generate:
            console.print_error(f"No project found in {str(directory)}")
            exit(1)
        generator_name = generator_name if generator_name is not None else "cmake"
        return cls(directory=directory, project=project_to_generate, generator_name=generator_name, toolchain=toolchain, profile=profile)
    
    def is_feature_enabled(self, project: Project, feature_name: str) -> bool:
        return any(profile.is_feature_enabled(project_type=project.type, feature_name=feature_name) for profile in self.toolchain.compiler.profiles)
    
    def is_asan_enabled(self, project: Project):
        return self.is_feature_enabled(project, "ASAN") or self.is_asan_static_enabled(project) or self.is_asan_dynamic_enabled(project)
    
    def is_asan_static_enabled(self, project: Project):
        return self.is_feature_enabled(project, "ASAN_STATIC")
    
    def is_asan_dynamic_enabled(self, project: Project):
        return self.is_feature_enabled(project, "ASAN_DYNAMIC")
    
    def output_directory_for_config(self, config: str) -> str: 
        return self._cmake_context.output_directory_for_config(config)


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
    
    
    def _generateConfigProject(self, cmakelist_generate_context: CMakeListsGenerateContext):
        match cmakelist_generate_context.project.type:
            case ProjectType.bin:
                self._generateBinCMakeLists(cmakelist_generate_context)
            case ProjectType.lib:
                self._generateLibCMakeLists(cmakelist_generate_context)
            case ProjectType.dyn:
                self._generateDynCMakeLists(cmakelist_generate_context)       
    
    def _generateBinCMakeLists(self, cmakelist_generate_context: CMakeListsGenerateContext):
        project: BinProject = cmakelist_generate_context.project
        toolchain: Toolchain = cmakelist_generate_context.toolchain

        os.makedirs(cmakelist_generate_context.cmakelists_directory, exist_ok=True)
        # Write the CMakeLists.txt file
        with open(cmakelist_generate_context.cmakefile, "w", encoding="utf-8") as f:
             # Write CMake common
            f.write("cmake_minimum_required(VERSION 3.18)\n")
            
            # Write project description
            f.write(f"# {project.name} description\n")                   
            f.write(f"project({project.name} LANGUAGES CXX )\n")
            f.write("\n")
            
            # Create per profile configurations
            profile_name_list = list[(str,str)]()
            if cmakelist_generate_context.cmake_generator_name.is_multi_profile():
                for profile in toolchain.compiler.profiles:
                    profile_name_list.append((profile.name, profile.name.upper()))
                f.write(f"set(CMAKE_CONFIGURATION_TYPES {';'.join([p[0] for p in profile_name_list])} CACHE STRING \"\" FORCE)\n")

            for profile_name, upper_profile_name in profile_name_list:
                if( profile := toolchain.get_profile(profile_name)) is None:
                    console.print_warning(f"Profile {profile_name} not found in {self.name}")
                    exit(1)
                cxx_linker_flags = profile.linker_flags_for_project_type(project.type)
                f.write(f"set(CMAKE_EXE_LINKER_FLAGS_{upper_profile_name} \"{' '.join(cxx_linker_flags)}\" CACHE STRING \"\" FORCE)\n")
                cxx_compiler_flags = profile.compiler_flags_for_project_type(project.type)
                f.write(f"set(CMAKE_CXX_FLAGS_{upper_profile_name} \"{' '.join(cxx_compiler_flags)}\" CACHE STRING \"\" FORCE)\n")
                   

            # Write project sources
            if project.sources:
                normalized_src = self._resolve_sources(project.sources, project.name)
                src_str:str =""
                for src in normalized_src:
                    src_str += f"\n\t{src}"
                f.write(f"add_executable({project.name} {src_str})\n")
                f.write("\n")
            
            # Add ASAN if activated
            if cmakelist_generate_context.is_asan_enabled(project):
                if toolchain.compiler.is_clangcl_based():
                    if(asan_lib_path := asan.get_msvc_asan_lib_path(toolchain)) is None:
                            exit(1)
                    f.write(f"target_link_libraries({project.name} PRIVATE \"{asan_lib_path}\")\n")
                    f.write(f"target_link_options({project.name}  PRIVATE \"/WHOLEARCHIVE:{asan_lib_path}\")\n")
                        
                f.write(f"target_compile_definitions({project.name} PRIVATE _DISABLE_VECTOR_ANNOTATION)\n")
                f.write(f"target_compile_definitions({project.name} PRIVATE _DISABLE_STRING_ANNOTATION)\n")

            # Write output name
            f.write(f"# {project.name} output name\n")
            if cmakelist_generate_context.cmake_generator_name.is_multi_profile():
                f.write(f"set_target_properties({project.name} PROPERTIES OUTPUT_NAME {project.name})\n")
                f.write(f"set_target_properties({project.name} PROPERTIES\n")
                for profile_name, upper_profile_name in profile_name_list:
                    output_directory = cmakelist_generate_context.output_directory_for_config(profile_name)
                    f.write(f"  RUNTIME_OUTPUT_DIRECTORY_{upper_profile_name} \"{str(output_directory)}\"\n")
                f.write(")\n")                   
            else:
                f.write(f"set_target_properties({project.name} PROPERTIES OUTPUT_NAME {project.name})\n")
                f.write(f"set_target_properties({project.name} PROPERTIES\n")
                output_directory = cmakelist_generate_context.output_directory_for_config(cmakelist_generate_context.profile)
                f.write(f"  RUNTIME_OUTPUT_DIRECTORY   \"{output_directory}\"\n")
                f.write(")\n")
            f.write("\n")

            # Write dependencies
            for dep_project in project.dependencies:
                dep_cmakelist_dir = CMakeContext.resolveCMakeListsDirectory(current_directory=cmakelist_generate_context.current_directory,
                                                                        toolchain=toolchain,
                                                                        project=dep_project)
                dep_build_dir = CMakeContext.resolveProjectBuildDirectory(current_directory=cmakelist_generate_context.current_directory,
                                                                        toolchain=toolchain,
                                                                        project=dep_project)
                f.write(f"# Add {dep_project.name} dependency\n")
                f.write(f"if(NOT TARGET {dep_project.name})\n")
                f.write(f"  add_subdirectory(\"{dep_cmakelist_dir.resolve().as_posix()}\" \"{dep_build_dir.resolve().as_posix()}\")\n")
                f.write(f"endif()\n")
                f.write(f"target_link_libraries({project.name} PRIVATE {dep_project.name})\n") 
                f.write(f"target_include_directories({project.name} PRIVATE $<TARGET_PROPERTY:{dep_project.name},INTERFACE_INCLUDE_DIRECTORIES>)\n")
                f.write("\n")
                
    def _generateLibCMakeLists(self, cmakelist_generate_context: CMakeListsGenerateContext):
        project: LibProject = cmakelist_generate_context.project
        toolchain: Toolchain = cmakelist_generate_context.toolchain

        os.makedirs(cmakelist_generate_context.cmakelists_directory, exist_ok=True)
        # Write the CMakeLists.txt file
        with open(cmakelist_generate_context.cmakefile, "w", encoding="utf-8") as f:
           # Write CMake common
            f.write("cmake_minimum_required(VERSION 3.18)\n")

            # Write project description
            f.write(f"# {project.name} description\n")                   
            f.write(f"project({project.name} LANGUAGES CXX )\n")
            f.write("\n")

            # Create per profile configurations
            profile_name_list = list[(str,str)]()
            if cmakelist_generate_context.cmake_generator_name.is_multi_profile():
                for profile in toolchain.compiler.profiles:
                    profile_name_list.append((profile.name, profile.name.upper()))
                f.write(f"set(CMAKE_CONFIGURATION_TYPES {';'.join([p[0] for p in profile_name_list])} CACHE STRING \"\" FORCE)\n")

            for profile_name, upper_profile_name in profile_name_list:
                if( profile := toolchain.get_profile(profile_name)) is None:
                    console.print_warning(f"Profile {profile_name} not found in {self.name}")
                    exit(1)
                cxx_compiler_flags = profile.compiler_flags_for_project_type(project.type)
                f.write(f"set(CMAKE_CXX_FLAGS_{upper_profile_name} \"{' '.join(cxx_compiler_flags)}\" CACHE STRING \"\" FORCE)\n")

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
            f.write(f"# {project.name} output name\n")
            if cmakelist_generate_context.cmake_generator_name.is_multi_profile():
                f.write(f"set_target_properties({project.name} PROPERTIES OUTPUT_NAME {project.name})\n")
                f.write(f"set_target_properties({project.name} PROPERTIES\n")
                for profile_name, upper_profile_name in profile_name_list:
                    output_directory = cmakelist_generate_context.output_directory_for_config(profile_name)
                    f.write(f" ARCHIVE_OUTPUT_DIRECTORY_{upper_profile_name} \"{output_directory}\"\n")
                f.write(")\n")                   
            else:
                f.write(f"set_target_properties({project.name} PROPERTIES OUTPUT_NAME {project.name})\n")
                f.write(f"set_target_properties({project.name} PROPERTIES\n")
                output_directory = cmakelist_generate_context.output_directory_for_config(cmakelist_generate_context.profile)
                f.write(f"  ARCHIVE_OUTPUT_DIRECTORY   \"{output_directory}\"\n")
                f.write(")\n")
            f.write("\n")

            # Write dependencies
            for dep_project in project.dependencies:
                dep_cmakelist_dir = CMakeContext.resolveCMakeListsDirectory(current_directory=cmakelist_generate_context.current_directory,
                                                                        toolchain=toolchain,
                                                                        project=dep_project)
                dep_build_dir = CMakeContext.resolveProjectBuildDirectory(current_directory=cmakelist_generate_context.current_directory,
                                                                        toolchain=toolchain,
                                                                        project=dep_project)
                f.write(f"# Add {dep_project.name} dependency\n")
                f.write(f"if(NOT TARGET {dep_project.name})\n")
                f.write(f"  add_subdirectory(\"{dep_cmakelist_dir.resolve().as_posix()}\" \"{dep_build_dir.resolve().as_posix()}\")\n")
                f.write(f"endif()\n")
                f.write(f"target_link_libraries({project.name} PRIVATE {dep_project.name})\n") 
                f.write(f"target_include_directories({project.name} PRIVATE $<TARGET_PROPERTY:{dep_project.name},INTERFACE_INCLUDE_DIRECTORIES>)\n")
                f.write("\n")
                
            # Write package
            f.write("# Create alias\n")
            f.write(f"add_library({project.name}::{project.name} ALIAS {project.name})\n")
            f.write("include(CMakePackageConfigHelpers)\n")
            f.write("# Version file\n")
            f.write("write_basic_package_version_file(\n")
            f.write(f"  \"${{CMAKE_CURRENT_BINARY_DIR}}/{project.name}ConfigVersion.cmake\"\n")
            f.write("  VERSION 1.0.0\n")
            f.write("  COMPATIBILITY AnyNewerVersion\n")
            f.write(")\n")
            f.write("# Config file\n")
            f.write("configure_package_config_file(\n")
            f.write(f"  \"${{CMAKE_CURRENT_LIST_DIR}}/{project.name}Config.cmake.in\"\n")
            f.write(f"  \"${{CMAKE_CURRENT_BINARY_DIR}}/{project.name}Config.cmake\"\n")
            f.write(f"  INSTALL_DESTINATION lib/cmake/{project.name}\n")
            f.write(")\n")
            f.write("# Installation\n")
            f.write(f"install(TARGETS {project.name}\n")
            f.write(f" EXPORT {project.name}Targets\n")
            f.write(f" RUNTIME DESTINATION {project.name}\n") 
            f.write(f" ARCHIVE DESTINATION {project.name}\n")
            f.write(f" LIBRARY DESTINATION {project.name}\n") 
            f.write(")\n")

            if project.interface_directories:
                for interface in project.interface_directories:
                    f.write(f"install(DIRECTORY {str(interface.resolve().as_posix())} DESTINATION {project.name})\n")

            f.write("\n")
            f.write(f"# Install CMake config files\n")
            f.write(f"install(EXPORT {project.name}Targets\n")
            f.write(f" FILE {project.name}Targets.cmake\n")
            f.write(f" NAMESPACE {project.name}::\n")
            f.write(f" DESTINATION {project.name}/cmake\n")
            f.write(")\n")
            f.write(f"install(FILES\n")
            f.write(f" \"${{CMAKE_CURRENT_BINARY_DIR}}/{project.name}Config.cmake\"\n")
            f.write(f" \"${{CMAKE_CURRENT_BINARY_DIR}}/{project.name}ConfigVersion.cmake\"\n")
            f.write(f" DESTINATION {project.name}/cmake\n") 
            f.write(")\n")
        
        with open(cmakelist_generate_context.cmakelists_directory / f"{project.name}Config.cmake.in", "w", encoding="utf-8") as f:
            f.write(f"@PACKAGE_INIT@\n")
            f.write(f"include(\"${{CMAKE_CURRENT_LIST_DIR}}/{project.name}Targets.cmake\")\n")
            f.write(")\n")
    
    def _generateDynCMakeLists(self, cmakelist_generate_context: CMakeListsGenerateContext):
        project: LibProject = cmakelist_generate_context.project
        toolchain: Toolchain = cmakelist_generate_context.toolchain

        os.makedirs(cmakelist_generate_context.cmakelists_directory, exist_ok=True)
        # Write the CMakeLists.txt file
        with open(cmakelist_generate_context.cmakefile, "w", encoding="utf-8") as f:
           # Write CMake common
            f.write("cmake_minimum_required(VERSION 3.18)\n")

            # Write project description
            f.write(f"# {project.name} description\n")                   
            f.write(f"project({project.name} LANGUAGES CXX )\n")
            f.write("\n")
            
            # Create per profile configurations
            profile_name_list = list[(str,str)]()
            if cmakelist_generate_context.cmake_generator_name.is_multi_profile():
                for profile in toolchain.compiler.profiles:
                    profile_name_list.append((profile.name, profile.name.upper()))
                f.write(f"set(CMAKE_CONFIGURATION_TYPES {';'.join([p[0] for p in profile_name_list])} CACHE STRING \"\" FORCE)\n")
            for profile_name, upper_profile_name in profile_name_list:
                if( profile := toolchain.get_profile(profile_name)) is None:
                    console.print_warning(f"Profile {profile_name} not found in {self.name}")
                    exit(1)
                cxx_linker_flags = profile.linker_flags_for_project_type(project.type)
                f.write(f"set(CMAKE_SHARED_LINKER_FLAGS_{upper_profile_name} \"{' '.join(cxx_linker_flags)}\" CACHE STRING \"\" FORCE)\n")
                cxx_compiler_flags = profile.compiler_flags_for_project_type(project.type)
                f.write(f"set(CMAKE_CXX_FLAGS_{upper_profile_name} \"{' '.join(cxx_compiler_flags)}\" CACHE STRING \"\" FORCE)\n")

            # Write project sources
            if project.sources:
                normalized_src = self._resolve_sources(project.sources, project.name)
                src_str:str =""
                for src in normalized_src:
                    src_str += f"\n\t{src}"
                f.write(f"add_library({project.name} SHARED {src_str})\n")

            # Check ASAN 
            if cmakelist_generate_context.is_asan_enabled(project):
                if(asan_lib_path := asan.get_msvc_asan_dll_thunk_lib_path(cmakelist_generate_context.toolchain)) is None:
                    exit(1)
                f.write(f"target_link_libraries({project.name} PRIVATE \"{asan_lib_path}\")\n")
                

            #Write export definition for windows
            f.write(f"target_compile_definitions({project.name} PRIVATE {project.name.upper()}_EXPORTS)\n")

            # Write project interfaces
            if project.interface_directories:
                interface_str:str =""
                for interface in project.interface_directories:
                    interface_str += f"\n\t$<BUILD_INTERFACE:{str(interface.resolve().as_posix())}> $<INSTALL_INTERFACE:{interface.name}>"
                f.write(f"target_include_directories({project.name} PUBLIC {interface_str})\n")

            # Write output name
            f.write(f"# {project.name} output name\n")
            if cmakelist_generate_context.cmake_generator_name.is_multi_profile():
                f.write(f"set_target_properties({project.name} PROPERTIES OUTPUT_NAME {project.name})\n")
                f.write(f"set_target_properties({project.name} PROPERTIES\n")
                for profile_name, upper_profile_name in profile_name_list:
                    output_directory = cmakelist_generate_context.output_directory_for_config(profile_name)
                    f.write(f" LIBRARY_OUTPUT_DIRECTORY_{upper_profile_name} \"{output_directory}\"\n")
                    f.write(f" RUNTIME_OUTPUT_DIRECTORY_{upper_profile_name} \"{output_directory}\"\n")
                    f.write(f" ARCHIVE_OUTPUT_DIRECTORY_{upper_profile_name} \"{output_directory}\"\n")
                f.write(")\n")                   
            else:
                f.write(f"set_target_properties({project.name} PROPERTIES OUTPUT_NAME {project.name})\n")
                f.write(f"set_target_properties({project.name} PROPERTIES\n")
                output_directory = cmakelist_generate_context.output_directory_for_config(cmakelist_generate_context.profile)
                f.write(f"  LIBRARY_OUTPUT_DIRECTORY   \"{output_directory}\"\n")
                f.write(f"  RUNTIME_OUTPUT_DIRECTORY   \"{output_directory}\"\n")
                f.write(")\n")
            f.write("\n")

            # Write dependencies
            for dep_project in project.dependencies:
                dep_cmakelist_dir = CMakeContext.resolveCMakeListsDirectory(current_directory=cmakelist_generate_context.current_directory,
                                                                        toolchain=toolchain,
                                                                        project=dep_project)
                dep_build_dir = CMakeContext.resolveProjectBuildDirectory(current_directory=cmakelist_generate_context.current_directory,
                                                                        toolchain=toolchain,
                                                                        project=dep_project)
                f.write(f"# Add {dep_project.name} dependency\n")
                f.write(f"if(NOT TARGET {dep_project.name})\n")
                f.write(f"  add_subdirectory(\"{dep_cmakelist_dir.resolve().as_posix()}\" \"{dep_build_dir.resolve().as_posix()}\")\n")
                f.write(f"endif()\n")
                f.write(f"target_link_libraries({project.name} PRIVATE {dep_project.name})\n") 
                f.write(f"target_include_directories({project.name} PRIVATE $<TARGET_PROPERTY:{dep_project.name},INTERFACE_INCLUDE_DIRECTORIES>)\n")
                f.write("\n")
                
            # Write package
            f.write("# Create alias\n")
            f.write(f"add_library({project.name}::{project.name} ALIAS {project.name})\n")
            f.write("include(CMakePackageConfigHelpers)\n")
            f.write("# Version file\n")
            f.write("write_basic_package_version_file(\n")
            f.write(f"  \"${{CMAKE_CURRENT_BINARY_DIR}}/{project.name}ConfigVersion.cmake\"\n")
            f.write("  VERSION 1.0.0\n")
            f.write("  COMPATIBILITY AnyNewerVersion\n")
            f.write(")\n")
            f.write("# Config file\n")
            f.write("configure_package_config_file(\n")
            f.write(f"  \"${{CMAKE_CURRENT_LIST_DIR}}/{project.name}Config.cmake.in\"\n")
            f.write(f"  \"${{CMAKE_CURRENT_BINARY_DIR}}/{project.name}Config.cmake\"\n")
            f.write(f"  INSTALL_DESTINATION lib/cmake/{project.name}\n")
            f.write(")\n")
            f.write("# Installation\n")
            f.write(f"install(TARGETS {project.name}\n")
            f.write(f" EXPORT {project.name}Targets\n")
            f.write(f" RUNTIME DESTINATION {project.name}\n") 
            f.write(f" ARCHIVE DESTINATION {project.name}\n")
            f.write(f" LIBRARY DESTINATION {project.name}\n") 
            f.write(")\n")

            if project.interface_directories:
                for interface in project.interface_directories:
                    f.write(f"install(DIRECTORY {str(interface.resolve().as_posix())} DESTINATION {project.name})\n")

            f.write("\n")
            f.write(f"# Install CMake config files\n")
            f.write(f"install(EXPORT {project.name}Targets\n")
            f.write(f" FILE {project.name}Targets.cmake\n")
            f.write(f" NAMESPACE {project.name}::\n")
            f.write(f" DESTINATION {project.name}/cmake\n")
            f.write(")\n")
            f.write(f"install(FILES\n")
            f.write(f" \"${{CMAKE_CURRENT_BINARY_DIR}}/{project.name}Config.cmake\"\n")
            f.write(f" \"${{CMAKE_CURRENT_BINARY_DIR}}/{project.name}ConfigVersion.cmake\"\n")
            f.write(f" DESTINATION {project.name}/cmake\n") 
            f.write(")\n")
        
        with open(cmakelist_generate_context.cmakelists_directory / f"{project.name}Config.cmake.in", "w", encoding="utf-8") as f:
            f.write(f"@PACKAGE_INIT@\n")
            f.write(f"include(\"${{CMAKE_CURRENT_LIST_DIR}}/{project.name}Targets.cmake\")\n")
            f.write(")\n")

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
                self._generateConfigProject(cmakelist_generate_context)
                fingerprint.update_file(cmakelist_generate_context.cmakefile)
                fingerprint.update_file(project.file)
            fingerprint.save()
        else:
            console.print_step(f"✔️  All CMakeLists.txt are up-to-date")
        return unfreshlist

    def generate(self, cli_args: argparse.Namespace)-> list[CMakeContext]:
        cmakelist_generate_context = CMakeListsGenerateContext.from_cli_args(cli_args)
        return self.generate_project(cmakelist_generate_context=cmakelist_generate_context)