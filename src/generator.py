
from abc import ABC, abstractmethod
import console

class BaseGenerator(ABC):
    def __init__(self, name:str, description:str):
        self._name = name
        self._description = description

    @property
    def name(self) :
        return self._name
    
    @property
    def description(self) :
        return self._description
    
    @abstractmethod
    def generate(self, *args, **kwargs):
        pass

class GeneratorRegistry:
    def __init__(self):
        self._generators : dict[str, BaseGenerator] = {}
  
    @property
    def generators(self) -> dict[str, BaseGenerator]:
        return self._generators
    
    def register(self, generator: BaseGenerator):
        if generator.name in self.generators:
            console.print_error(f"{generator.name} generator already registered")
        else:
            self.generators[generator.name] = generator

GeneratorRegistry = GeneratorRegistry()
