"""Random-date round-trip tests (requirement #9).

Uses a seeded ``random.Random`` for full reproducibility (a failure will
always point at the exact same date, run after run) while still exercising
more than 10,000 dates per direction, as required.
"""

from __future__ import annotations

import datetime

import pytest

from tests.conftest import FULL_RANGE_JALALI_YEAR_END, FULL_RANGE_JALALI_YEAR_START
from waxt.calendar_converters import JalaliCalendar

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
        j = JalaliCalendar.gregorian_to_jalali(day.year, day.month, day.day)
        g_back = JalaliCalendar.jalali_to_gregorian(*j)
        assert g_back == (day.year, day.month, day.day), (day, j, g_back)
        checked += 1

    assert checked == SAMPLE_SIZE


def _random_valid_jalali_date(rng):
    year = rng.randint(FULL_RANGE_JALALI_YEAR_START, FULL_RANGE_JALALI_YEAR_END)
    month = rng.randint(1, 12)
    if month <= 6:
        max_day = 31
    elif month <= 11:
        max_day = 30
    else:
        max_day = 30 if JalaliCalendar.is_leap(year) else 29
    day = rng.randint(1, max_day)
    return (year, month, day)


def test_random_jalali_dates_round_trip(seeded_random):
    checked = 0
    for _ in range(SAMPLE_SIZE):
        j = _random_valid_jalali_date(seeded_random)
        g = JalaliCalendar.jalali_to_gregorian(*j)
        j_back = JalaliCalendar.gregorian_to_jalali(*g)
        assert j_back == j, (j, g, j_back)
        checked += 1

    assert checked == SAMPLE_SIZE


def test_random_gregorian_dates_produce_valid_jalali_components(seeded_random):
    """Every random Gregorian date in range must decompose into a
    structurally valid Jalali date (month in 1-12, day within the correct
    bound for that month)."""
    start = datetime.date(1600, 1, 1)
    end = datetime.date(2500, 12, 31)

    for day in _random_gregorian_dates(seeded_random, SAMPLE_SIZE, start, end):
        j_year, j_month, j_day = JalaliCalendar.gregorian_to_jalali(
            day.year, day.month, day.day
        )
        assert 1 <= j_month <= 12
        if j_month <= 6:
            assert 1 <= j_day <= 31
        elif j_month <= 11:
            assert 1 <= j_day <= 30
        else:
            assert 1 <= j_day <= (30 if JalaliCalendar.is_leap(j_year) else 29)
