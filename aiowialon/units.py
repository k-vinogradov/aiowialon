""" The module contains the wrapper functions which can be
    used as shortcuts for the most commonly used methods
    of the Wialon API.
"""
from typing import Optional, Iterable
from aiowialon.flags import join, Units
from aiowialon import Session


async def load_units(session: Session, flags: Optional[Iterable] = None) -> list:
    """Request the unit list by calling search_items method

    Arguments:
        session {Session} -- current active session
        flags {Optional[Iterable]} -- data representing flag set (default: {Units.GENERAL_PROPERTIES})

    Returns:
        list -- unit list
    """
    flags = set(flags) or {Units.GENERAL_PROPERTIES}
    response = await session.call(
        "core/search_items",
        {
            "spec": {
                "itemsType": "avl_unit",
                "propName": "sys_name",
                "propValueMask": "*",
                "propType": "list",
                "sortType": "sys_name",
            },
            "force": 1,
            "flags": join(flags),
            "from": 0,
            "to": 0,
        },
    )
    return response["items"]
