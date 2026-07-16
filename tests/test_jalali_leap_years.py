"""Leap-year tests (requirement #2).

Two independent notions of "leap year" are exercised here:

* Gregorian leap years, using Python's own ``calendar.isleap`` (and the
  fact that ``datetime.date`` refuses to build invalid dates) as the
  ground truth oracle. We never assert a hard-coded Jalali date for these;
  instead we verify that ``JalaliCalendar`` treats the Gregorian leap day
  as a real day that sits exactly one day before March 1st.
* Jalali leap years, using ``JalaliCalendar.is_leap`` together with the
  day-count of Esfand (12th month), which must be 30 in a leap year and 29
  otherwise.
"""

from __future__ import annotations

import calendar
import datetime

import pytest

from waxt.calendar_converters import JalaliCalendar

GREGORIAN_LEAP_YEARS = [
    1600,  # divisible by 400 -> leap
    2000,  # divisible by 400 -> leap
    1996,
    2004,
    2008,
    2012,
    2016,
    2020,
    2024,
    2028,
    2400,  # divisible by 400 -> leap
    2404,
]

GREGORIAN_NON_LEAP_YEARS = [
    1700,
    1800,
    1900,
    2100,
    2200,
    2300,
    1997,
    1998,
    1999,
    2001,
    2002,
    2003,
    2005,
    2021,
    2023,
    2025,
]


@pytest.mark.parametrize("year", GREGORIAN_LEAP_YEARS)
def test_gregorian_leap_year_has_feb_29(year):
    assert calendar.isleap(year) is True

    feb_29 = datetime.date(year, 2, 29)
    mar_1 = datetime.date(year, 3, 1)

    j_feb_29 = JalaliCalendar.gregorian_to_jalali(feb_29.year, feb_29.month, feb_29.day)
    j_mar_1 = JalaliCalendar.gregorian_to_jalali(mar_1.year, mar_1.month, mar_1.day)

    # Feb 29th must round-trip to itself and be exactly one Jalali day
    # before March 1st.
    assert JalaliCalendar.jalali_to_gregorian(*j_feb_29) == (year, 2, 29)
    assert JalaliCalendar.jalali_to_gregorian(*j_mar_1) == (year, 3, 1)
    assert j_feb_29 != j_mar_1
    assert _next_jalali_day(j_feb_29) == j_mar_1


@pytest.mark.parametrize("year", GREGORIAN_NON_LEAP_YEARS)
def test_gregorian_non_leap_year_has_no_feb_29(year):
    assert calendar.isleap(year) is False

    with pytest.raises(ValueError):
        datetime.date(year, 2, 29)

    feb_28 = datetime.date(year, 2, 28)
    mar_1 = datetime.date(year, 3, 1)

    j_feb_28 = JalaliCalendar.gregorian_to_jalali(feb_28.year, feb_28.month, feb_28.day)
    j_mar_1 = JalaliCalendar.gregorian_to_jalali(mar_1.year, mar_1.month, mar_1.day)

    assert _next_jalali_day(j_feb_28) == j_mar_1


def _next_jalali_day(j_date):
    """Return the Jalali date that immediately follows ``j_date``."""
    g_date = datetime.date(*JalaliCalendar.jalali_to_gregorian(*j_date))
    next_g_date = g_date + datetime.timedelta(days=1)
    return JalaliCalendar.gregorian_to_jalali(
        next_g_date.year, next_g_date.month, next_g_date.day
    )


# ---------------------------------------------------------------------------
# Jalali leap years
# ---------------------------------------------------------------------------

# Verified against jdatetime / public knowledge.
JALALI_LEAP_YEARS = [
    1201,
    1205,
    1210,
    1375,
    1379,
    1383,
    1387,
    1391,
    1395,
    1399,
    1403,
    1408,
]
JALALI_NON_LEAP_YEARS = [1400, 1401, 1402, 1404, 1405, 1396, 1397, 1398, 1376, 1377]


@pytest.mark.parametrize("year", JALALI_LEAP_YEARS)
def test_jalali_leap_year_has_30_days_in_esfand(year):
    assert JalaliCalendar.is_leap(year) is True

    # 30 Esfand must be valid...
    g = JalaliCalendar.jalali_to_gregorian(year, 12, 30)
    assert JalaliCalendar.gregorian_to_jalali(*g) == (year, 12, 30)

    # ...and it must be exactly one day before next year's Nowruz.
    nowruz_next = JalaliCalendar.jalali_to_gregorian(year + 1, 1, 1)
    day_before_nowruz = datetime.date(*nowruz_next) - datetime.timedelta(days=1)
    assert (day_before_nowruz.year, day_before_nowruz.month, day_before_nowruz.day) == g


@pytest.mark.parametrize("year", JALALI_NON_LEAP_YEARS)
def test_jalali_non_leap_year_has_29_days_in_esfand(year):
    assert JalaliCalendar.is_leap(year) is False

    with pytest.raises(ValueError):
        JalaliCalendar.jalali_to_gregorian(year, 12, 30)

    g = JalaliCalendar.jalali_to_gregorian(year, 12, 29)
    nowruz_next = JalaliCalendar.jalali_to_gregorian(year + 1, 1, 1)
    day_before_nowruz = datetime.date(*nowruz_next) - datetime.timedelta(days=1)
    assert (day_before_nowruz.year, day_before_nowruz.month, day_before_nowruz.day) == g


def test_jalali_leap_years_are_spaced_four_or_five_years_apart():
    """The 33-year-cycle approximation must never produce implausible gaps."""
    leap_years = [y for y in range(-61, 3178) if JalaliCalendar.is_leap(y)]
    gaps = {b - a for a, b in zip(leap_years, leap_years[1:])}
    assert gaps <= {4, 5}


def test_jalali_leap_year_ratio_matches_2820_year_cycle_approximation():
    """~683 leap years every 2820 years, i.e. a ratio of ~0.2423."""
    years = range(-61, 3178)
    leap_count = sum(1 for y in years if JalaliCalendar.is_leap(y))
    ratio = leap_count / len(years)
    assert 0.23 < ratio < 0.25
