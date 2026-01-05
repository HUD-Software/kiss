
import os
from pathlib import Path
from cli import KissParser
from cmake.cmake_context import CMakeContext
import console
from generate import GenerateContext
from generator import BaseGenerator
from project import  BinProject, LibProject, DynProject
from projectregistry import ProjectRegistry

class GeneratorCMake(BaseGenerator):
    @classmethod
    def add_cli_argument_to_parser(cls, parser: KissParser):
        parser.add_argument("-cov", "--coverage", help="enable code coverage", action='store_const', const=True)
        parser.add_argument("-san", "--sanitizer", help="enable sanitizer", action='store_const', const=True)


    def __init__(self, parser: KissParser = None):
        super().__init__("cmake", "Generate cmake CMakeLists.txt")
        self.coverage = getattr(parser, "coverage", False)
        self.sanitizer = getattr(parser, "sanitizer", False)

    def _split_path_with_pattern(self, path: Path):
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
    
    def _resolve_glob_source_path(self, base, pattern, rest):
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
                base_d, pattern_d, rest_d = self._split_path_with_pattern(src)
                all_files.update(self._resolve_glob_source_path(base_d, pattern_d, rest_d))
        return all_files
  
    def _resolve_sources(self, context:CMakeContext, src_list: list[Path]): 
        all_files = set()
        for src in src_list:
            base, pattern, rest = self._split_path_with_pattern(src)

            # We have a pattern like "**", "*" or "?"
            if pattern:
                all_files.update(self._resolve_glob_source_path(base, pattern, rest))
           
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
                cmakefile = self._generateBinCMakeLists(cmake_context, project)
            case LibProject() as project:
                cmakefile = self._generateLibCMakeLists(cmake_context, project)
            case DynProject() as project:
                cmakefile = self._generateDynCMakeLists(cmake_context, project)
        console.print_success(f"CMake {cmakefile} generated for {project.name}")


    def _generateBinCMakeLists(self, context:CMakeContext, project: BinProject) -> Path:
        os.makedirs(context.cmakelists_directory, exist_ok=True)
        project_name = project.name
        cmakefile = context.cmakelists_directory / "CMakeLists.txt"

        # Create context for each dependency
        cmake_dep_context_list = []
        for dependency in project.dependencies:
            cmake_dep_context_list.append(CMakeContext(project_directory=context.project_directory, platform_target=context.platform_target, project=dependency))

        # Write the CMakeLists.txt file
        with open(cmakefile, "w", encoding="utf-8") as f:
            # Write CMake common
            f.write("cmake_minimum_required(VERSION 3.18)\n")
            
            # Write project description
            f.write(f"""                    
# {project.name} description
project({project.name} LANGUAGES CXX )
set_target_properties({project_name} PROPERTIES OUTPUT_NAME {project.name})
""")
            # Write project sources
            if project.sources:
                normalized_src = self._resolve_sources(context, project.sources)
                src_str:str =""
                for src in normalized_src:
                    src_str += f"\n\t{src}"
                f.write(f"add_executable({project_name} {src_str})\n")

            # Write dependencies
            for cmake_dep_context in cmake_dep_context_list:
                cmake_dep_context : CMakeContext = cmake_dep_context
                f.write(f"""\n# Add {cmake_dep_context.project.name} dependency 
add_subdirectory("{cmake_dep_context.cmakelists_directory.resolve().as_posix()}")
target_link_libraries({project_name} PRIVATE {cmake_dep_context.project.name})
target_include_directories({project_name} PRIVATE $<TARGET_PROPERTY:{cmake_dep_context.project.name},INTERFACE_INCLUDE_DIRECTORIES>)
""")
                
        # Generate all dependency projects
        for cmake_dep_context in cmake_dep_context_list:
            self._generateProject(cmake_context=cmake_dep_context)
           
        return cmakefile

            
    def _generateLibCMakeLists(self, context:CMakeContext, project: LibProject):
        os.makedirs(context.cmakelists_directory, exist_ok=True)
        project_name = project.name
        cmakefile = context.cmakelists_directory / "CMakeLists.txt"

        # Create context for each dependency
        cmake_dep_context_list = []
        for dependency in project.dependencies:
            cmake_dep_context_list.append(CMakeContext(project_directory=context.project_directory, platform_target=context.platform_target, project=dependency))
    
        # Write the CMakeLists.txt file
        with open(cmakefile, "w", encoding="utf-8") as f:
            # Write CMake common
            f.write("cmake_minimum_required(VERSION 3.18)\n")

            # Write project description
            f.write(f"""                    
# {project.name} description
project({project.name} LANGUAGES CXX )
set_target_properties({project_name} PROPERTIES OUTPUT_NAME {project.name})
""")
            # Write project sources
            if project.sources:
                normalized_src = self._resolve_sources(context, project.sources)
                src_str:str =""
                for src in normalized_src:
                    src_str += f"\n\t{src}"
                f.write(f"add_library({project_name} STATIC {src_str})\n")

            # Write project interfaces
            if project.interface_directories:
                interface_str:str =""
                for interface in project.interface_directories:
                    interface_str += f"\n\t$<BUILD_INTERFACE:{str(interface.resolve().as_posix())}"
                f.write(f"target_include_directories({project_name} PUBLIC {interface_str})\n")

            # Write dependencies
            for cmake_dep_context in cmake_dep_context_list:
                cmake_dep_context : CMakeContext = cmake_dep_context
                f.write(f"""\n# Add {cmake_dep_context.project.name} dependency 
add_subdirectory("{cmake_dep_context.cmakelists_directory.resolve().as_posix()}")
target_link_libraries({project_name} PRIVATE {cmake_dep_context.project.name})
target_include_directories({project_name} PRIVATE $<TARGET_PROPERTY:{cmake_dep_context.project.name},INTERFACE_INCLUDE_DIRECTORIES>)
""")
        # Generate all dependency projects
        for cmake_dep_context in cmake_dep_context_list:
            self._generateProject(cmake_context=cmake_dep_context)
       
        return cmakefile
    
    def _generateDynCMakeLists(self, context:CMakeContext, project: LibProject):
        os.makedirs(context.cmakelists_directory, exist_ok=True)
        project_name = project.name
        cmakefile = context.cmakelists_directory / "CMakeLists.txt"
        # Create context for each dependency
        cmake_dep_context_list = []
        for dependency in project.dependencies:
            cmake_dep_context_list.append(CMakeContext(project_directory=context.project_directory, platform_target=context.platform_target, project=dependency))
    
        # Write the CMakeLists.txt file
        with open(cmakefile, "w", encoding="utf-8") as f:
            # Write CMake common
            f.write("cmake_minimum_required(VERSION 3.18)\n")

            # Write project description
            f.write(f"""                    
# {project.name} description
project({project.name} LANGUAGES CXX )
set_target_properties({project_name} PROPERTIES OUTPUT_NAME {project.name})
""")
            # Write project sources
            if project.sources:
                normalized_src = self._resolve_sources(context, project.sources)
                src_str:str =""
                for src in normalized_src:
                    src_str += f"\n\t{src}"
                f.write(f"add_library({project_name} SHARED {src_str})\n")

            # Write project interfaces
            if project.interface_directories:
                interface_str:str =""
                for interface in project.interface_directories:
                    interface_str += f"\n\t$<BUILD_INTERFACE:{str(interface.resolve().as_posix())}"
                f.write(f"target_include_directories({project_name} PUBLIC {interface_str})\n")

            # Write dependencies
            for cmake_dep_context in cmake_dep_context_list:
                cmake_dep_context : CMakeContext = cmake_dep_context
                f.write(f"""\n# Add {cmake_dep_context.project.name} dependency 
add_subdirectory("{cmake_dep_context.cmakelists_directory.resolve().as_posix()}")
target_link_libraries({project_name} PRIVATE {cmake_dep_context.project.name})
target_include_directories({project_name} PRIVATE $<TARGET_PROPERTY:{cmake_dep_context.project.name},INTERFACE_INCLUDE_DIRECTORIES>)
""")
        # Generate all dependency projects
        for cmake_dep_context in cmake_dep_context_list:
            self._generateProject(cmake_context=cmake_dep_context)
       

        return cmakefile

        # #if self.coverage:
        # coverage_cmake.generateCoverageCMakeFile(directories)
        # coverage_cmake.generateSanitizerCMakeFile(directories)

    def generate_project(self, generate_context: GenerateContext):
        context = CMakeContext(generate_context.directory, generate_context.platform_target, generate_context.project)
        self._generateProject(cmake_context=context)

    def generate(self, generate_context: GenerateContext):
        self.generate_project(generate_context=generate_context)

        

                
            
    