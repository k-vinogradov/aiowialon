from enum import Enum
from typing import List
from aiowialon.flags import Resources, join
from aiowialon.client import Session


class AreaFlags(Enum):
    """ Area requests data flags """

    SQUARE = 0x01
    PERIMETER = 0x02
    EDGES_AND_CENTER = 0x03
    POINTS = 0x08
    BASE = 0x10


async def load_areas(session: Session) -> list:
    """Load available geofence list

    Arguments:
        session {Session} -- active user session

    Returns:
        list -- geofence list
    """
    response = await session.call(
        "core/search_items",
        {
            "spec": {
                "itemsType": "avl_resource",
                "propName": "zone_library",
                "propValueMask": "*",
                "propType": "propitemname",
                "sortType": "zone_library",
            },
            "force": 1,
            "flags": join({Resources.BASE, Resources.GEOFENCES}),
            "from": 0,
            "to": 0,
        },
    )
    result = []
    for resource in response["items"]:
        for area in resource["zl"].values():
            result.append({"rid": resource["id"], **area})
    return result


async def search_areas_by_point(  # pylint: disable=too-many-arguments
    session: Session,
    latitude: float,
    longitude: float,
    resource: int = None,
    area_detail: bool = True,
    radius: int = 0,
) -> list:
    """
    Check if the point belongs to the areas or search
    the areas inside the search radius

    Arguments:
        session {Session} -- active session
        latitude {float} -- point latitude
        longitude {float} -- point longitude

    Keyword Arguments:
        resource {int} -- resource identifier, if None user account id is used (default: {None})
        area_detail {bool} -- request the area detail (default: {True})
        radius {int} -- area search radius (default: 0)

    Returns:
        list -- list of tuples (area_info, distance)
    """
    resource = resource or session.account_id
    responce = await session.call(
        "resource/get_zones_by_point",
        {
            "spec": {
                "zoneId": {resource: []},
                "lat": latitude,
                "lon": longitude,
                "radius": radius,
            }
        },
    )
    if not responce:
        return []

    result = [
        ({"id": int(gid)}, distance)
        for gid, distance in responce[str(resource)].items()
    ]

    if area_detail:
        area_id_list = [item[0]["id"] for item in result]
        detail = await get_areas_detail(session, area_id_list)
        for item in result:
            area_id = item[0]["id"]
            item[0].update(detail[area_id])

    return result


async def get_areas_detail(
    session: Session,
    area_id_list: List[int],
    resource: int = None,
    flags: List[AreaFlags] = None,
) -> dict:
    """Query the areas info

    Arguments:
        session {Session} -- active API session
        area_id_list {List[int]} -- area ID list

    Keyword Arguments:
        resource {int} -- owner resource ID, if None user acccount ID is used (default: None)
        flags {List[AreaFlags]} -- area data flags (default: [AreaFlags.BASE])

    Returns:
        dict -- key value pairs area_id -> area_info
    """
    flags = flags or [AreaFlags.BASE]
    resource = resource or session.account_id
    response = await session.call(
        "resource/get_zone_data",
        {"itemId": resource, "col": area_id_list, "flag": join(flags)},
    )
    return {area["id"]: area for area in response}


async def get_area_detail(
    session: Session, resource: int, area_id: int, flags: List[AreaFlags] = None
) -> dict:
    """Query the area detail

    Arguments:
        session {Session} -- active Wialon Remote API session
        resource {int} -- owner resource identifier
        area_id {int} -- area identifier list

    Keyword Arguments:
        flags {List[AreaFlags]} -- request flags (default: {None})

    Returns:
        dict -- key-value dictionary area_id -> area_detail
    """
    return (await get_areas_detail(session, [area_id], resource=resource, flags=flags))[
        area_id
    ]
