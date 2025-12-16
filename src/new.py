from pathlib import Path

import cli
import console
from project import PROJECT_FILE_NAME, BinProject, DynProject, LibProject, Project, ProjectType, ProjectYAML


def __new_project_in_project_file(project_file: Path,project: Project ):
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
            __new_project_in_project_file(project_file=project_file, project=project)