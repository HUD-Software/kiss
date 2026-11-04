from dataclasses import dataclass
from typing import Literal, Never


@dataclass(frozen=True, slots=True)
class Ok[T]:
    value: T

    def is_ok(self) -> Literal[True]:
        return True

    def is_err(self) -> Literal[False]:
        return False

    def unwrap(self) -> T:
        return self.value


@dataclass(frozen=True, slots=True)
class Err[E]:
    error: E

    def is_ok(self) -> Literal[False]:
        return False

    def is_err(self) -> Literal[True]:
        return True

    def unwrap(self) -> Never:
        if isinstance(self.error, BaseException):
            raise self.error
        raise UnwrapError(self.error)


class UnwrapError(Exception):
    def __init__(self, error: object):
        super().__init__(f"Called unwrap() on an Err: {error}")
        self.error = error

type Result[T, E] = Ok[T] | Err[E]