from pathlib import Path


class Context:
    def __init__(self, directory):
        self._directory = Path(directory)

    @property
    def directory(self) -> Path:
        return self._directory

        