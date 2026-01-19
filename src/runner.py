from abc import ABC, abstractmethod
import console

class BaseRunner(ABC):
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
    def run(self, *args, **kwargs):
        pass

class RunnerRegistry:
    def __init__(self):
        self._runners : dict[str, BaseRunner] = {}
  
    @property
    def runners(self) -> dict[str, BaseRunner]:
        return self._runners
    
    def register(self, runner: BaseRunner):
        if runner.name in self.runners:
            console.print_error(f"{runner.name} runner already registered")
        else:
            self.runners[runner.name] = runner

RunnerRegistry = RunnerRegistry()
