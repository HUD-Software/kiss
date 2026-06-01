from generator.generator import BaseGenerator

class CMakeGenerator(BaseGenerator):
    def __init__(self):
        super().__init__()

    def generate(self, workspace, output_dir) -> None:
        pass

    @classmethod
    def name(cls) -> str:
        return "cmake"

    @classmethod
    def supported_targets(cls) -> list[str]:
        return []