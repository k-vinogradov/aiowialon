import os
import pytest
from aiowialon.login import connect

ENV_ACCESS_KEY = "WIALON_ACCESS_KEY"
ENV_USERNAME = "WIALON_USERNAME"


# pylint: disable=redefined-outer-name


@pytest.fixture
def access_token():
    """ Get access token from the system variable """
    return os.environ[ENV_ACCESS_KEY]


@pytest.mark.asyncio
async def test_login(access_token):
    """ Test main connection routine """
    username = os.environ[ENV_USERNAME]
    async with connect(access_token) as session:
        assert username == session.username
