import cli
import console
from project import PROJECT_FILE_NAME, ProjectYAML


def cmd_add(add_params: cli.KissParser):
    project_name = add_params.project_name
    project_dir = add_params.directory
    project_file = project_dir / PROJECT_FILE_NAME
    yaml_file = ProjectYAML(file=project_file)
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
 - name : \"{add_params.dependency_name}\" 
   path : \"{add_params.path}\" """)
        # Warning if we give an absolute path
        if add_params.path.is_absolute():
            console.print_warning(f"⚠️  Warning: You are adding a dependency with an absolute path `{add_params.path}`. This may cause issues if the project is moved to another location.")
        yaml_path_dict = yaml_file.path_depencendies_to_yaml_dict(add_params.dependency_name, add_params.path)
        if not yaml_file.add_dependency_to_project(project_name, yaml_path_dict):
            console.print_error(f"Error: Unable to add dependency `{add_params.dependency_name}` to project `{project_name}` in file `{project_file}`")
            exit(1)
    elif add_params.git is not None:
        console.print_step(f"""Adding to the project `{project_name}` in file {project_file} the dependency :
 - name : \"{add_params.dependency_name}\" 
   git : \"{add_params.url}\" """)
        yaml_git_dict = yaml_file.git_depencendies_to_yaml_dict(add_params.dependency_name, add_params.url)
        if not yaml_file.add_dependency_to_project(project_name, yaml_git_dict):
            console.print_error(f"Error: Unable to add dependency `{add_params.dependency_name}` to project `{project_name}` in file `{project_file}`")
            exit(1)
    yaml_file.save_yaml()
