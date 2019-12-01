from math import asin, cos, radians, sin, sqrt

EARTH_RADIUS = 6371000.0


def distance(
    latitude_1: float, longitude_1: float, latitude_2: float, longitude_2: float
) -> float:
    """Calculate the distance between the two points defined by their coordinates

    Arguments:
        latitude_1 {float} -- first point's latitude
        longitude_1 {float} -- first point's longitude
        latitude_2 {float} -- second point's latitude
        longitude_2 {float} -- second point's longitude

    Returns:
        float -- distance
    """
    lat1, lon1, lat2, lon2 = map(
        radians, (latitude_1, longitude_1, latitude_2, longitude_2)
    )
    return (
        2
        * EARTH_RADIUS
        * asin(
            sqrt(
                sin((lat2 - lat1) / 2) ** 2
                + cos(lat1) * cos(lat2) * (sin((lon2 - lon1) / 2) ** 2)
            )
        )
    )
