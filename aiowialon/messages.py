from datetime import datetime
from itertools import zip_longest
from typing import Union
from aiowialon.client import Session
from aiowialon.exceptions import InvalidInput
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


class MessageLoader:
    """ Context messager to clean up the message loader after requests """

    def __init__(self, session: Session):
        self.session = session

    async def __aenter__(self):
        return self.session

    async def __aexit__(self, *_):
        await self.session.call("messages/unload")


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
    async with MessageLoader(session) as loader:  # type: Session
        response = await loader.call(
            "messages/load_interval",
            {
                "itemId": item_id,
                "timeFrom": timestamp(begin_time),
                "timeTo": timestamp(end_time),
                "flags": join(flags or {Messages.DATA}),
                "flagsMask": flag_mask,
                "loadCount": 0,
            },
        )
        return response["count"]


async def load_messages(
    session: Session,
    item_id: int,
    begin_time: Union[datetime, int, float],
    end_time: Union[datetime, int, float],
    flags: set = None,
    flag_mask: int = 0xFF00,
    count: int = 0xFFFFFFFF,
    include_sensor_data=False,
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
    async with MessageLoader(session) as loader:  # type: Session
        response = await loader.call(
            "messages/load_interval",
            {
                "itemId": item_id,
                "timeFrom": timestamp(begin_time),
                "timeTo": timestamp(end_time),
                "flags": join(flags or {Messages.DATA}),
                "flagsMask": flag_mask,
                "loadCount": count,
            },
        )
        messages = response["messages"]
        if include_sensor_data and messages:
            sensors = await loader.call(
                "unit/calc_sensors",
                {
                    "source": "",
                    "indexFrom": 0,
                    "indexTo": response["count"] - 1,
                    "unitId": item_id,
                    "sensorId": 0,
                },
            )
            if len(messages) != len(sensors):
                raise ValueError(
                    "Invalid data length. {} sensors data items has got for {} messages".format(
                        len(sensors), len(messages)
                    )
                )
            for message, sensor_data in zip_longest(messages, sensors):
                message["sensors_data"] = sensor_data

        return messages


# pylint: enable=too-many-arguments
