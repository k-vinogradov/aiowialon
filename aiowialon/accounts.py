from aiowialon.client import Session

MINIMAL_ACCOUNT_INFO = 1


def get_account_data(session: Session) -> dict:
    """Get Wialon account detail

    Arguments:
        session {Session} -- active session

    Returns:
        dict -- account info
    """
    return session.call(
        "account/get_account_data",
        {"itemId": session.account_id, "type": MINIMAL_ACCOUNT_INFO},
    )
