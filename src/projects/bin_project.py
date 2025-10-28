
import os
from pathlib import Path
import sys
import console
from projects.project_type import ProjectType


class BinProject:
    TYPE = ProjectType.bin
    SRC_EXTENSIONS = [".c", ".cpp"]
    SRC_LIST = []

    def __init__(self, name: str, description:str):
        self.name = name
        self.description = description

    def to_new_manifest(self) -> str:
        # Add Import statement
        content = f"from modules import Bin"
        if self.description:
            content += ", Description\n"

        # Empty line
        content += "\n"

        # Add decorator statement
        content += f'@Bin("{self.name}")\n'
        if self.description:
            content += f'@Description("{self.description}")\n'

        # Add class definition
        content += f"class {self.name.capitalize()}:\n"
        content += f"\tsrc=[{',\n'.join([f'\"{src}\"' for src in self.SRC_LIST])}]\n"
    
        content += "\tdef prebuild(self):\n"
        content += f'\t\tprint("Préparation du build pour {self.name}")\n'
        content += "\n"
        content += "\tdef postbuild(self):\n"
        content += f'\t\tprint("Finalisation du build pour {self.name}")\n'
        return content
    
    