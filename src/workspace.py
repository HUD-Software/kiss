class Workspace:
    def __init__(self, name: str, description: str = ""):
        self._name = name
        self._description = description
        self._projects = []
        
    @property
    def name(self) -> str:
        return self._name
    
    @property
    def description(self) -> str:
        return self._description
    
    @property
    def projects(self) -> list:
        return self._projects
