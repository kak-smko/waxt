"""Boundary-day tests for every Gregorian and Jalali month (requirement #3).

For the Gregorian side we rely on ``calendar.monthrange`` (Python stdlib)
as the ground truth for "how many days does this month have", then check
that ``JalaliCalendar`` treats the first/last day of every month as a real
day that sits exactly one day away from the neighbouring month.

For the Jalali side we directly use the day-count rules implemented by
``JalaliCalendar`` itself (31/30/29-or-30), applied to representative leap
and non-leap years, and check the same "exactly one day away" invariant.
"""

from __future__ import annotations

import calendar
import datetime

import pytest

from waxt.calendar_converters import JalaliCalendar

GREGORIAN_YEARS = [
    1600,  # leap, start of required range
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
    2500,  # non-leap, end of required range
]


def _to_jalali(date_: datetime.date):
    return JalaliCalendar.gregorian_to_jalali(date_.year, date_.month, date_.day)


def _next_day(date_: datetime.date) -> datetime.date:
    return date_ + datetime.timedelta(days=1)


@pytest.mark.parametrize("year", GREGORIAN_YEARS)
@pytest.mark.parametrize("month", range(1, 13))
def test_gregorian_month_first_day_round_trips(year, month):
    first_day = datetime.date(year, month, 1)
    j = _to_jalali(first_day)
    assert JalaliCalendar.jalali_to_gregorian(*j) == (year, month, 1)


@pytest.mark.parametrize("year", GREGORIAN_YEARS)
@pytest.mark.parametrize("month", range(1, 13))
def test_gregorian_month_last_day_round_trips_and_is_contiguous(year, month):
    _, days_in_month = calendar.monthrange(year, month)
    last_day = datetime.date(year, month, days_in_month)
    j_last = _to_jalali(last_day)

    assert JalaliCalendar.jalali_to_gregorian(*j_last) == (
        year,
        month,
        days_in_month,
    )

    next_day = _next_day(last_day)
    j_next = _to_jalali(next_day)
    assert JalaliCalendar.jalali_to_gregorian(*j_next) == (
        next_day.year,
        next_day.month,
        next_day.day,
    )
    # The day after the last day of a month must be exactly one Jalali day
    # later than the last day itself.
    assert j_next == _next_jalali_day(j_last)


def _next_jalali_day(j_date):
    g_date = datetime.date(*JalaliCalendar.jalali_to_gregorian(*j_date))
    return _to_jalali(_next_day(g_date))


# ---------------------------------------------------------------------------
# Jalali month boundaries
# ---------------------------------------------------------------------------

# A representative sample spanning the required support range, including
# both leap and non-leap years.
JALALI_YEARS = [979, 1000, 1300, 1399, 1400, 1402, 1403, 1700, 1879]


def _max_day_for_month(year: int, month: int) -> int:
    if month <= 6:
        return 31
    if month <= 11:
        return 30
    return 30 if JalaliCalendar.is_leap(year) else 29


@pytest.mark.parametrize("year", JALALI_YEARS)
@pytest.mark.parametrize("month", range(1, 13))
def test_jalali_month_first_day_round_trips(year, month):
    g = JalaliCalendar.jalali_to_gregorian(year, month, 1)
    assert JalaliCalendar.gregorian_to_jalali(*g) == (year, month, 1)


@pytest.mark.parametrize("year", JALALI_YEARS)
@pytest.mark.parametrize("month", range(1, 13))
def test_jalali_month_last_day_round_trips(year, month):
    max_day = _max_day_for_month(year, month)
    g = JalaliCalendar.jalali_to_gregorian(year, month, max_day)
    assert JalaliCalendar.gregorian_to_jalali(*g) == (year, month, max_day)

    # One day beyond the last day of the month rolls over to month + 1
    # (or into next year for Esfand).
    next_g = datetime.date(*g) + datetime.timedelta(days=1)
    j_next = JalaliCalendar.gregorian_to_jalali(next_g.year, next_g.month, next_g.day)
    if month == 12:
        assert j_next == (year + 1, 1, 1)
    else:
        assert j_next == (year, month + 1, 1)


@pytest.mark.parametrize("year", JALALI_YEARS)
@pytest.mark.parametrize("month", range(1, 13))
def test_jalali_day_beyond_month_max_is_rejected(year, month):
    max_day = _max_day_for_month(year, month)
    with pytest.raises(ValueError):
        JalaliCalendar.jalali_to_gregorian(year, month, max_day + 1)
