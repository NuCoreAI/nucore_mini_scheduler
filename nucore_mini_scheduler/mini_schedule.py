from __future__ import annotations

from datetime import datetime, timedelta, timezone
from uuid import uuid4


def _to_utc(dt: datetime) -> datetime:
    if dt.tzinfo is None:
        local_tz = datetime.now().astimezone().tzinfo
        dt = dt.replace(tzinfo=local_tz)
    return dt.astimezone(timezone.utc)


class MiniSchedule:
    def __init__(
        self,
        start_time: datetime | None = None,
        end_time: datetime | None = None,
        duration: int | timedelta | None = None,
        id: str | None = None,
        description: str | None = None,
    ):
        self._id: str = self._generate_or_keep_id(id)
        self._description: str | None = description
        self._start_time: datetime | None = None
        self._end_time: datetime | None = None
        self._duration: timedelta | None = None
        self._processed = False
        self._notified = False

        if start_time is not None:
            self.setStartTime(start_time)
        if duration is not None:
            self.setDuration(duration)
        elif end_time is not None:
            self.setEndTime(end_time)

    def _generate_or_keep_id(self, value: str | None) -> str:
        if value is None:
            return str(uuid4())
        return value

    def __eq__(self, other):
        if not isinstance(other, MiniSchedule):
            return NotImplemented
        return (
            self._id == other._id
            and self._description == other._description
            and self._start_time == other._start_time
            and self._end_time == other._end_time
            and self._duration == other._duration
        )

    def setId(self, id: str | None):
        self._id = self._generate_or_keep_id(id)

    def getId(self) -> str:
        return self._id

    def setDescription(self, description: str | None):
        self._description = description

    def getDescription(self) -> str | None:
        return self._description

    def _to_timedelta(self, duration: int | timedelta) -> timedelta:
        if isinstance(duration, timedelta):
            return duration
        return timedelta(seconds=duration)

    def setStartTime(self, start_time: datetime):
        self._start_time = _to_utc(start_time)
        if self._duration is not None:
            self._end_time = self._start_time + self._duration

    def getStartTime(self) -> datetime | None:
        return self._start_time

    def setEndTime(self, end_time: datetime):
        self._end_time = _to_utc(end_time)
        if self._start_time is not None:
            self._duration = self._end_time - self._start_time

    def getEndTime(self) -> datetime | None:
        return self._end_time

    def setDuration(self, duration: int | timedelta):
        self._duration = self._to_timedelta(duration)
        if self._start_time is not None:
            self._end_time = self._start_time + self._duration

    def getDuration(self) -> timedelta | None:
        return self._duration

    def isProcessed(self) -> bool:
        return self._processed

    def setProcessed(self):
        self._processed = True

    def isNotified(self) -> bool:
        return self._notified

    def setNotified(self):
        self._notified = True
