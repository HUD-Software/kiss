from abc import ABC, abstractmethod
import console

class BaseBuilder(ABC):
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
    def build(self, *args, **kwargs):
       pass


class BuilderRegistry:
    def __init__(self):
        self._builder : dict[str, BaseBuilder] = {}
  
    @property
    def builders(self) -> dict[str, BaseBuilder]:
        return self._builder
    
    def register(self, builder: BaseBuilder):
        if builder.name in self.builders:
            console.print_error(f"{builder.name} builder already registered")
        else:
            self.builders[builder.name] = builder

BuilderRegistry = BuilderRegistry()
