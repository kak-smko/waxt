"""Exhaustive full-range sweep for ``HijriCalendar`` (requirement #11:
full supported year range).

Walks *every single day* from 1600-01-01 to 2500-12-31 (~329,000 days) and
also every single Hijri calendar day across the equivalent Hijri year span
(AH 1008-1937, ~329,000 days too, since a Hijri year is ~354/355 days),
checking full round-trip identity in both directions.

Marked ``slow`` (it takes a couple of seconds) so it can be excluded from
quick local runs with ``pytest -m "not slow"``, while still running by
default and in CI.
"""

from __future__ import annotations

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

pytestmark = pytest.mark.slow


def test_every_gregorian_day_in_required_range_round_trips():
    count = 0
    for day in daterange(FULL_RANGE_START, FULL_RANGE_END):
        h = HijriCalendar.gregorian_to_hijri(day.year, day.month, day.day)
        g_back = HijriCalendar.hijri_to_gregorian(*h)
        assert g_back == (day.year, day.month, day.day), (day, h, g_back)
        count += 1

    expected = (FULL_RANGE_END - FULL_RANGE_START).days + 1
    assert count == expected


def test_every_hijri_day_in_required_range_round_trips():
    count = 0
    for year in range(FULL_RANGE_HIJRI_YEAR_START, FULL_RANGE_HIJRI_YEAR_END + 1):
        for month in range(1, 13):
            max_day = hijri_days_in_month(year, month)
            for day in range(1, max_day + 1):
                g = HijriCalendar.hijri_to_gregorian(year, month, day)
                h_back = HijriCalendar.gregorian_to_hijri(*g)
                assert h_back == (year, month, day), ((year, month, day), g, h_back)
                count += 1

    assert count > 300_000


def test_full_range_days_are_strictly_sequential():
    """Consecutive Gregorian days must map to strictly increasing Hijri
    tuples (no gaps, no repeats, no reordering) across the whole range."""
    previous = None
    for day in daterange(FULL_RANGE_START, FULL_RANGE_END):
        current = HijriCalendar.gregorian_to_hijri(day.year, day.month, day.day)
        if previous is not None:
            assert current > previous, (day, previous, current)
        previous = current


def test_full_hijri_range_days_are_strictly_sequential():
    """The Hijri-side equivalent: walking every Hijri day in the required
    range in calendar order must produce a strictly increasing sequence of
    Gregorian dates."""
    previous = None
    for year in range(FULL_RANGE_HIJRI_YEAR_START, FULL_RANGE_HIJRI_YEAR_END + 1):
        for month in range(1, 13):
            max_day = hijri_days_in_month(year, month)
            for day in range(1, max_day + 1):
                current = HijriCalendar.hijri_to_gregorian(year, month, day)
                if previous is not None:
                    assert current > previous, ((year, month, day), previous, current)
                previous = current
