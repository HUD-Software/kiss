from abc import ABC, abstractmethod

class BaseGenerator(ABC):

    @abstractmethod
    def generate(self, workspace, resolved) -> None:
        """Generate build files from resolved workspace."""
        pass
    @classmethod
    @abstractmethod
    def name(self) -> str:
        """Generator name (e.g. 'cmake', 'meson')."""
        pass
    
    @classmethod
    @abstractmethod
    def supported_targets(self) -> list[str]:
        """List of supported targets (e.g. ['x86_64-pc-windows-msvc'])."""
        pass