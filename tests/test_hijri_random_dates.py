"""Random-date round-trip tests for ``HijriCalendar`` (requirement #10:
>= 10,000 random dates).

Uses a seeded ``random.Random`` for full reproducibility (a failure will
always point at the exact same date, run after run) while still exercising
more than 10,000 dates per direction, as required.
"""

from __future__ import annotations

import datetime

from tests.conftest import (
    FULL_RANGE_HIJRI_YEAR_END,
    FULL_RANGE_HIJRI_YEAR_START,
    hijri_days_in_month,
)
from waxt.calendar_converters import HijriCalendar

SAMPLE_SIZE = 12_000


def _random_gregorian_dates(rng, count, start, end):
    span = (end - start).days
    for _ in range(count):
        offset = rng.randint(0, span)
        yield start + datetime.timedelta(days=offset)


def test_random_gregorian_dates_round_trip(seeded_random):
    start = datetime.date(1600, 1, 1)
    end = datetime.date(2500, 12, 31)

    checked = 0
    for day in _random_gregorian_dates(seeded_random, SAMPLE_SIZE, start, end):
        h = HijriCalendar.gregorian_to_hijri(day.year, day.month, day.day)
        g_back = HijriCalendar.hijri_to_gregorian(*h)
        assert g_back == (day.year, day.month, day.day), (day, h, g_back)
        checked += 1

    assert checked == SAMPLE_SIZE


def _random_valid_hijri_date(rng):
    year = rng.randint(FULL_RANGE_HIJRI_YEAR_START, FULL_RANGE_HIJRI_YEAR_END)
    month = rng.randint(1, 12)
    max_day = hijri_days_in_month(year, month)
    day = rng.randint(1, max_day)
    return (year, month, day)


def test_random_hijri_dates_round_trip(seeded_random):
    checked = 0
    for _ in range(SAMPLE_SIZE):
        h = _random_valid_hijri_date(seeded_random)
        g = HijriCalendar.hijri_to_gregorian(*h)
        h_back = HijriCalendar.gregorian_to_hijri(*g)
        assert h_back == h, (h, g, h_back)
        checked += 1

    assert checked == SAMPLE_SIZE


def test_random_gregorian_dates_produce_valid_hijri_components(seeded_random):
    """Every random Gregorian date in range must decompose into a
    structurally valid Hijri date (month in 1-12, day within the correct
    bound for that month/leap status)."""
    start = datetime.date(1600, 1, 1)
    end = datetime.date(2500, 12, 31)

    for day in _random_gregorian_dates(seeded_random, SAMPLE_SIZE, start, end):
        h_year, h_month, h_day = HijriCalendar.gregorian_to_hijri(
            day.year, day.month, day.day
        )
        assert 1 <= h_month <= 12
        assert 1 <= h_day <= hijri_days_in_month(h_year, h_month)


def test_random_hijri_dates_produce_strictly_ordered_gregorian_dates(seeded_random):
    """Two distinct, randomly chosen Hijri dates must never map to the
    same Gregorian date, and their relative order must be preserved."""
    dates = sorted({_random_valid_hijri_date(seeded_random) for _ in range(2000)})
    gregorian_dates = [HijriCalendar.hijri_to_gregorian(*h) for h in dates]
    assert gregorian_dates == sorted(gregorian_dates)
    assert len(set(gregorian_dates)) == len(gregorian_dates)
