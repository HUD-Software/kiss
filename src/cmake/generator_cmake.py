
import os
from pathlib import Path
from cli import KissParser
from cmake.cmake_context import CMakeContext
from cmake.fingerprint import Fingerprint
from config import Config
import console
from generate import GenerateContext
from generator import BaseGenerator
from project import  BinProject, LibProject, DynProject, Project

class GeneratorCMake(BaseGenerator):
    @classmethod
    def add_cli_argument_to_parser(cls, parser: KissParser):
        pass
        # parser.add_argument("-cov", "--coverage", help="enable code coverage", action='store_const', const=True)
        # parser.add_argument("-san", "--sanitizer", help="enable sanitizer", action='store_const', const=True)


    def __init__(self, parser: KissParser = None):
        super().__init__("cmake", "Generate cmake CMakeLists.txt")
        # self.coverage = getattr(parser, "coverage", False)
        # self.sanitizer = getattr(parser, "sanitizer", False)

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
                base_d, pattern_d, rest_d = GeneratorCMake._split_path_with_pattern(src)
                all_files.update(GeneratorCMake._resolve_glob_source_path(base_d, pattern_d, rest_d))
        return all_files
    
    @staticmethod
    def _resolve_sources(context:CMakeContext, src_list: list[Path]): 
        all_files = set()
        for src in src_list:
            base, pattern, rest = GeneratorCMake._split_path_with_pattern(src)

            # We have a pattern like "**", "*" or "?"
            if pattern:
                all_files.update(GeneratorCMake._resolve_glob_source_path(base, pattern, rest))
           
            #  There is not pattern and it's a file, just add it
            else:
                if not src.exists():
                    console.print_error(f"Error when generating CMake file for {context.project.name}: file {src} not found")
                    exit(1)
                if base.is_file(): 
                    all_files.add(f'"{base.resolve().as_posix()}"')

        return list(all_files)
    
    def _generateProject(self, cmake_context :CMakeContext):
        match cmake_context.project:
            case BinProject() as project:
                self._generateBinCMakeLists(cmake_context, project)
            case LibProject() as project:
                self._generateLibCMakeLists(cmake_context, project)
            case DynProject() as project:
                self._generateDynCMakeLists(cmake_context, project)       

    def _generateBinCMakeLists(self, context:CMakeContext, project: BinProject):
        os.makedirs(context.cmakelists_directory, exist_ok=True)
        # Write the CMakeLists.txt file
        with open(context.cmakefile, "w", encoding="utf-8") as f:
            # Write CMake common
            f.write("cmake_minimum_required(VERSION 3.18)\n")
            
            # Write project description
            f.write(f"""                    
# {project.name} description
project({project.name} LANGUAGES CXX )
""")
            # Write project sources
            if project.sources:
                normalized_src = self._resolve_sources(context, project.sources)
                src_str:str =""
                for src in normalized_src:
                    src_str += f"\n\t{src}"
                f.write(f"add_executable({project.name} {src_str})\n")

            # Write output name
            f.write(f"""                    
# {project.name} output name
set_target_properties({project.name} PROPERTIES OUTPUT_NAME {project.name})
set_target_properties({project.name} PROPERTIES
    RUNTIME_OUTPUT_DIRECTORY_DEBUG   "{context.output_directory(Config(is_release=False, is_debug_info=False)).resolve().as_posix()}"
    RUNTIME_OUTPUT_DIRECTORY_RELEASE "{context.output_directory(Config(is_release=True, is_debug_info=False)).resolve().as_posix()}"
    RUNTIME_OUTPUT_DIRECTORY_RELWITHDEBINFO "{context.output_directory(Config(is_release=True, is_debug_info=True)).resolve().as_posix()}"
)
target_link_options({project.name} PRIVATE /SUBSYSTEM:CONSOLE)
""")
            # Write dependencies
            for dep_project in project.dependencies:
                dep_ctx = CMakeContext(current_directory=context.current_directory, 
                            platform_target=context.platform_target, 
                            project=dep_project)
                f.write(f"""\n# Add {dep_project.name} dependency 
if(NOT TARGET {dep_project.name})
add_subdirectory("{dep_ctx.cmakelists_directory.resolve().as_posix()}" "{dep_ctx.build_directory.resolve().as_posix()}")
endif()
target_link_libraries({project.name} PRIVATE {dep_project.name})
target_include_directories({project.name} PRIVATE $<TARGET_PROPERTY:{dep_project.name},INTERFACE_INCLUDE_DIRECTORIES>)
""")

    def _generateLibCMakeLists(self, context:CMakeContext, project: LibProject):
        os.makedirs(context.cmakelists_directory, exist_ok=True)
        # Write the CMakeLists.txt file
        with open(context.cmakefile, "w", encoding="utf-8") as f:
            # Write CMake common
            f.write("cmake_minimum_required(VERSION 3.18)\n")

            # Write project description
            f.write(f"""                    
# {project.name} description
project({project.name} LANGUAGES CXX )
""")
            # Write project sources
            if project.sources:
                normalized_src = self._resolve_sources(context, project.sources)
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
    ARCHIVE_OUTPUT_DIRECTORY_DEBUG   "{context.output_directory(Config(is_release=False, is_debug_info=False)).resolve().as_posix()}"
    ARCHIVE_OUTPUT_DIRECTORY_RELEASE "{context.output_directory(Config(is_release=True, is_debug_info=False)).resolve().as_posix()}"
    ARCHIVE_OUTPUT_DIRECTORY_RELWITHDEBINFO "{context.output_directory(Config(is_release=True, is_debug_info=True)).resolve().as_posix()}"
)
""")
            # Write dependencies
            for dep_project in project.dependencies:
                dep_ctx = CMakeContext(current_directory=context.current_directory, 
                            platform_target=context.platform_target, 
                            project=dep_project)
                f.write(f"""\n# Add {dep_project.name} dependency 
if(NOT TARGET {dep_project.name})
add_subdirectory("{dep_ctx.cmakelists_directory.resolve().as_posix()}" "{dep_ctx.build_directory.resolve().as_posix()}")
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
        
        with open(context.cmakelists_directory / f"{project.name}Config.cmake.in", "w", encoding="utf-8") as f:
            f.write(f"""@PACKAGE_INIT@

include("${{CMAKE_CURRENT_LIST_DIR}}/{project.name}Targets.cmake")
""")
                
    def _generateDynCMakeLists(self, context:CMakeContext, project: LibProject):
        os.makedirs(context.cmakelists_directory, exist_ok=True)
        # Write the CMakeLists.txt file
        with open(context.cmakefile, "w", encoding="utf-8") as f:
            # Write CMake common
            f.write("cmake_minimum_required(VERSION 3.18)\n")

            # Write project description
            f.write(f"""                    
# {project.name} description
project({project.name} LANGUAGES CXX )
""")
            # Write project sources
            if project.sources:
                normalized_src = self._resolve_sources(context, project.sources)
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
    LIBRARY_OUTPUT_DIRECTORY_DEBUG   "{context.output_directory(Config(is_release=False, is_debug_info=False)).resolve().as_posix()}"
    LIBRARY_OUTPUT_DIRECTORY_RELEASE "{context.output_directory(Config(is_release=True, is_debug_info=False)).resolve().as_posix()}"
    LIBRARY_OUTPUT_DIRECTORY_RELWITHDEBINFO "{context.output_directory(Config(is_release=True, is_debug_info=True)).resolve().as_posix()}"
    RUNTIME_OUTPUT_DIRECTORY_DEBUG   "{context.output_directory(Config(is_release=False, is_debug_info=False)).resolve().as_posix()}"
    RUNTIME_OUTPUT_DIRECTORY_RELEASE "{context.output_directory(Config(is_release=True, is_debug_info=False)).resolve().as_posix()}"
    RUNTIME_OUTPUT_DIRECTORY_RELWITHDEBINFO "{context.output_directory(Config(is_release=True, is_debug_info=True)).resolve().as_posix()}"
)
""")
            # Write dependencies
            for dep_project in project.dependencies:
                dep_ctx = CMakeContext(project_directory=context.project_directory, 
                            platform_target=context.platform_target, 
                            project=dep_project)
                f.write(f"""\n# Add {dep_project.name} dependency 
if(NOT TARGET {dep_project.name})
add_subdirectory("{dep_ctx.cmakelists_directory.resolve().as_posix()}" "{dep_ctx.build_directory.resolve().as_posix()}")
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
        
        with open(context.cmakelists_directory / f"{project.name}Config.cmake.in", "w", encoding="utf-8") as f:
            f.write(f"""@PACKAGE_INIT@

include("${{CMAKE_CURRENT_LIST_DIR}}/{project.name}Targets.cmake")
""")
            
    def generate_project(self, generate_context: GenerateContext) -> list[Project]:
        # Create the finger print and load it
        fingerprint = Fingerprint(CMakeContext.resolveCMakeBuildDirectory(generate_context.directory, generate_context.platform_target))
        fingerprint.load_or_create()

        # List flatten projet to generate
        project_list_to_generate = generate_context.project.topological_sort_projects()

        # Create a CMakeContext list that keep the same order as the topoligical sort
        # Example:
        # project_list_to_generate is  A < B < C < D < E
        # if A, C, E are unfresh (order is the same as project_list_to_generate)
        # unfreshlist is A < C < E 
        unfreshlist : list[Project] = list()
        unfreshflags: list[bool] = [False] * len(project_list_to_generate)
        for i, project in enumerate(project_list_to_generate):
            # If the project is not fresh anymore add it to refresh
            if not (fingerprint.is_fresh_file(CMakeContext.resolveCMakefile(current_directory=generate_context.directory, platform_target=generate_context.platform_target, project=project)) and fingerprint.is_fresh_file(project.file)):
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
                ctx = CMakeContext(current_directory=generate_context.directory, platform_target=generate_context.platform_target, project=project)
                self._generateProject(ctx)
                fingerprint.update_file(ctx.cmakefile)
                fingerprint.update_file(project.file)
            fingerprint.save()
        else:
            console.print_step(f"✔️  All CMakeLists.txt are up-to-date")
        return unfreshlist

    def generate(self, generate_context: GenerateContext)-> list[CMakeContext]:
        return self.generate_project(generate_context=generate_context)

        

                
            
    