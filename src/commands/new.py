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
            new_project: LibProject = newLibProject(file, new_directory, new_params)
            with open(file, "w", encoding="utf-8") as f:
                f.write(new_project.to_new_manifest())
        case ProjectType.dyn:
            new_project: DynProject = newDynProject(file, new_directory, new_params)
            with open(file, "w", encoding="utf-8") as f:
                f.write(new_project.to_new_manifest())
    
    console.print_success(f"Project {new_project.name} created successfully.")


def newBinProject(file: str, new_directory: Path, new_params :NewParams):
        # Add a simple hello world main file
        relative_src_directory = "src"
        absolute_src_directory = os.path.join(new_directory, relative_src_directory)
        os.makedirs(absolute_src_directory, exist_ok=True)
        
        absolute_mainfile = os.path.join(absolute_src_directory, f"main.cpp")
        if os.path.exists(absolute_mainfile): 
            console.print_error(f"The file {absolute_mainfile} already exists !")
            sys.exit(2)
        
        with open(absolute_mainfile, "w", encoding="utf-8") as f:
            f.write('#include <iostream>\n\n')
            f.write('int main() {\n')
            f.write('    std::cout << "Hello, World!" << std::endl;\n')
            f.write('    return 0;\n')
            f.write('}\n')  

        return BinProject(name=new_params.project_name,file=file,description= new_params.description, sources=[os.path.join(relative_src_directory, f"main.cpp")])

def newLibProject(file: str, new_directory: Path, new_params :NewParams):
        # Create the main.cpp file
        relative_src_directory = "src"
        absolute_src_directory = os.path.join(new_directory, relative_src_directory)
        os.makedirs(absolute_src_directory, exist_ok=True)

        # Add a simple hello world main file
        absolute_libfile = os.path.join(absolute_src_directory, f"lib.cpp")
        if os.path.exists(absolute_libfile): 
            console.print_error(f"The file {absolute_libfile} already exists !")
            sys.exit(2)
        with open(absolute_libfile, "w", encoding="utf-8") as f:
            f.write('#include <iostream>\n\n')
            f.write('void hello_world() {\n')
            f.write('    std::cout << "Hello, World!" << std::endl;\n')
            f.write('}\n')  

        # Add the interface header
        relative_interface_directory = "interface"
        absolute_interface_directory = os.path.join(new_directory, relative_interface_directory)
        os.makedirs(absolute_interface_directory, exist_ok=True)

        absolute_header = os.path.join(absolute_interface_directory, f"lib.h")
        if os.path.exists(absolute_header): 
            console.print_error(f"The file {absolute_header} already exists !")
            sys.exit(2)

        with open(absolute_header, "w", encoding="utf-8") as f:
            f.write('#ifndef LIB_H\n')
            f.write('#define LIB_H\n\n')
            f.write('void hello_world();\n')
            f.write('\n#endif // LIB_H\n')

        return LibProject(
             name=new_params.project_name,
             file=file,
             description=new_params.description,
             interface_directories=[relative_interface_directory],
             sources=[os.path.join(relative_src_directory, f"lib.cpp")]
             )

def newDynProject(file: str, new_directory: Path, new_params :NewParams):
         # Create the main.cpp file
        relative_src_directory = "src"
        absolute_src_directory = os.path.join(new_directory, relative_src_directory)
        os.makedirs(absolute_src_directory, exist_ok=True)

        # Add a simple hello world main file
        absolute_libfile = os.path.join(absolute_src_directory, f"dyn.cpp")
        if os.path.exists(absolute_libfile): 
            console.print_error(f"The file {absolute_libfile} already exists !")
            sys.exit(2)
        with open(absolute_libfile, "w", encoding="utf-8") as f:
            f.write('#include <iostream>\n\n')
            f.write('void hello_world() {\n')
            f.write('    std::cout << "Hello, World!" << std::endl;\n')
            f.write('}\n')  

        # Add the interface header
        relative_interface_directory = "interface"
        absolute_interface_directory = os.path.join(new_directory, relative_interface_directory)
        os.makedirs(absolute_interface_directory, exist_ok=True)

        absolute_header = os.path.join(absolute_interface_directory, f"dyn.h")
        if os.path.exists(absolute_header): 
            console.print_error(f"The file {absolute_header} already exists !")
            sys.exit(2)

        with open(absolute_header, "w", encoding="utf-8") as f:
            f.write('#ifndef DYN_H\n')
            f.write('#define DYN_H\n\n')
            f.write('void hello_world();\n')
            f.write('\n#endif // DYN_H\n')

        return DynProject(
             name=new_params.project_name,
             file=file,
             description=new_params.description,
             interface_directories=[relative_interface_directory],
             sources=[os.path.join(relative_src_directory, f"dyn.cpp")]
             )