from abc import ABC, abstractmethod
from enum import Enum
from typing import List, Tuple, Iterable
from shapely.geometry import Point, Polygon
from aiowialon.flags import Resources, join
from aiowialon.client import Session
from aiowialon.utils import distance


class AreaFlags(Enum):
    """ Area requests data flags """

    SQUARE = 0x01
    PERIMETER = 0x02
    EDGES_AND_CENTER = 0x03
    POINTS = 0x08
    BASE = 0x10


class AreaType(Enum):
    """ Wialon area types """

    LINE = 1
    POLYGON = 2
    CIRCLE = 3


class Area(ABC):
    """ Wialon area (geofence) """

    def __init__(self, data, session=None):
        self.data = data
        self.session = session

    def __eq__(self, other):
        return (
            isinstance(other, type(self))
            and self.id() == other.id()
            and self.resource_id() == other.resource_id()
        )

    def __str__(self):
        return "{} ({})".format(self.name(), self.description())

    @abstractmethod
    def area_type(self) -> AreaType:
        pass

    @abstractmethod
    def contains(self, latitude, longitude) -> bool:
        pass

    def id(self) -> int:
        return self.data["id"]

    def resource_id(self) -> int:
        return self.data["rid"]

    def name(self) -> str:
        return self.data["n"]

    def description(self) -> str:
        return self.data["d"]

    def is_line(self) -> bool:
        return self.area_type() == AreaType.LINE

    def is_circle(self) -> bool:
        return self.area_type() == AreaType.CIRCLE

    def is_polygon(self) -> bool:
        return self.area_type() == AreaType.POLYGON


class CircleArea(Area):
    def area_type(self):
        return AreaType.CIRCLE

    def contains(self, latitude, longitude):
        return distance(latitude, longitude, *self.location()) <= self.radius()

    def radius(self) -> float:
        return self.data["p"][0]["r"]

    def location(self) -> Tuple[float, float]:
        return self.data["p"][0]["y"], self.data["p"][0]["x"]


class PolygonArea(Area):
    def area_type(self):
        return AreaType.POLYGON

    def contains(self, latitude, longitude) -> bool:
        point = Point(latitude, longitude)
        polygon = Polygon(self.points())
        return polygon.contains(point)

    def points(self) -> List[Tuple[float, float]]:
        return [(p["y"], p["x"]) for p in self.data["p"]]


def build_area(data):
    area_type = AreaType(data["t"])
    if area_type == AreaType.CIRCLE:
        return CircleArea(data)
    if area_type == AreaType.POLYGON:
        return PolygonArea(data)
    raise ValueError(f"Unsupported area type: {area_type.name()}")


async def load_areas(session: Session) -> List[Area]:
    """Load available area list

    Arguments:
        session {Session} -- active user session

    Returns:
        List[Area] -- Area instance list
    """
    return [build_area(item) for item in await load_areas_raw(session, load_detail=True)]


async def load_areas_raw(session: Session, load_detail: bool = False) -> list:
    """Load available geofence raw info list

    Arguments:
        session {Session} -- active user session

    Keyword Arguments:
        load_detail {bool} -- include area detail info (default: {False})

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

    if not load_detail:
        return [
            {"rid": resource["id"], **area}
            for resource in response["items"]
            for area in resource["zl"].values()
        ]

    result = []
    for resource in response["items"]:
        areas = [area["id"] for area in resource["zl"].values()]
        areas_detail = await get_areas_detail_raw(session, areas, resource["id"])
        result.extend(areas_detail.values())
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
        {"spec": {"zoneId": {resource: []}, "lat": latitude, "lon": longitude, "radius": radius,}},
    )
    if not responce:
        return []

    result = [({"id": int(gid)}, distance) for gid, distance in responce[str(resource)].items()]

    if area_detail:
        area_id_list = [item[0]["id"] for item in result]
        detail = await get_areas_detail_raw(session, area_id_list)
        for item in result:
            area_id = item[0]["id"]
            item[0].update(detail[area_id])

    return result


async def get_areas_detail(
    session: Session,
    area_id_list: Iterable[int],
    resource: int = None,
    flags: List[AreaFlags] = None,
):
    return {
        area_id: build_area(data)
        for area_id, data in (
            await get_areas_detail_raw(
                session, area_id_list=area_id_list, resource=resource, flags=flags
            )
        ).items()
    }


async def get_areas_detail_raw(
    session: Session,
    area_id_list: Iterable[int],
    resource: int = None,
    flags: List[AreaFlags] = None,
) -> dict:
    """Query the areas raw info

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
        {"itemId": resource, "col": list(area_id_list), "flag": join(flags)},
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
    return (await get_areas_detail_raw(session, [area_id], resource=resource, flags=flags))[area_id]
