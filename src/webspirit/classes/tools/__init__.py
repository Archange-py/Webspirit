"""
Répertoire contenant les différents modules qui gerent les classes et objets utilisé dans cette library.
"""

from webspirit.config.logger import DEBUG, INFO, debug, info, error, warning, critical

from webspirit.config.constants import DIR_WEBSPIRIT

from webspirit.classes.tools.contexterror import ecm

from types import ModuleType

from pathlib import Path

from typing import Any

import contextlib

import os, sys


sequence = lambda _list: ', '.join(_list) if _list else '0'
PATH_INIT: Path = DIR_WEBSPIRIT / __name__.removeprefix('webspirit.').replace('.', '/')

MODULES_NAMES: list[str] = [
    name.removesuffix('.py')
    for name in os.listdir(PATH_INIT)
    if '__init__.py' not in name and name.endswith('.py')
]

DIR_NAMES: list[str] = [
    name for name in os.listdir(PATH_INIT)
    if '__pycache__' not in name and os.path.isdir(str(PATH_INIT / name))
]

debug(f"Init dir '{os.path.relpath(PATH_INIT)}'")

if not MODULES_NAMES and not DIR_NAMES:
    debug(f"No module or directory found in '{os.path.relpath(PATH_INIT)}'")
    sys.exit()

debug(f"Found {sequence(MODULES_NAMES)} modules and {sequence(DIR_NAMES)} directory in '{os.path.relpath(PATH_INIT)}'")

MODULES: list[ModuleType] = [
    __import__(f'{__name__}.{module}', fromlist=[module])
    for module in MODULES_NAMES
]

DIRECTORIES: list[ModuleType] = [
    __import__(f'{__name__}.{dir}', fromlist=[dir])
    for dir in DIR_NAMES
]


_import_modules: str = ''
__all__: list[str] = []

for module in MODULES:
    if getattr(module, '__all__', None) is None:
        continue

    __all__.extend(module.__all__)
    _import_modules += f"from {module.__name__} import {sequence(module.__all__)};"

with ecm(f"Failed to load one of these modules : {sequence(MODULES_NAMES)}"):
    exec(_import_modules)

for dir in DIRECTORIES:
    if getattr(dir, '__all__', None) is not None:
        __all__.extend(dir.__all__)


def __getattr__(name: str) -> Any:
    debug(f"Get attribute {name} in {os.path.relpath(PATH_INIT)}")

    for module in MODULES:
        with contextlib.suppress(Exception):
            return getattr(module, name)
