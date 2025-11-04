import os
from pathlib import Path
import sys
import console
from kiss_parser import KissParser
from project import BinProject, LibProject, DynProject, ProjectType

class NewParams:
    def __init__(self, args: KissParser):
        self.project_directory:Path=Path(args.directory)
        self.project_name:str = args.project_name
        self.project_type:ProjectType = ProjectType(args.type)
        self.coverage_enabled:bool =args.coverage
        self.sanitizer_enabled:bool= args.sanitizer
        self.description:str= args.description

def cmd_new(new_params :NewParams):

    console.print_step(f"Creating a new {new_params.project_type} project named  `{new_params.project_name}`")

    #  Create the directory of the new project if not exists
    new_directory = os.path.join(new_params.project_directory, new_params.project_name)
    os.makedirs(new_directory, exist_ok=True)

    # Create the main python script file
    file = os.path.join(new_directory, f"{new_params.project_name}.py")
    if os.path.exists(file): 
        console.print_error(f"The file {file} already exists !")
        sys.exit(2)

    # Write the content of the main python script file
    match new_params.project_type:
        case ProjectType.bin:
            new_project: BinProject = newBinProject(file, new_directory, new_params)
            with open(file, "w", encoding="utf-8") as f:
                    f.write(new_project.to_new_manifest())
        case ProjectType.lib:
            new_project = LibProject(name=new_params.project_name, description=new_params.description)
            with open(file, "w", encoding="utf-8") as f:
                f.write(new_project.to_new_manifest())
        case ProjectType.dyn:
            new_project = DynProject(name=new_params.project_name, description=new_params.description)
            with open(file, "w", encoding="utf-8") as f:
                f.write(new_project.to_new_manifest())
    
    console.print_success(f"Project {new_project.name} created successfully.")


def newBinProject(file: str, new_directory: Path, new_params :NewParams):
        # Create the main.cpp file
        src_directory = os.path.join(os.path.join(new_directory, "src"))
        os.makedirs(src_directory, exist_ok=True)

        mainfile = os.path.join(src_directory, f"main.cpp")
        if os.path.exists(mainfile): 
            console.print_error(f"The file {mainfile} already exists !")
            sys.exit(2)

        bin = BinProject(name=new_params.project_name,file=file,description= new_params.description, src=["src/main.cpp"])

        # Add simple hello world content
        with open(mainfile, "w", encoding="utf-8") as f:
            f.write('#include <iostream>\n\n')
            f.write('int main() {\n')
            f.write('    std::cout << "Hello, World!" << std::endl;\n')
            f.write('    return 0;\n')
            f.write('}\n')  


        return bin