"""
Les différentes constantes pour manipuler aisément les différents dossiers, sous-dossiers,
fichiers dans l'arborescence complète du projet.
"""

from os.path import expanduser, dirname

from pathlib import Path


# Toutes les constantes pour les chemins de l'arborescence
HOME_DIR: Path = Path(expanduser('~'))
ROOT_DIR: Path = Path(dirname(dirname(dirname(dirname(__file__)))))

DIR_SRC: Path = ROOT_DIR / 'src'
DIR_WEBSPIRIT: Path = DIR_SRC / 'webspirit'

DIR_EXAMPLES: Path = ROOT_DIR / 'examples'
DIR_EXAMPLES_DATA: Path = DIR_EXAMPLES / 'data'
DIR_EXAMPLES_GENERATED: Path = DIR_EXAMPLES / 'generated'
DIR_EXAMPLES_NOTEBOOKS: Path = DIR_EXAMPLES / 'notebooks'

DIR_TMP: Path = DIR_WEBSPIRIT / 'tmp'
DIR_DATA: Path = DIR_WEBSPIRIT / 'data'
DIR_ADDONS: Path = DIR_WEBSPIRIT / 'addons'
DIR_CONFIG: Path = DIR_WEBSPIRIT / 'config'
DIR_CLASSES: Path = DIR_WEBSPIRIT / 'classes'
DIR_RESOURCES: Path = DIR_WEBSPIRIT / 'resources'
DIR_DOWNLOADS: Path = DIR_WEBSPIRIT / 'downloads'
DIR_APPLICATION: Path = DIR_WEBSPIRIT / 'application'

DIR_DATA_USER: Path = DIR_DATA / 'user'
DIR_DATA_SETTINGS: Path = DIR_DATA / 'settings'

PATH_SETTINGS: Path = DIR_DATA_SETTINGS / 'settings.json'
PATH_USER: Path = DIR_DATA_SETTINGS / 'user.json'

PATH_FORMATS: Path = DIR_DATA / 'formats.json'

PATH_LANGUAGES: Path = DIR_DATA / 'languages.csv'
PATH_MUSICS_LIST: Path = DIR_DATA / 'musics.csv'
PATH_TMP_MUSICS: Path = DIR_TMP / 'tmp_musics.csv'

PATH_FFMPEG: Path = DIR_RESOURCES / 'FFmpeg/bin/ffmpeg.exe'

PATH_GITIGNORE: Path = ROOT_DIR / '.gitignore'

# Les différents type de média à télécharger
AUDIO: str = 'audio'
VIDEO: str = 'video'
SUBTITLES: str = 'subtitles'
AUDIO_VIDEO: str = f'{AUDIO}_{VIDEO}'


__all__: list[str] = [
    var for var in globals() if var.isupper()
]