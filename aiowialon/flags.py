from enum import Enum
from functools import reduce
from typing import Set


def join(flags: Set[Enum]) -> int:
    """ Reduce the flag set to the single integer """
    return reduce(lambda acc, flag: acc | flag.value, flags, 0)


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


class Messages(Enum):
    """ Messages queries flags """

    DATA = 0x0000
    SMS = 0x0100
    COMMAND = 0x0200
    EVENT = 0x0600
    LOG = 0x1000


class DataMessageExtensions(Enum):
    """ Data message extension flags """

    POSITION = 0x01
    INPUT = 0x02
    OUTPUT = 0x04
    STATE = 0x08
    ALARM = 0x10
    DRIVER = 0x20
    LBS = 0x20000


class EventMessageExtension(Enum):
    """ Event message extension flags """

    SIMPLE = 0x0
    VIOLATION = 0x1
    MAINTENANCE = 0x2
    ROUTE_CONTROL = 0x4


class Resources(Enum):
    """ Resource data flags """

    BASE = 0x00000001
    CUSTOM_PROPERTIES = 0x00000002
    BILLING_PROPERTIES = 0x00000004
    CUSTOM_FIELDS = 0x00000008
    MESSAGES = 0x00000020
    GUID = 0x00000040
    ADMINISTRATIVE_FIELDS = 0x00000080
    DRIVERS = 0x00000100
    JOBS = 0x00000200
    NOTIFICATIONS = 0x00000400
    POIS = 0x00000800
    GEOFENCES = 0x00001000
    REPORT_TEMPLATES = 0x00002000
    AUTOATTACHABLE_UNITS_FOR_DRIVERS = 0x00004000
    DRIVER_GROUPS = 0x00008000
    TRAILERS = 0x00010000
    TRAILER_GROUPS = 0x00020000
    AUTOATTACHABLE_UNITS_FOR_TRAILERS = 0x00040000
    ORDERS = 0x00080000
    GEOFENCES_GROUPS = 0x00100000
    TAGS = 0x00200000
    AUTOBINDING_UNIT_LISTS = 0x00400000
    TAGS_GROUPS = 0x00800000
