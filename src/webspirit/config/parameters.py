"""
Les constantes générées de manière dynamique par le fichier settings.json
"""


from webspirit.config.files_constants import (
    PATH_SETTINGS,

    DIR_RESOURCES,
    DIR_WEBSPIRIT,
)

from pathlib import Path

from typing import Any

import json


DEFAULT: str = 'default'

def load_json(path: Path) -> dict:
    with path.open('r', encoding='utf-8') as file:
        return json.load(file)

SETTINGS: dict[str, Any] = load_json(PATH_SETTINGS)


PATH_FFMPEG: Path = DIR_RESOURCES / 'FFmpeg/bin/ffmpeg.exe' if SETTINGS['FFmpegPath'] == DEFAULT else SETTINGS['FFmpegPath']

LOG_NAME: str = 'webspirit.log' if SETTINGS['LogFileName'] == DEFAULT else SETTINGS['LogFileName']
DIR_LOGS: Path = DIR_WEBSPIRIT / 'logs' if SETTINGS['LogDir'] == DEFAULT else SETTINGS['LogDir']
PATH_LOGS: Path = DIR_LOGS / LOG_NAME


__all__: list[str] = [
    var for var in globals() if var.isupper()
]