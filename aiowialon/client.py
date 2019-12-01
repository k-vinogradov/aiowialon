""" Async context manager to create Wialon Remote API connection. """

import json
import os
from datetime import datetime
from logging import getLogger
from aiohttp import ClientSession
from aiowialon.extensions import APIError, get_error

DEFAULT_API_HOST = "http://hst-api.wialon.com"
DEFAULT_API_PATH = "/wialon/ajax.html"

DEBUG_STORE_RESPONSES_CONTENT = os.getenv("STORE_WIALON_RESPONSES", None)

LOGGER = getLogger(__name__)


class Session:
    """ Wialon Remote API connection async context manager. """

    # pylint: disable=bad-continuation,too-many-instance-attributes

    def __init__(
        self,
        token: str,
        host: str = DEFAULT_API_HOST,
        path: str = DEFAULT_API_PATH,
        timeout=None,
    ):
        self.token = token
        self.host = host
        self.path = path
        self.sid = None
        self.username = None
        self.user_id = None
        self.account_id = None
        self.client_session = None  # type: ClientSession
        self.timeout = timeout
        self.session_info = {}

    async def __aenter__(self):
        headers = {"Content-Type": "application/x-www-form-urlencoded"}
        self.client_session = ClientSession(headers=headers)
        try:
            return await self.login()
        except Exception as exp:
            await self.client_session.close()
            raise exp

    async def __aexit__(self, exc_type, exc_value, traceback):
        await self.logout()

    async def call(self, method: str, params: dict = None):
        """Execute Wialon RemoteAPI method

        Arguments:
            method {str} -- method name
            params {dict} == method parameters (default: {})

        Returns:
            dict -- method response content
        """
        params = params or {}
        full_param_set = dict(svc=method, params=json.dumps(params))
        if self.sid is not None:
            full_param_set["sid"] = self.sid
        url = self.host + self.path

        # Execute method call
        LOGGER.debug("Call API method %s (sid %s)", method, self.sid)
        async with self.client_session.post(
            url, timeout=self.timeout, params=full_param_set
        ) as resp:
            content = await resp.json()

        if DEBUG_STORE_RESPONSES_CONTENT:
            # Store request/response data to the JSON file to debug
            prefix = "{method_name}-{datetime}".format(
                method_name=method.replace("/", "_"),
                datetime=datetime.now().strftime("%Y%m%d%H%M%S"),
            )
            data = {
                "request": {
                    "method": method,
                    "params": params,
                    "query": full_param_set,
                },
                "response": content,
            }
            counter = 0
            while True:
                filename = f"{prefix}-{counter}.json"
                filepath = os.path.join(DEBUG_STORE_RESPONSES_CONTENT, filename)
                try:
                    with open(filepath, "x") as outfile:
                        json.dump(data, outfile, indent=2)
                except FileExistsError:
                    counter += 1
                else:
                    LOGGER.debug("API response stored to %s", filepath)
                    break

        if "error" in content and content["error"] > 0:
            code = content["error"]
            reason = content.get("reason", None)
            raise get_error(code)(self.sid, code, reason)

        return content

    async def login(self):
        """ Login to the Wialon Remote API """
        if self.sid is not None:
            return self
        session_info = await self.call("token/login", {"token": self.token})
        LOGGER.debug(
            "User %s logged in to %s (sid %s)",
            session_info["user"]["nm"],
            session_info["host"],
            session_info["eid"],
        )
        self.sid = session_info["eid"]
        self.username = session_info["user"]["nm"]
        self.user_id = session_info["user"]["id"]
        self.account_id = session_info["user"]["bact"]
        self.session_info = session_info
        return self

    async def logout(self):
        """ Logout Remote Wialon API session """
        try:
            if self.sid is not None:
                await self.call("core/logout")
                LOGGER.debug("User %s logged out (sid %s)", self.username, self.sid)
        except APIError as exp:
            if exp.code > 1:
                raise exp
        finally:
            await self.client_session.close()
            self.sid = None
            self.client_session = None


def connect(
    token: str,
    api_host: str = DEFAULT_API_HOST,
    api_path: str = DEFAULT_API_PATH,
    timeout: int = None,
) -> Session:
    """Create Wialon Remote API connection

    Arguments:
        token {str} -- wialon access token

    Keyword Arguments:
        api_host {str} -- Remote API host (default: {DEFAULT_API_HOST})
        api_path {str} -- Remote AIP query path (default: {DEFAULT_API_PATH})
        timeout {int} -- client session timeout

    Returns:
        Session -- Remote API connection context manager
    """
    return Session(token, host=api_host, path=api_path, timeout=timeout)
