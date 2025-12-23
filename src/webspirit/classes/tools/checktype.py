from webspirit.config.logger import DEBUG, INFO, debug, info, error, warning, critical

from functools import partial, update_wrapper, wraps

from inspect import BoundArguments, signature

from typing import Any, Callable, Self

from .contexterror import ecm, re

from types import UnionType

from pathlib import Path


__all__: list[str] = [
    'CheckType',
    # 'ValidatePathOrUrl',
]


class CheckType:
    SELF: str = 'self'
    RETURN: str = 'return'

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
            self.arguments_no_self: dict[str, object] = self.arguments.copy() # type: ignore
            self.arguments_no_self.pop(CheckType.SELF, None)

            empty_call: bool = not bool(self.name_parameters)

            for parameter in self.name_parameters:
                if parameter not in self.arguments_no_self.keys():
                    re(f"'{parameter}' parameter isn't defined in the {self.function.__name__}({', '.join(self.arguments.keys())})")

            if any(
                parameter not in self.annotations_no_return for parameter in self.arguments_no_self
            ) and empty_call:
                re(f"You must annotate parameters of {self.function.__name__}({': <type>, '.join(self.arguments.keys())}: <type>)")

            if any(
                parameter not in self.annotations_no_return for parameter in self.name_parameters
            ) and not empty_call:
                re(f"You must annotate '{', '.join(self.name_parameters)}' {'parameter(s)' if len(self.name_parameters) > 1 else 'parameter'} of {self.function.__name__}({': <type>, '.join(self.name_parameters)}: <type>)")

            if empty_call:
                for parameter in self.annotations_no_return:
                    self.validate_and_convert_type(parameter)

            else:
                for parameter in self.name_parameters:
                    self.validate_and_convert_type(parameter)

            _return: Any = self.function(*self.signature.args, **self.signature.kwargs)
            return self.convert(CheckType.RETURN, _return, self.annotations[CheckType.RETURN]) if self._return else _return

        return wrapper

    def __call_without_parenthesis__(self, *args: tuple, **kwargs: dict) -> Any:
        self.signature: BoundArguments = signature(self.function).bind(*args, **kwargs)
        self.signature.apply_defaults()

        self.arguments: dict[str, object] = dict(self.signature.arguments)
        self.arguments_no_self: dict[str, object] = self.arguments.copy()
        self.arguments_no_self.pop(CheckType.SELF, None)

        if any(
            parameter not in self.annotations_no_return for parameter in self.arguments_no_self
        ):
            re(f"You must annotate parameters of {self.function.__name__}({': <type>, '.join(self.arguments.keys())}: <type>)")

        for parameter in self.annotations_no_return:
            self.validate_and_convert_type(parameter)

        _return: Any = self.function(*self.signature.args, **self.signature.kwargs)

        return self.convert(CheckType.RETURN, _return, self.annotations[CheckType.RETURN]) if self._return else _return

    def __call__(self, *args: tuple, **kwargs: dict) -> Callable[..., Any] | Any:
        if not self.without_parentheses:
            self.function: Callable[..., Any] = args[0]

        update_wrapper(self, self.function)

        self.annotations: dict[str, Any] = self.function.__annotations__

        self.annotations_no_return: dict[str, Any] = self.annotations.copy()
        self.annotations_no_return.pop(CheckType.RETURN, None)

        self.annotations_clean: dict[str, Any] = self.annotations_no_return.copy()
        self.annotations_clean.pop(CheckType.SELF, None)

        if not self.annotations_clean:
            warning(f"{self.function.__name__} function hasn't parameters")

        if self._return and self.annotations.get(CheckType.RETURN) is None:
            re(f"You must annotate the return of {self.function.__name__}(...) -> <type>")

        if self.without_parentheses:
            return self.__call_without_parenthesis__(*args, **kwargs)

        else:
            return self.__call_with_parenthesis__()

    def __get__(self, object_, type_=None):
        if object_ is None:
            if isinstance(self.function, classmethod):
                return partial(self.__call__, type_)

            else:
                return self.__call__

        return partial(self.__call__, object_)

    def validate_and_convert_type(self, parameter: str):
        given: object = self.arguments[parameter]
        asked: type = self.annotations[parameter]

        if type(given) != asked:
            if self._convert:
                self.signature.arguments[parameter] = self.convert(parameter, given, asked)

            else:
                re(f"The parameter {parameter} of {self.function.__name__} with a '{given}' value must be of type {asked} but you have given '{given}' with a type {type(given)}")

    def convert(self, parameter: str, value: object, annotation: type | UnionType | str) -> object | None:
        flag: bool = annotation is None or 'None' in str(annotation) # None is in annotation of the argument
        is_none: bool = value is None # The provided argument is None

        if is_none and flag:
            return None

        if isinstance(annotation, UnionType):
            annotation: str = str(annotation)

        if isinstance(annotation, str) and ' | ' in annotation:
            annotations: list[type] = []

            # An error has occurred, with the converting of '{annotation}' annotations to a list of available types (Use this syntax : 'type1 | type2 | ... | None' in incremental order of preference)
            for i, _type in enumerate(annotation.split(' | ')):
                with ecm(f"Can't convert string annotation '{_type}' to a real type (n°{i} of {annotation.split(' | ')})", level=DEBUG):
                    annotations.append(eval(_type.split('.')[-1]))

        else:
            annotations: list[type] = [annotation]

        with ecm():
            annotations.remove(None)

        for i, _type in enumerate(annotations):
            with ecm(f"The parameter {parameter} of {self.function.__name__} with a '{value}' value can't be converted to {_type} (n°{i} of {annotations})", level=INFO):
                if type(value) is _type:
                    debug(f"Skip converting for the parameter {parameter} of {self.function.__name__} with a '{value}' value and a type {type(value)} because is already of type {_type}")
                    converted = value

                else:
                    converted = _type(value)
                    debug(f"Change the parameter {parameter} of {self.function.__name__} with a '{value}' value and a type {type(value)} to type {_type}")

                return converted

        if flag:
            return None

        re(f"The parameter {parameter} of {self.function.__name__} with a '{value}' value can't be converted to one of {annotation}", ValueError)


class ValidatePathOrUrl(CheckType):
    def __init__(self, *parameters: tuple, convert: bool = True, exist: bool = False):
        self.exist = exist
        super().__init__(*parameters, convert=convert)
"""
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
            info(f"Create {Path(value)}, because doesn't exist")

        if returned is not None:
            debug(f"Change '{value}' of type {type(value)} to type {type(returned)}")
            return returned

        _re(f"'{parameter}' object with '{value}' must be a valid url or a path to a csv or a txt file", ValueError)
"""