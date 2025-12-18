
from abc import ABC, abstractmethod
import argparse
import console
from project import ProjectRegistry


class BaseGenerator(ABC):
    def __init__(self, name:str, description:str):
        self.name_ = name
        self.description_ = description

    @property
    def name(self) :
        return self.name_
    
    @property
    def description(self) :
        return self.description_
    
    @abstractmethod
    def generate(self, *args, **kwargs):
        pass

class GeneratorRegistry:
    def __init__(self):
        self.generators_ : dict[str, BaseGenerator] = {}
  
    @property
    def generators(self) -> dict[str, BaseGenerator]:
        return self.generators_
    
    def register(self, generator: BaseGenerator):
        if generator.name in self.generators:
            console.print_error(f"{generator.name} generator already registered")
        else:
            self.generators[generator.name] = generator

GeneratorRegistry = GeneratorRegistry()


def cmd_generate(generate_params:  argparse.ArgumentParser):
    # Load the project in the directory
    ProjectRegistry.load_projects_in_directory(generate_params.directory, False)

    # Check that the target project exists
    if generate_params.project_name is not None:
        project = ProjectRegistry.projects().get(generate_params.project_name)
        if not project : 
            console.print_error(f"No project found in  {generate_params.directory}")
    else:
        if len(ProjectRegistry.projects() > 1):
            ## List projects name that is presents
            console.print_error(f"Multiple project found in {generate_params.directory}" + 
                                f"{[name for name in ProjectRegistry.project]}")
        project_name = project_dir.name

    # console.print_step("Generating build scripts...")
    # ModuleRegistry.load_modules(generate_params.project_directory)
    # project = ModuleRegistry.get(generate_params.project_name)
    # if not project:
    #     console.print_error(f"Aucun projet trouvé dans le dossier {generate_params.project_directory}")
    #     sys.exit(2)
    
    # generate_params.generator.generate(generate_params, project)        