import asyncio
import dataclasses
import enum
import time
from datetime import datetime

class IntervalType(enum.Enum):
    MONTH = "month"
    WEEK = "week"
    DAY = "day"
    HOUR = "hour"
    MINUTE = "minute"
    SEC = "second"

    def interval_type_to_sec(self):
        if self.value in IntervalType.SEC:
            return 1
        if self.value in IntervalType.MINUTE:
            return 60
        if self.value in IntervalType.HOUR:
            return 60 * 60
        if self.value in IntervalType.DAY:
            return 60 * 60 * 24
        if self.value in IntervalType.WEEK:
            return 60 * 60 * 24 * 7
        if self.value in IntervalType.MONTH:
            return 60 * 60 * 24 * 7 * 4


@dataclasses.dataclass(frozen=True)
class Interval:
    interval_type: IntervalType
    interval_num: float

    async def interval_to_sec(self) -> float:
        return self.interval_num * self.interval_type.interval_type_to_sec()


async def date_seconds_difference(date_base, relative_date):
    d_supposed = relative_date
    if isinstance(relative_date, str):
        d_supposed = datetime.strptime(relative_date, '%d/%m/%y %H:%M:%S')
    d_now = date_base
    if isinstance(date_base, str):
        d_supposed = datetime.strptime(date_base, '%d/%m/%y %H:%M:%S')
    difference = (d_now - d_supposed).total_seconds()
    return difference



def time_measure(coroutine):
    async def wrapped(args, *kwargs):
        start_time = time.time()
        try:
            asyncio.run(coroutine(args, *kwargs))
        except Exception as e:
            print(e)
            print("interrupt:")
            end_time_ex = time.time()
            run_time_ex = end_time_ex - start_time
            print(run_time_ex)
        finally:
            print("crash/end")
            end_time = time.time()
            run_time = end_time - start_time
            print(run_time)

    return wrapped
