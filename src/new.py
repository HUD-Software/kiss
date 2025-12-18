import os
from pathlib import Path
import cli
import console
from project import PROJECT_FILE_NAME, BinProject, DynProject, LibProject, Project, ProjectType, ProjectYAML

def __new_project_in_project_file(project_file: Path, project: Project):
    yaml_file = ProjectYAML(file=project_file)

    # If the file exist load it and check that the project does not already exists or a dependency with the same name already exists
    if project_file.exists():
        if not yaml_file.load_yaml():
            console.print_error(f"Error: Unable to load existing project file `{project_file}`")
            exit(1)
        # Check that the project does not already exists in the yaml file
        if yaml_file.is_project_present(project):
            console.print_error(f"Error: Project `{project.name}` already exists in `{project_file}`")
            exit(1)
        # Check that no dependency with the same name exists
        yaml_project_with_dependency_with_same_name = yaml_file.get_yaml_project_with_dependency(project.name)
        if yaml_project_with_dependency_with_same_name is not None:
            console.print_error(f"Error: `{project.name}` dependency already exists in project `{yaml_project_with_dependency_with_same_name.get('name')}` in `{project_file}`")
            exit(1)
    # Add the project to the yaml file
    if not yaml_file.add_project(project=project):
        console.print_error(f"Error: Unable to add project `{project.name}` to `{project_file}`")
        return
    # Save the file
    if not yaml_file.save_yaml():
        console.print_error(f"Error: Unable to save project file `{project_file}`")
        return
    console.print_success(f"Project `{project.name}` created successfully in `{project_file}`")
    
def __new_bin_project_in_project_file(project_file: Path, project: BinProject, populate : bool):
    # If we want to populate the project
    # First check if the file we want to create does not already exist
    # Add them the to project sources
    if populate:
        relative_src_directory = Path("src")
        absolute_src_directory = project.path / relative_src_directory
        absolute_mainfile = absolute_src_directory / "main.cpp"
        if os.path.exists(absolute_mainfile): 
            console.print_error(f"The file {absolute_mainfile} already exists !")
            exit(2)
        project.sources.append(relative_src_directory / "main.cpp")

    # Create the project in the project file
    __new_project_in_project_file(project_file=project_file, project=project)

    # Everything is ok we can create the files now
    if populate:
        project.path.mkdir(parents=True, exist_ok=True)
        os.makedirs(absolute_src_directory, exist_ok=True)
        with open(absolute_mainfile, "w", encoding="utf-8") as f:
            f.write('#include <iostream>\n\n')
            f.write('int main() {\n')
            f.write('    std::cout << "Hello, World!" << std::endl;\n')
            f.write('    return 0;\n')
            f.write('}\n')

def __new_lib_project_in_project_file(project_file: Path, project: LibProject, populate : bool):
    # If we want to populate the project
    # First check if the file we want to create does not already exist
    # Add them the to project sources
    if populate:
        relative_src_directory = Path("src")
        absolute_src_directory = project.path / relative_src_directory
        absolute_libfile = absolute_src_directory / "lib.cpp"
        if os.path.exists(absolute_libfile): 
            console.print_error(f"The file {absolute_libfile} already exists !")
            exit(2)
        project.sources.append(relative_src_directory / "lib.cpp")

        relative_interface_directory = Path("interface") / project.name
        absolute_interface_directory = project.path / relative_interface_directory
        absolute_header = absolute_interface_directory / "lib.h"
        if os.path.exists(absolute_header): 
            console.print_error(f"The file {absolute_header} already exists !")
            exit(2)
        project.interface_directories.append(relative_interface_directory)

    # Create the project in the project file
    __new_project_in_project_file(project_file=project_file, project=project)
    
     # Everything is ok we can create the files now
    if populate:
        project.path.mkdir(parents=True, exist_ok=True)
        os.makedirs(absolute_src_directory, exist_ok=True)
        with open(absolute_libfile, "w", encoding="utf-8") as f:
            f.write('#include <iostream>\n\n')
            f.write('void hello_world() {\n')
            f.write('    std::cout << "Hello, World!" << std::endl;\n')
            f.write('}\n')
        os.makedirs(absolute_interface_directory, exist_ok=True)
        with open(absolute_header, "w", encoding="utf-8") as f:
            f.write('#ifndef LIB_H\n')
            f.write('#define LIB_H\n\n')
            f.write('void hello_world();\n')
            f.write('\n#endif // LIB_H\n')

def __new_dyn_project_in_project_file(project_file: Path, project: LibProject, populate : bool):
    # If we want to populate the project
    # First check if the file we want to create does not already exist
    # Add them the to project sources
    if populate:
        relative_src_directory = Path("src")
        absolute_src_directory = project.path / relative_src_directory
        absolute_dynfile = absolute_src_directory / "dyn.cpp"
        if os.path.exists(absolute_dynfile): 
            console.print_error(f"The file {absolute_dynfile} already exists !")
            exit(2)
        project.sources.append(relative_src_directory / "dyn.cpp")

        relative_interface_directory = Path("interface") / project.name
        absolute_interface_directory = project.path / relative_interface_directory
        absolute_header = absolute_interface_directory / "dyn.h"
        if os.path.exists(absolute_header): 
            console.print_error(f"The file {absolute_header} already exists !")
            exit(2)
        project.interface_directories.append(relative_interface_directory)

    # Create the project in the project file
    __new_project_in_project_file(project_file=project_file, project=project)
    
     # Everything is ok we can create the files now
    if populate:
        project.path.mkdir(parents=True, exist_ok=True)
        os.makedirs(absolute_src_directory, exist_ok=True)
        with open(absolute_dynfile, "w", encoding="utf-8") as f:
            f.write('#include <iostream>\n\n')
            f.write('void hello_world() {\n')
            f.write('    std::cout << "Hello, World!" << std::endl;\n')
            f.write('}\n')
        os.makedirs(absolute_interface_directory, exist_ok=True)
        with open(absolute_header, "w", encoding="utf-8") as f:
            f.write('#ifndef DYN_H\n')
            f.write('#define DYN_H\n\n')
            f.write('void hello_world();\n')
            f.write('\n#endif // DYN_H\n')

def cmd_new(new_params :cli.KissParser):
    if new_params.existing:
        project_dir = new_params.directory / new_params.project_name
        project_file =  new_params.directory / PROJECT_FILE_NAME
        console.print_step(f"Creating a new {new_params.project_type} project named `{new_params.project_name}` in existing project file `{project_file}`")
        if project_dir.exists():
            console.print_error(f"Error: Project directory '{project_dir}' already exists")
            exit(1)
       
        if not project_file.exists():
            console.print_error(f"Error: Project file `{project_file}` does not exists")
            exit(1)
    else:
        # Create the file PROJECT_FILE_NAME in the specified directory or add the project to this file if not exists
        project_dir = new_params.directory / new_params.project_name
        project_file = project_dir / PROJECT_FILE_NAME
        console.print_step(f"Creating a new {new_params.project_type} project named `{new_params.project_name}` in `{project_file}`")
        if project_dir.exists():
            console.print_error(f"Error: Project directory '{project_dir}' already exists")
            exit(1)
    
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
            __new_bin_project_in_project_file(project_file=project_file, project=project, populate=not new_params.empty)

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
            __new_lib_project_in_project_file(project_file=project_file, project=project, populate=not new_params.empty)

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
            __new_dyn_project_in_project_file(project_file=project_file, project=project, populate=not new_params.empty)