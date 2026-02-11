import argparse
import os
from pathlib import Path
from typing import Self
import cli
import console
from context import Context
from project import BinProject, DynProject, LibProject, Project, ProjectType
from yaml_file import PROJECT_FILE_NAME, YamlProjectFile


class NewContext(Context):
    def __init__(self, directory:Path, project_file: Path, existing: bool, project_type: ProjectType, populate:bool, project_name:str, project_description:str):
        super().__init__(directory)
        self._existing = existing
        self._project_file = Path(project_file)
        self._project_type = ProjectType(project_type)
        self._populate = populate
        self._project_name = project_name
        self._project_description = project_description

    @classmethod
    def from_cli_args(cls, cli_args: argparse.Namespace) -> Self:
        if cli_args.existing:
            project_dir = cli_args.directory / cli_args.project_name
            project_file =  cli_args.directory / PROJECT_FILE_NAME
            console.print_step(f"Creating a new {cli_args.project_type} project named `{cli_args.project_name}` in existing project file `{project_file}`")
            if project_dir.exists():
                console.print_error(f"Error: Project directory '{project_dir}' already exists")
                exit(1)
        
            if not project_file.exists():
                console.print_error(f"Error: Project file `{project_file}` does not exists")
                exit(1)
        else:
            # Create the file PROJECT_FILE_NAME in the specified directory or add the project to this file if not exists
            project_dir = cli_args.directory / cli_args.project_name
            project_file = project_dir / PROJECT_FILE_NAME
            console.print_step(f"Creating a new {cli_args.project_type} project named `{cli_args.project_name}` in `{project_file}`")
            if project_dir.exists():
                console.print_error(f"Error: Project directory '{project_dir}' already exists")
                exit(1)
        return cls(
            directory=project_dir, 
            project_file=project_file, 
            existing=cli_args.existing, 
            populate=not cli_args.empty,
            project_type=cli_args.project_type,
            project_name=cli_args.project_name,
            project_description=cli_args.description
        )


    @property
    def is_adding_in_existing_file(self) -> bool:
        return self._existing
    
    @property
    def project_type_to_create(self) -> ProjectType:
        return self._project_type
    
    @property
    def project_file(self) -> Path:
        return self._project_file
    
    @property
    def populate(self) -> bool:
        return self._populate
    
    @property
    def project_name(self) -> bool:
        return self._project_name
    
    @property
    def project_description(self) -> bool:
        return self._project_description
    
    
def __new_project_in_project_file(new_context: NewContext, project: Project):
    yaml_file = YamlProjectFile(file=new_context.project_file)

    # If the file exist load it and check that the project does not already exists or a dependency with the same name already exists
    if new_context.project_file.exists():
        if not yaml_file.load_yaml():
            console.print_error(f"Error: Unable to load existing project file `{new_context.project_file}`")
            exit(1)
        # Check that the project does not already exists in the yaml file
        if yaml_file.is_project_in_yaml(project.name):
            console.print_error(f"Error: Project `{project.name}` already exists in `{new_context.project_file}`")
            exit(1)
        # Check that no dependency with the same name exists
        yaml_project_with_dependency_with_same_name = yaml_file.get_yaml_project_with_dependency(project.name)
        if yaml_project_with_dependency_with_same_name is not None:
            console.print_error(f"Error: `{project.name}` dependency already exists in project `{yaml_project_with_dependency_with_same_name.get('name')}` in `{new_context.project_file}`")
            exit(1)
    # Add the project to the yaml file
    if not yaml_file.add_yaml_project(project.to_yaml_project()):
        console.print_error(f"Error: Unable to add project `{project.name}` to `{new_context.project_file}`")
        exit(1)
    # Save the file
    if not yaml_file.save_yaml():
        console.print_error(f"Error: Unable to save project file `{new_context.project_file}`")
        exit(1)
    
def __new_bin_project_in_project_file(new_context: NewContext):
    project = BinProject(
            file=new_context.project_file,
            path=new_context.directory,
            name=new_context.project_name,
            description=new_context.project_description,
            version="0.1.0",
            sources=[]
        )
     
    # If we want to populate the project
    # First check if the file we want to create does not already exist
    # Add them the to project sources
    if new_context.populate:
        relative_src_directory = Path("src")
        absolute_mainfile = project.path / relative_src_directory / "main.cpp"
        if absolute_mainfile.exists(): 
            console.print_error(f"The file {absolute_mainfile} already exists !")
            exit(1)
        project.sources.append(relative_src_directory / "main.cpp")

    # Create the project in the project file
    __new_project_in_project_file(new_context=new_context, project=project)

    # Everything is ok we can create the files now
    if new_context.populate:
        project.path.mkdir(parents=True, exist_ok=True)
        os.makedirs(absolute_mainfile.parent, exist_ok=True)
        with open(absolute_mainfile, "w", encoding="utf-8") as f:
            f.write('#include <iostream>\n\n')
            f.write('int main() {\n')
            f.write('    std::cout << "Hello, World!" << std::endl;\n')
            f.write('    return 0;\n')
            f.write('}\n')

def __new_lib_project_in_project_file(new_context: NewContext):
    project = LibProject(
                file=new_context.project_file,
                path=new_context.directory,
                name=new_context.project_name,
                description=new_context.project_description,
                version="0.1.0",
                sources=[],
                interface_directories=[]
            )
    
    # If we want to populate the project
    # First check if the file we want to create does not already exist
    # Add them the to project sources
    if new_context.populate:
        relative_src_directory = Path("src")
        absolute_libfile = project.path / relative_src_directory / "lib.cpp"
        if absolute_libfile.exists(): 
            console.print_error(f"The file {absolute_libfile} already exists !")
            exit(1)
        project.sources.append(relative_src_directory / "lib.cpp")

        relative_interface_directory = Path("interface")
        absolute_header = project.path / relative_interface_directory / project.name / "lib.h"
        if absolute_header.exists(): 
            console.print_error(f"The file {absolute_header} already exists !")
            exit(1)
        project.interface_directories.append(relative_interface_directory)

    # Create the project in the project file
    __new_project_in_project_file(new_context=new_context, project=project)
    
     # Everything is ok we can create the files now
    if new_context.populate:
        project.path.mkdir(parents=True, exist_ok=True)
        os.makedirs(absolute_libfile.parent, exist_ok=True)
        with open(absolute_libfile, "w", encoding="utf-8") as f:
            f.write('#include <iostream>\n\n')
            f.write('void hello_world() {\n')
            f.write('    std::cout << "Hello, World!" << std::endl;\n')
            f.write('}\n')
        os.makedirs(absolute_header.parent, exist_ok=True)
        with open(absolute_header, "w", encoding="utf-8") as f:
            f.write('#ifndef LIB_H\n')
            f.write('#define LIB_H\n\n')
            f.write('void hello_world();\n')
            f.write('\n#endif // LIB_H\n')

def __new_dyn_project_in_project_file(new_context: NewContext):
    project = DynProject(
                file=new_context.project_file,
                path=new_context.directory,
                name=new_context.project_name,
                description=new_context.project_description,
                version="0.1.0",
                sources=[],
                interface_directories=[]
            )
    # If we want to populate the project
    # First check if the file we want to create does not already exist
    # Add them the to project sources
    if new_context.populate:
        relative_src_directory = Path("src")
        absolute_dynfile = project.path / relative_src_directory / "dyn.cpp"
        if absolute_dynfile.exists(): 
            console.print_error(f"The file {absolute_dynfile} already exists !")
            exit(1)
        project.sources.append(relative_src_directory / "dyn.cpp")

        relative_interface_directory = Path("interface")
        absolute_header = project.path / relative_interface_directory / project.name / "dyn.h"
        if absolute_header.exists(): 
            console.print_error(f"The file {absolute_header} already exists !")
            exit(1)
        project.interface_directories.append(relative_interface_directory)

    # Create the project in the project file
    __new_project_in_project_file(new_context=new_context, project=project)
    
     # Everything is ok we can create the files now
    if new_context.populate:
        project.path.mkdir(parents=True, exist_ok=True)
        os.makedirs(absolute_dynfile.parent, exist_ok=True)
        with open(absolute_dynfile, "w", encoding="utf-8") as f:
            f.write('#include <iostream>\n\n')
            f.write('void hello_world() {\n')
            f.write('    std::cout << "Hello, World!" << std::endl;\n')
            f.write('}\n')
        os.makedirs(absolute_header.parent, exist_ok=True)
        with open(absolute_header, "w", encoding="utf-8") as f:
            f.write('#ifndef DYN_H\n')
            f.write('#define DYN_H\n\n')
            f.write('void hello_world();\n')
            f.write('\n#endif // DYN_H\n')

def cmd_new(cli_args: argparse.Namespace):
    new_context = NewContext.from_cli_args(cli_args)
    match new_context.project_type_to_create:
        case ProjectType.bin:
            __new_bin_project_in_project_file(new_context)

        case ProjectType.lib:
            __new_lib_project_in_project_file(new_context)

        case ProjectType.dyn:
            __new_dyn_project_in_project_file(new_context)

    console.print_success(f"Project `{new_context.project_name}` created successfully in `{new_context.project_file}`")