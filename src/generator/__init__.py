from generator.cmake.cmake_generator import CMakeGenerator
from generator.generator import BaseGenerator

GENERATORS: dict[str, type[BaseGenerator]] = {
    CMakeGenerator.name(): CMakeGenerator,
}

def get_generator(name: str) -> BaseGenerator:
    if name not in GENERATORS:
        raise ValueError(f"Unknown generator: {name!r}. Available: {list(GENERATORS.keys())}")
    return GENERATORS[name]()