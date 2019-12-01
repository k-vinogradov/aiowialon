from datetime import datetime
from aiowialon.login import Session

FLAG_DATA = 0x0000
FLAG_SMS = 0x0100
FLAG_COMMAND = 0x0200
FLAG_EVENT = 0x0600
FLAG_LOG = 0x1000

DATA_POSITION = 0x01
DATA_INPUT = 0x02
DATA_OUTPUT = 0x04
DATA_STATE = 0x08
DATA_ALARM = 0x10
DATA_DRIVER = 0x20
DATA_LBS = 0x20000

EVENT_EVENT_SIMPLE = 0x0
EVENT_VIOLATION = 0x1
EVENT_MAINTENANCE = 0x2
EVENT_ROUTE_CONTROL = 0x4


def get_messages_count(
        session: Session,
        item_id: int,
        start_time: datetime,
        end_time: datetime,
        flag=FLAG_DATA,
        flag_mask=0xFF00,
):  # pylint: disable=too-many-arguments
    pass
