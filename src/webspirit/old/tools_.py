
from config.logger import log, INFO, ERROR, WARNING

from typing import Optional, Iterable, Any

from urllib.parse import urlparse

from pathlib import Path

import json, csv, re, os


class ReprMixin:
    def __repr__(self) -> str:
        if issubclass(self.__class__, (str)):
            return f"{self.__class__.__name__}('{self}')"

        return f"{self.__class__.__name__}({', '.join(f"{k.removeprefix('_')}={v!r}" for k, v in vars(self).items())})"

class BaseCSVString(str, ReprMixin):
    def __new__(cls, string: str):
        if not string:
            log("The string must not be empty", WARNING)
            return

        return str.__new__(cls, string)

    def __str__(self) -> str:
        return self

    __repr__ = ReprMixin.__repr__

class NameDescriptor(BaseCSVString):
    def __new__(cls, string: str):
        _string: Optional[str] = string if cls.is_descriptor(string) else None

        if not _string:
            message: str = f"'{string}' must has only these characters: '_', and 'a', 'b', 'c', ..., 'z' and 'A', 'B', 'C', ..., 'Z'"
            log(message, ERROR)
            raise TypeError(message)

        return super().__new__(cls, _string)

    @staticmethod
    def is_descriptor(descriptor: 'str | NameDescriptor') -> bool:
        return descriptor.replace('_', '').isalpha()

class HyperLink(BaseCSVString):
    def __new__(cls, string: str):
        _string: Optional[str] = string if cls.is_url(string) else None

        if not _string:
            message: str = f"'{string}' must be a valid hyperlink"
            log(message, ERROR)
            raise TypeError(message)

        return super().__new__(cls, _string)

    @staticmethod
    def is_url(url: 'str | HyperLink') -> bool:
        pattern = re.compile(r'^(https?|ftp)://[^\s/$.?#].[^\s]*$', re.IGNORECASE)
        result = urlparse(url)

        return bool(re.match(pattern, url)) and all([result.scheme, result.netloc])

class StrPath(Path, ReprMixin):
    def __init__(self, string: str | Path):
        if not (StrPath.is_path(string) or StrPath.is_path(string, dir=True)):
            message: str = f"'{string}' must be a valid path to a file or a directory"
            log(message, ERROR)
            raise TypeError(message)

        return super().__init__(string)

    def relpath(self) -> Path:
        return Path(os.path.relpath(self))

    @staticmethod
    def is_path(string: 'StrPath', dir: bool = False, suffix: Optional[str | Iterable[str]] = None) -> bool:
        is_file: bool = os.path.isfile(string) and os.path.exists(string)

        if dir:
            return os.path.isdir(string) and os.path.exists(string)

        elif suffix:
            if isinstance(suffix, str):
                suffix = [suffix]

            return is_file and Path(string).suffix[1:] in suffix

        return is_file

class CSVString:
    def __new__(cls, string: str, default: Optional[type] = None, strict: bool = False):
        if not string:
            return None

        if NameDescriptor.is_descriptor(string):
            cls = NameDescriptor

        elif HyperLink.is_url(string):
            cls = HyperLink

        elif StrPath.is_path(string):
            return Path(string)

        elif strict:
            message: str = f"'{string}' must be a valid url or path or a name descriptor."
            log(message, ERROR)
            raise TypeError(message)

        elif default is None:
            return

        else:
            cls = default

        return str.__new__(cls, string)

class Music(ReprMixin):
    def __init__(self, youtube_url: HyperLink, spotify_url: HyperLink | None = None, path: Path | None = None, format: str = None, type: str = None):
        self.youtube_url = youtube_url
        self.spotify_url = spotify_url
        self.path = path
        self.format = format
        self.type = type

    def __iter__(self):
        return iter([self.youtube_url, self.spotify_url, self.path, self.format, self.type])

    def __eq__(self, other: 'Music') -> bool:
        return self.youtube_url == other.youtube_url and self.format == other.format and self.type == other.format

    def to_line(self) -> str:
        return ", ".join(map(str, iter(self)))

class CSV(ReprMixin):
    HORIZONTAL: tuple[str] = ('h', 'H', 'horizontal', 'Horizontal')
    VERTICAL: tuple[str] = ('v', 'V', 'vertical', 'Vertical')

    def __init__(self, path: StrPath, default_headers: list[NameDescriptor | str] = None, force_headers: bool = False, data_type: Optional[type] = None, default_value: Optional[str] = None, sens: str = 'H'):
        if CSV.is_csv(path):
            self._path = Path(path)

        else:
            message: str = f"{path} isn't a good path to a csv file"
            log(message, ERROR)
            raise TypeError(message)

        if sens in CSV.HORIZONTAL + CSV.VERTICAL:
            self.sens = sens

        else:
            message: str = f"{sens} must be in {CSV.HORIZONTAL} or in {CSV.VERTICAL}"
            log(message, ERROR)
            raise TypeError(message)

        self.data_type = data_type
        self.force_headers = force_headers
        self.default_value = default_value
        self.default_headers = default_headers

        self.init()

    def __str__(self) -> str:
        return self.path.name

    def _repr_html_(self) -> str:
        headers: str = "".join(
            f"<td>{descriptor}</td>" for descriptor in self.headers
        )

        row: str = "".join(
            f"<tr>{"".join(f"<th>{value}</th>" for value in values)}</tr>"
            for values in zip(
               *[self.dict.values() if self.sens in CSV.HORIZONTAL else [line[1:] for line in self.table]][0]
            )
        )

        return f"<h4><i>{self}</i></h4><table><thead><tr>{headers}</tr></thead><tbody>{row}</tbody></table>"

    @property
    def path(self) -> StrPath:
        return self._path

    @path.setter
    def path(self, value: StrPath):
        if CSV.is_csv(value):
            self._path = StrPath(value)
            self.init()

        else:
            message: str = f"{value} isn't a good path to a csv file"
            log(message, ERROR)
            raise TypeError(message)

    @path.deleter
    def path(self):
        message: str = f"You can delete 'path' attribute of a {self.__class__.__class__} instance"
        log(message, ERROR)
        raise TypeError(message)

    @property
    def length(self) -> int:
        return len(self.headers)

    @length.setter
    def length(self, _):
        message: str = f"You can't set a new length of a {self.__class__.__class__} instance"
        log(message, ERROR)
        raise TypeError(message)

    @length.deleter
    def length(self, _):
        message: str = f"You can't delete a length of a {self.__class__.__class__} instance"
        log(message, ERROR)
        raise TypeError(message)

    @property
    def width(self) -> int:
        return max(len(line) for line in self.dict.values()) + 1

    @width.setter
    def width(self, _):
        message: str = f"You can't set a new width of a {self.__class__.__class__} instance"
        log(message, ERROR)
        raise TypeError(message)

    @width.deleter
    def width(self, _):
        message: str = f"You can't delete a width of a {self.__class__.__class__} instance"
        log(message, ERROR)
        raise TypeError(message)

    def __getitem__(self, name: str | int) -> Optional[list[CSVString | Any]]:
        if isinstance(name, str):
            return self.dict[name]

        elif isinstance(name, int):
            return self.table[name]

    def __setitem__(self, name: str | int, value: Any | list[Any]):
        if isinstance(name, str):
            self.dict[name] = value
            self.set_table_from_dict()

        elif isinstance(name, int):
            self.table[name] = value
            self.set_dict_from_table()

        elif isinstance(name, tuple):
            self.table[name[0]][name[1]] = value
            self.set_dict_from_table()

    def __eq__(self, value: 'CSV') -> bool:
        return value.path == self.path if isinstance(value, self.__class__) else False

    def __hash__(self) -> int:
        return hash(self.path)

    def init(self) -> tuple[list[list[Optional[CSVString]]], dict[NameDescriptor, list[HyperLink]]]:
        try:
            self._reader: list[list[str]] = list(csv.reader(open(self.path, encoding='utf-8'), delimiter=',')) #  escapechar=' '
            log(f"Load csv data in '{os.path.relpath(self.path)}'", INFO)

        except Exception as error:
            log(f"An error was occurred to the loading of the .csv file {self.path}: {error}", ERROR)
            raise error

        self.check_headers()

        self.data_type, kwargs_data_class = (self.data_type, {}) if self.data_type else (CSVString, {'default':self.data_type})

        if self.sens in CSV.VERTICAL:
            self.table: list[list[Optional[CSVString]]] = [
                [self.data_type(self._get(line, j), **kwargs_data_class) for line in self._reader[1:]]
                for j in range(len(self.headers))
            ]

            for i, header in enumerate(self.headers):
                self.table[i].insert(0, header)

        elif self.sens in CSV.HORIZONTAL:
            self.table: list[list[Optional[CSVString]]] = [
                [self.data_type(self._get(line, i), **kwargs_data_class) for i in range(len(self.headers))]
                for line in self._reader[1:]
            ]

            self.table.insert(0, self.headers)

        self.set_dict_from_table()

        log(f"Structured {self.sens} data of '{self.path.name}' csv file", INFO)

        return self.table, self.dict

    def set_table_from_dict(self) -> list[list[Optional[CSVString]]]:
        self.table: list[list[Optional[CSVString]]] = [
            [key] + value for key, value in self.dict.items()
        ]

        if self.sens in CSV.HORIZONTAL:
            self.table: list[list[Optional[CSVString]]] = [
                [self.table[i][j] for i in range(self.length)]
                for j in range(self.width)
            ]

        return self.table

    def set_dict_from_table(self) -> dict[NameDescriptor, list[HyperLink]]:
        if self.sens in CSV.VERTICAL:
            self.dict: dict[NameDescriptor, list[HyperLink]] = {
                header:line[1:] for header, line in zip(self.headers, self.table)
            }

        elif self.sens in CSV.HORIZONTAL:
            self.dict: dict[NameDescriptor, list[HyperLink]] = {
                header:[line[i] for line in self.table[1:]] for i, header in enumerate(self.headers)
            }

        return self.dict

    def check_headers(self) -> list[NameDescriptor]:
        if CSV.is_header(self._reader[0]) and not self.force_headers:
            self.headers: list[NameDescriptor] = list(map(NameDescriptor, self._reader[0]))

        else:
            self.headers: list[NameDescriptor] = list(map(NameDescriptor, self.default_headers))
            self._reader.insert(0, self.default_headers)

        return self.headers

    def save(self):
        try:
            self.sens = 'H'
            # self.set_table_from_dict()

            with self.path.open('w', encoding='utf-8') as file:
                file.writelines(", ".join(map(str, line)) + '\n' for line in self.table)

            log(f"Save the data in '{os.path.relpath(self.path)}'", INFO)

        except Exception as error:
            message: str = f"An error was occurred when saving data in '{os.path.relpath(self.path)}: {error}"
            log(message, ERROR)
            raise TypeError(message) from error

    def _get(self, iterable: Iterable[Any], index: int) -> Optional[Any]:
        try:
            obj: Any = iterable[index]
            return self.default_value if obj is None or obj in ('None', ' ', '') else obj

        except Exception as e:
            return self.default_value

    @staticmethod
    def is_csv(path: StrPath) -> bool:
        return StrPath.is_path(path, suffix='csv')

    @staticmethod
    def is_header(line: list[Any]) -> bool:
        return all(map(NameDescriptor.is_descriptor, line))

import pandas as pd
from typing import List, Dict, Optional, Union

class CSV:
    def __init__(self, filepath: Optional[str] = None):
        self.df = pd.DataFrame()
        self.filepath = filepath
        if filepath:
            self.load(filepath)

    # ======== Chargement et sauvegarde ========

    def load(self, filepath: str, **kwargs):
        self.df = pd.read_csv(filepath, **kwargs)
        self.filepath = filepath

    def save(self, filepath: Optional[str] = None, **kwargs):
        if path := filepath or self.filepath:
            self.df.to_csv(path, index=False, **kwargs)
        else:
            raise ValueError("No file path provided.")

    # ======== Accès aux représentations ========

    @property
    def headers(self) -> List[str]:
        return self.df.columns.tolist()

    @headers.setter
    def headers(self, new_headers: List[str]):
        if len(new_headers) != len(self.df.columns):
            raise ValueError("New headers length must match current number of columns.")
        self.df.columns = new_headers

    @property
    def rows_table(self) -> List[List[Union[str, int, float]]]:
        return self.df.values.tolist()

    @rows_table.setter
    def rows_table(self, table: List[List[Union[str, int, float]]]):
        if not self.headers:
            raise ValueError("Set headers before assigning rows_table.")
        self.df = pd.DataFrame(table, columns=self.headers)

    @property
    def rows_dicts(self) -> List[Dict[str, Union[str, int, float]]]:
        return self.df.to_dict(orient="records")

    @rows_dicts.setter
    def rows_dicts(self, dicts: List[Dict[str, Union[str, int, float]]]):
        self.df = pd.DataFrame(dicts)

    @property
    def columns(self) -> Dict[str, List[Union[str, int, float]]]:
        return self.df.to_dict(orient="list")

    @columns.setter
    def columns(self, cols: Dict[str, List[Union[str, int, float]]]):
        self.df = pd.DataFrame(cols)

    # ======== Accès/modification cellule/colonne/ligne ========

    def update_cell(self, row_idx: int, col: str, value: Union[str, int, float]):
        self.df.at[row_idx, col] = value

    def get_row(self, index: int) -> Dict[str, Union[str, int, float]]:
        return self.df.iloc[index].to_dict()

    def add_row(self, row: Union[Dict[str, Union[str, int, float]], List[Union[str, int, float]]]):
        if isinstance(row, dict):
            self.df = pd.concat([self.df, pd.DataFrame([row])], ignore_index=True)
        elif isinstance(row, list):
            if len(row) != len(self.df.columns):
                raise ValueError("Row length must match number of columns.")
            self.df.loc[len(self.df)] = row
        else:
            raise TypeError("Row must be a list or dict.")

    def remove_row(self, index: int):
        self.df = self.df.drop(index).reset_index(drop=True)

    def get_column(self, col: str) -> List[Union[str, int, float]]:
        return self.df[col].tolist()

    def update_column(self, col: str, values: List[Union[str, int, float]]):
        if len(values) != len(self.df):
            raise ValueError("Column length must match number of rows.")
        self.df[col] = values

    # ======== Utilitaires ========

    def filter(self, expr: str) -> 'CSV':
        """Retourne un nouveau CSV filtré avec une expression Pandas."""
        new_csv = CSV()
        new_csv.df = self.df.query(expr).copy()
        return new_csv

    def __str__(self):
        return str(self.df)

    def __len__(self):
        return len(self.df)

    def head(self, n=5):
        return self.df.head(n)

    def tail(self, n=5):
        return self.df.tail(n)

class JSON:
    @staticmethod
    def load(path: StrPath) -> dict:
        name: str = os.path.split(path)[1]
    
        with open(path, 'r', encoding='utf-8') as file:
            log(f"Load {name} in '{os.path.relpath(path)}'", INFO)
            return json.load(file)

    @staticmethod
    def save(path: StrPath, data: dict):
        name: str = os.path.split(path)[1]

        with open(path, 'w', encoding='utf-8') as file:
            log(f"Save {name} in '{os.path.relpath(path)}'", INFO)
            json.dump(data, file, indent=2)
