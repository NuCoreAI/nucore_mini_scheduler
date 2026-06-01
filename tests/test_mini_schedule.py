import unittest
from datetime import datetime, timedelta, timezone

from nucore_mini_scheduler import MiniSchedule, MiniScheduler


class TestMiniSchedule(unittest.TestCase):
    def test_duration_calculates_end(self):
        start = datetime(2026, 1, 1, 10, 0, tzinfo=timezone.utc)
        schedule = MiniSchedule(start_time=start, duration=120)
        self.assertEqual(schedule.getEndTime(), start + timedelta(seconds=120))

    def test_non_utc_time_is_converted_to_utc(self):
        est = timezone(timedelta(hours=-5))
        start_local = datetime(2026, 1, 1, 10, 0, tzinfo=est)
        end_local = datetime(2026, 1, 1, 11, 0, tzinfo=est)
        schedule = MiniSchedule(start_time=start_local, end_time=end_local)
        self.assertEqual(schedule.getStartTime(), datetime(2026, 1, 1, 15, 0, tzinfo=timezone.utc))
        self.assertEqual(schedule.getEndTime(), datetime(2026, 1, 1, 16, 0, tzinfo=timezone.utc))


class TestMiniScheduler(unittest.TestCase):
    def test_build_schedule_groups_start_and_end_points(self):
        base = datetime(2026, 1, 1, 0, 0, tzinfo=timezone.utc)
        s1 = MiniSchedule(start_time=base, duration=60)
        s2 = MiniSchedule(start_time=base, duration=120)
        scheduler = MiniScheduler()
        points = scheduler._build_schedule([s1, s2])
        self.assertEqual(len(points), 3)
        self.assertEqual(len(points[0].starting), 2)
        self.assertEqual(len(points[1].ending), 1)
        self.assertEqual(len(points[2].ending), 1)

    def test_remove_future_callback_removes_matching_callback(self):
        scheduler = MiniScheduler()

        def cb1(_):
            return None

        def cb2(_):
            return None

        scheduler.registerFutureCallback(cb1, 5)
        scheduler.registerFutureCallback(cb2, 10)
        scheduler.removeFutureCallback(cb1)
        self.assertEqual(len(scheduler.future_callbacks), 1)
        self.assertIs(scheduler.future_callbacks[0].callback, cb2)


if __name__ == "__main__":
    unittest.main()
