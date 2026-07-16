"""Exhaustive full-range sweep (requirement #10).

Walks *every single day* from 1600-01-01 to 2500-12-31 (~329,000 days) and
also every single Jalali calendar day across the equivalent Jalali year
span, checking full round-trip identity in both directions.

Marked ``slow`` (it takes a few seconds) so it can be excluded from quick
local runs with ``pytest -m "not slow"``, while still running by default
and in CI.
"""

from __future__ import annotations

import datetime

import pytest

from tests.conftest import (
    FULL_RANGE_END,
    FULL_RANGE_JALALI_YEAR_END,
    FULL_RANGE_JALALI_YEAR_START,
    FULL_RANGE_START,
    daterange,
)
from waxt.calendar_converters import JalaliCalendar

pytestmark = pytest.mark.slow


def test_every_gregorian_day_in_required_range_round_trips():
    count = 0
    for day in daterange(FULL_RANGE_START, FULL_RANGE_END):
        j = JalaliCalendar.gregorian_to_jalali(day.year, day.month, day.day)
        g_back = JalaliCalendar.jalali_to_gregorian(*j)
        assert g_back == (day.year, day.month, day.day), (day, j, g_back)
        count += 1

    expected = (FULL_RANGE_END - FULL_RANGE_START).days + 1
    assert count == expected


def test_every_jalali_day_in_required_range_round_trips():
    count = 0
    for year in range(FULL_RANGE_JALALI_YEAR_START, FULL_RANGE_JALALI_YEAR_END + 1):
        for month in range(1, 13):
            if month <= 6:
                max_day = 31
            elif month <= 11:
                max_day = 30
            else:
                max_day = 30 if JalaliCalendar.is_leap(year) else 29

            for day in range(1, max_day + 1):
                g = JalaliCalendar.jalali_to_gregorian(year, month, day)
                j_back = JalaliCalendar.gregorian_to_jalali(*g)
                assert j_back == (year, month, day), ((year, month, day), g, j_back)
                count += 1

    assert count > 300_000


def test_full_range_days_are_strictly_sequential():
    """Consecutive Gregorian days must map to strictly increasing Jalali
    tuples (no gaps, no repeats, no reordering) across the whole range."""
    previous = None
    for day in daterange(FULL_RANGE_START, FULL_RANGE_END):
        current = JalaliCalendar.gregorian_to_jalali(day.year, day.month, day.day)
        if previous is not None:
            assert current > previous, (day, previous, current)
        previous = current
