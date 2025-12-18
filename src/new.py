import os
from pathlib import Path
import cli
import console
from project import PROJECT_FILE_NAME, BinProject, DynProject, LibProject, Project, ProjectType, ProjectYAML

def __populate_bin(project: BinProject):
    relative_src_directory = Path("src")
    absolute_src_directory = project.path / relative_src_directory
    os.makedirs(absolute_src_directory, exist_ok=True)
    
    absolute_mainfile = absolute_src_directory / "main.cpp"
    if os.path.exists(absolute_mainfile): 
        console.print_error(f"The file {absolute_mainfile} already exists !")
        exit(2)
    
    with open(absolute_mainfile, "w", encoding="utf-8") as f:
        f.write('#include <iostream>\n\n')
        f.write('int main() {\n')
        f.write('    std::cout << "Hello, World!" << std::endl;\n')
        f.write('    return 0;\n')
        f.write('}\n')
    project.sources.append(relative_src_directory / "main.cpp")

def __populate_lib(project: LibProject):
    # Create the lib.cpp file
    relative_src_directory = Path("src")
    absolute_src_directory = project.path / relative_src_directory
    os.makedirs(absolute_src_directory, exist_ok=True)

    # Add a simple hello world lib.cpp file
    absolute_libfile = absolute_src_directory / "lib.cpp"
    if os.path.exists(absolute_libfile): 
        console.print_error(f"The file {absolute_libfile} already exists !")
        exit(2)
    with open(absolute_libfile, "w", encoding="utf-8") as f:
        f.write('#include <iostream>\n\n')
        f.write('void hello_world() {\n')
        f.write('    std::cout << "Hello, World!" << std::endl;\n')
        f.write('}\n')  
    project.sources.append(relative_src_directory / "lib.cpp")

    # Add the interface header
    relative_interface_directory = Path("interface") / project.name
    absolute_interface_directory = project.path / relative_interface_directory
    os.makedirs(absolute_interface_directory, exist_ok=True)

    absolute_header = absolute_interface_directory / "lib.h"
    if os.path.exists(absolute_header): 
        console.print_error(f"The file {absolute_header} already exists !")
        exit(2)

    with open(absolute_header, "w", encoding="utf-8") as f:
        f.write('#ifndef LIB_H\n')
        f.write('#define LIB_H\n\n')
        f.write('void hello_world();\n')
        f.write('\n#endif // LIB_H\n')

    project.interface_directories.append(relative_interface_directory)


def __populate_dyn(project: LibProject):
    # Create the dyn.cpp file
    relative_src_directory = Path("src")
    absolute_src_directory = project.path / relative_src_directory
    os.makedirs(absolute_src_directory, exist_ok=True)

    # Add a simple hello world dyn.cpp file
    absolute_libfile = absolute_src_directory / "dyn.cpp"
    if os.path.exists(absolute_libfile): 
        console.print_error(f"The file {absolute_libfile} already exists !")
        exit(2)
    with open(absolute_libfile, "w", encoding="utf-8") as f:
        f.write('#include <iostream>\n\n')
        f.write('void hello_world() {\n')
        f.write('    std::cout << "Hello, World!" << std::endl;\n')
        f.write('}\n')  
    project.sources.append(relative_src_directory / "dyn.cpp")

    # Add the interface header
    relative_interface_directory = Path("interface") / project.name
    absolute_interface_directory = project.path / relative_interface_directory
    os.makedirs(absolute_interface_directory, exist_ok=True)

    absolute_header = absolute_interface_directory / "dyn.h"
    if os.path.exists(absolute_header): 
        console.print_error(f"The file {absolute_header} already exists !")
        exit(2)

    with open(absolute_header, "w", encoding="utf-8") as f:
        f.write('#ifndef DYN_H\n')
        f.write('#define DYN_H\n\n')
        f.write('void hello_world();\n')
        f.write('\n#endif // DYN_H\n')

    project.interface_directories.append(relative_interface_directory)

def __new_project_in_project_file(project_file: Path, project: Project):
    yaml_file = ProjectYAML(file=project_file)
    if project_file.exists():
        if not yaml_file.load_yaml():
            console.print_error(f"Error: Unable to load existing project file `{project_file}`")
            exit(1)
        if yaml_file.is_project_present(project):
            console.print_error(f"Error: Project `{project.name}` already exists in `{project_file}`")
            exit(1)
    if not yaml_file.add_project(project=project):
        console.print_error(f"Error: Unable to add project `{project.name}` to `{project_file}`")
        return
    if not yaml_file.save_yaml():
        console.print_error(f"Error: Unable to save project file `{project_file}`")
        return
    console.print_success(f"Project `{project.name}` created successfully in `{project_file}`")

def cmd_new(new_params :cli.KissParser):
    if new_params.existing:
        project_dir = new_params.directory
        project_file =  new_params.directory / PROJECT_FILE_NAME
        if not project_file.exists():
            console.print_error(f"Error: Project file `{project_file}` does not exists.")
            exit(1)
        console.print_step(f"Creating a new {new_params.project_type} project named `{new_params.project_name}` in existing project file `{project_file}`")
    else:
        # Create the file PROJECT_FILE_NAME in the specified directory or add the project to this file if not exists
        project_dir = new_params.directory / new_params.project_name
        project_dir.mkdir(parents=True, exist_ok=True)
        project_file = project_dir / PROJECT_FILE_NAME
        console.print_step(f"Creating a new {new_params.project_type} project named  `{new_params.project_name}` in `{project_file}`")
    
    match new_params.project_type:
        case ProjectType.bin:
            project = BinProject(
                file=project_file,
                path=project_dir,
                name=new_params.project_name,
                description=new_params.description,
                version="0.1.0",
                sources=[]
            )
            if not new_params.empty:
                __populate_bin(project=project)
            __new_project_in_project_file(project_file=project_file, project=project)

        case ProjectType.lib:
            project = LibProject(
                file=project_file,
                path=project_dir,
                name=new_params.project_name,
                description=new_params.description,
                version="0.1.0",
                sources=[],
                interface_directories=[]
            )
            if not new_params.empty:
                __populate_lib(project=project)
            __new_project_in_project_file(project_file=project_file, project=project)
        case ProjectType.dyn:
            project = DynProject(
                file=project_file,
                path=project_dir,
                name=new_params.project_name,
                description=new_params.description,
                version="0.1.0",
                sources=[],
                interface_directories=[]
            )
            if not new_params.empty:
                __populate_dyn(project=project)
            __new_project_in_project_file(project_file=project_file, project=project)