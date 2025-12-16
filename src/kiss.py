from pathlib import Path
import console
from project import BinProject, LibProject, ProjectRegistry, ProjectType, PROJECT_FILE_NAME, ProjectYAML
import cli

def cmd_list(list_params: cli.KissParser):
    ProjectRegistry.load_projects_in_directory(path=list_params.directory, recursive=list_params.recursive)
    if len(ProjectRegistry.items()) == 0:
        console.print_error("Aucun projet trouvé !")
    else:
        for project in ProjectRegistry.projects():
                console.print_success(f"--> Projet trouvé : {project.file}")
                console.print(f"    - name : {project.name}")
                console.print(f"    - description : {project.description}")
                console.print(f"    - path : {project.path}")
                match project:
                    case BinProject() as bin_project:
                        console.print(f"    - sources : {bin_project.sources}")
                    case LibProject() as lib_project:
                        console.print(f"    - sources : {lib_project.sources}")
                        console.print(f"    - interface directories : {lib_project.interface_directories}")
                # case DynProject() as dyn_project:
                #     console.print(f"    - sources : {dyn_project.sources}")
                #     console.print(f"    - interface directories : {dyn_project.interface_directories}")

def cmd_new(new_params :cli.KissParser):
    # Create the file PROJECT_FILE_NAME in the specified directory or add the project to this file if not exists
    project_dir = new_params.directory / new_params.project_name
    project_dir.mkdir(parents=True, exist_ok=True)
    project_file = project_dir / PROJECT_FILE_NAME
    console.print_step(f"Creating a new {new_params.project_type} project named  `{new_params.project_name}` in `{project_file}`")

    yaml_file = ProjectYAML(file=project_file)
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
            
            console.print_success(f"Project `{project.name}` created successfully in `{project_dir}`")
        # case ProjectType.dyn:
        #     ...
        # case ProjectType.lib:
        #     ...
        # case ProjectType.workspace:
        #     ...
def cmd_new_existing(new_params :cli.KissParser):
    project_file =  new_params.directory / PROJECT_FILE_NAME
    if not project_file.exists():
        console.print_error(f"Error: Project file `{project_file}` does not exists.")
        exit(1)
    console.print_step(f"Creating a new {new_params.project_type} project named `{new_params.project_name}` in existing project file `{project_file}`")
    yaml_file = ProjectYAML(file=project_file)
    match new_params.project_type:
        case ProjectType.bin:
            project = BinProject(
                file=project_file,
                path=new_params.directory,
                name=new_params.project_name,
                description=new_params.description,
                version="0.1.0",
                sources=[]
            )
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

def main():

    args = cli.UserParams.from_args()

    if args.option == "list": 
        cmd_list(list_params=args)
    
    elif args.option == "new":
        if args.existing:
            cmd_new_existing(new_params=args)
        else:
            cmd_new(new_params=args)
    
    elif args.option == "add": 
        cmd_add(add_params=args)
        
    # elif args.option == "generate": 
    #     commands.generate.cmd_generate(generate_params=args)
    
    # elif args.option == "build": 
    #     commands.build.cmd_build(build_params=args)
    
    # elif args.option == "run": 
    #     commands.run.cmd_run(run_params=args)
            
if __name__ == "__main__":
    main()

