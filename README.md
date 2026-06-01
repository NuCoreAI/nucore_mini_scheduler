# nucore_mini_scheduler

Mini Scheduler that fires events to callback listeners. It uses start/end times and walks through a sorted timeline.

## Installation

```bash
# local editable install
pip install -e .

# once published on PyPI
pip install nucore-mini-scheduler
```

## Quick start

```python
from datetime import datetime, timedelta, timezone

from nucore_mini_scheduler import MiniSchedule, MiniScheduler


def on_event(segment: MiniSchedule):
		print(
				"event",
				segment.getId(),
				segment.getDescription(),
				segment.getStartTime(),
				segment.getEndTime(),
				"processed=", segment.isProcessed(),
		)


scheduler = MiniScheduler()
scheduler.registerCallback(on_event)

start = datetime.now(timezone.utc) + timedelta(seconds=3)
segment = MiniSchedule(
		id=None,  # auto-generated
		description="demo segment",
		start_time=start,
		duration=10,
)

scheduler.setTimeSeries([segment])
```

## MiniSchedule

Represents one schedulable segment.

- `id` is always non-null.
- If `id=None`, a UUID string is generated.
- `description` is optional and may be `None`.
- Datetimes are normalized to UTC.

### Constructor

```python
MiniSchedule(
		start_time: datetime | None = None,
		end_time: datetime | None = None,
		duration: int | timedelta | None = None,
		id: str | None = None,
		description: str | None = None,
)
```

### Time rules

- If `duration` is provided with `start_time`, then `end_time = start_time + duration`.
- If `end_time` is provided with `start_time`, then `duration = end_time - start_time`.
- Naive datetimes are treated as local time, then converted to UTC.

### Equality behavior

`MiniSchedule` uses value-based equality (`__eq__`). Two segments are equal if all of the following match:

- `id`
- `description`
- `start_time`
- `end_time`
- `duration`

This is used by `MiniScheduler.setTimeSeries(...)` to ignore a new list when its content is equal to the current time series.

## MiniScheduler

Thread-based scheduler that consumes a list of `MiniSchedule` and emits callbacks.

### Callbacks

- `registerCallback(callback)`:
	callback is invoked around start/end transitions.
- `registerFutureCallback(callback, duration_seconds)`:
	callback is invoked for segments that begin within the look-ahead window.

### Core methods

- `setTimeSeries(ts: list[MiniSchedule])`:
	starts the worker thread when needed, stops current run, swaps series, then starts scheduling.
	If `ts` is equal in value to the current list, it is ignored.
- `stop()`:
	requests scheduler stop and clears current time-series state.

## Public exports

- `MiniSchedule`
- `MiniScheduler`
- `FutureCallback`
- `SchedulePoint`
- `SchedulerControl`

## Build and publish to PyPI

1. Build distribution artifacts:

```bash
python3 -m pip install --upgrade build twine
python3 -m build
```

2. Validate artifacts:

```bash
python3 -m twine check dist/*
```

3. Upload to TestPyPI first (recommended):

```bash
python3 -m twine upload --repository testpypi dist/*
```

4. Upload to PyPI:

```bash
python3 -m twine upload dist/*
```

5. Install from PyPI:

```bash
pip install nucore-mini-scheduler
```
