from abc import ABC, abstractmethod
import console

class BaseCleaner(ABC):
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
    def clean(self, *args, **kwargs):
        pass

class CleanerRegistry:
    def __init__(self):
        self._cleaners : dict[str, BaseCleaner] = {}
  
    @property
    def cleaners(self) -> dict[str, BaseCleaner]:
        return self._cleaners
    
    def register(self, cleaner: BaseCleaner):
        if cleaner.name in self.cleaners:
            console.print_error(f"{cleaner.name} cleaner already registered")
        else:
            self.cleaners[cleaner.name] = cleaner

CleanerRegistry = CleanerRegistry()
