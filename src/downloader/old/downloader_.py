
from config.constants import (
    INFO, ERROR, WARNING, DEBUG,
    FFMPEG_LOCATION, LOGGER, log,
    AUDIO, VIDEO, AUDIO_VIDEO, SUBTITLES,
    DIR_DATA, DIR_MUSIC, PATH_MUSICS_LIST,
    PATH_SETTINGS, PATH_FORMATS, PATH_LANGUAGES
)

from tools import (
    JSON, CSV, BaseCSVString, StrPath, HyperLink, NameDescriptor, CSVString, ReprMixin, Music,
)

from typing import Optional, Any

from pathlib import Path

import yt_dlp

import os


LANGUAGES_HEADERS: list[NameDescriptor] = [NameDescriptor(name) for name in ['Languages', 'Keys']]
LANGUAGES: CSV = CSV(PATH_LANGUAGES, LANGUAGES_HEADERS, data_type=BaseCSVString)

SETTINGS: dict[str, str | bool] = JSON.load(PATH_SETTINGS)
CONFIGURATION: dict[str, dict[str, str | list[dict[str, str]]]] = JSON.load(PATH_FORMATS)

DEFAULT_TYPE: str = SETTINGS['DownloadType']
DEFAULT_FORMAT: str = SETTINGS['DownloadFormat']
DEFAULT_LANGUAGE: str = 'fr'


class Downloader(ReprMixin):
    TMP_MUSICS_PATH: Path = DIR_DATA / 'tmp_musics.csv'
    MUSICS_HEADERS: list[NameDescriptor] = [NameDescriptor(name) for name in ['YouTube_url', 'Spotify_url', 'Path', 'Format', 'Type']]
    _OUTPUT_PATH: Path = ''
    def __init__(self,
            source: HyperLink | StrPath | list[HyperLink | StrPath] = PATH_MUSICS_LIST,
            output_dir: StrPath = DIR_MUSIC,
            type: str = DEFAULT_TYPE,
            format: str = DEFAULT_FORMAT,
            language: list[str] | str = DEFAULT_LANGUAGE
        ):

        self.type = type
        self.format = format
        self.language = language
        self.tmp_file: Path = Downloader.TMP_MUSICS_PATH
        self.source: list[HyperLink | StrPath] = [source] if isinstance(source, (str, StrPath, HyperLink)) else source

        os.makedirs(output_dir, exist_ok=True)
        self.output_dir = StrPath(output_dir)

        try:
            self.tmp_file.open('x').close()

        except FileExistsError as error:
            log(f"{os.path.relpath(self.tmp_file)} already exist")

        self.csv_file = CSV(self.tmp_file, Downloader.MUSICS_HEADERS)

        return
        self.list_csv_path: set[Path] = set()
        for _url in url:
            if isinstance(_url, (list, tuple, set)):
                url.extend(_url)
                continue

            if HyperLink.is_url(_url):
                self.csv_file.table.append(list(Music(_url)))
                self.csv_file.set_dict_from_table()
                self.list_csv_path.add(Downloader.TMP_MUSICS_PATH)

                log(f"Successful append {_url} to the default csv file", INFO)

            elif StrPath.is_path(_url, suffix=('csv', 'txt')):
                path: Path = Path(_url)

                if path.suffix[1:] == 'txt':
                    original_path = path.name
                    path = path.with_suffix('.csv')
                    log(f"Change the extension of {original_path} from '.txt' to '.csv'", INFO)

                ext_csv: CSV = CSV(path, MUSICS_HEADERS)
                table: list[list[Optional[CSVString]]] = ext_csv.table[1:] if CSV.is_header(ext_csv.table[0]) else ext_csv.table

                self.csv_file.table.extend(table)
                self.list_csv_path.add(path)

                log(f"Successful append {os.path.relpath(path)} contents to the default csv file", INFO)

            else:
                message: str = f"{_url} isn't an HyperLink or a StrPath"
                log(message, ERROR)
                raise TypeError(message)

        self.csv_file.set_dict_from_table()
        self.csv_file.save()

    def format_source(self) -> list[Path]:
        pass

    def get_musics(self) -> list[Music]:
        return [
            Music(*args) for args in zip(*self.csv_file.dict.values())
        ]

    @staticmethod
    def postprocess_hook(path: str):
        global _OUTPUT_PATH
        _OUTPUT_PATH = Path(path)

    def get_options(self) -> dict[str, Any]:
        options = {
            'logger': LOGGER,
            'noplaylist': True,
            'ffmpeg_location': FFMPEG_LOCATION,
            'post_hooks': [Downloader.postprocess_hook],
            'format': CONFIGURATION[self.type][self.format].get("FORMAT", ''),
            'outtmpl': os.path.join(self.output_dir, "%(title)s.%(ext)s"),
            'postprocessors': CONFIGURATION[self.type][self.format].get("POSTPROCESSORS", [])
        }

        if self.type == SUBTITLES:
            #options["writeautomaticsub"] = CONFIGURATION[type][format].get("WRITEAUTO", True)
            options["skip_download"] = True
            options["subtitlesformat"] = "vtt"#CONFIGURATION[self.type][self.format]["SUBTITLESFORMAT"]
            options["writesubtitles"] = CONFIGURATION[self.type][self.format]["WRITESUBTITLES"]
            options['subtitleslangs'] = ['en']#[self.language]

        return options

    def download(self, clear: bool = False):
        os.chdir(self.output_dir)

        musics: list[Music] = self.get_musics()
        print(len(musics))
        ydl_opts: dict[str, Any] = self.get_options()

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                for i, music in enumerate(musics):
                    if music.path and music.path.suffix[1:] == self.format and music.type == self.type:
                        log(f"Skip download for '{music.youtube_url}' because already download for '{self.type}' in '{self.format}'", INFO)
                        continue

                    try:
                        info_dict = ydl.extract_info(music.youtube_url, download=True)

                    except Exception as e:
                        message: str = f"URL {music.youtube_url} download failed: {e}"
                        log(message, ERROR)
                        raise TypeError(message) from e

                    if isinstance(info_dict, dict):
                        print(type(_OUTPUT_PATH), _OUTPUT_PATH, music, i)
                        music.path = _OUTPUT_PATH.replace(Path(str(_OUTPUT_PATH.absolute()).replace(' ', '_')))
                        log(f"Download {music.youtube_url} an save it in {os.path.relpath(music.path)}", INFO)

                    else:
                        message: str = 'Failed to use the result of the extract_info method as a dict.'
                        log(message, ERROR)
                        raise TypeError(message)

                    music.format, music.type = self.format, self.type
                    self.csv_file.table[i + 1] = list(music)

        except Exception as exception:
            log(exception, ERROR)
            raise exception

        finally:
            self.csv_file.save()
 
            if clear:
                self.clear()

        return self

    def playlist(self, name: str):
        _name: str = f'{name}.m3u8'
        destination: Path = Path(self.output_dir) / _name
        musics: list[str] = [str(music.path.absolute()) + '\n' for music in self.get_musics() if music.path != None]

        with destination.open('w', encoding='utf-8') as file:
            log(f"Created {_name} in '{self.output_dir}'", INFO)

            file.write(f"#EXTM3U\n#{_name}\n")
            file.writelines(musics)

        log(f"Successful filled {_name} with {len(musics)} musics in '{self.csv_file.path}'", INFO)

    def clear(self):
        try:
            os.remove(self.csv_file.path)

        except Exception as exception:
            log(f"Can't delete the path of the temporary csv file {os.path.relpath(self.csv_file.path)}", ERROR)
            raise exception


if __name__ == '__main__':
    args: list[str] = ['subtitles', 'vtt', 'fr']
    args: list[str] = ['audio', 'm4a']
    playlist = Downloader(r"src\data\musics.csv", DIR_MUSIC, *args)
    print(playlist.csv_file)

    #playlist.download()#.playlist("gorillaz")
    #playlist.clear()
