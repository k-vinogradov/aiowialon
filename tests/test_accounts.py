import pytest
from aiowialon.accounts import get_account_data


@pytest.mark.asyncio
async def test_get_account_data(session):
    """ Test that active user account info isn't empty """
    account_info = await get_account_data(session)
    assert account_info
