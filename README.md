# Waxt

[![PyPI version](https://img.shields.io/pypi/v/waxt.svg)](https://pypi.org/project/waxt/)
[![Python versions](https://img.shields.io/pypi/pyversions/waxt.svg)](https://pypi.org/project/waxt/)
[![License](https://img.shields.io/badge/license-BSD--3--Clause-blue.svg)](LICENSE)
[![Code style: Black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Typed](https://img.shields.io/badge/typing-typed-blue.svg)](https://mypy-lang.org/)

**Waxt** is a dependency-free Python library for working with Gregorian, Jalali
(Persian/Solar), and civil Hijri (Islamic/tabular) dates through one immutable,
`datetime`-like API.

```python
from waxt import DateTime

jalali = DateTime(1404, 3, 25, 14, 30, calendar="jalali")

jalali.to_datetime()                 # datetime.datetime(2025, 6, 15, 14, 30)
jalali.to_calendar("hijri")          # same value, displayed as a Hijri date
jalali.strftime("%d %B %Y, %H:%M")  # "25 Khordad 1404, 14:30"
```

- Familiar API modeled on `datetime.datetime`
- Calendar conversion without changing the represented value
- Calendar-aware parsing, formatting, and month arithmetic
- Standard `tzinfo` and `zoneinfo` interoperability
- Full type hints and no third-party runtime dependencies

## Installation

```bash
python -m pip install waxt
```

Waxt requires Python 3.10 or newer.

## Quick start

### Create and convert dates

The `calendar` argument controls how the constructor interprets `year`, `month`,
and `day`. It accepts `"gregorian"` (the default), `"jalali"`, or `"hijri"`.

```python
from waxt import DateTime

jalali = DateTime(1404, 3, 25, 14, 30, calendar="jalali")
gregorian = jalali.to_calendar("gregorian")
hijri = jalali.to_calendar("hijri")

(jalali.year, jalali.month, jalali.day)        # (1404, 3, 25)
(gregorian.year, gregorian.month, gregorian.day)  # (2025, 6, 15)
jalali == gregorian == hijri                   # True
```

`to_calendar()` changes the calendar representation only. It does not change
the underlying wall time, timezone, or represented instant.

### Interoperate with the standard library

```python
from datetime import datetime
from waxt import DateTime

standard = datetime(2025, 6, 15, 14, 30)
jalali = DateTime.from_datetime(standard, calendar="jalali")

jalali.isoformat()   # "1404-03-25T14:30:00"
jalali.to_datetime() # datetime.datetime(2025, 6, 15, 14, 30)
```

`to_datetime()` always returns the equivalent Gregorian
`datetime.datetime`. Waxt values can also be compared with standard-library
`datetime` values when Python's usual naive/aware comparison rules permit it.

### Get the current date and time

```python
from datetime import timezone
from zoneinfo import ZoneInfo
from waxt import DateTime

tehran_now = DateTime.now(ZoneInfo("Asia/Tehran"), calendar="jalali")
utc_now = DateTime.now(timezone.utc, calendar="gregorian")
today = DateTime.today(calendar="hijri")
```

### Parse and format

```python
from waxt import DateTime

value = DateTime.strptime(
    "1404-03-25 14:30 +0330",
    "%Y-%m-%d %H:%M %z",
    calendar="jalali",
)

value.strftime("%Y/%m/%d %H:%M") # "1404/03/25 14:30"
value.strftime("%d %B %Y")       # "25 Khordad 1404"
value.isoformat(timespec="minutes") # "1404-03-25T14:30+03:30"
```

For Jalali and Hijri values, calendar-aware formatting includes `%Y`, `%y`,
`%m`, `%d`, `%j`, `%b`, and `%B`. Other directives, including time and timezone
directives, follow the standard library's `strftime()` behavior.

### Perform date arithmetic

```python
from datetime import timedelta
from waxt import DateTime

value = DateTime(1404, 6, 31, calendar="jalali")

value + timedelta(days=1) # 1404-07-01
value.add_days(1)         # 1404-07-01
value.add_months(1)       # 1404-07-30 (clamped to the target month)
```

`timedelta` arithmetic operates on the underlying Gregorian datetime and keeps
the selected calendar for the result. `add_months()` advances calendar months
and clamps the day when the target month is shorter.

### Work with timezones

Waxt accepts any standard `tzinfo` implementation, including
`zoneinfo.ZoneInfo`. Its country-based `tzinfo()` helper also uses IANA rules,
including daylight-saving and historical changes.

```python
from datetime import timezone
from zoneinfo import ZoneInfo
from waxt import DateTime

utc_value = DateTime(2025, 6, 15, 10, tzinfo=timezone.utc)
tehran_value = utc_value.astimezone(ZoneInfo("Asia/Tehran"))

tehran_value.to_datetime().isoformat() # "2025-06-15T13:30:00+03:30"
```

Waxt also bundles basic metadata for ISO 3166-1 alpha-2 country codes:

```python
from waxt import country, tzinfo

iran = country("IR")
iran.name       # "Iran, Islamic Republic of"
iran.timezone   # "Asia/Tehran"
iran.calendar   # "persian"
iran.rtl        # True

tehran = tzinfo("IR")
tehran.utcoffset(None) # datetime.timedelta(seconds=12600)
```

The object returned by Waxt's `tzinfo()` helper applies daylight-saving
transitions and historical offset changes from the representative IANA timezone
listed for the country. For countries spanning multiple timezones, use
`ZoneInfo` directly to select a more specific zone.

## Important calendar semantics

Waxt stores every value internally as a Gregorian `datetime`, while the
`calendar` property controls the exposed date fields and calendar-aware output.
As a result:

- `year`, `month`, `day`, `isoformat()`, and calendar-aware `strftime()` output
  use the selected calendar.
- `to_datetime()` and `date()` return standard-library Gregorian values.
- POSIX timestamps, ordinals, ISO week dates, timezone behavior, and comparisons
  retain standard Python semantics.
- Hijri conversion uses the arithmetic civil/tabular calendar. It may differ
  from observational, regional, or Umm al-Qura calendars by one or more days.

## API overview

`DateTime` is available from `waxt` and `waxt.datetime`. A lowercase `datetime`
alias is also available from `waxt.datetime`.

| API | Purpose |
|---|---|
| `DateTime(...)` | Construct a value using Gregorian, Jalali, or Hijri fields |
| `now()`, `today()` | Create the current local value in a selected calendar |
| `from_datetime()`, `to_datetime()` | Convert to and from `datetime.datetime` |
| `fromisoformat()`, `strptime()` | Parse calendar date fields |
| `to_calendar()` | Return the same value in another calendar representation |
| `isoformat()`, `strftime()` | Format using the selected calendar |
| `astimezone()` | Convert an aware value to another timezone |
| `add_days()`, `add_months()` | Apply calendar-preserving arithmetic |
| `replace()` | Return a value with selected fields changed |
| `country()` | Look up bundled country metadata |
| `tzinfo()` | Return a country timezone with IANA transition rules |

Calendar constants are available as `DateTime.CALENDAR_GREGORIAN`,
`DateTime.CALENDAR_JALALI`, and `DateTime.CALENDAR_HIJRI`.

## Development

Clone the repository and install the development and test dependencies:

```bash
git clone https://github.com/kak-smko/waxt.git
cd waxt
python -m venv .venv
source .venv/bin/activate
python -m pip install -e ".[dev,test]"
```

Run the test suite:

```bash
pytest
```

Run formatting, linting, and type checks:

```bash
black --check waxt tests
isort --check-only waxt tests
flake8 waxt tests
mypy waxt
```

## Contributing

Bug reports and pull requests are welcome on
[GitHub](https://github.com/kak-smko/waxt). When changing behavior, include or
update tests that cover the affected calendar and boundary cases.

## License

Waxt is distributed under the [BSD 3-Clause License](LICENSE).
