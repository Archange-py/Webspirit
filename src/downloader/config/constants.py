"""
The file that is contains constants and function to manipulate files
"""

from . import files_constants as files_const
from .import logger

from typing import Any


def __getattr__(name: str) -> Any:
    for module in [files_const, logger]:
        try:
            return getattr(module, name)

        except:
            pass


AUDIO: str = 'audio'
VIDEO: str = 'video'
SUBTITLES: str = 'subtitles'
AUDIO_VIDEO: str = AUDIO + '_' + VIDEO


if __name__ == "__main__":
    pass