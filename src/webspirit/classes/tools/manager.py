from webspirit.classes.tools.contexterror import ecm, re

from webspirit.classes.tools.checktype import CheckType

from webspirit.classes.tools.typing import StrPath

from webspirit.config.logger import info, debug

from abc import ABCMeta, ABC, abstractmethod

from typing import Self, Any

from threading import Lock

from shutil import copy2

import json, os


__all__: list[str] = [
    'ManagerMeta',
    'BaseManager',

    'load_manager',

    'JsonManager',
    'load_json',
    'save_json',
    'delete_json',

    'CsvManager',
]


class ManagerMeta(ABCMeta):
    _instances: dict[tuple[type, StrPath | None], Any] = {}
    _lock: Lock = Lock()

    @CheckType('path')
    def __call__(cls: type, path: StrPath, *args, **kwargs):
        key: tuple[type, StrPath | None] = (cls, path.absolute())

        with cls._lock:
            if key not in cls._instances:
                instance = super().__call__(path, *args, **kwargs)
                cls._instances[key] = instance

        return cls._instances[key]

class BaseManager(dict, ABC, metaclass=ManagerMeta):
    _registry: dict[str, type] = {}
    DEFAULT_VALUE: str = 'default'

    def __init_subclass__(cls: type, *, extension: str | None = None, **kwargs):
        super().__init_subclass__(**kwargs)

        if extension is None:
            re(f"{cls.__name__} doit définir une extension, exemple: class JsonManager(BaseManager, extension='.json')", error=ValueError)

        if extension in cls._registry:
            re(f"Extension '{extension}' déjà utilisée dans la classe {cls._registry[extension].__name__}", error=ValueError)

        cls.extension: str = extension
        cls._registry[extension] = cls

    @CheckType
    @abstractmethod
    def __init__(self, path: StrPath):
        self.path = path
        self.check()
        super().__init__(self._get_data())

    @abstractmethod
    def _get_data(self) -> dict:
        "Renvoie le dictionnaire à utiliser pour initialiser l'héritage de dict"

    def check(self):
        self.path = StrPath(self.path, exist=False)

        if StrPath.is_path(self.path, dir=True):
            re(f"Le chemin fourni est un répertoire au lieu d'être un fichier pour le manager {self.__class__.__name__}", error=ValueError)

        if self.path.suffix != self.extension:
            re(f"Le fichier fourni n'a pas la bonne extension '{self.extension}' pour le manager {self.__class__.__name__}", error=ValueError)

        if not StrPath.is_path(self.path.dirname(), dir=True):
            with ecm(f"Une erreur est survenue lors de la création du répertoire de {self.path.name}ERROR", _raise=True):
                os.makedirs(self.path.dirname(), exist_ok=True)

                info(f"Création du répertoire {self.path.dirname()} pour le fichier {self.path.name}")

        if not StrPath.is_path(self.path):
            with ecm(f"Une erreur est survenue lors de la création du fichier {self.path.name}ERROR", _raise=True):
                with self.path.open('w', encoding='utf-8') as file:
                    file.write('{}')

                    info(f"Création d'un fichier vide {self.path.relpath()}, car il n'existe pas")

        self.path = StrPath(self.path)

    def __setattr__(self, name: str, value: Any) -> None:
        object.__setattr__(self, name, value)

        if name == 'path' and not getattr(self, '_suppress_check_on_path_set', False):
            object.__setattr__(self, '_suppress_check_on_path_set', True)

            try:
                self.check()

            finally:
                object.__setattr__(self, '_suppress_check_on_path_set', False)

    @abstractmethod
    def load(self):
        "Charge les données depuis le fichier source"

    @abstractmethod
    def save(self, data: dict | None = None):
        "Sauvegarde les données dans le fichier source"

    def delete(self):
        with ecm(f"Une erreur est survenue lors de la suppression de {self.path.relpath()}"):
            os.remove(self.path)

            info(f"Delete '{self.path.name}' in '{self.path.dirname()}' directory")

    @CheckType
    def copy(self, destination: StrPath) -> Any:
        if not StrPath.is_path(destination, dir=True):
            destination = destination.dirname()

            info(f"La destination fournie '{destination.relpath()}' est un fichier, utilisation du répertoire parent")

        os.makedirs(destination.dirname(), exist_ok=True)

        with ecm(f"Une erreur est survenue lors de la copie de {self.path.relpath()}ERROR"):
            copy2(self.path, destination)

            info(f"Copy '{self.path.name}' in '{destination.relpath()}' directory")

        return JsonManager(destination / self.path.name)


class JsonManager(BaseManager, extension='.json'):
    def _get_data(self) -> dict:
        return self.load()

    def load(self) -> 'Self':
        with ecm(f"Une erreur est survenue lors du chargement de {self.path.relpath()}ERROR", _raise=True):
            with self.path.open('r', encoding='utf-8') as file:
                dico: dict = json.load(file)

                info(f"Load '{self.path.name}' in '{self.path.dirname().relpath()}' directory")

        self.update(dico)
        return self

    def save(self, data: dict | None = None) -> dict:
        if data is None:
            data = dict(self)

        with ecm(f"Une erreur est survenue lors de la sauvegarde de {self.path.relpath()}ERROR", _raise=True):
            with self.path.open('w', encoding='utf-8') as file:
                json.dump(data, file, indent=2, sort_keys=True)

                info(f"Save {self.path.name} in '{self.path.dirname()}'")


@CheckType
def load_json(path: StrPath) -> JsonManager:
    return JsonManager(path).load()

def save_json(data: dict | JsonManager | None, path: StrPath | None = None) -> dict:
    if data is None and path is None:
        re("Vous devez fournir à minima des données et/ou un chemin pour sauvegarder le fichier json", error=ValueError)

    elif data is None:
        manager: JsonManager = JsonManager(path)
        data = dict(manager)

        return manager.save(data)

    elif path is None:
        if isinstance(data, JsonManager):
            path = data.path

            return data.save(dict(data))

    else:
        return JsonManager(path).save(data)


@CheckType
def delete_json(path: StrPath):
    JsonManager(path).delete()


class CsvManager(BaseManager, extension='.csv'):
    def load(self):
        print("Loading CSV")


@CheckType
def load_manager(path: StrPath) -> Any:
    """Récupère une instance du manager associé à l'extension du fichier fourni.

    Args:
        path (StrPath): Le chemin vers le fichier.

    Returns:
        Any: Une instance du manager associé à l'extension du fichier fourni.
    """
    with ecm(f"EX_TYPE: EX_VALUE - Aucun manager trouvé pour le fichier {path.name}, d'extension {path.suffix}", _raise=True):
        return BaseManager._registry[path.suffix](path)
