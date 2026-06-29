# 🗓️ Waxt

[![PyPI version](https://img.shields.io/pypi/v/waxt.svg)](https://pypi.org/project/waxt/)
[![Python Versions](https://img.shields.io/pypi/pyversions/waxt.svg)](https://pypi.org/project/waxt/)
[![License](https://img.shields.io/badge/license-BSD--3--Clause-blue.svg)](https://opensource.org/licenses/BSD-3-Clause)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Typed](https://img.shields.io/badge/typing-fully%20typed-blue)](https://mypy-lang.org/)

A modern Python library for converting dates between **Jalali (Persian/Solar)**, **Hijri (Islamic/Lunar)**, and **Gregorian** calendars with full timezone support.

---

## 📦 Installation

```bash
pip install waxt
```

Requires Python 3.10+ and `pytz`.

---

## ✨ Features

| Feature | Description |
|---|---|
| 🔄 **Multi-Calendar** | Jalali (Persian/Solar), Hijri (Islamic/Lunar), Gregorian |
| 🌍 **Timezone Aware** | Full `pytz` timezone support — convert, localize, compare |
| 📅 **Date Arithmetic** | Add days/months with calendar-aware month lengths and leap years |
| 🎨 **Flexible Formatting** | Custom format strings (`%Y`, `%m`, `%d`, `%H`, `%M`, `%S`) |
| 📝 **Parsing** | Parse date strings back to `datetime` from any calendar |
| 🌐 **Localized Month Names** | Persian (`fa`), Arabic (`ar`), English (`en`) |
| 🧪 **Well Tested** | Comprehensive test suite with round-trip integrity checks |
| 🎯 **Type Hints** | Fully typed for great IDE support |
| 🪶 **Lightweight** | Only dependency: `pytz` |

---

## 🚀 Quick Start

### Create a DateService

`DateService` is the main entry point. Configure it with a timezone and calendar type.

```python
from waxt.date_service import DateService

# Jalali (Persian) calendar in Tehran
svc = DateService(timezone="Asia/Tehran", calendar="jalali")

# Hijri (Islamic) calendar in Riyadh
svc = DateService(timezone="Asia/Riyadh", calendar="hijri")

# Gregorian calendar in UTC (default-like)
svc = DateService(timezone="UTC", calendar="gregorian")
```

Calendar options: `"jalali"`, `"hijri"`, `"gregorian"`.

---

### Current Date & Time

```python
svc = DateService(timezone="Asia/Tehran", calendar="jalali")

now = svc.now()                     # current datetime in Tehran
now_utc = svc.now_utc()            # current datetime in UTC
```

---

### Get Date Components (Year, Month, Day)

Returns components in the configured calendar:

```python
from datetime import datetime

svc = DateService(timezone="Asia/Tehran", calendar="jalali")

dt = datetime(2025, 6, 15)
year, month, day = svc.get_date_components(dt)
# (1404, 3, 25) — Jalali equivalent
```

---

### Format Dates

```python
svc = DateService(timezone="Asia/Tehran", calendar="jalali")
dt = datetime(2025, 6, 15, 14, 30, 0)

# Default format: YYYY/MM/DD
svc.format_date(dt)                        # "1404/03/25"

# With time
svc.format_date(dt, include_time=True)     # "1404/03/25 14:30:00"

# Custom format string
svc.format_date(dt, format_str="%Y-%m-%d") # "1404-03-25"
svc.format_date(dt, format_str="%d/%m/%Y %H:%M")  # "25/03/1404 14:30"
```

Format specifiers: `%Y` (year), `%m` (month), `%d` (day), `%H` (hour), `%M` (minute), `%S` (second).

---

### Parse Date Strings

Parse a date string into a `datetime` object. Input is interpreted in the configured calendar.

```python
svc = DateService(timezone="Asia/Tehran", calendar="jalali")

dt = svc.parse_date("1404/03/25")
# datetime(2025, 6, 15, 0, 0, 0) — Gregorian equivalent

dt = svc.parse_date("1404-03-25 14:30:00")
# datetime(2025, 6, 15, 14, 30, 0)
```

---

### Timezone Conversion

```python
from datetime import datetime
import pytz

svc = DateService(timezone="Asia/Tehran", calendar="gregorian")

utc_dt = datetime(2025, 6, 15, 10, 0, 0, tzinfo=pytz.UTC)

# UTC → Tehran
local_dt = svc.to_company_timezone(utc_dt)
# datetime(2025, 6, 15, 13, 30, 0, tzinfo=...)

# Tehran → UTC
back_to_utc = svc.to_utc(local_dt)
# datetime(2025, 6, 15, 10, 0, 0, tzinfo=UTC)
```

---

### Date Arithmetic

```python
from datetime import datetime

svc = DateService(timezone="UTC", calendar="jalali")
dt = datetime(2025, 6, 15)

# Add days (works on Gregorian datetime)
dt2 = svc.add_days(dt, 10)        # datetime(2025, 6, 25)

# Add months (calendar-aware — respects month lengths and leap years)
dt3 = svc.add_months(dt, 3)       # +3 Jalali months from 1404/03/25

# Negative values work too
svc.add_days(dt, -5)
svc.add_months(dt, -2)
```

---

### Month Names

```python
svc = DateService(timezone="UTC", calendar="jalali")
svc.get_month_name(1, locale="fa")  # "فروردین"
svc.get_month_name(1, locale="en")  # "Farvardin"

svc = DateService(timezone="UTC", calendar="hijri")
svc.get_month_name(1, locale="ar")  # "محرم"
svc.get_month_name(1, locale="en")  # "Muharram"

svc = DateService(timezone="UTC", calendar="gregorian")
svc.get_month_name(1, locale="en")  # "January"
svc.get_month_name(1, locale="fa")  # "ژانویه"
```

---

### Day Boundaries

```python
svc = DateService(timezone="UTC", calendar="gregorian")
dt = datetime(2025, 6, 15, 14, 30, 0)

svc.start_of_day(dt)  # datetime(2025, 6, 15, 0, 0, 0)
svc.end_of_day(dt)    # datetime(2025, 6, 15, 23, 59, 59, 999999)
```

---

### Factory Helper

```python
from waxt.date_service import create_date_service_for_company

# Reads timezone and calendar attributes from a company object
svc = create_date_service_for_company(company)
```

---

## 📚 API Reference

### `DateService(timezone, calendar)`

| Method | Returns | Description |
|---|---|---|
| `now()` | `datetime` | Current time in configured timezone |
| `now_utc()` | `datetime` | Current UTC time |
| `to_company_timezone(utc_dt)` | `datetime` | Convert UTC → local timezone |
| `to_utc(local_dt)` | `datetime` | Convert local → UTC |
| `get_date_components(dt)` | `(year, month, day)` | Extract date parts in configured calendar |
| `format_date(dt, format_str, include_time)` | `str` | Format date with calendar-aware year/month/day |
| `parse_date(date_str, format_str, time_component)` | `datetime` | Parse date string → Gregorian `datetime` |
| `get_month_name(month, locale)` | `str` | Month name in `fa`, `ar`, or `en` |
| `add_days(dt, days)` | `datetime` | Add/subtract days |
| `add_months(dt, months)` | `datetime` | Add/subtract months (calendar-aware) |
| `get_year_month(dt)` | `(year, month)` | Get year+month only |
| `start_of_day(dt)` | `datetime` | Set time to 00:00:00 |
| `end_of_day(dt)` | `datetime` | Set time to 23:59:59.999999 |

### Calendar Constants

| Constant | Value |
|---|---|
| `DateService.CALENDAR_JALALI` | `"jalali"` |
| `DateService.CALENDAR_HIJRI` | `"hijri"` |
| `DateService.CALENDAR_GREGORIAN` | `"gregorian"` |

---

## 🧪 Development

### Setup

```bash
git clone https://github.com/kak-smko/waxt.git
cd waxt
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev,test]"
```

### Run tests

```bash
pytest           # with coverage
pytest -x -v     # stop on first failure, verbose
```

### Lint & type check

```bash
black waxt tests
isort waxt tests
mypy waxt
flake8 waxt tests
```

---

## 📄 License

BSD-3-Clause. See [LICENSE](LICENSE).
