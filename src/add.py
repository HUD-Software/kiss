import cli
import console
from yaml_file import PROJECT_FILE_NAME, YamlProjectFile


def cmd_add(add_params: cli.KissParser):
    project_name = add_params.project_name
    project_dir = add_params.directory
    project_file = project_dir / PROJECT_FILE_NAME
    yaml_file = YamlProjectFile(file=project_file)
    # Check that the project file exists
    if not yaml_file.load_yaml():
        console.print_warning(f"Error: Unable to load project file `{project_file}`")
        exit(1)
    # Check that the target project exists
    if add_params.project_name is not None:
        if not yaml_file.is_project_name_present(add_params.project_name):
            console.print_error(f"Error: Project `{add_params.project_name}` does not exists in `{project_file}`")
            exit(1)
        project_name = add_params.project_name
    else:
        project_name = project_dir.name
    
    if add_params.path is not None:
        console.print_step(f"""Adding to the project `{project_name}` in file {project_file} the dependency :
 - name : {add_params.dependency_name} 
   path : {add_params.path} """)
        # Warning if we give an absolute path
        if add_params.path.is_absolute():
            console.print_warning(f"⚠️  Warning: You are adding a dependency with an absolute path `{add_params.path}`. This may cause issues if the project is moved to another location.")
            
        # Check that dependency directory exists
        dependency_dir = project_dir / add_params.path
        if not dependency_dir.exists():
            console.print_error(f"Error: Directory '{dependency_dir}' does not exists.")
            exit(1)

        # Check that we have a kiss.yaml in the dependency directory
        dependency_file = dependency_dir / PROJECT_FILE_NAME
        if not dependency_file.exists():
            if not yaml_file.is_project_name_present(add_params.dependency_name):
                console.print_error(f"Error: Missing '{PROJECT_FILE_NAME}' file in '{dependency_dir}' directory. \n"+
                                    f"       Add 'kiss.yaml' file to '{dependency_dir}' project directory.\n" + 
                                    f"       Or add it to target project '{project_name}' in file {project_file}.")
                exit(1)

        # Add the dependency to the project yaml
        yaml_path_dict = yaml_file.path_depencendies_to_yaml_dict(add_params.dependency_name, add_params.path)
        if not yaml_file.add_dependency_to_project(project_name, yaml_path_dict):
            console.print_error(f"Error: Unable to add dependency `{add_params.dependency_name}` to project `{project_name}` in file `{project_file}`")
            exit(1)
    elif add_params.git is not None:
        console.print_step(f"""Adding to the project `{project_name}` in file {project_file} the dependency :
 - name : {add_params.dependency_name} 
   git : {add_params.git} """)
        yaml_git_dict = yaml_file.git_depencendies_to_yaml_dict(add_params.dependency_name, add_params.git)
        if not yaml_file.add_dependency_to_project(project_name, yaml_git_dict):
            console.print_error(f"Error: Unable to add dependency `{add_params.dependency_name}` to project `{project_name}` in file `{project_file}`")
            exit(1)
    if not yaml_file.save_yaml():
        console.print_error(f"Error: Unable to save project file `{project_file}`")
        exit(1)
