from typing import Any, Callable, Iterable, Self, TypeAlias, Union

from ..config.logger import log, INFO, ERROR, WARNING, DEBUG

from inspect import BoundArguments, Signature, signature

from .contexterror import re as _re

from urllib.parse import urlparse

from functools import wraps

from types import UnionType

from pathlib import Path

from re import Match

import re, os


__all__: list[str] = [
    'HyperLink',
    'StrPath',
    'CheckType',
    'ValidatePathOrUrl'
]


class _PathOrURL:
    pass

class HyperLink(str, _PathOrURL):
    def __new__(cls, string: str, exist: bool = True):
        if not exist:
            log(f"Skip existing test for {string}", DEBUG)

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
        match: Match = re.search(pattern, self)

        return match.group(1) if match else ''

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
            log(f"Skip existing test for '{string}'", DEBUG)

        elif not (StrPath.is_path(string) or StrPath.is_path(string, dir=True)):
            _re(f"'{string}' must be a valid path to a file or a directory")

        strpath = super().__new__(cls, string)
        strpath.exists = exist

        return strpath

    def __str__(self) -> str:
        return os.path.relpath(super().__str__())

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}('{self.relpath()}')"

    def relpath(self) -> 'StrPath':
        return StrPath(os.path.relpath(self), exist=self.exists)

    def dirname(self) -> 'StrPath':
        return StrPath(os.path.dirname(self), exist=self.exists)

    def copy(self) -> 'StrPath':
        return StrPath(self, exist=self.exists)

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

    def __init__(self, *parameters: tuple, convert: bool = True, return_: bool = False):
        if len(parameters) == 1 and not isinstance(parameters[0], str):
            self.without_parentheses: bool = True
            self.function: Callable[..., Any] = parameters[0]

        else:
            self.without_parentheses: bool = False
            self.name_parameters = parameters

        self._return = return_
        self._convert = convert

    def __call_with_parenthesis__(self) -> Callable[..., Any]:
        @wraps(self.function)
        def wrapper(cls: Self | Any, *args: tuple, **kwargs: dict) -> Any:
            self.signature: BoundArguments = signature(self.function).bind(cls, *args, **kwargs) # type: ignore
            self.signature.apply_defaults()

            self.arguments: dict[str, object] = dict(self.signature.arguments) # type: ignore
            self.arguments.pop(CheckType.SELF, None)

            empty_call: bool = not bool(self.name_parameters)

            for parameter in self.name_parameters:
                if parameter not in self.arguments.keys():
                    _re(f"'{parameter}' parameter isn't defined in the {self.function.__name__}({', '.join(self.arguments.keys())})")

            if any(
                parameter not in self.annotations_no_return for parameter in self.arguments
            ) and empty_call:
                _re(f"You must annotate parameters of {self.function.__name__}({': <type>, '.join(self.arguments.keys())}: <type>)")

            if any(
                parameter not in self.annotations_no_return for parameter in self.name_parameters
            ) and not empty_call:
                _re(f"You must annotate '{', '.join(self.name_parameters)}' {'parameter(s)' if len(self.name_parameters) > 1 else 'parameter'} of {self.function.__name__}({': <type>, '.join(self.name_parameters)}: <type>)")

            if empty_call:
                for parameter in self.annotations_no_return:
                    self.validate_and_convert_type(parameter)

            else:
                for parameter in self.name_parameters:
                    self.validate_and_convert_type(parameter)

            _return: Any = self.function(*self.signature.args, **self.signature.kwargs)
            return self.convert('return', _return, self.annotations['return']) if self._return else _return

        return wrapper

    def __call_without_parenthesis__(self, *args: tuple, **kwargs: dict) -> Any:
        self.signature: Signature = signature(self.function)

        if str(self.signature).startswith(f'({CheckType.SELF}'):
            self.signature: BoundArguments = self.signature.bind(None, *args, **kwargs)

        else:
            self.signature: BoundArguments = self.signature.bind(*args, **kwargs)

        self.signature.apply_defaults()

        self.arguments: dict[str, object] = dict(self.signature.arguments)
        self.arguments.pop(CheckType.SELF, None)

        if any(
            parameter not in self.annotations_no_return for parameter in self.arguments
        ):
            _re(f"You must annotate parameters of {self.function.__name__}({': <type>, '.join(self.arguments.keys())}: <type>)")

        for parameter in self.annotations_no_return:
            self.validate_and_convert_type(parameter)

        _return: Any = self.function(*self.signature.args, **self.signature.kwargs)

        return self.convert('return', _return, self.annotations['return']) if self._return else _return

    def __call__(self, *args: tuple, **kwargs: dict) -> Callable[..., Any] | Any:
        if not self.without_parentheses:
            self.function: Callable[..., Any] = args[0]

        self.annotations: dict[str, Any] = self.function.__annotations__
        self.annotations_no_return: dict[str, Any] = self.annotations.copy()
        self.annotations_no_return.pop('return', None)

        if self._return and self.annotations.get('return') is None:
            _re(f"You must annotate the return of {self.function.__name__}(...) -> <type>")

        if self.without_parentheses:
            return self.__call_without_parenthesis__(*args, **kwargs)

        else:
            return self.__call_with_parenthesis__()

    def validate_and_convert_type(self, parameter: str):
        given: object = self.arguments[parameter]
        asked: type = self.annotations[parameter]

        if type(given) != asked:
            if self._convert:
                self.signature.arguments[parameter] = self.convert(parameter, given, asked)

            else:
                _re(f"The parameter {parameter} of {self.function.__name__} with a '{given}' value must be of type {asked} but you have given '{given}' with a type {type(given)}")

    def convert(self, parameter: str, value: object, annotation: type | UnionType) -> object | None:
        flag: bool = False

        if isinstance(annotation, UnionType) and 'None' in str(annotation):
            annotation = eval(str(annotation)[:-7])
            flag = True

        try:
            if type(value) is annotation:
                log(f"Skip converting for the parameter {parameter} of {self.function.__name__} with a '{value}' value and a type {type(value)} because is already of type {annotation}", DEBUG)

            else:
                converted = annotation(value)
                log(f"Change the parameter {parameter} of {self.function.__name__} with a '{value}' value and a type {type(value)} to type {annotation}", DEBUG)

            return converted

        except Exception as exception:
            if flag:
                return None

            _re(f"The parameter {parameter} of {self.function.__name__} with a '{value}' value can't be converted to {annotation}", ValueError, exception)

class ValidatePathOrUrl(CheckType):
    def __init__(self, *parameters: tuple, convert: bool = True, exist: bool = False):
        self.exist = exist
        super().__init__(*parameters, convert=convert)

    def convert(self, parameter: str, value: str | Path | PathOrURL | None, annotation: type[PathOrURL]) -> PathOrURL:
        if isinstance(value, annotation) or value is None:
            return value

        returned: PathOrURL | None = None

        if HyperLink.is_url(str(value)) and issubclass(HyperLink, annotation):
            returned = HyperLink(value)

        if StrPath.is_path(value, dir=False, suffix=['csv', 'txt']) and issubclass(StrPath, annotation):
            returned = StrPath(value)

        if self.exist and issubclass(StrPath, annotation):
            with Path(value).open('w', encoding='utf-8'): pass
            returned = StrPath(value)
            log(f"Create {Path(value)}, because doesn't exist", DEBUG)

        if returned is not None:
            log(f"Change '{value}' of type {type(value)} to type {type(returned)}", DEBUG)
            return returned

        _re(f"'{parameter}' object with '{value}' must be a valid url or a path to a csv or a txt file", ValueError)
