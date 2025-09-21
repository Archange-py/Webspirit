from .checktype import ValidatePathOrUrl, StrPath, HyperLink

from ..config.logger import log, INFO, ERROR, WARNING, DEBUG
from ..config.constants import DIR_TMP, PATH_TMP_MUSICS

from pandas.errors import EmptyDataError

from .contexterror import ecm

from pandas import DataFrame

from typing import Iterable

from os.path import dirname

from pathlib import Path

from os import remove

import pandas as pd


class Music:
    @ValidatePathOrUrl()
    def __init__(
            self,
            youtube_url: HyperLink,
            path: StrPath | None = None,
            extension: str | None = None,
            type: str | None = None,
            spotify_url: HyperLink | None = None,
            picture: StrPath | None = None,
            meta: StrPath | None = None
        ):
        self.youtube_url = youtube_url
        self.path = path
        self.extension = extension
        self.type = type
        self.spotify_url = spotify_url
        self.picture = picture
        self.meta = meta
        
    def __str__(self) -> str:
        return self.youtube_url

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({', '.join(f"{k.removeprefix('_')}={v!r}" for k, v in vars(self).items())})"

    def __iter__(self):
        return iter([
            self.youtube_url, self.path, self.extension, self.type, self.spotify_url, self.picture, self.meta
        ])

    def __eq__(self, other: 'Music') -> bool:
        return self.youtube_url == other.youtube_url and self.extension == other.extension and self.type == other.type and self.meta == other.meta

    def to_line(self) -> str: # TODO: voir si je l'enlève
        return ", ".join(map(str, iter(self)))


class CSVManager:
    HEADERS: list[str] = ['YouTubeUrl', 'Path', 'Extension', 'Type', 'SpotifyUrl', 'Picture', 'Meta']

    @ValidatePathOrUrl('path', exist=True)
    def __init__(self, path: StrPath = PATH_TMP_MUSICS, headers: list[str] = HEADERS):
        self.path = path
        self.headers = headers

        try:
            self.df: DataFrame = pd.read_csv(
                self.path,
                sep=',',
                encoding='utf-8',
                names=self.headers,
            )

        except EmptyDataError:
            self.df: DataFrame = DataFrame(columns=self.headers)

        log(f"Load '{self.path.name}' in '{self.path.dirname()}'", INFO)

        self.save()

    def __str__(self) -> str:
        return self.path.name

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(path={self.path.relpath()}, length={self.length}, width={self.width})"

    def _repr_html_(self) -> str:
        return self.df._repr_html_()

    @property
    def length(self) -> int:
        return self.df.shape[1]

    @length.setter
    def length(self, _):
        ecm(f"You can't set a new length of a {self.__class__.__class__} instance")

    @length.deleter
    def length(self, _):
        ecm(f"You can't delete a length of a {self.__class__.__class__} instance")

    @property
    def width(self) -> int:
        return self.df.shape[0]

    @width.setter
    def width(self, _):
        ecm(f"You can't set a new width of a {self.__class__.__class__} instance")

    @width.deleter
    def width(self, _):
        ecm(f"You can't delete a width of a {self.__class__.__class__} instance")

    @property
    def size(self) -> int:
        return (self.length, self.width)

    @size.setter
    def size(self, _):
        ecm(f"You can't set the size attribute")

    @size.deleter
    def size(self, _):
        ecm(f"You can't delete the size attribute")

    @ValidatePathOrUrl('resource')
    def append(self, resource: StrPath): # TODO  | Iterable[PathOrURL] <--- Parcourir la liste et associer chacun à son type
        if not issubclass(type(resource), Iterable):
            resource: Iterable[Path] = [resource]

        for new_path in resource:
            new_file: DataFrame = pd.read_csv(
                sep=',',
                encoding='utf-8',
                names=self.headers,
                filepath_or_buffer=new_path,
            )

            self.df = pd.concat([self.df, new_file], ignore_index=True)

            log(f"Load '{new_path}' in '{new_path.dirname()}'", INFO)

        self.save()

    @ValidatePathOrUrl('output_path')
    def save(self, output_path: StrPath | None = None):
        if output_path is None:
            output_path = self.path

        self.df.to_csv(output_path, sep=',', encoding='utf-8', index=False)

        log(f"Save the DataFrame in '{output_path.relpath()}'", INFO)

    def delete(self):
        remove(self.path)