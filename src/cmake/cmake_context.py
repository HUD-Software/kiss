from collections import defaultdict, deque
from pathlib import Path
from typing import Self
from cmake.fingerprint import Fingerprint
import console
from platform_target import PlatformTarget
from project import Project
import hashlib

class CMakeContext:
    project_directory: Path
    cmakelists_directory : Path
    build_directory : Path

    def __init__(self, project_directory: Path, platform_target: PlatformTarget, project: Project):
        self._project_directory = project_directory
        root_build_directory = self.resolveBuildDirectory(project_directory=project_directory, platform_target=platform_target)
        h = int.from_bytes(hashlib.sha256(str(project.file).encode()).digest()[:4], "little" )& 0xFFFFFFFF
        self._build_directory = root_build_directory / "build" /  f"{project.name}_{h:08x}"
        self._cmakelists_directory =  root_build_directory / "CMakeLists" / f"{project.name}_{h:08x}"
        self._project = project
        self._platform_target = platform_target
        self._cmakefile = self.cmakelists_directory / "CMakeLists.txt"
        self._cmakecache = self._build_directory / "CMakeCache.txt"
        self._dependencies_context : list[Self] = []
    
    @staticmethod
    def resolveBuildDirectory(project_directory: Path, platform_target: PlatformTarget) -> Path:
        return  project_directory / "build" / platform_target.name / "cmake"

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
    def cmakecache(self) -> Path:
        return self._cmakecache
    
    @property
    def project(self) -> Path:
        return self._project
    
    @property
    def platform_target(self) -> PlatformTarget:
        return self._platform_target
    
    @property
    def dependencies_context(self) -> list[Self]:
        return self._dependencies_context
    
    def _topologicalSortProjects(self) -> list[Self]:
        """
        Kahn Algorithm
        Retourne une liste de ce projet et ses dépendances triées par ordre de priorité ( Si A dépend de B, A est après B).

        @return :
        - liste des contexts dans l'ordre de dépendances
        - lève une exception si le graphe contient un cycle de dépendances
        """
        # 1. Collecte du sous-graphe (DFS)
        all_contexts: set[Self] = set()
        visiting: set[Self] = set()

        def collect(context :Self, parent_context: Self):
            # Detect cyclic dependency
            if context in visiting:
                console.print_error(f"⚠️ Error: Cyclic dependency between '{context.project.name}' and '{parent_context.project.name}'")
                exit(1)
            visiting.add(context)

            # Visit the context only once
            if context in all_contexts:
                return

            # Visit dependency
            for dep_context in context.dependencies_context:
                collect(dep_context, context)
                
            visiting.remove(context)
            all_contexts.add(context)
        collect(self,  None)

        # 2. Construction du graphe inversé
        graph = defaultdict(list)     # dep -> [dependants]
        in_degree = defaultdict(int)  # nombre de dépendances restantes

        for context in all_contexts:
            in_degree[context] = 0
        for context in all_contexts:
            for dep_ctx in context.dependencies_context:
                graph[dep_ctx].append(context)
                in_degree[context] += 1

        # 3. Kahn : leaf en premier
        queue = deque(
            context for context in all_contexts if in_degree[context] == 0
        )

        ordered = []

        while queue:
            context = queue.popleft()
            ordered.append(context)

            for dependant in graph[context]:
                in_degree[dependant] -= 1
                if in_degree[dependant] == 0:
                    queue.append(dependant)

        return ordered
