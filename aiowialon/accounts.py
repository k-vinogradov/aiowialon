from typing import Coroutine

from aiowialon.client import Session

MINIMAL_ACCOUNT_INFO = 1


def get_account_data(session: Session) -> Coroutine:
    """Get Wialon account detail

    Arguments:
        session {Session} -- active session

    Returns:
        Coroutine -- coroutine returning account info dictionary
    """
    return session.call(
        "account/get_account_data", {"itemId": session.account_id, "type": MINIMAL_ACCOUNT_INFO},
    )
