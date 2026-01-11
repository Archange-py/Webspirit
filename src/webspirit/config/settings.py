"""
Les constantes générées de manière dynamique grâce aux valeurs définies dans les fichier json de configurations.
"""


from webspirit.config.constants import DIR_DATA_SETTINGS, PATH_SETTINGS, PATH_USER

from webspirit.classes.tools.manager import BaseManager, JsonManager

from webspirit.classes.tools.contexterror import ecm, re

from webspirit.classes.tools.checktype import CheckType

from webspirit.classes.tools.typing import StrPath

from IPython.display import DisplayHandle, display

from webspirit.config.logger import DEBUG

from collections.abc import Iterable

import ipywidgets as widgets

from types import ModuleType

from typing import Any

import json, os



class Parameter(dict):
    def __init__(self, name: str, schema: StrPath = PATH_SETTINGS, user: StrPath = PATH_USER, dir_config: StrPath = DIR_DATA_SETTINGS):
        self.dir_config = dir_config

        self.schema = JsonManager(schema)
        self.user = JsonManager(user)

        self.name = name

        if self.name in self.schema:
            self.meta = self.schema[self.name]

        else:
            re(f"Le paramètre '{self.name}' n'existe pas dans la configuration {self.schema.path.relpath()}", KeyError)

        super().__init__(self.meta)

    def __str__(self) -> str:
        return self.name

    def __repr__(self) -> str:
        return f"{self.name}: {self.resource}"

    def get_default(self) -> Any:
        """Récupère la valeur par défaut du paramètre en fonction des différentes sources possibles"""
        if self.name in self.user:
            return self.user[self.name]

        elif self.default is not None:
            return self.default

        elif self.object is not None:
            return self.get_default_obj()

        re(f"Le paramètre '{self.name}' n'a pas de valeur défini correctement dans '{self.schema.path.relpath()}'")

    def get_default_obj(self) -> Any:
        """Récupère la valeur par défaut du paramètre en fonction de l'objet source et des options pré-définies"""
        if isinstance(self.obj, Iterable):
            if self.value in self.obj:
                return self.value

            else:
                re(f"Le paramètre '{self.name}' défini par défaut dans le champs source avec '{self.value}' n'existe pas dans {self.obj}", ValueError)

        elif hasattr(self.obj, '__getitem__') and self.index is not None:
            return self.obj[self.index]

        elif self.attr is not None and hasattr(self.obj, self.attr):
            return getattr(self.obj, self.attr)

        return self.obj

    def get_options(self) -> Iterable | None:
        """Récupère les valeurs possibles du paramètre si l'objet source est itérable"""
        return list(self.obj) if isinstance(self.obj, Iterable) else None

    def get_obj(self) -> Any | None:
        """Récupère l'objet source défini dans le paramètre de configuration"""
        if self.object is None:
            return None

        lib: list[str] = self.object.split('.')

        with ecm(_raise=True):
            module: ModuleType = __import__('.'.join(lib[:-1]), fromlist=[lib[-2]])

        if (obj := getattr(module, lib[-1], None)) is None:
            re(f"Le module '{module}' n'a pas d'attribut '{lib[-1]}' pour le paramètre {self.name}", AttributeError)

        os.chdir(self.dir_config)

        if hasattr(obj, '__call__') and len(params := self.params):
            obj = obj(*params)

        return obj

    def serial(self) -> Any | None:
        """Renvoi le paramètre serializable avec les normes d'un fichier json"""
        with ecm(f"Impossible de sérialiser la valeur '{self.resource}' de type '{type(self.resource)}' du paramètre '{self.name}'", level=DEBUG):
            json.dumps(self.resource)

            return self.resource

        return str(self.resource)

    def get_widgets(self) -> Any | None:
        """Génère un widget ipywidgets en fonction du type de paramètre défini"""
        if self.type == 'bool':
            return widgets.Checkbox(value=self.resource, description=self.label)

        elif self.type == 'text':
            return widgets.Text(value=self.resource or '', description=self.label)

        elif self.type == 'list':
            return widgets.Dropdown(options=self.options, value=self.resource, description=self.label)

        elif self.type == 'path':
            w = widgets.Text(value=self.resource or '', description=self.label)
            w.placeholder = "Chemin du dossier/fichier ..."

            return w

        return None

    @property
    def resource(self) -> Any:
        """La valeur du paramètre dans la configuration"""
        return self.get_default()

    @property
    def options(self) -> Iterable | None:
        """Si défini, les valeurs possibles du paramètre"""
        return self.get_options()

    @property
    def obj(self) -> Any | None:
        """Si défini, l'objet source qui permet de récupérer la valeur du paramètre"""
        return self.get_obj()

    @property
    def type(self) -> str | None: return self.meta.get('type', None)

    @property
    def label(self) -> str | None: return self.meta.get('label', None)

    @property
    def default(self) -> Any | None: return self.meta.get('default', None)

    @property
    def source(self) -> dict | None: return self.meta.get('source', None)

    @property
    def object(self) -> str | None: return self.source.get('object', None)

    @property
    def params(self) -> list[Any]: return self.source.get('params', [])

    @property
    def default_src(self) -> dict: return self.source.get('default', {})

    @property
    def value(self) -> Any | None: return self.default_src.get('value', None)

    @property
    def attr(self) -> Any | None: return self.default_src.get('attr', None)

    @property
    def index(self) -> Any | None: return self.default_src.get('index', None)

class ConfigManager(dict):
    @CheckType
    def __init__(self, schema: StrPath = PATH_SETTINGS, user: StrPath = PATH_USER, dir_config: StrPath = DIR_DATA_SETTINGS):
        self.dir_config =  dir_config

        self.schema = JsonManager(schema)
        self.user = JsonManager(user)

        self.config: dict[str, Parameter] = self.build()
        self.user.save({
            name: parameter.serial() for name, parameter in self.config.items()
        })

        super().__init__(self.user.to_dict())

    def __str__(self) -> str:
        return json.dumps({
            name: parameter.resource for name, parameter in self.config.items()
        }, indent=2, ensure_ascii=False)

    __repr__ = __str__

    def build(self) -> dict[str, Parameter]:
        """Construit les paramètres de configuration avec leurs valeurs respectives à partir du schéma défini"""
        return {
            name: Parameter(name, self.schema.path, self.user.path, self.dir_config)
            for name in self.schema
        }

    def save(self):
        """Sauvegarde la configuration actuelle dans le fichier utilisateur"""
        self.user.save(self)

    def reset(self, *parameters: list[str] | None):
        """Supprime le fichier avec les données de l'utilisateur si parameters est null, sinon supprime les paramètres donnés dans parameters

        Args:
            parameters (list[str] | None, optional): La liste de paramètres à supprimer. Defaults to None.
        """
        if not len(parameters):
            self.clear()
            self.save()

            self.config = self.build()

        else:
            for name in parameters:
                if name in self:
                    self.pop(name)

            self.save()

SETTINGS: ConfigManager = ConfigManager(PATH_SETTINGS, PATH_USER, DIR_DATA_SETTINGS)

class IPythonConfig:
    def __init__(self, manager: ConfigManager = SETTINGS):
        self.manager = manager

        self.widgets_map: dict[str, Any | None] = {}
        self.ui_elements: list[Any | None] = []

    def _repr_pretty_(self, *_) -> DisplayHandle:
        return self.display()

    def save_config(self, *_):
        self.manager.user.save({
            k: w.value for k, w in self.widgets_map.items()
        })

    def reset_config(self, *_):
        self.manager.reset(list(self.manager.keys()))

    def display(self) -> DisplayHandle:
        """Construit et affiche l'interface de configuration interactive dans un notebook IPython"""
        for parameter in self.manager.config.values():
            widget = parameter.get_widgets()
            self.widgets_map[parameter.name] = widget
            self.ui_elements.append(widget)

        save_button = widgets.Button(description='Save')
        save_button.on_click(self.save_config)

        reset_button = widgets.Button(description='Reset')
        reset_button.on_click(self.reset_config)

        self.ui_elements.append(widgets.HBox([save_button, reset_button]))

        return display(widgets.VBox(self.ui_elements))

INTERACTIVE: IPythonConfig = IPythonConfig(SETTINGS)


__all__: list[str] = [
    'Parameter',
    'ConfigManager',
    'IPythonConfig',
    'SETTINGS',
    'INTERACTIVE',
]
