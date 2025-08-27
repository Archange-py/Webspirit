from ..config.logger import log, LOGGER, Logger, INFO, ERROR, WARNING, DEBUG

from typing import Callable, TypeVar, ParamSpec

from traceback import format_exception

from types import TracebackType

from functools import wraps


P = ParamSpec("P")
R = TypeVar("R")


class ErrorContextManager:
    def __init__(self, message: str, level: int = ERROR, logger: Logger = LOGGER):
        self.message = message
        self.level = level
        self.logger = logger

    def __call__(self, fonction: Callable[P, R]) -> Callable[P, R]:
        @wraps(fonction)
        def _function(*args: P.args, **kwargs: P.kwargs) -> R:
            with self:
                return fonction(*args, **kwargs)

        return _function

    def __enter__(self):
        return self

    def __exit__(self, exc_type: type[BaseException] | None, exc_value: BaseException | None, traceback: TracebackType | None) -> bool:
        if exc_type is not None:
            tb_str = ''.join(format_exception(exc_type, exc_value, traceback))
            self.logger.log(self.level, f"{self.message}\n{tb_str}")

            return True

        return False

def ecm(message: str, error: type = TypeError, level: int = ERROR, logger: Logger = LOGGER):
    log(message, level, logger)
    raise error(message)
