import os
import sys

class NewArgs:
    def __init__(self, directory, name, type_):
        self._directory = directory
        self._name = name
        self._type = type_
        

    @property
    def directory(self):
        return self._directory

    @property
    def type(self):
        return self._type
    
    @property
    def name(self):
        return self._name


def cmd_new(newArgs):
    print(f"Creating a new {newArgs.type} project named {newArgs.name}")
    new_directory = os.path.join(newArgs.directory, newArgs.name)
    if os.path.isdir(new_directory):
        sys.exit(f"Erreur : le dossier {new_directory} existe déjà")

    os.makedirs(new_directory, exist_ok=True)


def createPyFile():
    