import logging

from aiowialon.client import Session, connect

logging.getLogger(__name__).setLevel(logging.DEBUG)


def add_log_handler(handler: logging.Handler) -> None:
    """Add log handler to the module logger

    Arguments:
        handler {logging.Handler} -- log handler
    """
    logging.getLogger(__name__).addHandler(handler)
