from enum import Enum, auto
from typing import Tuple

# todo: y.mezentsev need remove? used in method filter
EMPTY_VALUES: Tuple[list, tuple, dict, None] = ([], (), {}, None)


class NullsPosition(Enum):
    first = auto()
    last = auto()
