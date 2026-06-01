# nucore_mini_scheduler
Mini Scheduler that fires events to callback listeners. It uses start/end times and walks through a sorted list.

## Main objects

- `MiniSchedule`: schedule segment with UTC start/end and optional duration (seconds or `timedelta`). If duration is provided, end time is calculated from start + duration.
- `MiniScheduler`: thread-based scheduler that processes `MiniSchedule` series and notifies registered callbacks for start/end/future events.
