
from project import Project, ProjectType
from typing import Callable

class BinProject(Project):
    def __init__(self, name:str, file: str, description: str = None, src: list[str] = [], prebuild: Callable[[], None] = None, postbuild: Callable[[], None] = None):
        super().__init__(name=name, 
                         type=ProjectType.bin, 
                         file=file, 
                         description=description, 
                         prebuild=prebuild, 
                         postbuild=postbuild)
        self._src = src

    @property
    def src(self) -> list[str]:
        return self._src

    def to_new_manifest(self) -> str:
        # Add Import statements
        content = f"from modules import Bin"
        if self.description:
            content += ", Description\n"
        else:
            content += "\n"
        #Add line separate after the import statements
        content += "\n"

        # Add decorator statement
        content += f'@Bin("{self.name}")\n'
        if self.description:
            content += f'@Description("{self.description}")\n'

        # Format class name properly (e.g. my_project → MyProject)
        content += f"class {Project.to_pascal(self.name)}:\n"

        # Add src files
        src_list = ",\n".join([f'"{src}"' for src in self.src])
        content += f"\tsrc=[{src_list}]\n"
    
        # Add prebuild and postbuild fonctions
        content += "\tdef prebuild(self):\n"
        content += f'\t\tprint("Préparation du build pour {self.name}")\n'
        content += "\n"
        content += "\tdef postbuild(self):\n"
        content += f'\t\tprint("Finalisation du build pour {self.name}")\n'
        return content
    
    