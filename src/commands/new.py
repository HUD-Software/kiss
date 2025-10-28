import os
from pathlib import Path
import sys
import console
import params
from projects import BinProject, LibProject, DynProject, ProjectType

def cmd_new(newParams :params.NewParams):
    console.print_step(f"Creating a new {newParams.project_type} project named {newParams.project_name}")

    #  Create the directory of the new project if not exists
    new_directory = os.path.join(newParams.directory, newParams.project_name)
    os.makedirs(new_directory, exist_ok=True)

    # Create the python script file
    pyFile = os.path.join(new_directory, f"{newParams.project_name}.py")
    if os.path.exists(pyFile): 
        console.print_error(f"The file {pyFile} already exists !")
        sys.exit(2)

    # Write the content of the python script file
    match newParams.project_type:
        case ProjectType.bin:
            new_project: BinProject = newBinProject(new_directory, newParams)
            with open(pyFile, "w", encoding="utf-8") as f:
                    f.write(new_project.to_new_manifest())

        case ProjectType.lib:
            lib = LibProject(name=newParams.project_name, description=newParams.description)
            with open(pyFile, "w", encoding="utf-8") as f:
                f.write(lib.to_new_manifest())
        case ProjectType.dyn:
            dyn = DynProject(name=newParams.project_name, description=newParams.description)
            with open(pyFile, "w", encoding="utf-8") as f:
                f.write(dyn.to_new_manifest())

def newBinProject(new_directory: Path, newParams :params.NewParams):
        # Create the main.cpp file
        src_directory = os.path.join(os.path.join(new_directory, "src"))
        os.makedirs(src_directory, exist_ok=True)

        mainfile = os.path.join(src_directory, f"main.cpp")
        if os.path.exists(mainfile): 
            console.print_error(f"The file {mainfile} already exists !")
            sys.exit(2)

        # Add simple hello world content
        with open(mainfile, "w", encoding="utf-8") as f:
            f.write('#include <iostream>\n\n')
            f.write('int main() {\n')
            f.write('    std::cout << "Hello, World!" << std::endl;\n')
            f.write('    return 0;\n')
            f.write('}\n')  

        bin = BinProject(name=newParams.project_name, description=newParams.description)
        bin.SRC_LIST.append("src/main.cpp")
        return bin