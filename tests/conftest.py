import asyncio
import os
from urllib.parse import urlparse, parse_qs
import pytest
from mechanicalsoup import StatefulBrowser
from aiowialon.client import connect


ACCESS_TOKEN_VARIABLE = "WIALON_ACCESS_TOKEN"
USERNAME_VARIABLE = "WIALON_USERNAME"
PASSWORD_VARIABLE = "WIALON_PASSWORD"

DEFAULT_USERNAME = "wialon_test"
DEFAULT_PASSWORD = "test"

AUTH_URL = "http://w.glonass24.com/login.html"

# pylint: disable=redefined-outer-name,missing-function-docstring


@pytest.fixture(scope="session")
def username():
    return os.getenv(USERNAME_VARIABLE, DEFAULT_USERNAME)


@pytest.fixture(scope="session")
def password():
    return os.getenv(PASSWORD_VARIABLE, DEFAULT_PASSWORD)


@pytest.fixture(scope="session")
def access_token(username: str, password: str):
    if ACCESS_TOKEN_VARIABLE in os.environ:
        return os.environ[ACCESS_TOKEN_VARIABLE]
    browser = StatefulBrowser()
    browser.open(AUTH_URL)
    browser.select_form("#auth-form")
    browser["login"] = username
    browser["passw"] = password
    browser.submit_selected()
    url = urlparse(browser.get_url())
    token = parse_qs(url.query)["access_token"][0]
    return token


@pytest.yield_fixture(scope="session")
def event_loop(request):  # pylint: disable=unused-argument
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
async def session(access_token: str):
    async with connect(access_token) as session:
        yield session
