
from collections import deque
import os
from pathlib import Path
from typing import Optional
from cli import KissParser
from cmake.cmake_context import CMakeContext
import console
from generate import GenerateContext
from generator import BaseGenerator
from project import  BinProject, LibProject, DynProject

class GeneratorCMake(BaseGenerator):
    @classmethod
    def add_cli_argument_to_parser(cls, parser: KissParser):
        parser.add_argument("-cov", "--coverage", help="enable code coverage", action='store_const', const=True)
        parser.add_argument("-san", "--sanitizer", help="enable sanitizer", action='store_const', const=True)


    def __init__(self, parser: KissParser = None):
        super().__init__("cmake", "Generate cmake CMakeLists.txt")
        self.coverage = getattr(parser, "coverage", False)
        self.sanitizer = getattr(parser, "sanitizer", False)

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
    
    # Create a tree of CMakeContext to generate
    @staticmethod
    def _listProjectToGenerate(cmake_context :CMakeContext) -> list[CMakeContext]:
        for dependency_project in cmake_context.project.dependencies:
            for ctx in GeneratorCMake._listProjectToGenerate(CMakeContext(project_directory=cmake_context.project_directory, platform_target=cmake_context.platform_target, project=dependency_project, fingerprint=cmake_context.fingerprint)):
                cmake_context.dependencies_context.append(ctx)

        # If the current project if not fresh, we regenerate it
        # If one of the dependency is not fresh, we regenerate the dependency AND the current project
        # Else we generate nothing
        to_generate_list :list[CMakeContext] = []
        if not cmake_context.fingerprint.is_fresh_file(cmake_context.cmakefile):
            to_generate_list.append(cmake_context)
        elif cmake_context.dependencies_context:
            to_generate_list.append(cmake_context)
        return to_generate_list
    
    def _generateProject(self, cmake_context :CMakeContext):
        match cmake_context.project:
            case BinProject() as project:
                self._generateBinCMakeLists(cmake_context, project)
            case LibProject() as project:
                self._generateLibCMakeLists(cmake_context, project)
            case DynProject() as project:
                self._generateDynCMakeLists(cmake_context, project)
        cmake_context.fingerprint.update_file(cmake_context.cmakefile)       

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
""")
        
            # Write dependencies
            for cmake_dep_context in context.dependencies_context:
                f.write(f"""\n# Add {cmake_dep_context.project.name} dependency 
add_subdirectory("{cmake_dep_context.cmakelists_directory.resolve().as_posix()}" "{cmake_dep_context.cmakelists_directory.resolve().as_posix()}")
target_link_libraries({project.name} PRIVATE {cmake_dep_context.project.name})
target_include_directories({project.name} PRIVATE $<TARGET_PROPERTY:{cmake_dep_context.project.name},INTERFACE_INCLUDE_DIRECTORIES>)
""")
                
        context.fingerprint.update_file(context.cmakefile)

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
                    interface_str += f"\n\t$<BUILD_INTERFACE:{str(interface.resolve().as_posix())}"
                f.write(f"target_include_directories({project.name} PUBLIC {interface_str})\n")

            # Write output name
            f.write(f"""                    
# {project.name} output name
set_target_properties({project.name} PROPERTIES OUTPUT_NAME {project.name})
""")
            # Write dependencies
            for cmake_dep_context in context.dependencies_context:
                f.write(f"""\n# Add {cmake_dep_context.project.name} dependency 
add_subdirectory("{cmake_dep_context.cmakelists_directory.resolve().as_posix()}" "{cmake_dep_context.cmakelists_directory.resolve().as_posix()}")
target_link_libraries({project.name} PRIVATE {cmake_dep_context.project.name})
target_include_directories({project.name} PRIVATE $<TARGET_PROPERTY:{cmake_dep_context.project.name},INTERFACE_INCLUDE_DIRECTORIES>)
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
                    interface_str += f"\n\t$<BUILD_INTERFACE:{str(interface.resolve().as_posix())}"
                f.write(f"target_include_directories({project.name} PUBLIC {interface_str})\n")

            # Write output name
            f.write(f"""                    
# {project.name} output name
set_target_properties({project.name} PROPERTIES OUTPUT_NAME {project.name})
""")
            # Write dependencies
            for cmake_dep_context in context.dependencies_context:
                f.write(f"""\n# Add {cmake_dep_context.project.name} dependency 
add_subdirectory("{cmake_dep_context.cmakelists_directory.resolve().as_posix()}" "{cmake_dep_context.cmakelists_directory.resolve().as_posix()}")
target_link_libraries({project.name} PRIVATE {cmake_dep_context.project.name})
target_include_directories({project.name} PRIVATE $<TARGET_PROPERTY:{cmake_dep_context.project.name},INTERFACE_INCLUDE_DIRECTORIES>)
""")        
        context.fingerprint.update_file(context.cmakefile)

    @staticmethod
    def print_generated(context):
        stack = [(context, 0)]

        while stack:
            ctx, depth = stack.pop()
            indent = "  " * depth
            console.print_success(f"{indent}- {ctx.cmakefile.relative_to(ctx.project_directory)} generated for {ctx.project.name}")

            # Ajouter les enfants à la pile
            for child in reversed(ctx.dependencies_context):
                stack.append((child, depth + 1))

    @staticmethod
    def print_tree(node: CMakeContext, prefix: str = "", is_last: bool = True, is_root: bool = True):
        """Affiche un arbre avec ├─, └─ et │, sans symbole pour la racine"""
        if is_root:
            console.print_success(f"{node.cmakefile.relative_to(node.project_directory)} generated for {node.project.name}")
        else:
            branch = "└─" if is_last else "├─"
            console.print_success(f"{prefix}{branch} {node.cmakefile.relative_to(node.project_directory)} generated for {node.project.name}")

        children = node.dependencies_context
        for i, child in enumerate(children):
            new_prefix = prefix + ("│  " if not is_last else "")
            GeneratorCMake.print_tree(child, new_prefix, i == len(children) - 1, is_root=False)

    def generate_project(self, generate_context: GenerateContext):
        console.print_step("Generate CMakeLists.txt...")
        context = CMakeContext(project_directory=generate_context.directory, 
                               platform_target=generate_context.platform_target, 
                               project=generate_context.project,
                               fingerprint=None)
        context.fingerprint.load_or_create()
        to_generate = self._listProjectToGenerate(cmake_context=context)
        for generated_cmakecontext in to_generate:
            generated_list : list[CMakeContext] = generated_cmakecontext.flatten_leaf_to_root()
            for to_generate in generated_list:
                print(to_generate.project.name)
                self._generateProject(to_generate)
            GeneratorCMake.print_tree(generated_cmakecontext)

        context.fingerprint.save()

    def generate(self, generate_context: GenerateContext):
        self.generate_project(generate_context=generate_context)

        

                
            
    