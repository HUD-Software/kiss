from abc import ABC, abstractmethod
from pathlib import Path


class BaseGenerator(ABC):

    @abstractmethod
    def name(self) -> str:
        """Generator identifier, e.g. 'cmake'."""

    @abstractmethod
    def generate(self, project: dict, project_dir: Path) -> None:
        """Generate build files for the given project inside project_dir."""

    @abstractmethod
    def build(self, project: dict, project_dir: Path, profile: str) -> int:
        """Invoke the build system. Returns the process exit code."""

    def supported_targets(self) -> list[str]:
        return ["*"]
