"""
The file that is contains constants and function to manipulate files
"""


from . import files_constants as files_const
from .import logger

from typing import Any

import contextlib


def __getattr__(name: str) -> Any:
    for module in [files_const, logger]:
        with contextlib.suppress(Exception):
            return getattr(module, name)


AUDIO: str = 'audio'
VIDEO: str = 'video'
SUBTITLES: str = 'subtitles'
AUDIO_VIDEO: str = f'{AUDIO}_{VIDEO}'

__all__: list[str] = [
    var for var in globals() if var.isupper()
] + logger.__all__ + files_const.__all__
