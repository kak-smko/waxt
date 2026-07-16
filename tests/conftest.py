"""Shared fixtures, constants and helpers for the ``waxt`` test suite.

The suite covers both calendar converters implemented in
``waxt.calendar_converters``:

* ``JalaliCalendar`` (Jalali/Persian <-> Gregorian) - the ``test_jalali_*``
  modules.
* ``HijriCalendar`` (Hijri/Islamic <-> Gregorian) - the ``test_hijri_*``
  modules, which received the same exhaustive treatment (known cases, leap
  years, boundaries, invalid inputs, round trips, property-based and random
  tests, full-range sweeps, performance benchmarks and cross-library
  comparison).
"""

from __future__ import annotations

import datetime
import random
from typing import Iterator, Tuple, Type

import pytest

from waxt.calendar_converters import HijriCalendar, JalaliCalendar

try:
    from hypothesis import HealthCheck, settings

    settings.register_profile(
        "waxt",
        deadline=None,
        suppress_health_check=[HealthCheck.too_slow, HealthCheck.data_too_large],
    )
    settings.load_profile("waxt")
except ImportError:  # pragma: no cover - hypothesis is a test-only dependency
    pass


# ---------------------------------------------------------------------------
# Domain constants - Jalali
# ---------------------------------------------------------------------------

#: The full Gregorian range that the test suite is required to exercise
#: (requirement #10): every single day between these two dates (inclusive)
#: must round-trip correctly through ``JalaliCalendar``.
FULL_RANGE_START = datetime.date(1600, 1, 1)
FULL_RANGE_END = datetime.date(2500, 12, 31)

#: The corresponding Jalali year span for ``FULL_RANGE_START``/``FULL_RANGE_END``.
FULL_RANGE_JALALI_YEAR_START = 979
FULL_RANGE_JALALI_YEAR_END = 1879

#: Windows (Gregorian dates, inclusive on both ends) where ``JalaliCalendar``
#: and the third-party ``jdatetime`` package disagree about whether a given
#: Jalali year is a leap year.
#:
#: Both libraries implement the same *family* of algorithm: an approximation
#: of the Persian calendar's ~2820-year leap cycle using a table of
#: 33-year-ish "break points" (the algorithm popularised by Kazimierz
#: Borkowski and used by ``jalaali-js``). ``waxt`` and ``jdatetime`` however
#: use slightly different break-point tables, which produces a well-defined,
#: reproducible one-day disagreement for a handful of Jalali years, always
#: starting exactly at Nowruz and always resolved again by the *next*
#: Nowruz. This was discovered empirically while building this test suite
#: (see ``tests/test_jalali_cross_library.py`` for the full write-up and a
#: regression test that pins these exact windows down).
KNOWN_JDATETIME_DIVERGENCE_WINDOWS: Tuple[Tuple[datetime.date, datetime.date], ...] = (
    (datetime.date(1600, 3, 20), datetime.date(1601, 3, 20)),
    (datetime.date(1633, 3, 20), datetime.date(1634, 3, 20)),
    (datetime.date(1666, 3, 20), datetime.date(1667, 3, 20)),
    (datetime.date(1699, 3, 20), datetime.date(1700, 3, 20)),
    (datetime.date(1798, 3, 20), datetime.date(1799, 3, 20)),
    (datetime.date(2256, 3, 20), datetime.date(2257, 3, 20)),
    (datetime.date(2289, 3, 20), datetime.date(2290, 3, 20)),
    (datetime.date(2322, 3, 21), datetime.date(2323, 3, 21)),
    (datetime.date(2355, 3, 21), datetime.date(2356, 3, 20)),
    (datetime.date(2388, 3, 20), datetime.date(2389, 3, 20)),
    (datetime.date(2421, 3, 20), datetime.date(2422, 3, 20)),
    (datetime.date(2454, 3, 20), datetime.date(2455, 3, 20)),
    (datetime.date(2487, 3, 20), datetime.date(2488, 3, 19)),
)


def is_in_known_divergence_window(day: datetime.date) -> bool:
    """Return True if ``day`` falls inside a known waxt/jdatetime divergence window."""
    return any(start <= day <= end for start, end in KNOWN_JDATETIME_DIVERGENCE_WINDOWS)


# ---------------------------------------------------------------------------
# Domain constants - Hijri
# ---------------------------------------------------------------------------
#
# ``HijriCalendar`` implements a *tabular / arithmetic* Islamic calendar
# (not the observation-based Umm al-Qura calendar):
#
# * Epoch: Hijri 1-1-1 == Gregorian 622-07-19 (proleptic), i.e. Julian Day
#   Number 1948440 - the well-known "civil" tabular-calendar epoch.
# * Leap rule: ``(11 * year + 25) % 30 < 11``, i.e. 11 leap (355-day) years
#   per 30-year cycle, with Dhu al-Hijjah growing from 29 to 30 days in a
#   leap year.
#
# ``HijriCalendar`` has no explicit min/max year constant of its own,
# either. Its practical range is instead bounded by delegating to
# ``datetime.date`` (Python's proleptic Gregorian calendar, years 1-9999)
# inside ``hijri_to_gregorian``. See ``test_hijri_support_boundaries.py``
# for the exact, empirically-derived edges of that range.

#: The full Gregorian range that the test suite is required to exercise for
#: Hijri as well (mirrors ``FULL_RANGE_START``/``FULL_RANGE_END`` above, so
#: both calendars are validated over the exact same Gregorian window).
FULL_RANGE_HIJRI_YEAR_START = 1008
FULL_RANGE_HIJRI_YEAR_END = 1937

#: Sanity-checked at suite-authoring time:
#:   HijriCalendar.gregorian_to_hijri(1600, 1, 1)   == (1008, 6, 13)
#:   HijriCalendar.gregorian_to_hijri(2500, 12, 31)  == (1937, 2, 8)
#: The year bounds above are deliberately widened by exactly one full
#: Hijri year on each end (1008 down from 1009, 1937 kept) so that every
#: Gregorian day in ``FULL_RANGE_START``..``FULL_RANGE_END`` is covered by
#: at least one full corresponding Hijri year of coverage.


def daterange(start: datetime.date, end: datetime.date) -> Iterator[datetime.date]:
    """Yield every ``datetime.date`` from ``start`` to ``end``, inclusive."""
    current = start
    one_day = datetime.timedelta(days=1)
    while current <= end:
        yield current
        current += one_day


def hijri_days_in_month(h_year: int, h_month: int) -> int:
    """Number of days in a given Hijri month, per ``HijriCalendar``'s rules."""
    if h_month % 2 == 1:
        return 30
    if h_month == 12 and HijriCalendar.is_leap(h_year):
        return 30
    return 29


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture(scope="session")
def jalali() -> Type[JalaliCalendar]:
    """The class under test. All of its public methods are static."""
    return JalaliCalendar


@pytest.fixture(scope="session")
def hijri() -> Type[HijriCalendar]:
    """The class under test. All of its public methods are static."""
    return HijriCalendar


@pytest.fixture(scope="session")
def full_range() -> Tuple[datetime.date, datetime.date]:
    return (FULL_RANGE_START, FULL_RANGE_END)


@pytest.fixture(scope="session")
def hijri_full_range() -> Tuple[datetime.date, datetime.date]:
    return (FULL_RANGE_START, FULL_RANGE_END)


@pytest.fixture
def seeded_random() -> random.Random:
    """A ``random.Random`` instance seeded for fully reproducible test runs."""
    return random.Random(20260715)
