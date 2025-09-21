from ..config.logger import log, LOGGER, Logger, INFO, ERROR, WARNING, DEBUG

from typing import Callable, TypeVar, ParamSpec

from traceback import format_exception

from types import TracebackType

from functools import wraps


__all__: list[str] = [
    'ErrorContextManager', 'ecm',
    'raise_error', 're'
]


P = ParamSpec("P")
R = TypeVar("R")


class ErrorContextManager:
    def __init__(self, message: str = '', level: int = WARNING, logger: Logger = LOGGER, let: bool = True, error: bool = False):
        self.let = let
        self.level = level
        self.error = error
        self.logger = logger
        self.message = message

    def __call__(self, fonction: Callable[P, R]) -> Callable[P, R]:
        @wraps(fonction)
        def _function(*args: P.args, **kwargs: P.kwargs) -> R:
            with self:
                return fonction(*args, **kwargs)

        return _function

    def __enter__(self):
        return self

    def __exit__(self, exc_type: type[BaseException] | None, exc_value: BaseException | None, traceback: TracebackType | None) -> bool:
        if exc_type is not None and self.let:
            tb_str = ''.join(format_exception(exc_type, exc_value, traceback))

            if self.message:
                log(
                    f"{self.message}\n{tb_str}" if self.error else self.message,
                    self.level,
                    self.logger
                )

            return True

        return False

ecm = ErrorContextManager


def raise_error(message: str = '', error: type = TypeError, cause: Exception = None, logger: Logger = LOGGER):
    log(message, ERROR, logger)

    if cause is None:
        raise error(message)

    else:
        raise error(message) from cause


re = raise_error