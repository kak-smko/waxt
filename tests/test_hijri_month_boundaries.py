"""Boundary-day tests for every Gregorian and Hijri month (requirement #3).

For the Gregorian side we rely on ``calendar.monthrange`` (Python stdlib)
as ground truth for "how many days does this month have", then check that
``HijriCalendar`` treats the first/last day of every Gregorian month as a
real day that sits exactly one day away from the neighbouring month.

For the Hijri side we directly use the day-count rule implemented by
``HijriCalendar`` itself: odd months always have 30 days, even months have
29 days (30 for Dhu al-Hijjah - month 12 - in a leap year), applied to a
representative sample of leap and non-leap years, checking the same
"exactly one day away" invariant plus the requirement #4 "first/last day
of every Hijri month" case explicitly.
"""

from __future__ import annotations

import calendar
import datetime

import pytest

from tests.conftest import hijri_days_in_month
from waxt.calendar_converters import HijriCalendar

GREGORIAN_YEARS = [
    1600,  # leap
    1601,  # non-leap
    1700,  # non-leap century year
    1800,  # non-leap century year
    1900,  # non-leap century year
    1999,  # non-leap
    2000,  # leap century year
    2001,  # non-leap
    2024,  # leap
    2100,  # non-leap century year
    2400,  # leap century year
    2500,  # non-leap
]


def _to_hijri(date_: datetime.date):
    return HijriCalendar.gregorian_to_hijri(date_.year, date_.month, date_.day)


def _next_day(date_: datetime.date) -> datetime.date:
    return date_ + datetime.timedelta(days=1)


def _next_hijri_day(h_date):
    g_date = datetime.date(*HijriCalendar.hijri_to_gregorian(*h_date))
    return _to_hijri(_next_day(g_date))


@pytest.mark.parametrize("year", GREGORIAN_YEARS)
@pytest.mark.parametrize("month", range(1, 13))
def test_gregorian_month_first_day_round_trips(year, month):
    first_day = datetime.date(year, month, 1)
    h = _to_hijri(first_day)
    assert HijriCalendar.hijri_to_gregorian(*h) == (year, month, 1)


@pytest.mark.parametrize("year", GREGORIAN_YEARS)
@pytest.mark.parametrize("month", range(1, 13))
def test_gregorian_month_last_day_round_trips_and_is_contiguous(year, month):
    _, days_in_month = calendar.monthrange(year, month)
    last_day = datetime.date(year, month, days_in_month)
    h_last = _to_hijri(last_day)

    assert HijriCalendar.hijri_to_gregorian(*h_last) == (year, month, days_in_month)

    next_day = _next_day(last_day)
    h_next = _to_hijri(next_day)
    assert HijriCalendar.hijri_to_gregorian(*h_next) == (
        next_day.year,
        next_day.month,
        next_day.day,
    )
    # The day after the last day of a Gregorian month must be exactly one
    # Hijri day later than the last day itself.
    assert h_next == _next_hijri_day(h_last)


# ---------------------------------------------------------------------------
# Hijri month boundaries (requirement #4: first/last day of every month)
# ---------------------------------------------------------------------------

# A representative sample spanning the required support range, including
# both Hijri leap and non-leap years (see test_hijri_leap_years.py).
HIJRI_LEAP_SAMPLE_YEARS = [1, 12, 500, 1400, 1446]
HIJRI_NON_LEAP_SAMPLE_YEARS = [2, 10, 1300, 1401, 1445, 1447]
HIJRI_YEARS = HIJRI_LEAP_SAMPLE_YEARS + HIJRI_NON_LEAP_SAMPLE_YEARS


@pytest.mark.parametrize("year", HIJRI_YEARS)
@pytest.mark.parametrize("month", range(1, 13))
def test_hijri_month_first_day_round_trips(year, month):
    g = HijriCalendar.hijri_to_gregorian(year, month, 1)
    assert HijriCalendar.gregorian_to_hijri(*g) == (year, month, 1)


@pytest.mark.parametrize("year", HIJRI_YEARS)
@pytest.mark.parametrize("month", range(1, 13))
def test_hijri_month_last_day_round_trips(year, month):
    max_day = hijri_days_in_month(year, month)
    g = HijriCalendar.hijri_to_gregorian(year, month, max_day)
    assert HijriCalendar.gregorian_to_hijri(*g) == (year, month, max_day)

    # One day beyond the last day of the month rolls over to month + 1
    # (or into next year for Dhu al-Hijjah).
    next_g = datetime.date(*g) + datetime.timedelta(days=1)
    h_next = HijriCalendar.gregorian_to_hijri(next_g.year, next_g.month, next_g.day)
    if month == 12:
        assert h_next == (year + 1, 1, 1)
    else:
        assert h_next == (year, month + 1, 1)


@pytest.mark.parametrize("year", HIJRI_YEARS)
@pytest.mark.parametrize("month", range(1, 13))
def test_hijri_day_beyond_month_max_is_rejected(year, month):
    max_day = hijri_days_in_month(year, month)
    with pytest.raises(ValueError, match="Invalid Hijri day"):
        HijriCalendar.hijri_to_gregorian(year, month, max_day + 1)


@pytest.mark.parametrize("year", HIJRI_YEARS)
@pytest.mark.parametrize("month", range(1, 13))
def test_hijri_month_length_is_29_or_30_only(year, month):
    max_day = hijri_days_in_month(year, month)
    assert max_day in (29, 30)
    if month % 2 == 1:
        assert max_day == 30
    elif month == 12:
        assert max_day == (30 if HijriCalendar.is_leap(year) else 29)
    else:
        assert max_day == 29


@pytest.mark.parametrize("month", range(1, 13))
def test_odd_months_always_have_30_days_regardless_of_leap_status(month):
    """Odd Hijri months (Muharram, Rabi' al-awwal, ... Dhu al-Qi'dah) are
    unaffected by leap status - only month 12 changes."""
    if month % 2 != 1:
        pytest.skip("only relevant for odd months")
    for year in (1, 2, 1400, 1401, 1445, 1446):
        assert hijri_days_in_month(year, month) == 30


@pytest.mark.parametrize("month", [2, 4, 6, 8, 10])
def test_even_non_dhul_hijjah_months_always_have_29_days(month):
    """Even months other than Dhu al-Hijjah (month 12) always have 29 days,
    regardless of whether the year is a leap year."""
    for year in (1, 2, 1400, 1401, 1445, 1446):
        assert hijri_days_in_month(year, month) == 29
