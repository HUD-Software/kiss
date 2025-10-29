from project import ProjectType
class DynProject:
    TYPE = ProjectType.dyn
    def __init__(self, name: str, description:str=""):
        self.name = name
        self.description = description