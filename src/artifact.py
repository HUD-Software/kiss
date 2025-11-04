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
        self._platform_target = platform_target
        self._config = config
        self._project = project
        
        
    @property
    def extension(self) -> str:
        if not getattr(self, "_extension", None):
            try:
                self._extension = EXTENSIONS[(self._platform_target, self._project.type)]
            except KeyError:
                raise ValueError(f"Combinaison non supportée: {self._platform_target}, {type}")
        return self._extension

    @property
    def name(self) -> str:
        if not getattr(self, "_name", None):
            import platform
            match platform.system():
                case "Windows":
                    self._name =  self._project.name + "." + self.extension
                case _: 
                    raise ValueError(f"Plateforme non supportée: { platform.system()}")
        return self._name
    
    @property
    def is_executable(self) -> bool:
        return self.extension == "exe"
    
  
