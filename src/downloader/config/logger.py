"""
The logger file.
"""


from . import files_constants as file_const

from logging import (
    StreamHandler, Formatter, Logger, getLogger,
    DEBUG, INFO, WARNING, ERROR, CRITICAL
)

from logging.handlers import RotatingFileHandler

from colorlog import ColoredFormatter


file_const.DIR_LOGS.mkdir(exist_ok=True)

LOG_LEVEL: int = DEBUG
BACKUP_COUNT: int = 3 # Up to 3 backup files
MAX_BYTES: int = 5 * 1024 * 1024 # 5 Mo
FORMAT_PATTERN: str = "{asctime} {levelname:<8} {filename:<16} {message}"
LOG_COLORS: dict[str, str] = {
    'DEBUG': 'cyan',
    'INFO': 'green',
    'WARNING': 'yellow',
    'ERROR': 'red',
    'CRITICAL': 'bold_red',
}


def get_file_formatter() -> Formatter:
    return Formatter(
        fmt=FORMAT_PATTERN,
        datefmt="%Y-%m-%d %H:%M:%S",
        style="{",
    )

def get_console_formatter() -> ColoredFormatter:
    return ColoredFormatter(
        fmt=FORMAT_PATTERN,
        datefmt="%Y-%m-%d %H:%M:%S",
        log_colors=LOG_COLORS,
        style="{"
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

        console_formatter: ColoredFormatter = get_console_formatter()
        console_handler: StreamHandler = StreamHandler()
        # console_handler.setFormatter(console_formatter)

        file_formatter: Formatter = get_file_formatter()
        file_handler: RotatingFileHandler = get_file_handler()
        file_handler.setFormatter(file_formatter)

        logger.addHandler(console_handler)
        logger.addHandler(file_handler)

    return logger


LOGGER: Logger = get_logger(__name__)

def log(message: str, level: int = LOG_LEVEL, logger: Logger = LOGGER):
    logger.log(
        level=level,
        msg=str(message),
    )
