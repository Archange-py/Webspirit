from webspirit.config.logger import (
    log, LOGGER, Logger, INFO, ERROR, WARNING, DEBUG,
    debug, info, error, warning, critical
)

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
    def __init__(self, message: str = 'EX_TYPE - EX_VALUE', level: int = WARNING, _raise: bool = False, logger: Logger = LOGGER):
        """Un gestionnaire de contexte qui fonctionne similairement à contextlib.suppress(Exception).

        Args:
            message (str, optional): Le message affiché dans les logs. Il peut prendre différents mots-clés pré-définis. On a ERROR, EX_TYPE, et EX_VALUE par exemple. Defaults to ''.
            level (int, optional): Le niveau du message pour le log. Defaults to WARNING.
            _raise (bool, optional): Permet de provoquer l'erreur original en plus d'afficher un message dans le log. Defaults to False.
            logger (Logger, optional): Un logger pour gérer les logs. Defaults to LOGGER.
        """
        self.level = level
        self._raise = _raise
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

    def __exit__(self, EX_TYPE: type[BaseException] | None, EX_VALUE: BaseException | None, traceback: TracebackType | None) -> bool:
        if EX_TYPE is not None:
            ERROR: str = '\n' + ''.join(format_exception(EX_TYPE, EX_VALUE, traceback))

            if self.message:
                log(self.message.replace('ERROR', ERROR).replace('EX_TYPE', EX_TYPE.__name__).replace('EX_VALUE', str(EX_VALUE)), self.level, self.logger)

        return False if self._raise else True


ecm = ErrorContextManager


def raise_error(message: str = '', error: type = TypeError, cause: Exception = None, logger: Logger = LOGGER):
    error(message, logger)

    if cause is None:
        raise error(message)

    else:
        raise error(message) from cause

re = raise_error