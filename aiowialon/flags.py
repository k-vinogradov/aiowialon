from enum import Enum
from functools import reduce
from typing import Set


class Units(Enum):
    """ Units queries flags"""

    GENERAL_PROPERTIES = 0x00000001
    CUSTOM_PROPERTIES = 0x00000002
    CUSTOM_FIELDS = 0x00000008
    MESSAGES = 0x00000020
    ADVANCED_PROPERTIES = 0x00000100
    LAST_MESSAGE_AND_POSITION = 0x00000400
    SENSORS = 0x00001000
    COUNTERS = 0x00002000
    MESSAGE_PARAMETERS = 0x00100000
    CONNECTION = 0x00200000
    POSSITION = 0x00400000


def join(flags: Set[Enum]) -> int:
    """ Reduce the flag set to the single integer """
    return reduce(lambda acc, flag: acc | flag.value, flags, 0)
