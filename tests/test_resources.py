import pytest
from aiowialon.resources import load_areas_raw, get_areas_detail_raw, get_area_detail


@pytest.mark.asyncio
async def test_load_areas(session):
    """ Test if load_areas(...) returns non empty list """
    areas = await load_areas_raw(session)
    assert isinstance(areas, list)
    assert len(areas) > 0


@pytest.mark.asyncio
async def test_get_areas_detail(session):
    """
    Query for detail for all available resources/areas and test that
    at least one isn't empty.
    """
    resources = {}
    for area in await load_areas_raw(session):
        if area["rid"] in resources:
            resources[area["rid"]].append(area["id"])
        else:
            resources[area["rid"]] = [area["id"]]
    at_least_one_is_not_empty = False
    for rid, areas in resources.items():
        detail = await get_areas_detail_raw(session, areas, resource=rid)
        at_least_one_is_not_empty = at_least_one_is_not_empty or len(detail) > 0
    assert at_least_one_is_not_empty


@pytest.mark.asyncio
async def test_get_area_detail(session):
    """ Test get_area_detail """
    area = (await load_areas_raw(session))[0]
    detail = await get_area_detail(session, area["rid"], area["id"])
    assert detail
