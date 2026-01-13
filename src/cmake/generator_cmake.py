
from collections import defaultdict, deque
import os
from pathlib import Path
from typing import Optional
from cli import KissParser
from cmake.cmake_context import CMakeContext
from cmake.fingerprint import Fingerprint
import console
from generate import GenerateContext
from generator import BaseGenerator
from project import  BinProject, LibProject, DynProject, Project

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
    
    # # Create a tree of CMakeContext to generate
    # @staticmethod
    # def _topologicalSortProjects(project:Project) -> list[Project]:
    #     """
    #     Kahn Algorithm
    #     graph : dictionnaire {u: [v1, v2, ...]}
    #             représente les arêtes u -> v

    #     retourne :
    #     - liste des sommets dans un ordre topologique
    #     - lève une exception si le graphe contient un cycle
    #     """
    #     # 1. Collecte du sous-graphe (DFS)
    #     all_projects: set[Project] = set()
    #     visiting: set[Project] = set()

    #     def collect(project :Project, parent_project: Project):
    #         # Detect cyclic dependency
    #         if project in visiting:
    #             console.print_error(f"⚠️ Error: Cyclic dependency between '{project.name}' and '{parent_project.name}'")
    #             exit(1)
    #         visiting.add(project)

    #         # Visit the project only once
    #         if project in all_projects:
    #             return

    #         # Visit dependency
    #         for dep_project in project.dependencies:
    #             collect(dep_project, project)
                
    #         visiting.remove(project)
    #         all_projects.add(project)
    #     collect(project,  None)

    #     # 2. Construction du graphe inversé
    #     graph = defaultdict(list)     # dep -> [dependants]
    #     in_degree = defaultdict(int)  # nombre de dépendances restantes

    #     for project in all_projects:
    #         in_degree[project] = 0
    #     for project in all_projects:
    #         for dep_ctx in project.dependencies:
    #             graph[dep_ctx].append(project)
    #             in_degree[project] += 1

    #     # 3. Kahn : leaf en premier
    #     queue = deque(
    #         project for project in all_projects if in_degree[project] == 0
    #     )

    #     ordered = []

    #     while queue:
    #         project = queue.popleft()
    #         ordered.append(project)

    #         for dependant in graph[project]:
    #             in_degree[dependant] -= 1
    #             if in_degree[dependant] == 0:
    #                 queue.append(dependant)

    #     return ordered
    
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
""")
        
            # Write dependencies
            for cmake_dep_context in context.dependencies_context:
                f.write(f"""\n# Add {cmake_dep_context.project.name} dependency 
add_subdirectory("{cmake_dep_context.cmakelists_directory.resolve().as_posix()}" "{cmake_dep_context.cmakelists_directory.resolve().as_posix()}")
target_link_libraries({project.name} PRIVATE {cmake_dep_context.project.name})
target_include_directories({project.name} PRIVATE $<TARGET_PROPERTY:{cmake_dep_context.project.name},INTERFACE_INCLUDE_DIRECTORIES>)
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

        # Create the finger print and load it
        fingerprint = Fingerprint(CMakeContext.resolveBuildDirectory(generate_context.directory, generate_context.platform_target))
        fingerprint.load_or_create()

        # List flatten projet to generate
        project_list_to_generate = generate_context.project._topologicalSortProjects()

        # Create a CMakeContext list that keep the same order as the topoligical sort
        unfreshlist : set[CMakeContext] = set()
        for project in project_list_to_generate:
            context = CMakeContext(project_directory=generate_context.directory, 
                                   platform_target=generate_context.platform_target, 
                                   project=project)
            if not fingerprint.is_fresh_file(context.cmakefile):
                unfreshlist.add(context)
            for deps in project_list_to_generate:
                if deps in unfreshlist:
                    unfreshlist.add(context)

        # unfresh_list_to_generate : list[CMakeContext] = []
        # for project in project_list_to_generate:
        #     if project in unfreshlist:
        #         unfresh_list_to_generate.append(project)
        
        for ctx in unfreshlist:
            print(ctx.project.name)
            self._generateProject(ctx)
        # project_context_to_generate : list[CMakeContext] = []
        
        # for project_to_generate in project_list_to_generate:
        #     context = CMakeContext(project_directory=generate_context.directory, 
        #                            platform_target=generate_context.platform_target, 
        #                            project=project_to_generate)
            
        #     project_context_to_generate.append(context)
        #     # Add dependencies
        #     for project_to_generate in project_to_generate.dependencies:
        #             project_to_generate.dependencies


        # Add dependencies

        # for i, context in enumerate(project_context_to_generate):
        #     # The project is not fresh, add it to the generation list and it's parents
        #     if not fingerprint.is_fresh_file(context.cmakefile):

        # for project_to_generate in project_list_to_generate:
        #     context = CMakeContext(project_directory=generate_context.directory, 
        #                  platform_target=generate_context.platform_target, 
        #                  project=project_to_generate)

        #     # If the project is no more fresh regenerate it
        #     if not fingerprint.is_fresh_file(context.cmakefile):
        #         print(project_to_generate.name)
        #         self._generateProject(context)
        #         fingerprint.update_file(context.cmakefile)

        # fingerprint.save()

    def generate(self, generate_context: GenerateContext):
        self.generate_project(generate_context=generate_context)

        

                
            
    