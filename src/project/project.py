import re
import console
import modules


class Project:
    @staticmethod
    def to_pascal( name: str) -> str:
        """
        Convert a string like "my_project", "my-project", "myProject",
        "my project" -> "MyProject".
        """
        if not name:
            return ""

        # 1) Turn camelCase into snake-ish by inserting '_' before Upper after lower/digit:
        s = re.sub(r'([a-z0-9])([A-Z])', r'\1_\2', name)

        # 2) Replace separators (space, dash, multiple underscores) by a single non-alnum split
        parts = re.split(r'[^0-9A-Za-z]+', s)

        # 3) Capitalize each part and join
        return ''.join(part.capitalize() for part in parts if part)

    @staticmethod
    def default_project(directory:str) -> str|None:
        modules.load_modules(directory)
        if not modules.registered_projects:
            return None 
        default_project_name ,default_project = next(iter(modules.registered_projects.items()))
        # Warn the user if we found more than 1 project
        if len(modules.registered_projects) > 1:
            console.print_warning(f"We found more than 1 projet in the directory {directory}.")
            for project_name ,project in modules.registered_projects.items():
                console.print_warning(f"- {project_name} : {project._project_file}")
            console.print_warning(f"\nUse {default_project_name} : {default_project._project_file}")
        return default_project_name
