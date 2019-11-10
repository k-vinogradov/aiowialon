""" Async context manager to create Wialon Remote API connection. """

import json
import os
from datetime import datetime
from logging import getLogger
from aiohttp import ClientSession

DEFAULT_API_HOST = "http://hst-api.wialon.com"
DEFAULT_API_PATH = "/wialon/ajax.html"

DEBUG_STORE_RESPONSES_CONTENT = os.getenv("STORE_WIALON_RESPONSES", None)

LOGGER = getLogger(__name__)

ERROR_CODES = {
    0: "Successful operation",
    1: "Invalid session",
    2: "Invalid service name",
    3: "Invalid result",
    4: "Invalid input",
    5: "Error performing request",
    6: "Unknown error",
    7: "Access denied",
    8: "Invalid user name or password",
    9: "Authorization server is unavailable",
    10: "Reached limit of concurrent requests",
    11: "Password reset error",
    14: "Billing error",
    1001: "No messages for selected interval",
    1002: (
        "Item with such unique property already exists or "
        "it cannot be created according to billing restrictions"
    ),
    1003: "Only one request is allowed at the moment",
    1004: "Limit of messages has been exceeded",
    1005: "Execution time has exceeded the limit",
    1006: "Exceeding the limit of attempts to enter a two-factor authorization code",
    1011: "Your IP has changed or session has expired",
    2014: (
        "Selected user is a creator for some system objects, "
        "thus this user cannot be bound to a new account"
    ),
    2015: (
        "Sensor deleting is forbidden because of using "
        "in another sensor or advanced properties of the unit"
    ),
}


class APIError(RuntimeError):
    """ General API client error. """

    def __init__(self, sid: str, code: int, reason: str):
        self.code = code
        self.description = ERROR_CODES.get(code, "Unknown error")
        self.reason = (
            reason or self.description
        )  # because of the 'reason' field is optional
        self.sid = sid
        if reason:
            self.message = f"{self.description}: {reason}"
        else:
            self.message = f"{self.description}"
        LOGGER.error("Wialon API error: %s (sid %s)", self, sid)
        RuntimeError.__init__(self)

    def __str__(self):
        return self.message


class AuthError(APIError):
    """ Wialon API authentication error. """


CODE_TO_EXCEPTION_MAP = {7: AuthError, 8: AuthError, 9: AuthError}


class Session:
    """ Wialon Remote API connection async context manager. """

    # pylint: disable=bad-continuation,too-many-instance-attributes

    def __init__(
        self, token: str, host: str = DEFAULT_API_HOST, path: str = DEFAULT_API_PATH
    ):
        self.token = token
        self.host = host
        self.path = path
        self.sid = None
        self.username = None
        self.user_id = None
        self.account_id = None
        self.client_session = None  # type: ClientSession
        self.session_info = {}

    async def __aenter__(self):
        headers = {"Content-Type": "application/x-www-form-urlencoded"}
        self.client_session = ClientSession(headers=headers)
        try:
            session_info = await self.call("token/login", token=self.token)
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
        except Exception as exp:
            await self.client_session.close()
            raise exp

    async def __aexit__(self, exc_type, exc_value, traceback):
        try:
            if self.sid is not None:
                await self.call("core/logout")
                LOGGER.debug("User %s logged out (sid %s)", self.username, self.sid)
        except APIError as exp:
            if exp.code > 1:
                raise exp
        finally:
            await self.client_session.close()

    async def call(self, method: str, **kwargs):
        """Execute Wialon RemoteAPI method

        Arguments:
            method {str} -- method name

        Returns:
            dict -- method response content
        """
        query_params = dict(svc=method, params=json.dumps(kwargs))
        if self.sid is not None:
            query_params["sid"] = self.sid
        url = self.host + self.path

        # Execute method call
        LOGGER.debug("Call API method %s (sid %s)", method, self.sid)
        async with self.client_session.post(url, params=query_params) as resp:
            content = await resp.json()

        if DEBUG_STORE_RESPONSES_CONTENT:
            # Store request/response data to the JSON file to debug
            prefix = "{method_name}-{datetime}".format(
                method_name=method.replace("/", "_"),
                datetime=datetime.now().strftime("%Y%m%d%H%M%S"),
            )
            data = {
                "request": {"method": method, "params": kwargs, "query": query_params},
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
            raise CODE_TO_EXCEPTION_MAP.get(code, APIError)(self.sid, code, reason)

        return content


# pylint: disable=bad-continuation
def connect(
    token: str, api_host: str = DEFAULT_API_HOST, api_path: str = DEFAULT_API_PATH
) -> Session:
    """Create Wialon Remote API connection

    Arguments:
        token {str} -- wialon access token

    Keyword Arguments:
        api_host {str} -- Remote API host (default: {DEFAULT_API_HOST})
        api_path {str} -- Remote AIP query path (default: {DEFAULT_API_PATH})

    Returns:
        Session -- Remote API connection context manager
    """
    return Session(token, host=api_host, path=api_path)
