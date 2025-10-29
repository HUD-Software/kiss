from enum import Enum

class ProjectType(str, Enum):
    bin = "bin"
    lib = "lib"
    dyn = "dyn"
    
    def manifestText(self, projectName: str) -> str:
        return f'@{self.manifestImportText()}("{projectName}")'
        
    def manifestImportText(self) -> str:
        if self is ProjectType.bin:
            return "Bin"
        elif self is ProjectType.lib:
            return "Lib"
        elif self is ProjectType.dyn:
            return "Dyn"
        else:
            raise ValueError(f"Unknown ProjectType: {self}")
        
