from config import Config
from platform_target import PlatformTarget
from project.project import Project
from project.project_type import ProjectType

EXTENSIONS = {
        (PlatformTarget.x86_64_pc_windows_msvc, ProjectType.bin): "exe",
        (PlatformTarget.x86_64_pc_windows_msvc, ProjectType.lib): "lib",
        (PlatformTarget.x86_64_pc_windows_msvc, ProjectType.dyn): "dll",
    }

class Artifact:
    
    def __init__(self,  project: Project, platform_target: PlatformTarget, config : Config):
        import platform
        match platform.system():
            case "Windows":
                self._name = project.name + "." + Artifact.extension(platform_target, project.type)
            case _: 
                raise ValueError(f"Plateforme non supportée: { platform.system()}")

    @property
    def name(self) -> str:
        return self._name
    
    def extension(platform_target : PlatformTarget, type : ProjectType) -> str:
        try:
            return EXTENSIONS[(platform_target, type)]
        except KeyError:
            raise ValueError(f"Combinaison non supportée: {platform_target}, {type}")

