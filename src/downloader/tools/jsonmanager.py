from ..config.logger import log, INFO, ERROR, WARNING, DEBUG

from .checktype import CheckType, StrPath

import os, json


class JSONManager:
    @staticmethod
    @CheckType()
    def load(path: StrPath) -> dict:
        name: str = os.path.split(path)[1]
    
        with open(path, 'r', encoding='utf-8') as file:
            log(f"Load '{name}' in '{os.path.relpath(path)}'", INFO)
            return json.load(file)

    @staticmethod
    @CheckType()
    def save(path: StrPath, data: dict):
        name: str = os.path.split(path)[1]

        with open(path, 'w', encoding='utf-8') as file:
            log(f"Save {name} in '{os.path.relpath(path)}'", INFO)
            json.dump(data, file, indent=2)