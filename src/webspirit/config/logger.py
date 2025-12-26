"""
The logger file.
"""


from . import dynamic_constants as file_const

from logging import (
    StreamHandler, Formatter, Logger, getLogger,
    DEBUG, INFO, WARNING, ERROR, CRITICAL
)

from IPython import InteractiveShell, get_ipython

from logging.handlers import RotatingFileHandler

from colorlog import ColoredFormatter

from rich.console import Console

from functools import partial

from typing import Any


file_const.DIR_LOGS.mkdir(exist_ok=True)

CONSOLE = Console()
STACK_LEVEL: int = 5
LOG_LEVEL: int = DEBUG
BACKUP_COUNT: int = 3 # Up to 3 backup files
MAX_BYTES: int = 5 * 1024 * 1024 # 5 Mo

LIGHT_PURPLE: str = "\033[38;5;177m"
RESET: str = "\033[0m"

FORMAT_PATTERN: str = "{asctime:<20} {filename:>20}:{lineno:<5} {levelname:<8} {message}"
FORMAT_PATTERN_COLORS: str = "{light_black}{asctime:<20} \033[38;5;177m{filename:>20}\033[0m:{purple}{lineno:<5} {log_color}{levelname:<8}{reset} {white}{message}"

LOG_COLORS: dict[str, str] = {
    'DEBUG': 'cyan',
    'INFO': 'green',
    'WARNING': 'yellow',
    'ERROR': 'red',
    'CRITICAL': 'bold_red',
}


class NotebookFormatter(ColoredFormatter):
    def format(self, record) -> str:
        ip: InteractiveShell = get_ipython()

        if ip is not None and record.filename.endswith('.py') and record.filename[:-3].isdigit():
            cell_num: int = ip.execution_count
            record.filename = f"In[{cell_num}]"

        return super().format(record)

def get_file_formatter() -> Formatter:
    return Formatter(
        fmt=FORMAT_PATTERN,
        datefmt="%Y-%m-%d %H:%M:%S",
        style="{",
    )

def get_console_formatter() -> NotebookFormatter:
    return NotebookFormatter(
        fmt=FORMAT_PATTERN_COLORS,
        datefmt="%Y-%m-%d %H:%M:%S",
        log_colors=LOG_COLORS,
        style="{",
    )

def get_file_handler() -> RotatingFileHandler:
    return RotatingFileHandler(
        filename=file_const.PATH_LOGS,
        backupCount=BACKUP_COUNT,
        maxBytes=MAX_BYTES,
        encoding='utf-8'
    )

def get_logger(name: str) -> Logger:
    logger: Logger = getLogger(name)

    if not logger.hasHandlers():
        logger.setLevel(LOG_LEVEL)

        console_formatter: NotebookFormatter = get_console_formatter()
        console_handler: StreamHandler = StreamHandler()
        console_handler.setFormatter(console_formatter)

        file_formatter: Formatter = get_file_formatter()
        file_handler: RotatingFileHandler = get_file_handler()
        file_handler.setFormatter(file_formatter)

        logger.addHandler(console_handler)
        logger.addHandler(file_handler)

        logger.propagate = False

    return logger


LOGGER: Logger = get_logger(__name__)

def log(message: Any, level: int = LOG_LEVEL, logger: Logger | None = None):
    if logger is None:
        logger = LOGGER

    logger.log(
        level=level,
        msg=str(message),
        stacklevel=STACK_LEVEL
    )


debug = partial(log, level=DEBUG)
info = partial(log, level=INFO)
warning = partial(log, level=WARNING)
error = partial(log, level=ERROR)
critical = partial(log, level=CRITICAL)


__all__: list[str] = [
    var for var in globals() if var.isupper()
] + [
    'get_file_formatter',
    'get_console_formatter',
    'get_file_handler',
    'get_logger',
    'log',
    'debug',
    'info',
    'warning',
    'error',
    'critical'
]