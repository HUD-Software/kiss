from pathlib import Path
from generator import BaseGenerator
from modules import ModuleRegistry
from platform_target import SupportedTarget
from project import Project

class GenerateParams:
    def __init__(self, directory:Path, project_name:str, generator:BaseGenerator, platform_target:SupportedTarget):
        self.directory = directory
        self.project_name = project_name if project_name else Project.default_project(directory)
        self.generator = generator
        self.platform_target = platform_target

def cmd_generate(generateParams: GenerateParams):
    # If the no project name is present, search for the one loadable in the current directory
    import console, sys
    console.print_step("Generating build scripts...")
    ModuleRegistry.load_modules(generateParams.directory)
    project = ModuleRegistry.get(generateParams.project_name)
    if not project:
        console.print_error(f"Aucun projet trouvé dans le dossier {generateParams.directory}")
        sys.exit(2)
    
    import os, platform
    from compiler import Compiler

    console.print(f"directory = {generateParams.directory}")
    console.print(f"project_name = {generateParams.project_name}")
    console.print(f"generator = {generateParams.generator.name()}")
    console.print(f"platform_target = {generateParams.platform_target}")
    if platform.system() == "Windows":
        from toolset import VSToolset
        console.print(f"latest_toolset = {VSToolset.get_latest_toolset(Compiler.cl)}")

    # Create the directory where the CMakeLists.txt will be created
    build_directory = os.path.join(generateParams.directory, "build", generateParams.platform_target.name, generateParams.generator.name())
    os.makedirs(build_directory, exist_ok=True)

    # Generate CMakeLists.txt
    src_str = "\n".join(project.src)

    with open(os.path.join(build_directory, "CMakeLists.txt"), "w", encoding="utf-8") as f:
        f.write(f"""cmake_minimum_required(VERSION 3.18)

project({project.name} LANGUAGES CXX )

add_executable({project.name}
{src_str}
)
""")
        