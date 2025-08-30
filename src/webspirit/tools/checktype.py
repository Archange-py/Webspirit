from typing import Any, Callable, Iterable, Self, TypeAlias, Union

from ..config.logger import log, INFO, ERROR, WARNING, DEBUG

from inspect import BoundArguments, signature

from .contexterror import re as _re

from urllib.parse import urlparse

from functools import wraps

from types import UnionType

from pathlib import Path

import re, os


class _PathOrURL:
    pass

class HyperLink(str, _PathOrURL):
    def __new__(cls, string: str):
        if not cls.is_url(string):
            _re(f"'{string}' must be a valid hyperlink")

        return super().__new__(cls, string)

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}('{self}')"

    def copy(self) -> 'HyperLink':
        return HyperLink(self)

    @property
    def id(self):
        return self[-11:]

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
    def __new__(cls, string: str | Path):
        if not (StrPath.is_path(string) or StrPath.is_path(string, dir=True)):
            _re(f"'{string}' must be a valid path to a file or a directory")

        return super().__new__(cls, string)

    def __str__(self) -> str:
        return os.path.relpath(super().__str__())

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}('{self.relpath()}')"

    def relpath(self) -> 'StrPath':
        return StrPath(os.path.relpath(self))

    def dirname(self) -> 'StrPath':
        return StrPath(os.path.dirname(self))

    def copy(self) -> 'StrPath':
        return StrPath(self)

    @staticmethod
    def is_path(string: 'str | Path | StrPath', dir: bool = False, suffix: str | Iterable[str] | None = None) -> bool:
        is_file: bool = os.path.isfile(string) and os.path.exists(string)

        if dir:
            return os.path.isdir(string) and os.path.exists(string)

        elif suffix:
            if isinstance(suffix, str):
                suffix = [suffix]

            return is_file and Path(string).suffix[1:] in suffix

        return is_file

PathOrURL: TypeAlias = Union[StrPath, HyperLink]

class CheckType:
    SELF: str = 'self'

    def __init__(self, *parameters: tuple, convert: bool = True):
        self.parameters = parameters
        self._convert = convert

    def __call__(self, function: Callable[..., Any]) -> Callable[..., Any]:
        self.function = function
        self.annotations = self.function.__annotations__
        self.signature = signature(self.function)

        if not self.annotations:
            _re("You must annotate the definition of your function")

        @wraps(function)
        def wrapper(cls: Self, *args: tuple, **kwargs: dict) -> Any:
            bound = self.signature.bind(cls, *args, **kwargs)
            bound.apply_defaults()
            arguments = {param:obj for param, obj in bound.arguments.items() if param != CheckType.SELF}

            if not bool(self.parameters):
                for (parameter, asked), given in zip(self.annotations.items(), arguments.values()):
                    self.validate_and_convert_type(given, asked, parameter, bound)

            else:
                for parameter in self.parameters:
                    if parameter in arguments:
                        asked, given = self.annotations[parameter], arguments[parameter]
                        self.validate_and_convert_type(given, asked, parameter, bound)

            return self.function(*bound.args, **bound.kwargs)

        return wrapper

    def validate_and_convert_type(self, given: object, asked: type, parameter: str, bound: BoundArguments):
        if type(given) != asked and self._convert:
            bound.arguments[parameter] = self.convert(parameter, bound.arguments[parameter], self.annotations[parameter])

        elif type(given) != asked:
            _re(f"For the '{parameter}' parameter, it must be of type {asked}, but you have given '{given}' with a type of {type(given)}")

    def convert(self, parameter: str, value: object, annotation: type | UnionType) -> object | None:
        flag: bool = False

        if isinstance(annotation, UnionType) and 'None' in str(annotation):
            annotation = eval(str(annotation)[:-7])
            flag = True

        try:
            converted = annotation(value)
            log(f"Change '{value}' of type {type(value)} to type {annotation}", DEBUG)

            return converted

        except Exception as exception:
            if flag:
                return None

            _re(f"'{parameter}' object with '{value}' value, can't be converted to {annotation}", ValueError)

class ValidatePathOrUrl(CheckType):
    def __init__(self, *parameters: tuple, convert: bool = True, exist_ok: bool = False):
        self.exist_ok = exist_ok
        super().__init__(*parameters, convert=convert)

    def convert(self, parameter: str, value: str | Path | PathOrURL | None, annotation: type[PathOrURL]) -> PathOrURL:
        if isinstance(value, annotation) or value is None:
            return value

        returned: PathOrURL | None = None # type: ignore

        if HyperLink.is_url(str(value)) and issubclass(HyperLink, annotation):
            returned = HyperLink(value)

        if StrPath.is_path(value, dir=False, suffix=['csv', 'txt']) and issubclass(StrPath, annotation):
            returned = StrPath(value)

        if self.exist_ok and issubclass(StrPath, annotation):
            with Path(value).open('w', encoding='utf-8'): pass
            returned = StrPath(value)
            log(f"Create {Path(value)}, because doesn't exist", DEBUG)

        if not returned is None:
            log(f"Change '{value}' of type {type(value)} to type {type(returned)}", DEBUG)
            return returned

        _re(f"'{parameter}' object with '{value}' must be a valid url or a path to a csv or a txt file", ValueError)
