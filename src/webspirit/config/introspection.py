"""
Un module qui fournit des fonctions utiles pour manipuler des objets, et avoir des aides
pour les Jupiter Notebooks, ou encore les fichiers Readme pour la présentation du dépôt.
"""

from webspirit.config.constants import DIR_WEBSPIRIT, PATH_GITIGNORE

from webspirit.classes.webfiles import HyperLink, StrPath

from webspirit.classes.tools.contexterror import ecm, re

from webspirit.classes.tools.checktype import CheckType

from importlib import import_module

from typing import Any

import json, os


__all__ : list[str] = [
    'show',
    'links_from_cell',
    'tree_directory'
]


def show(obj: Any):
    print('str  :', obj, '\nrepr :', repr(obj))

@CheckType('notebook')
def links_from_cell(notebook: StrPath, index: int = 0, type: type = HyperLink) -> list[type]:
    with notebook.open('r', encoding='utf-8') as f:
        notebook = json.load(f)

    cell: dict = notebook['cells'][index]

    return [
        type(link.removesuffix('\n').removesuffix('  ')) for link in cell['source']
    ]   if cell['cell_type'] in ('markdown', 'raw') else ['']

@CheckType('root', 'ignore', 'indent', 'branch', 'close', 'empty')
def tree_directory(
        root: StrPath = DIR_WEBSPIRIT,
        ignore: StrPath = PATH_GITIGNORE,
        show_var: bool = False,
        show_doc: bool = False,
        show_files: bool = True,
        indent: str = '│   ',
        branch: str = '├── ',
         close: str = '└── ',
         empty: str = '    ',
    ) -> str:
    """Construit une représentation textuelle propre et esthétique d'un répertoire

    Args:
        root (StrPath, optional): Chemin du dossier racine à explorer. Defaults to DIR_WEBSPIRIT.
        ignore (StrPath, optional): Un fichier .gitignore qui permet de restreindre l'affichage de manière dynamique. Defaults to PATH_GITIGNORE.
        show_var (bool, optional): Permet d'afficher les variable contenue dans '__all__' de chaque module. Defaults to False.
        show_doc (bool, optional): Permet d'afficher la documentation de chaque module. Defaults to False.
        show_files (bool, optional): Permet d'afficher les fichiers contenu dans les dossiers. Defaults to True.
        indent (str, optional): La branche d'indentation normale. Defaults to '│   '.
        branch (str, optional): La branche d'intersection. Defaults to '├── '.
        close (str, optional): La branche finale. Defaults to '└── '.
        empty (str, optional): Un espace vide. Defaults to '    '.

    Raises:
        TypeError: Lève une erreur si le chemin 'root' ne mène pas à un dossier

    Returns:
        str: Arborescence formatée
    """
    if not StrPath.is_path(root, dir=True):
        re(f"The path {root} isn't a valid directory")

    @CheckType('directory')
    def get_entries(directory: StrPath) -> list[StrPath] | None:
        if not StrPath.is_path(directory, dir=True):
            re(f"The path {directory} isn't a valid directory")
 
        entries: list[StrPath] = sorted(
            [
                StrPath(path) for path in directory.iterdir()
                if show_files or (not show_files and not StrPath.is_path(path))
            ],
            key=lambda path: (StrPath.is_path(path), path.name.lower())
        )

        return entries if len(entries) else None

    @CheckType('path')
    def get_library(path: StrPath) -> str:
        if not (path.is_dir() or StrPath.is_path(path, ext='.py')):
            re(f"The path {path} isn't valid")

        return path.as_posix()[len(root.as_posix())-len(root.name):].replace('/', '.').removesuffix('.py')

    @CheckType('path')
    def get_vars(path: StrPath) -> list[str] | None:
        library: str = get_library(path)
        vars: None = None

        with ecm(f"EX_TYPE: EX_VALUE - An error was occurred while tried to get the '__all__' variable of the '{library}' library"):
            vars: list[str] | None = getattr(import_module(library), '__all__', None)

        return vars

    @CheckType('path')
    def get_doc(path: StrPath) -> str | None:
        library: str = get_library(path)
        doc: None = None

        with ecm(f"EX_TYPE: EX_VALUE - An error was occurred while tried to get the '__doc__' variable of the '{library}' library"):
            doc: str | None = getattr(import_module(library), '__doc__', None)

        return doc

    def _format_dir(entries: list[StrPath], prefix: str = '') -> str:
        lines: list[str] = []

        for i, path in enumerate(entries):
            end_prefix: str = close if i == len(entries) - 1 else branch
            lines.append(f"{prefix}{end_prefix}{path.name}")

            final_prefix: str = f"{prefix}{empty if i == len(entries) - 1 else indent}"

            if show_var and not path.name.startswith('__') and (path.is_dir() or StrPath.is_path(path, ext='.py')) and (vars := get_vars(path)) is not None:
                vars: list[str] = sorted(vars)
                N: int = 8

                for i, var in enumerate(vars):
                    if i % 8 == N - 1:
                        vars[i] = f"{var}\n{final_prefix}"

                lines.append(f'{final_prefix}({len(vars)}) - {', '.join(vars).replace(f'\n{final_prefix}, ', f',\n{final_prefix}')}')

            if show_doc and not path.name.startswith('__') and (path.is_dir() or StrPath.is_path(path, ext='.py')) and (doc := get_doc(path)) is not None:
                lines.append(f'{final_prefix}{doc.removeprefix('\n').removesuffix('\n').replace('\n', f"\n{final_prefix}")}')

            if path.is_dir() and (next_entries := get_entries(path)) is not None:
                sub: str = _format_dir(next_entries, f"{final_prefix}")
                lines.append(sub if sub.strip() else prefix)

        return '\n'.join(lines)

    if (init_entries := get_entries(root)) is not None:
        return f"{root.name}\n{_format_dir(init_entries)}"

    else:
        return root.name
