from logging import getLogger

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


class InvalidInput(APIError):
    """ Invalid API input error """


CODE_TO_EXCEPTION_MAP = {4: InvalidInput, 7: AuthError, 8: AuthError, 9: AuthError}


def get_error(error_code: int) -> APIError:
    """Error exception factory

    Arguments:
        error_code {int} -- error code

    Returns:
        APIError -- exception subclass
    """
    return CODE_TO_EXCEPTION_MAP.get(error_code, APIError)
