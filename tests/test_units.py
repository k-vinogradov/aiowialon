import pytest
from aiowialon.units import load_units


@pytest.mark.asyncio
async def test_load_units(session):
    """ Test that unit list length isn't empty """
    units = await load_units(session)
    assert len(units) > 0
