
from project import Project, ProjectType

class Workspace(Project):
    def __init__(self, name:str, file: str, description: str = None, sources: list[str] = []):
        super().__init__(name=name, 
                         type=ProjectType.bin, 
                         file=file, 
                         description=description, 
                         prebuild=None, 
                         postbuild=None)
        self._projects = sources