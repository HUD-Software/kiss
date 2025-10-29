
from project import Project, ProjectType
from typing import Callable

class DynProject(Project):
    def __init__(self, name:str, file: str, description: str = None, src: list[str] = [], interface: list[str] = [], prebuild: Callable[[], None] = None, postbuild: Callable[[], None] = None):
        super().__init__(name=name, 
                         type=ProjectType.dyn, 
                         file=file, 
                         description=description, 
                         prebuild=prebuild, 
                         postbuild=postbuild)
        self._src = src
        self._interface = interface

    @property
    def src(self) -> list[str]:
        return self._src 

    @property
    def interface(self) -> list[str]:
        return self._interface