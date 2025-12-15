class Workspace:
    def __init__(self, name: str, description: str = ""):
        self.name = name
        self.description_ = description
        self.projects_ = []
        
    @property
    def name(self) -> str:
        return self.name
    
    @property
    def description(self) -> str:
        return self.description_
    
    @property
    def projects(self) -> list:
        return self.projects_
