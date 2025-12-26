"""
Les différentes constantes pour manipuler aisément les différents dossiers, sous-dossiers,
fichiers dans l'arborescence complète du projet.
"""

from os.path import expanduser, dirname

from pathlib import Path


HOME_DIR: Path = Path(expanduser('~'))
ROOT_DIR: Path = Path(dirname(dirname(dirname(dirname(__file__)))))

DIR_SRC: Path = ROOT_DIR / 'src'
DIR_WEBSPIRIT: Path = DIR_SRC / 'webspirit'

DIR_EXAMPLES: Path = DIR_WEBSPIRIT / 'examples'
DIR_EXAMPLES_DATA: Path = DIR_EXAMPLES / 'data'
DIR_EXAMPLES_GENERATED: Path = DIR_EXAMPLES / 'generated'
DIR_EXAMPLES_NOTEBOOKS: Path = DIR_EXAMPLES / 'notebooks'

DIR_TMP: Path = DIR_WEBSPIRIT / 'tmp'
DIR_ADDONS: Path = DIR_WEBSPIRIT / 'addons'
DIR_CONFIG: Path = DIR_WEBSPIRIT / 'config'
DIR_CLASSES: Path = DIR_WEBSPIRIT / 'classes'
DIR_RESOURCES: Path = DIR_WEBSPIRIT / 'resources'
DIR_DOWNLOADS: Path = DIR_WEBSPIRIT / 'downloads'
DIR_APPLICATION: Path = DIR_WEBSPIRIT / 'application'

DIR_CONFIG_DATA: Path = DIR_CONFIG / 'data'
DIR_CONFIG_DATA_USER: Path = DIR_CONFIG_DATA / 'user'

DIR_CLASSES_TOOLS: Path = DIR_CLASSES / 'tools'

PATH_LANGUAGES: Path = DIR_CONFIG_DATA / 'languages.csv'

PATH_MUSICS_LIST: Path = DIR_CONFIG_DATA / 'musics.csv'
PATH_TMP_MUSICS: Path = DIR_TMP / 'tmp_musics.csv'

PATH_SETTINGS: Path = DIR_CONFIG_DATA / 'settings.json'
PATH_FORMATS: Path = DIR_CONFIG_DATA / 'formats.json'

PATH_GITIGNORE: Path = ROOT_DIR / '.gitignore'


__all__: list[str] = [
    var for var in globals() if var.isupper()
]