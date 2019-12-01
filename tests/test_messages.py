from datetime import datetime, timedelta

import pytest
from aiowialon.messages import load_messages, get_messages_count
from aiowialon.units import load_units


@pytest.mark.asyncio
async def test_get_messages_count(session):
    """ Check if at least one unit has non-empty message list """
    at_least_one_unit_has_messages = False
    for unit in await load_units(session):
        if await get_messages_count(
            session,
            unit["id"],
            begin_time=datetime.now() - timedelta(days=1),
            end_time=datetime.now(),
        ):
            at_least_one_unit_has_messages = True
            break
    assert at_least_one_unit_has_messages


@pytest.mark.asyncio
async def test_load_messages(session):
    """ Check if at least one unit has non-empty message list """
    at_least_one_unit_has_messages = False
    for unit in await load_units(session):
        if await load_messages(
            session,
            unit["id"],
            begin_time=datetime.now() - timedelta(days=1),
            end_time=datetime.now(),
        ):
            at_least_one_unit_has_messages = True
            break
    assert at_least_one_unit_has_messages
