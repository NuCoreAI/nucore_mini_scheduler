import threading
import time
from datetime import timedelta

from .datetime_util import get_current_utc_time
from .mini_schedule import MiniSchedule


class FutureCallback:
    def __init__(self, callback: callable, duration: int):
        self.callback = callback
        self.duration = duration


class SchedulePoint:
    def __init__(self, time):
        self.time = time
        self.starting = []
        self.ending = []

    def __repr__(self):
        return (
            f"SchedulePoint({self.time}, "
            f"starts={len(self.starting)}, "
            f"ends={len(self.ending)})"
        )


class SchedulerControl:
    def __init__(self):
        self.stop_event = threading.Event()
        self.start_event = threading.Event()
        self.stopped = True

    def wait_for_stop(self, timeout=None):
        self.stopped = False
        return self.stop_event.wait(timeout=timeout)

    def wait_for_start(self, timeout=None):
        self.stopped = True
        return self.start_event.wait(timeout=timeout)

    def start(self):
        self.stop_event.clear()
        self.start_event.set()

    def stop(self):
        self.stop_event.set()
        time.sleep(0.5)
        self.start_event.clear()

    def is_start_set(self):
        return self.start_event.is_set()

    def is_stop_set(self):
        return self.stop_event.is_set()

    def is_stopped(self):
        return self.stopped


class MiniScheduler(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.timeseries: list[MiniSchedule] | None = None
        self.callbacks = []
        self.future_callbacks = []
        self.scheduler_control = SchedulerControl()
        self.stop()
        self.current_index = 0

    def registerCallback(self, callback):
        self.callbacks.append(callback)

    def removeCallback(self, callback):
        try:
            self.callbacks.remove(callback)
        except Exception:
            pass

    def registerFutureCallback(self, callback, duration: int):
        self.future_callbacks.append(FutureCallback(callback, duration))

    def removeFutureCallback(self, callback):
        try:
            for i in range(len(self.future_callbacks)):
                f_callback = self.future_callbacks[i]
                if f_callback == callback:
                    del self.future_callbacks[i]
        except Exception:
            pass

    def setTimeSeries(self, ts: list[MiniSchedule]):
        if not self.is_alive():
            self.start()
        if self.timeseries == ts:
            return
        while not self.scheduler_control.is_stop_set():
            self.scheduler_control.stop()
        self.timeseries = ts
        self.scheduler_control.start()

    def _build_schedule(self, timeseries: list[MiniSchedule]) -> list[SchedulePoint]:
        points = {}
        for segment in timeseries:
            start = segment.getStartTime()
            end = segment.getEndTime()

            if start not in points:
                points[start] = SchedulePoint(start)
            points[start].starting.append(segment)

            if end not in points:
                points[end] = SchedulePoint(end)
            points[end].ending.append(segment)

        return sorted(points.values(), key=lambda p: p.time)

    def _notify_start_events(self, point: SchedulePoint, check_end: bool):
        try:
            for callback in self.callbacks:
                for segment in (point.ending if check_end else point.starting):
                    if not segment.isProcessed() and not segment.isNotified():
                        callback(segment)
                        segment.setNotified()
        except Exception:
            pass

    def _notify_end_events(self, point: SchedulePoint):
        try:
            for callback in self.callbacks:
                for segment in point.ending:
                    if not segment.isProcessed():
                        segment.setProcessed()
                        callback(segment)
        except Exception:
            pass

    def _notify_future_events(self, schedule: list[SchedulePoint], from_index: int):
        try:
            for f_callback in self.future_callbacks:
                current_time = get_current_utc_time()
                future_time = current_time + timedelta(seconds=f_callback.duration)
                for i in range(from_index, len(schedule)):
                    point = schedule[i]
                    if point.time > future_time:
                        break
                    for segment in point.starting:
                        if not segment.isProcessed():
                            f_callback.callback(segment)
        except Exception:
            pass

    def run(self):
        while True:
            self.scheduler_control.wait_for_start(timeout=1800)
            if self.scheduler_control.is_stop_set():
                continue

            schedule = self._build_schedule(self.timeseries)

            point_index = 0
            now = get_current_utc_time()
            while point_index < len(schedule) and schedule[point_index].time <= now:
                for segment in schedule[point_index].starting:
                    if now > segment.getEndTime():
                        segment.setProcessed()
                point_index += 1

            while point_index < len(schedule) and not self.scheduler_control.is_stop_set():
                point = schedule[point_index]
                current_time = get_current_utc_time()

                time_diff = (point.time - current_time).total_seconds()
                if time_diff > 0:
                    self._notify_start_events(point, True)
                    self._notify_future_events(schedule, point_index)
                    self.scheduler_control.wait_for_stop(timeout=time_diff)
                    if self.scheduler_control.is_stop_set():
                        break

                self._notify_end_events(point)
                self._notify_start_events(point, False)

                point_index += 1

            if not self.scheduler_control.is_stop_set():
                self.scheduler_control.stop()

    def stop(self):
        if self.scheduler_control.is_stopped():
            return
        self.scheduler_control.stop()
        self.timeseries = None
        self.current_index = 0
