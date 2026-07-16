"""Leap-year tests for ``HijriCalendar`` (requirement #2).

Two independent notions of "leap year" are exercised here:

* Gregorian leap years, using Python's own ``calendar.isleap`` as ground
  truth, to make sure ``HijriCalendar`` treats the Gregorian leap day
  (Feb 29th) as a real day sitting exactly one day before March 1st.
* Hijri leap years, using ``HijriCalendar.is_leap`` together with the
  day-count of Dhu al-Hijjah (12th month), which must be 30 in a leap year
  and 29 otherwise, per the ``(11 * year + 25) % 30 < 11`` tabular rule.
"""

from __future__ import annotations

import calendar
import datetime

import pytest

from waxt.calendar_converters import HijriCalendar

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


def _to_hijri(date_: datetime.date):
    return HijriCalendar.gregorian_to_hijri(date_.year, date_.month, date_.day)


def _next_hijri_day(h_date):
    g_date = datetime.date(*HijriCalendar.hijri_to_gregorian(*h_date))
    next_g_date = g_date + datetime.timedelta(days=1)
    return _to_hijri(next_g_date)


@pytest.mark.parametrize("year", GREGORIAN_LEAP_YEARS)
def test_gregorian_leap_year_has_feb_29(year):
    assert calendar.isleap(year) is True

    feb_29 = datetime.date(year, 2, 29)
    mar_1 = datetime.date(year, 3, 1)

    h_feb_29 = _to_hijri(feb_29)
    h_mar_1 = _to_hijri(mar_1)

    # Feb 29th must round-trip to itself and be exactly one Hijri day
    # before March 1st.
    assert HijriCalendar.hijri_to_gregorian(*h_feb_29) == (year, 2, 29)
    assert HijriCalendar.hijri_to_gregorian(*h_mar_1) == (year, 3, 1)
    assert h_feb_29 != h_mar_1
    assert _next_hijri_day(h_feb_29) == h_mar_1


@pytest.mark.parametrize("year", GREGORIAN_NON_LEAP_YEARS)
def test_gregorian_non_leap_year_has_no_feb_29(year):
    assert calendar.isleap(year) is False

    with pytest.raises(ValueError):
        datetime.date(year, 2, 29)

    feb_28 = datetime.date(year, 2, 28)
    mar_1 = datetime.date(year, 3, 1)

    h_feb_28 = _to_hijri(feb_28)
    h_mar_1 = _to_hijri(mar_1)

    assert _next_hijri_day(h_feb_28) == h_mar_1


# ---------------------------------------------------------------------------
# Hijri leap years
# ---------------------------------------------------------------------------

# Derived directly from the ``(11 * year + 25) % 30 < 11`` rule, i.e. years
# congruent (mod 30) to 1, 4, 6, 9, 12, 15, 17, 20, 23, 25, 28.
HIJRI_LEAP_YEARS = [1, 4, 6, 9, 12, 15, 17, 20, 23, 25, 28, 31, 1400, 1446]
HIJRI_NON_LEAP_YEARS = [2, 3, 5, 7, 8, 10, 11, 13, 14, 1401, 1445, 1447, 1500]


@pytest.mark.parametrize("year", HIJRI_LEAP_YEARS)
def test_hijri_leap_year_has_30_days_in_dhul_hijjah(year):
    assert HijriCalendar.is_leap(year) is True

    # 30 Dhu al-Hijjah must be valid...
    g = HijriCalendar.hijri_to_gregorian(year, 12, 30)
    assert HijriCalendar.gregorian_to_hijri(*g) == (year, 12, 30)

    # ...and it must be exactly one day before next year's 1 Muharram.
    next_muharram = HijriCalendar.hijri_to_gregorian(year + 1, 1, 1)
    day_before = datetime.date(*next_muharram) - datetime.timedelta(days=1)
    assert (day_before.year, day_before.month, day_before.day) == g


@pytest.mark.parametrize("year", HIJRI_NON_LEAP_YEARS)
def test_hijri_non_leap_year_has_29_days_in_dhul_hijjah(year):
    assert HijriCalendar.is_leap(year) is False

    with pytest.raises(ValueError, match="Invalid Hijri day"):
        HijriCalendar.hijri_to_gregorian(year, 12, 30)

    g = HijriCalendar.hijri_to_gregorian(year, 12, 29)
    next_muharram = HijriCalendar.hijri_to_gregorian(year + 1, 1, 1)
    day_before = datetime.date(*next_muharram) - datetime.timedelta(days=1)
    assert (day_before.year, day_before.month, day_before.day) == g


def test_hijri_leap_years_follow_fixed_30_year_cycle():
    """Unlike the Jalali 33-year approximation, the Hijri leap rule here is
    an exact, unconditional 30-year cycle: leap-ness depends only on
    ``year % 30``."""
    for year in range(1, 3001):
        assert HijriCalendar.is_leap(year) == HijriCalendar.is_leap(year + 30)


def test_hijri_leap_year_count_per_30_year_cycle_is_eleven():
    leap_count = sum(1 for y in range(1, 31) if HijriCalendar.is_leap(y))
    assert leap_count == 11


def test_hijri_leap_year_total_days_per_cycle_is_10631():
    """354 (common year) * 19 + 355 (leap year) * 11 == 10631 days per
    30-year cycle - the standard tabular-Islamic-calendar invariant."""
    total_days = sum(355 if HijriCalendar.is_leap(y) else 354 for y in range(1, 31))
    assert total_days == 10631


@pytest.mark.parametrize("year", [0, -1, -30, -29, 3000, 3001])
def test_is_leap_never_raises_for_any_integer_year(year):
    """``is_leap`` performs no range validation - it is a pure modular
    arithmetic function that accepts any integer, including zero and
    negative years (there is no "year zero doesn't exist" guard)."""
    result = HijriCalendar.is_leap(year)
    assert isinstance(result, bool)
