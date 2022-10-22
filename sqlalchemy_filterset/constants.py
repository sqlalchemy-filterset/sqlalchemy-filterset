from enum import Enum, auto
from typing import Tuple

EMPTY_VALUES: Tuple[list, tuple, dict, str, None] = ([], (), {}, "", None)


class NullsPosition(Enum):
    first = auto()
    last = auto()
