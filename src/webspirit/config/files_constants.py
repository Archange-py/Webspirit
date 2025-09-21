"""
Constants of directory, names and absolute path to manipulate files.
"""


from os.path import dirname

from pathlib import Path


ROOT_DIR: Path = Path(dirname(dirname(__file__)))

DIR_TMP: Path = ROOT_DIR / 'tmp'
DIR_LOGS: Path = ROOT_DIR / 'logs'
DIR_DATA: Path = ROOT_DIR / 'data'
DIR_CONFIG: Path = ROOT_DIR / 'config'
DIR_DOWNLOADS: Path = ROOT_DIR / 'downloads'

DIR_MUSIC: Path = DIR_DOWNLOADS / 'music'
DIR_PICTURE: Path = DIR_DOWNLOADS / 'picture'

LOG_NAME: str = 'stdout.log'
PATH_LOGS: Path = DIR_LOGS / LOG_NAME

LANGUAGES_NAME: str = "languages.csv"
PATH_LANGUAGES: Path = DIR_DATA / LANGUAGES_NAME

MUSICS_LIST_NAME: str = 'musics.csv'
PATH_MUSICS_LIST: Path = DIR_DATA / MUSICS_LIST_NAME

PATH_TMP_MUSICS: Path = DIR_TMP / 'tmp_musics.csv'

PATH_SETTINGS: Path = DIR_DATA / 'settings.json'
PATH_FORMATS: Path = DIR_DATA / 'formats.json'

FFMPEG_LOCATION: str = r"C:\Users\Blondel\Documents\Programmation\Python\Projects\Webspirit\src\data\FFmpeg\bin\ffmpeg.exe"#str(Path(r'.\src\data\FFmpeg\bin\ffmpeg.exe'))


__all__: list[str] = [
    var for var in globals() if var.isupper()
]