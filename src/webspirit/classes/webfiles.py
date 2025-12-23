from webspirit.config.logger import DEBUG, INFO, debug, info, error, warning, critical

from webspirit.classes.tools.contexterror import re as _re

from typing import TypeAlias, Union

from urllib.parse import urlparse

from pathlib import Path

import re, os


__all__: list[str] = [
    'HyperLink',
    'StrPath',
    'SuffixPath',
    'JsonPath',
    'CsvPath',
]


class _PathOrURL:
    pass

class HyperLink(str, _PathOrURL):
    def __new__(cls, string: str, exist: bool = True):
        if not exist:
            debug(f"Skip existing test for {string}")

        elif not cls.is_url(string):
            _re(f"'{string}' must be a valid hyperlink")

        return super().__new__(cls, string)

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}('{self}')"

    def copy(self) -> 'HyperLink':
        return HyperLink(self)

    @property
    def id(self) -> str:
        pattern: str = r'(?:https?://(?:www\.)?youtube\.com/watch\?v=|https?://(?:www\.)?youtu\.be/)([a-zA-Z0-9_-]{11})'
        match: re.Match = re.search(pattern, self)

        return match[1] if match else ''

    @id.setter
    def id(self):
        _re("You can't set id attribute")

    @id.deleter
    def id(self):
        _re("You can't delete id attribute")

    @staticmethod
    def is_url(url: 'str | HyperLink') -> bool:
        pattern = re.compile(r'^(https?|ftp)://[^\s/$.?#].[^\s]*$', re.IGNORECASE)
        result = urlparse(url)

        return bool(re.match(pattern, url)) and all([result.scheme, result.netloc])

class StrPath(Path, _PathOrURL):
    def __new__(cls, string: str | Path, exist: bool = True):
        if not exist:
            debug(f"Skip existing test for '{string}'")

        elif not (StrPath.is_path(string) or StrPath.is_path(string, dir=True)):
            _re(f"'{string}' must be a valid path to a file or a directory")

        return super().__new__(cls, string, exist)

    def __init__(self, string: str | Path, exist: bool = True):
        super().__init__(string)

        self.exist = exist

    def __str__(self) -> str:
        return super().__str__()

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}('{self}')"

    def relpath(self) -> 'StrPath':
        return StrPath(os.path.relpath(self), exist=self.exist)

    def dirname(self) -> 'StrPath':
        return StrPath(os.path.dirname(self), exist=self.exist)

    def copy(self) -> 'StrPath':
        return StrPath(self, exist=self.exist)

    @staticmethod
    def is_path(string: 'str | Path | StrPath', dir: bool = False, ext: str | list[str] | None = None) -> bool:
        is_file: bool = os.path.isfile(string) and os.path.exists(string)

        if dir:
            return os.path.isdir(string) and os.path.exists(string)

        elif ext:
            ext: list[str] = [ext] if isinstance(ext, str) else ext

            return is_file and StrPath(string).suffix in ext

        return is_file

class SuffixPath(StrPath):
    def __new__(cls, string: str | Path, _=None, exist: bool = True):
        return super().__new__(cls, string, exist)

    def __init__(self, string: str | Path, ext: str | list[str], exist: bool = True):
        super().__init__(string, exist)

        self.ext = SuffixPath.check_ext(ext)

        if self.suffix[1:] not in self.ext:
            _re(f"{string} isn't a path of type {', '.join(map(lambda name: f"'{name}'", ext))}")

    @staticmethod
    def check_ext(ext: str | list[str]) -> list[str]:
        ext = [ext.removeprefix('.')] if isinstance(ext, str) else [name.removeprefix('.') for name in ext]

        if not all(name.isalpha() for name in ext):
            _re(f"All extensions that you provided : {', '.join(map(lambda name: f"'{name}'", ext))} must be like this : '.png', '.csv', '.json' (but without the dot if you want)")

        return ext

    def relpath(self) -> 'SuffixPath':
        return SuffixPath(os.path.relpath(self), ext=self.ext, exist=self.exist)

    def dirname(self) -> 'SuffixPath':
        return SuffixPath(os.path.dirname(self), ext=self.ext, exist=self.exist)

    def copy(self) -> 'SuffixPath':
        return SuffixPath(self, ext=self.ext, exist=self.exist)

class JsonPath(SuffixPath):
    SUFFIX: list[str] = ['.json']

    def __init__(self, string: str | Path, exist: bool = True):
        super().__init__(string, JsonPath.SUFFIX, exist)

class CsvPath(SuffixPath):
    SUFFIX: list[str] = ['.csv']

    def __init__(self, string: str | Path, exist: bool = True):
        super().__init__(string, CsvPath.SUFFIX, exist)


PathOrURL: TypeAlias = Union[StrPath, HyperLink]
