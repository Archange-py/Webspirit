from webspirit.config.logger import DEBUG, INFO, debug, info, error, warning, critical

from .contexterror import ecm, re

from .checktype import CheckType

from ..webfiles import StrPath

import  json, os


__all__: list[str] = [
    'JSONManager',
    'load_json',
    'save_json'
]


class JSONManager(dict):
    SUFFIX: list[str] = ['.json']
    JSON: StrPath | None = None

    @CheckType
    def __init__(self, path: StrPath):
        self.path = path

        super().__init__(self.load())

    @staticmethod
    def check(path: StrPath):
        if not (path.suffix in JSONManager.SUFFIX):
            re(f"The file provided hasn't the common json extension {JSONManager.SUFFIX[0]}")

        if not StrPath.is_path(path.dirname(), dir=True):
            with ecm(f"An error is occurred when tried to create the directory of {path.name}ERROR"):
                os.makedirs(path.dirname(), exist_ok=True)

                info(f"Created the directory {path.dirname()} for the {path.name} file")

        if not StrPath.is_path(path):
            with ecm(f"An error is occurred when tried to create the file {path.name}ERROR"):
                with path.open('w', encoding='utf-8') as file:
                    file.write('{}')

                    info(f"Created an empty file {path}, because doesn't exist")

    @CheckType
    @staticmethod
    def load_json(path: StrPath) -> dict:
        JSONManager.check(path)

        with ecm(f"An error was occurred with the load of {path.relpath()}ERROR"):
            with path.open('r', encoding='utf-8') as file:
                info(f"Load '{path.name}' in '{path.dirname()}' directory")

                return json.load(file)

    def load(self) -> dict:
        return JSONManager.load_json(self.path)

    @CheckType('path')
    @staticmethod
    def save_json(data: 'dict | JSONManager', path: StrPath | None = None):
        JSONManager.check(path)

        if path is None:
            if isinstance(data, JSONManager):
                path: StrPath = data.path

            else:
                re("You must give the path argument if you don't provide a JSONManager object to the data argument of the save_json static method")

        with ecm(f"An error was occurred with the save of {path.relpath()}"):
            with path.open('w', encoding='utf-8') as file:
                json.dump(data, file, indent=2, sort_keys=True)

                info(f"Save {path.name} in '{path.dirname()}'")

    @CheckType
    def save(self, data: 'dict | JSONManager | None' = None):
        if data is None:
            data = self

        JSONManager.save_json(data, self.path)

    @CheckType
    @staticmethod
    def delete_json(self, path: StrPath | None = None):
        if StrPath.is_path(path, suffix=JSONManager.SUFFIX):
            if path is None:
                path = JSONManager.JSON

            with ecm(f"An error was occurred with the save of {path.relpath()}"):
                os.remove(path)

        else:
            re(f"{path.relpath()} didn't exists, or it is not a json path")

    def delete(self):
        JSONManager.delete_json(self.path)

@CheckType
def load_json(path: StrPath):
    JSONManager.JSON = path
    debug(f"Current path of the JSON variable is '{JSONManager.JSON}'")

    return JSONManager.load_json(path)

@CheckType('path')
def save_json(data: JSONManager | dict, path: StrPath | None = None) -> dict:
    if path is None:
        if isinstance(data, JSONManager):
            path: StrPath = data.path

            debug(f"Use the current path of the JSONManager object '{JSONManager.JSON}' given to the 'data' argument, because 'path' argument provided is None")

        else:
            if JSONManager.JSON is None:
                re('You must use first the load_json function and provide a path to a json file that can be used after here')

            path: StrPath = JSONManager.JSON

            debug(f"Use the current path of the JSON variable '{JSONManager.JSON}', because the 'path' argument provided is None")

    return JSONManager.save_json(data, path)

def delete_json(path: StrPath):
    pass