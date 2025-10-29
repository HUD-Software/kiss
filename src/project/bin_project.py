
from project import ProjectType, Project


class BinProject:
    TYPE = ProjectType.bin
    SRC_LIST = []

    def __init__(self, name: str, description:str):
        self.name = name
        self.description = description

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
        src_list = ",\n".join([f'"{src}"' for src in self.SRC_LIST])
        content += f"\tsrc=[{src_list}]\n"
    
        # Add prebuild and postbuild fonctions
        content += "\tdef prebuild(self):\n"
        content += f'\t\tprint("Préparation du build pour {self.name}")\n'
        content += "\n"
        content += "\tdef postbuild(self):\n"
        content += f'\t\tprint("Finalisation du build pour {self.name}")\n'
        return content
    
    