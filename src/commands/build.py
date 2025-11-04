from pathlib import Path
from builder import BaseBuilder
from modules import ModuleRegistry
from platform_target import SupportedTarget
from project.project import Project

class BuildParams:
    def __init__(self, directory:Path, project_name:str, builder:BaseBuilder, platform_target:SupportedTarget):
        self.project_directory = directory
        self.project_name = project_name if project_name else Project.default_project(directory)
        self.builder = builder
        self.platform_target = platform_target

def cmd_build(buildParams: BuildParams):
    import console, sys

    ModuleRegistry.load_modules(buildParams.project_directory)
    project = ModuleRegistry.get(buildParams.project_name)
    if not project:
        console.print_error(f"Aucun projet trouvé dans le dossier {buildParams.project_directory}")
        sys.exit(2)
    
    console.print_step(f"Building project {project.name} in {project.file}...")

    import platform
    from compiler import Compiler

    console.print(f"directory = {buildParams.project_directory}")
    console.print(f"project_name = {buildParams.project_name}")
    console.print(f"builder = {buildParams.builder.name()}")
    console.print(f"platform_target = {buildParams.platform_target}")
    if platform.system() == "Windows":
        from toolset import VSToolset
        console.print(f"latest_toolset = {VSToolset.get_latest_toolset(Compiler.cl)}")

    buildParams.builder.build(buildParams, project)