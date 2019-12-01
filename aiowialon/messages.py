from datetime import datetime
from typing import Union
from aiowialon.client import Session
from aiowialon.extensions import InvalidInput
from aiowialon.flags import Messages, join


def timestamp(date: Union[datetime, int, float]) -> int:
    """Adjust any datetime value to POSIX timestamp

    Arguments:
        date {Union[datetime, int, float]} -- datetime instance or timestamp

    Returns:
        int -- integer POSIX timestamp
    """
    if isinstance(date, (float, int)):
        return int(date)
    return int(date.timestamp())


# def date_time(timestamp: int) -> datetime:
#     """Convert POSIX timestamp to the datetime instance

#     Arguments:
#         timestamp {int} -- POSIX timestamp

#     Returns:
#         datetime -- datetime instance
#     """
#     return datetime.utcfromtimestamp(timestamp)


# pylint: disable=too-many-arguments
async def _call_load_messages(
    session: Session,
    item_id: int,
    begin_time: Union[datetime, int, float],
    end_time: Union[datetime, int, float],
    flags: set,
    flag_mask: int,
    count: int,
):
    try:
        await session.call("messages/unload")
    except InvalidInput:
        pass
    return await session.call(
        "messages/load_interval",
        {
            "itemId": item_id,
            "timeFrom": timestamp(begin_time),
            "timeTo": timestamp(end_time),
            "flags": join(flags),
            "flagsMask": flag_mask,
            "loadCount": count,
        },
    )


async def get_messages_count(
    session: Session,
    item_id: int,
    begin_time: Union[datetime, int, float],
    end_time: Union[datetime, int, float],
    flags: set = None,
    flag_mask: int = 0xFF00,
) -> int:
    """Get the number of messages received during the time interval.

    Arguments:
        session {Session} -- Wialon API session
        item_id {int} -- item identifier
        begin_time {Union[datetime, int, float]} -- datetime for the beginning of the interval
        end_time {Union[datetime, int, float]} -- date time of end of the interval

    Keyword Arguments:
        flags {set} -- request flags (default: {None})
        flag_mask {[type]} -- flag mask (default: {0xFF00})

    Returns:
        int -- the number of messages
    """
    return (
        await _call_load_messages(
            session,
            item_id,
            begin_time,
            end_time,
            flags or {Messages.DATA},
            flag_mask,
            0,
        )
    )["count"]


async def load_messages(
    session: Session,
    item_id: int,
    begin_time: Union[datetime, int, float],
    end_time: Union[datetime, int, float],
    flags: set = None,
    flag_mask: int = 0xFF00,
    count: int = 0xFFFFFFFF,
) -> list:
    """Load the messages received during the time interval.

    Arguments:
        session {Session} -- Wialon API session
        item_id {int} -- item identifier
        begin_time {Union[datetime, int, float]} -- datetime for the beginning of the interval
        end_time {Union[datetime, int, float]} -- datetime of end of the interval

    Keyword Arguments:
        flags {set} -- request flags (default: {None})
        flag_mask {[type]} -- flag mask (default: {0xFF00})
        count {int} -- the number of messages to load (default: {0xFFFFFFFF})

    Returns:
        list -- message list
    """
    return (
        await _call_load_messages(
            session,
            item_id,
            begin_time,
            end_time,
            flags or {Messages.DATA},
            flag_mask,
            count,
        )
    )["messages"]


# pylint: enable=too-many-arguments
