import os
from pathlib import Path
from kiss_parser import KissParser
from project.project import Project


class CMakeDirectories:
    project_directory: Path
    cmakelists_directory : Path
    build_directory : Path

    def __init__(self, args : KissParser, project: Project):
        self.project_directory = Path(args.project_directory)
        self.build_directory = self.project_directory / "build" / args.platform_target.name / "cmake"
        self.cmakelists_directory =  self.build_directory / project.name
