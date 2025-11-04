from project import Project,ProjectType
from typing import Callable

class LibProject(Project):
    def __init__(self, name:str, file: str, description: str = None, interface_directories: list[str] = [], sources: list[str] = [], prebuild: Callable[[], None] = None, postbuild: Callable[[], None] = None):
        super().__init__(name=name, 
                         type=ProjectType.lib, 
                         file=file, 
                         description=description, 
                         prebuild=prebuild, 
                         postbuild=postbuild)
        self._sources = sources
        self._interface_directories = interface_directories


    @property
    def sources(self) -> list[str]:
        return self._sources 

    @property
    def interface_directories(self) -> list[str]:
        return self._interface_directories
    
    def to_new_manifest(self) -> str:
        # Add Import statements
        content = f"from modules import Lib"
        if self.description:
            content += ", Description\n"
        else:
            content += "\n"
        #Add line separate after the import statements
        content += "\n"

        # Add decorator statement
        content += f'@Lib("{self.name}")\n'
        if self.description:
            content += f'@Description("{self.description}")\n'

        # Format class name properly (e.g. my_project → MyProject)
        content += f"class {Project.to_pascal(self.name)}:\n"

        # Add interface directories
        interface_dir_list = ",\n".join([f'"{interface}"' for interface in self.interface_directories])
        content += f"\n\t# List all interface directories in the INTERFACES variable\n"
        content += f"\tINTERFACES=[{interface_dir_list}]\n"

        # Add src files
        src_list = ",\n".join([f'"{src}"' for src in self.sources])
        content += f"\n\t# List all source files in the SOURCES variable\n"
        content += f"\tSOURCES=[{src_list}]\n"
    
        # Add prebuild and postbuild fonctions
        content += f"\n\t# Run python code before compilation\n"
        content += "\tdef prebuild(self):\n"
        content += f'\t\tprint("Préparation du build pour {self.name}")\n'
        content += f"\n\t# Run python code after compilation\n"
        content += "\tdef postbuild(self):\n"
        content += f'\t\tprint("Finalisation du build pour {self.name}")\n'
        return content