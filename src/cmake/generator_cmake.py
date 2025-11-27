
import os
from pathlib import Path
import sys
from cmake.cmake_directories import CMakeDirectories
from cmake import coverage_cmake
import console
from generator import GeneratorRegistry
from kiss_parser import KissParser
from modules import ModuleRegistry
from platform_target import PlatformTarget
from project import Project, BinProject, LibProject, DynProject, Workspace

@GeneratorRegistry.register("cmake", "Generate cmake CMakeLists.txt")
class GeneratorCMake:
     
    @classmethod
    def add_cli_argument_to_parser(cls, parser: KissParser):
        parser.add_argument("-cov", "--coverage", help="enable code coverage", action='store_const', const=True)
        parser.add_argument("-san", "--sanitizer", help="enable sanitizer", action='store_const', const=True)


    def __init__(self, parser: KissParser = None):
        self.coverage = getattr(parser, "coverage", False)
        self.sanitizer = getattr(parser, "sanitizer", False)

    def __resolve_sources(self, src_list: list[str], project_directory): 
        import glob
        result = []
        for src in src_list:
            # Nettoyage des caractères d'échappement et normalisation
            clean = src.encode('unicode_escape').decode().replace("\\", "/")

            # Chemin relatif à project_dir si nécessaire
            path = Path(clean)
            if not path.is_absolute():
                path = project_directory / path

            # Converti en str avec / pour glob
            pattern = str(path)

            # Ajouter ** si le motif contient **
            matches = glob.glob(pattern)

            for match in matches:
                path_str = str(Path(match).resolve()).replace("\\", "/")
                result.append(f'"{path_str}"')
        return result
    
    def __generateBinCMakeLists(self, directories:CMakeDirectories, project: BinProject) -> Path:
        os.makedirs(directories.cmakelists_directory, exist_ok=True)
        # Generate CMakeLists.txt
        normalized_src = self.__resolve_sources(project.sources, directories.project_directory)
        src_str = "\n".join(normalized_src)
        normalized_project_name = Project.to_pascal(project.name)
        cmakefile = directories.cmakelists_directory / "CMakeLists.txt"
        with open(cmakefile, "w", encoding="utf-8") as f:
            f.write(f"""cmake_minimum_required(VERSION 3.18)

project(\"{project.name}\" LANGUAGES CXX )

add_executable({normalized_project_name}
{src_str}
)
set_target_properties({normalized_project_name} PROPERTIES OUTPUT_NAME \"{project.name}\")
""")
        return cmakefile

            
    def __generateLibCMakeLists(self, directories:CMakeDirectories, project: LibProject):
        os.makedirs(directories.cmakelists_directory, exist_ok=True)
        # Generate CMakeLists.txt
        normalized_src = self.__resolve_sources(project.sources, directories.project_directory)
        src_str = "\n".join(normalized_src)
        normalized_interface = self.__resolve_sources(project.interface_directories, directories.project_directory)
        interface_str = "\n".join(normalized_interface)
        normalized_project_name = Project.to_pascal(project.name)
        cmakefile = directories.cmakelists_directory / "CMakeLists.txt"
        with open(cmakefile, "w", encoding="utf-8") as f:
            f.write(f"""cmake_minimum_required(VERSION 3.18)

project(\"{project.name}\" LANGUAGES CXX )

add_library({normalized_project_name} STATIC 
{src_str}
)
target_include_directories({normalized_project_name} PUBLIC {interface_str})

set_target_properties({normalized_project_name} PROPERTIES OUTPUT_NAME \"{project.name}\")
""")
        return cmakefile
            
    def __generateDynCMakeLists(self, directories:CMakeDirectories, project: LibProject):
        os.makedirs(directories.cmakelists_directory, exist_ok=True)
        # Generate CMakeLists.txt
        normalized_src = self.__resolve_sources(project.sources, directories.project_directory)
        src_str = "\n".join(normalized_src)
        normalized_interface = self.__resolve_sources(project.interface_directories, directories.project_directory)
        interface_str = "\n".join(normalized_interface)
        normalized_project_name = Project.to_pascal(project.name)
        cmakefile = directories.cmakelists_directory / "CMakeLists.txt"
        with open(cmakefile, "w", encoding="utf-8") as f:
            f.write(f"""cmake_minimum_required(VERSION 3.18)

project(\"{project.name}\" LANGUAGES CXX )

add_library({normalized_project_name} SHARED 
{src_str}
)
target_include_directories({normalized_project_name} PUBLIC {interface_str})

set_target_properties({normalized_project_name} PROPERTIES OUTPUT_NAME \"{project.name}\")
""")
        return cmakefile

        # #if self.coverage:
        # coverage_cmake.generateCoverageCMakeFile(directories)
        # coverage_cmake.generateSanitizerCMakeFile(directories)

    def generate_project(self, project_directory: Path, platform_target:PlatformTarget, project: Project):
        directories = CMakeDirectories(project_directory, platform_target,project)
        match project:
            case BinProject() as project:
                cmakefile = self.__generateBinCMakeLists(directories, project)
                console.print_success(f"CMake {cmakefile} generated for {project.name}")
            case LibProject() as project:
                cmakefile = self.__generateLibCMakeLists(directories, project)
                console.print_success(f"CMake {cmakefile} generated for {project.name}")
            case DynProject() as project:
                cmakefile = self.__generateDynCMakeLists(directories, project)
                console.print_success(f"CMake {cmakefile} generated for {project.name}")
            case Workspace() as project :
                for project_path in project.project_paths:
                    ModuleRegistry.load_modules(project_path)
                    project = ModuleRegistry.get_from_dir(project_path)
                    if not project:
                        console.print_error(f"Project {project_path} not found.")
                        sys.exit(2)
                    self.generate_project(project.directory, platform_target, project)

    def generate(self, args : KissParser, project: Project):
        self.generate_project(project_directory = args.project_directory,
                        platform_target= args.platform_target,
                        project=project)

        

                
            
    