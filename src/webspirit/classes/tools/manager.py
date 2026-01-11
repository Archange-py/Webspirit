"""
Implémentation des différentes classes pour la gestion des fichiers, comme json ou csv,
comportant des données à manipuler.
"""


from webspirit.classes.tools.contexterror import ecm, re

from webspirit.classes.tools.checktype import CheckType

from webspirit.classes.tools.typing import StrPath

from abc import ABCMeta, ABC, abstractmethod

from webspirit.config.logger import info

from typing import Iterator, Self, Any

from threading import Lock

from shutil import copy2

import json, os


__all__: list[str] = [
    'ManagerMeta',
    'BaseManager',

    'DEFAULT_VALUE',

    'load_manager',

    'JsonManager',
    'load_json',
    'save_json',
    'delete_json',

    'CsvManager',
]


class ManagerMeta(ABCMeta):
    instances: dict[tuple[type, StrPath | None], Any] = {}
    _lock: Lock = Lock()

    def __call__(cls: type, path: StrPath, *args, **kwargs):
        path = StrPath(path, exist=False)
        key: tuple[type, StrPath | None] = (cls, path.absolute())

        with cls._lock:
            if key not in cls.instances:
                instance = super().__call__(path, *args, **kwargs)
                cls.instances[key] = instance

        return cls.instances[key]

class BaseManager(ABC, metaclass=ManagerMeta):
    registry: dict[str, type] = {}
    repr_format: bool = True

    def __init_subclass__(cls: type, *, extension: str | None = None, **kwargs):
        super().__init_subclass__(**kwargs)

        if extension is None:
            re(f"{cls.__name__} doit définir une extension, exemple: class JsonManager(BaseManager, extension='.json')", error=ValueError)

        if extension in cls.registry:
            re(f"Extension '{extension}' déjà utilisée dans la classe {cls.registry[extension].__name__}", error=ValueError)

        cls.extension: str = extension
        cls.registry[extension] = cls

    def __init__(self, path: StrPath):
        self.path = StrPath(path, exist=False)
        self._data: dict | list = {}
        self._raw_data: dict | list = {}
        self.load()

    def __str__(self) -> str:
        return self.path.relpath().as_posix()

    def __repr__(self) -> str:
        return json.dumps(self._data, indent=2, ensure_ascii=False) if self.__class__.repr_format else self.__str__()

    def __setattr__(self, name: str, value: Any) -> None:
        object.__setattr__(self, name, value)

        if name == 'path' and not getattr(self, '_suppress_check_on_path_set', False):
            object.__setattr__(self, '_suppress_check_on_path_set', True)

            try:
                self.path = self.path.absolute()
                self._check()

            finally:
                object.__setattr__(self, '_suppress_check_on_path_set', False)

    def __getitem__(self, key: str | int) -> Any:
        if isinstance(self._data, dict):
            if not isinstance(key, str):
                re(f"Index de liste attendu (str) pour {self.path.relpath()}")

            return self._data[key]

        elif isinstance(self._data, list):
            if not isinstance(key, int):
                re(f"Index de liste attendu (int) pour {self.path.relpath()}")

            return self._data[key]

        else:
            re("Formatage json non supporté")

    def __setitem__(self, key: str | int, value: Any):
        if isinstance(self._data, dict):
            if not isinstance(key, str):
                re(f"Index de liste attendu (str) pour {self.path.relpath()}")

            self._data[key] = value

        elif isinstance(self._data, list):
            if not isinstance(key, int):
                re(f"Index de liste attendu (int) pour {self.path.relpath()}")

            self._data[key] = value

        else:
            re("Formatage json non supporté")

    def __iter__(self) -> Iterator:
        return iter(self._data)

    def __len__(self) -> int:
        return len(self._data)

    @property
    def raw_data(self) -> dict | list:
        return self._raw_data

    @property
    def data(self) -> dict | list:
        return self._data

    def _check(self):
        """Valide et normalise le chemin utilisé par le manager. Cette méthode s'assure que le fichier cible existe, possède la bonne extension et que son répertoire est correctement créé.

        Raises:
            ValueError: Si le chemin pointe vers un répertoire ou si l'extension du fichier ne correspond pas à celle attendue par le manager.
        """
        self.path = StrPath(self.path, exist=False)

        if StrPath.is_path(self.path, dir=True):
            re(f"Le chemin fourni est un répertoire au lieu d'être un fichier pour le manager {self.__class__.__name__}", error=ValueError)

        if self.path.suffix != self.extension:
            re(f"Le fichier fourni n'a pas la bonne extension '{self.extension}' pour le manager {self.__class__.__name__}", error=ValueError)

        if not StrPath.is_path(self.path.dirname(), dir=True):
            with ecm(f"Une erreur est survenue lors de la création du répertoire de {self.path.name}ERROR", _raise=True):
                os.makedirs(self.path.dirname(), exist_ok=True)

                info(f"Création du répertoire {self.path.dirname().relpath()} pour le fichier {self.path.name}")

        if not StrPath.is_path(self.path) or self.path.stat().st_size == 0:
            with ecm(f"Une erreur est survenue lors de la création du fichier {self.path.name}ERROR", _raise=True):
                with self.path.open('w', encoding='utf-8') as file:
                    file.write('{}')

                    info(f"Création d'un fichier vide {self.path.relpath()}, car il n'existe pas")

        self.path = StrPath(self.path)

    def to_dict(self) -> dict:
        """Retourne les données du manager sous forme de dictionnaire.

        Returns:
            dict: Les données internes du manager sous forme de dictionnaire.

        Raises:
            Exception: Si les données ne sont pas stockées dans un format de type dict.
        """
        if isinstance(self._data, dict):
            return self._data

        else:
            re('Les données ne peuvent pas être récupérées sous un format de type dict')

    def to_list(self) -> list:
        """Retourne les données du manager sous forme de liste.

        Returns:
            list: Les données internes du manager sous forme de liste.

        Raises:
            Exception: Si les données ne sont pas stockées dans un format de type list.
        """
        if isinstance(self._data, list):
            return self._data

        else:
            re('Les données ne peuvent pas être récupérées sous un format de type list')


    @abstractmethod
    def load_raw(self) -> dict | list:
        "Charge les données brutes du fichier source"

    @abstractmethod
    def load(self) -> Self:
        "Formate les données brutes pour correspondre avec celles attendues, et met à jours le manager"

    @abstractmethod
    def save(self, data: dict | list | None = None) -> Self:
        "Sauvegarde les données dans le fichier source"

    def delete(self):
        "Supprime le fichier source de manière transparente"
        with ecm(f"Une erreur est survenue lors de la suppression de {self.path.relpath()}"):
            os.remove(self.path)

            info(f"Delete '{self.path.name}' in '{self.path.dirname().relpath()}' directory")

        BaseManager.instances.pop((self.__class__, self.path.absolute()))

    @CheckType
    def copy(self, destination: StrPath) -> 'JsonManager | CsvManager':
        """Copie le fichier source avec ses métadonnées dans un autre fichier de destination.

        Args:
            destination (StrPath): Le répertoire final où sera enregistrer le fichier qui sera une copie conforme de l'original.

        Returns:
            JsonManager | CsvManager: Le manager vers la copie du fichier original.
        """
        if not StrPath.is_path(destination, dir=True):
            destination = destination.dirname()

            info(f"La destination fournie '{destination.relpath()}' est un fichier, utilisation du répertoire parent")

        os.makedirs(destination.dirname(), exist_ok=True)

        with ecm(f"Une erreur est survenue lors de la copie de {self.path.relpath()}ERROR"):
            copy2(self.path, destination)

            info(f"Copy '{self.path.name}' in '{destination.relpath()}' directory")

        return self.__class__(destination / self.path.name)

class JsonManager(BaseManager, extension='.json'):
    def load_raw(self) -> dict | list:
        with ecm(f"Une erreur est survenue lors du chargement de {self.path.relpath()}ERROR", _raise=True):
            with self.path.open('r', encoding='utf-8') as file:
                data: dict | list = json.load(file)

                info(f"Load '{self.path.name}' in '{self.path.dirname().relpath()}' directory")

        self._raw_data: dict | list = data

        return self._raw_data

    def load(self) -> Self:
        self._data: dict | list = self.load_raw()

        return self

    def save(self, data: dict | list | None = None) -> Self:
        if data is None:
            data = self._data

        with ecm(f"Une erreur est survenue lors de la sauvegarde de {self.path.relpath()}ERROR", _raise=True):
            with self.path.open('w', encoding='utf-8') as file:
                json.dump(data, file, indent=2, sort_keys=True)

                info(f"Save {self.path.name} in '{self.path.dirname().relpath()}'")

        self._data = data
    
        return self

def load_json(path: StrPath) -> JsonManager:
    """Crée un gestionnaire json pour le fichier fourni.

    Args:
        path (StrPath): Le chemin vers le fichier json.

    Returns:
        JsonManager: Une instance de JsonManager associée au fichier fourni.
    """
    return JsonManager(path)

def save_json(data: dict | list | JsonManager | None, path: StrPath | None = None) -> JsonManager:
    """Sauvegarde des données json dans un fichier en gérant plusieurs cas d'entrée. Cette fonction peut utiliser soit des données brutes, soit un JsonManager existant, et créer ou mettre à jour le fichier cible.

    Args:
        data (dict | list | JsonManager | None): Les données à sauvegarder ou un JsonManager existant. Peut être None si un chemin est fourni pour charger et sauvegarder.
        path (StrPath | None): Le chemin vers le fichier json à sauvegarder. Peut être None si un JsonManager est fourni.

    Returns:
        JsonManager: Une instance de JsonManager correspondant au fichier sauvegardé.

    Raises:
        ValueError: Si ni les données ni le chemin ne sont fournis.
    """
    if data is None and path is None:
        re("Vous devez fournir à minima des données et/ou un chemin pour sauvegarder le fichier json", error=ValueError)

    elif data is None:
        return JsonManager(path).save()

    elif path is None and isinstance(data, JsonManager):
        return data.save()

    else:
        return JsonManager(path).save(data)

def delete_json(path: StrPath | JsonManager):
    """Supprime un fichier json en acceptant soit un chemin soit un manager.

    Args:
        path (StrPath | JsonManager): Le chemin vers le fichier json ou une instance de JsonManager pointant vers ce fichier.
    """
    if isinstance(path, JsonManager):
        path: StrPath = path.path

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
        return BaseManager.registry[path.suffix](path)
