from typing import Union

from watchgod import Change


def tictoc(tic: float, toc: float) -> float:
    return round(1000 * (toc - tic), 1)


def change_to_str(change: Change) -> str:
    if change == 1:
        return "add"
    elif change == 2:
        return "modify"
    else:
        return "delete"


def listify(obj):
    if isinstance(obj, list):
        return obj
    elif obj is None:
        return []
    else:
        return [obj]
