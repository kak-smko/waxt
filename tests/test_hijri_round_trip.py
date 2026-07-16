"""Targeted round-trip tests for ``HijriCalendar`` (requirement #8: Hijri
<-> Gregorian round trips).

These complement (but do not duplicate) the exhaustive sweep in
``test_hijri_full_range_sweep.py`` and the large random samples in
``test_hijri_random_dates.py``: this module checks round-trip identity for
specific, deliberately chosen "interesting" dates (month/year boundaries,
extremes of the required range, etc.) using small, fast-running
parametrized cases.
"""

from __future__ import annotations

import calendar
import datetime

import pytest

from tests.conftest import (
    FULL_RANGE_END,
    FULL_RANGE_HIJRI_YEAR_END,
    FULL_RANGE_HIJRI_YEAR_START,
    FULL_RANGE_START,
    daterange,
    hijri_days_in_month,
)
from waxt.calendar_converters import HijriCalendar

INTERESTING_GREGORIAN_DATES = [
    (1600, 1, 1),
    (1600, 12, 31),
    (1700, 2, 28),
    (1800, 6, 15),
    (1900, 2, 28),
    (2000, 2, 29),
    (2024, 2, 29),
    (2024, 3, 20),
    (2100, 2, 28),
    (2400, 2, 29),
    (2500, 12, 31),
]


@pytest.mark.parametrize("g_year, g_month, g_day", INTERESTING_GREGORIAN_DATES)
def test_gregorian_to_hijri_to_gregorian_round_trip(g_year, g_month, g_day):
    h = HijriCalendar.gregorian_to_hijri(g_year, g_month, g_day)
    assert HijriCalendar.hijri_to_gregorian(*h) == (g_year, g_month, g_day)


INTERESTING_HIJRI_DATES = [
    (1, 1, 1),
    (1, 12, 30),
    (2, 12, 29),
    (10, 6, 29),
    (500, 7, 30),
    (1000, 1, 1),
    (1400, 12, 30),
    (1445, 9, 1),
    (1446, 12, 30),
    (1937, 2, 8),
]


@pytest.mark.parametrize("h_year, h_month, h_day", INTERESTING_HIJRI_DATES)
def test_hijri_to_gregorian_to_hijri_round_trip(h_year, h_month, h_day):
    g = HijriCalendar.hijri_to_gregorian(h_year, h_month, h_day)
    assert HijriCalendar.gregorian_to_hijri(*g) == (h_year, h_month, h_day)


@pytest.mark.parametrize(
    "year",
    [1600, 1601, 1700, 1800, 1900, 1999, 2000, 2024, 2100, 2400, 2499, 2500],
)
def test_every_gregorian_month_boundary_round_trips_for_year(year):
    for month in range(1, 13):
        _, days_in_month = calendar.monthrange(year, month)
        for day in (1, days_in_month):
            h = HijriCalendar.gregorian_to_hijri(year, month, day)
            assert HijriCalendar.hijri_to_gregorian(*h) == (year, month, day)


@pytest.mark.parametrize(
    "year",
    [1, 2, 10, 100, 500, 1000, 1300, 1400, 1445, 1446, 1447, 1500],
)
def test_every_hijri_month_boundary_round_trips_for_year(year):
    for month in range(1, 13):
        for day in (1, hijri_days_in_month(year, month)):
            g = HijriCalendar.hijri_to_gregorian(year, month, day)
            assert HijriCalendar.gregorian_to_hijri(*g) == (year, month, day)


def test_strided_full_range_round_trip_smoke():
    """A fast (~2200-sample) stride over the entire required range, as a
    quick smoke test independent of the heavier exhaustive sweep."""
    checked = 0
    for day in daterange(FULL_RANGE_START, FULL_RANGE_END):
        if day.toordinal() % 151 != 0:
            continue
        h = HijriCalendar.gregorian_to_hijri(day.year, day.month, day.day)
        assert HijriCalendar.hijri_to_gregorian(*h) == (day.year, day.month, day.day)
        checked += 1
    assert checked > 2000


def test_strided_full_hijri_range_round_trip_smoke():
    """The Hijri-side equivalent: stride over every Hijri year in the
    required range, checking the first day of every month."""
    checked = 0
    for year in range(FULL_RANGE_HIJRI_YEAR_START, FULL_RANGE_HIJRI_YEAR_END + 1, 3):
        for month in range(1, 13):
            g = HijriCalendar.hijri_to_gregorian(year, month, 1)
            h_back = HijriCalendar.gregorian_to_hijri(*g)
            assert h_back == (year, month, 1), ((year, month, 1), g, h_back)
            checked += 1
    assert checked > 3000
