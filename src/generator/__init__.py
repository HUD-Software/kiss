from generator.generator import BaseGenerator
from generator.cmake.cmake_generator import CMakeGenerator

# Registry of all available generators
GENERATORS: dict[str, type[BaseGenerator]] = {
    "cmake": CMakeGenerator,
}


def get_generator(name: str) -> BaseGenerator:
    """Instantiate a generator by name. Raises ValueError if unknown."""
    if name not in GENERATORS:
        available = ", ".join(GENERATORS.keys())
        raise ValueError(f"Unknown generator '{name}'. Available: {available}")
    return GENERATORS[name]()


def available_generators() -> list[str]:
    return list(GENERATORS.keys())
