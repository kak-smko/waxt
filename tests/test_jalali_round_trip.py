"""Targeted round-trip tests (requirement #7).

These complement (but do not duplicate) the exhaustive sweep in
``test_jalali_full_range_sweep.py`` and the large random samples in
``test_jalali_random_dates.py``: this module checks round-trip identity
for specific, deliberately chosen "interesting" dates (month/year
boundaries, extremes of the required range, etc.) using small,
fast-running parametrized cases.
"""

from __future__ import annotations

import calendar
import datetime

import pytest

from tests.conftest import FULL_RANGE_END, FULL_RANGE_START, daterange
from waxt.calendar_converters import JalaliCalendar

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
def test_gregorian_to_jalali_to_gregorian_round_trip(g_year, g_month, g_day):
    j = JalaliCalendar.gregorian_to_jalali(g_year, g_month, g_day)
    assert JalaliCalendar.jalali_to_gregorian(*j) == (g_year, g_month, g_day)


INTERESTING_JALALI_DATES = [
    (979, 1, 1),
    (1000, 6, 31),
    (1300, 12, 29),
    (1399, 12, 30),
    (1400, 12, 29),
    (1402, 12, 29),
    (1403, 12, 30),
    (1879, 10, 10),
]


@pytest.mark.parametrize("j_year, j_month, j_day", INTERESTING_JALALI_DATES)
def test_jalali_to_gregorian_to_jalali_round_trip(j_year, j_month, j_day):
    g = JalaliCalendar.jalali_to_gregorian(j_year, j_month, j_day)
    assert JalaliCalendar.gregorian_to_jalali(*g) == (j_year, j_month, j_day)


@pytest.mark.parametrize(
    "year",
    [1600, 1601, 1700, 1800, 1900, 1999, 2000, 2024, 2100, 2400, 2499, 2500],
)
def test_every_month_boundary_round_trips_for_year(year):
    for month in range(1, 13):
        _, days_in_month = calendar.monthrange(year, month)
        for day in (1, days_in_month):
            j = JalaliCalendar.gregorian_to_jalali(year, month, day)
            assert JalaliCalendar.jalali_to_gregorian(*j) == (year, month, day)


def test_strided_full_range_round_trip_smoke():
    """A fast (~2200-sample) stride over the entire required range, as a
    quick smoke test independent of the heavier exhaustive sweep."""
    checked = 0
    for day in daterange(FULL_RANGE_START, FULL_RANGE_END):
        if day.toordinal() % 151 != 0:
            continue
        j = JalaliCalendar.gregorian_to_jalali(day.year, day.month, day.day)
        assert JalaliCalendar.jalali_to_gregorian(*j) == (day.year, day.month, day.day)
        checked += 1
    assert checked > 2000
