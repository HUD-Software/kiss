from project import ProjectRegistry
from pathlib import Path


directory = Path.cwd() / "tests"
print(directory)
ProjectRegistry().load_projects_in_directory(path=directory, recursive=True)