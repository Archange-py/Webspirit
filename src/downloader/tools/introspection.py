from typing import Any


def show(obj: Any):
    print('str :', str(obj))
    print('repr :', repr(obj))

def exception(obj: Any, *args, **kwargs) -> Exception | None:
    try:
        instance: Any = obj(*args, **kwargs)
        return

    except Exception as error:
        return error