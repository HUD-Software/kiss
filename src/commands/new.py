import os
from pathlib import Path
import sys
import console

from project import BinProject, LibProject, DynProject, ProjectType

class NewParams:
    def __init__(self, directory:Path, project_name:str, project_type:ProjectType, coverage_enabled:str, sanitizer_enabled:str, description:str):
        self.directory = directory
        self.project_name = project_name
        self.project_type = project_type
        self.coverage_enabled = coverage_enabled
        self.sanitizer_enabled = sanitizer_enabled
        self.description = description

def cmd_new(newParams :NewParams):
    console.print_step(f"Creating a new {newParams.project_type} project named  `{newParams.project_name}`")

    #  Create the directory of the new project if not exists
    new_directory = os.path.join(newParams.directory, newParams.project_name)
    os.makedirs(new_directory, exist_ok=True)

    # Create the main python script file
    pyFile = os.path.join(new_directory, f"{newParams.project_name}.py")
    if os.path.exists(pyFile): 
        console.print_error(f"The file {pyFile} already exists !")
        sys.exit(2)

    # Write the content of the main python script file
    match newParams.project_type:
        case ProjectType.bin:
            new_project: BinProject = newBinProject(pyFile, new_directory, newParams)
            with open(pyFile, "w", encoding="utf-8") as f:
                    f.write(new_project.to_new_manifest())
        case ProjectType.lib:
            new_project = LibProject(name=newParams.project_name, description=newParams.description)
            with open(pyFile, "w", encoding="utf-8") as f:
                f.write(new_project.to_new_manifest())
        case ProjectType.dyn:
            new_project = DynProject(name=newParams.project_name, description=newParams.description)
            with open(pyFile, "w", encoding="utf-8") as f:
                f.write(new_project.to_new_manifest())
    
    console.print_success(f"Project {new_project.name} created successfully.")


def newBinProject(pyFile: str, new_directory: Path, newParams :NewParams):
        # Create the main.cpp file
        src_directory = os.path.join(os.path.join(new_directory, "src"))
        os.makedirs(src_directory, exist_ok=True)

        mainfile = os.path.join(src_directory, f"main.cpp")
        if os.path.exists(mainfile): 
            console.print_error(f"The file {mainfile} already exists !")
            sys.exit(2)

        bin = BinProject(name=newParams.project_name,file=pyFile,description= newParams.description, src=["src/main.cpp"])

        # Add simple hello world content
        with open(mainfile, "w", encoding="utf-8") as f:
            f.write('#include <iostream>\n\n')
            f.write('int main() {\n')
            f.write('    std::cout << "Hello, World!" << std::endl;\n')
            f.write('    return 0;\n')
            f.write('}\n')  


        return bin