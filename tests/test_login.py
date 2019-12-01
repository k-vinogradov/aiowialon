import pytest
from aiowialon import connect

@pytest.mark.asyncio
async def test_login(access_token):
    """ Test main connection routine """
    async with connect(access_token) as session:
        assert session.username
