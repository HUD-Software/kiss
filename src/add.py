import argparse
import cli
import console
from yaml_file import PROJECT_FILE_NAME, YamlProjectFile


def cmd_add(cli_args: argparse.Namespace):
    project_name = cli_args.project_name
    project_dir = cli_args.directory
    project_file = project_dir / PROJECT_FILE_NAME
    yaml_file = YamlProjectFile(file=project_file)
    # Check that the project file exists
    if not yaml_file.load_yaml():
        console.print_warning(f"Error: Unable to load project file `{project_file}`")
        exit(1)
    # Check that the target project exists
    if cli_args.project_name is not None:
        if not yaml_file.is_project_name_present(cli_args.project_name):
            console.print_error(f"Error: Project `{cli_args.project_name}` does not exists in `{project_file}`")
            exit(1)
        project_name = cli_args.project_name
    else:
        project_name = project_dir.name
    
    if cli_args.path is not None:
        console.print_step(f"""Adding to the project `{project_name}` in file {project_file} the dependency :
 - name : {cli_args.dependency_name} 
   path : {cli_args.path} """)
        # Warning if we give an absolute path
        if cli_args.path.is_absolute():
            console.print_warning(f"⚠️  Warning: You are adding a dependency with an absolute path `{cli_args.path}`. This may cause issues if the project is moved to another location.")
            
        # Check that dependency directory exists
        dependency_dir = project_dir / cli_args.path
        if not dependency_dir.exists():
            console.print_error(f"Error: Directory '{dependency_dir}' does not exists.")
            exit(1)

        # Check that we have a kiss.yaml in the dependency directory
        dependency_file = dependency_dir / PROJECT_FILE_NAME
        if not dependency_file.exists():
            if not yaml_file.is_project_name_present(cli_args.dependency_name):
                console.print_error(f"Error: Missing '{PROJECT_FILE_NAME}' file in '{dependency_dir}' directory. \n"+
                                    f"       Add 'kiss.yaml' file to '{dependency_dir}' project directory.\n" + 
                                    f"       Or add it to target project '{project_name}' in file {project_file}.")
                exit(1)

        # Add the dependency to the project yaml
        yaml_path_dict = yaml_file.path_depencendies_to_yaml_dict(cli_args.dependency_name, cli_args.path)
        if not yaml_file.add_dependency_to_project(project_name, yaml_path_dict):
            console.print_error(f"Error: Unable to add dependency `{cli_args.dependency_name}` to project `{project_name}` in file `{project_file}`")
            exit(1)
    elif cli_args.git is not None:
        console.print_step(f"""Adding to the project `{project_name}` in file {project_file} the dependency :
 - name : {cli_args.dependency_name} 
   git : {cli_args.git} """)
        yaml_git_dict = yaml_file.git_depencendies_to_yaml_dict(cli_args.dependency_name, cli_args.git)
        if not yaml_file.add_dependency_to_project(project_name, yaml_git_dict):
            console.print_error(f"Error: Unable to add dependency `{cli_args.dependency_name}` to project `{project_name}` in file `{project_file}`")
            exit(1)
    if not yaml_file.save_yaml():
        console.print_error(f"Error: Unable to save project file `{project_file}`")
        exit(1)
