from webspirit.tools.checktype import CheckType, HyperLink, StrPath

from typing import Any

import json


__all_ : list[str] = [
    'show',
    'get_constants',
    'links_from_cell'
]


def show(obj: Any):
    print('str  :', obj, '\nrepr :', repr(obj))

@CheckType('notebook')
def links_from_cell(notebook: StrPath, index: int = 0, type: type = HyperLink) -> list[type]:
    with notebook.open('r', encoding='utf-8') as f:
        notebook = json.load(f)

    cell: dict = notebook['cells'][index]

    return [
        type(link.removesuffix('\n').removesuffix('  ')) for link in cell['source']
    ]   if cell['cell_type'] in ('markdown', 'raw') else ['']