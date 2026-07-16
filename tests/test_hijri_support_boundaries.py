"""Tests probing the boundaries of ``HijriCalendar``'s supported range
(requirements #11 and #13).

``HijriCalendar`` has no explicit min/max Hijri year constant of its own.
Its practical range is instead bounded indirectly, because
``hijri_to_gregorian`` builds a real ``datetime.date`` internally
(``epoch + timedelta(days=...)``), and Python's ``datetime.date`` only
supports proleptic Gregorian years 1-9999.

The exact edges below were derived empirically (via binary search) while
building this suite, by calling ``HijriCalendar.hijri_to_gregorian``
directly and observing where it starts raising ``OverflowError``:

* Upper edge: ``hijri_to_gregorian(9666, 1, 1) == (9999, 10, 2)`` still
  succeeds, but ``hijri_to_gregorian(9667, 1, 1)`` overflows (would need
  Gregorian year 10000+). The *last day* of AH 9666 also overflows, so the
  highest Hijri year whose **entire year** stays in range is 9665.
* Lower edge: ``hijri_to_gregorian(-639, 1, 1) == (1, 8, 9)`` still
  succeeds, but ``hijri_to_gregorian(-640, 1, 1)`` underflows (would need
  Gregorian year 0 or earlier, which ``datetime.date`` does not support).

These are consequences of delegating to ``datetime.date``, not deliberate
design constants, so they are documented here as empirically-derived
boundaries rather than asserted as "the" official supported range - if the
internal implementation of ``hijri_to_gregorian`` ever changes (e.g. to
avoid going through ``datetime.date``), these exact numbers could shift.
"""

from __future__ import annotations

import datetime

import pytest

from tests.conftest import (
    FULL_RANGE_END,
    FULL_RANGE_START,
    hijri_days_in_month,
)
from waxt.calendar_converters import HijriCalendar

UPPER_LAST_FULL_YEAR = 9665
UPPER_FIRST_OVERFLOWING_YEAR = 9667
UPPER_PARTIAL_YEAR = 9666  # 1 Muharram works, but not every day of the year.

LOWER_LAST_FULL_YEAR = -639
LOWER_FIRST_UNDERFLOWING_YEAR = -640


def test_required_range_start_boundary():
    start = datetime.date(1600, 1, 1)
    h = HijriCalendar.gregorian_to_hijri(start.year, start.month, start.day)
    assert HijriCalendar.hijri_to_gregorian(*h) == (1600, 1, 1)

    one_day_before = start - datetime.timedelta(days=1)
    h_before = HijriCalendar.gregorian_to_hijri(
        one_day_before.year, one_day_before.month, one_day_before.day
    )
    assert HijriCalendar.hijri_to_gregorian(*h_before) == (
        one_day_before.year,
        one_day_before.month,
        one_day_before.day,
    )


def test_required_range_end_boundary():
    end = datetime.date(2500, 12, 31)
    h = HijriCalendar.gregorian_to_hijri(end.year, end.month, end.day)
    assert HijriCalendar.hijri_to_gregorian(*h) == (2500, 12, 31)

    one_day_after = end + datetime.timedelta(days=1)
    h_after = HijriCalendar.gregorian_to_hijri(
        one_day_after.year, one_day_after.month, one_day_after.day
    )
    assert HijriCalendar.hijri_to_gregorian(*h_after) == (
        one_day_after.year,
        one_day_after.month,
        one_day_after.day,
    )


def test_gregorian_epoch_of_datetime_module_before_hijri_epoch_raises():
    """``datetime.date``'s own lower bound (0001-01-01) is before the
    Hijri epoch (622-07-19), so it raises ValueError."""
    with pytest.raises(ValueError, match="Date is before Hijri epoch"):
        HijriCalendar.gregorian_to_hijri(1, 1, 1)


def test_gregorian_max_supported_year_round_trips():
    """``datetime.date``'s own upper bound (9999-12-31) must round-trip
    normally through ``gregorian_to_hijri`` without raising."""
    h = HijriCalendar.gregorian_to_hijri(9999, 12, 31)
    assert HijriCalendar.hijri_to_gregorian(*h) == (9999, 12, 31)


@pytest.mark.parametrize("year", [UPPER_LAST_FULL_YEAR - 1, UPPER_LAST_FULL_YEAR])
def test_upper_boundary_last_fully_supported_hijri_year(year):
    """Every day of these years, including 29/30 Dhu al-Hijjah, must
    convert without raising."""
    for month in range(1, 13):
        max_day = hijri_days_in_month(year, month)
        g_first = HijriCalendar.hijri_to_gregorian(year, month, 1)
        g_last = HijriCalendar.hijri_to_gregorian(year, month, max_day)
        assert HijriCalendar.gregorian_to_hijri(*g_first) == (year, month, 1)
        assert HijriCalendar.gregorian_to_hijri(*g_last) == (year, month, max_day)


def test_upper_boundary_partial_year_first_day_works_but_year_end_overflows():
    """AH 9666: 1 Muharram is still representable (right at the edge of
    Gregorian year 9999), but by the end of the year the Gregorian date
    would need to be in year 10000+, which ``datetime.date`` rejects."""
    g_first = HijriCalendar.hijri_to_gregorian(UPPER_PARTIAL_YEAR, 1, 1)
    assert g_first[0] == 9999
    assert HijriCalendar.gregorian_to_hijri(*g_first) == (UPPER_PARTIAL_YEAR, 1, 1)

    max_day = hijri_days_in_month(UPPER_PARTIAL_YEAR, 12)
    with pytest.raises((OverflowError, ValueError)):
        HijriCalendar.hijri_to_gregorian(UPPER_PARTIAL_YEAR, 12, max_day)


def test_upper_boundary_first_fully_overflowing_hijri_year():
    with pytest.raises((OverflowError, ValueError)):
        HijriCalendar.hijri_to_gregorian(UPPER_FIRST_OVERFLOWING_YEAR, 1, 1)


@pytest.mark.parametrize("year", [LOWER_LAST_FULL_YEAR, LOWER_LAST_FULL_YEAR + 1])
def test_lower_boundary_last_supported_hijri_year(year):
    """These (negative/pre-epoch) Hijri years still produce a valid
    ``datetime.date``-representable Gregorian date, per the documented
    lack of a ``h_year >= 1`` guard (see test_hijri_invalid_inputs.py)."""
    g = HijriCalendar.hijri_to_gregorian(year, 1, 1)
    assert isinstance(g, tuple)
    assert g[0] >= 1


def test_lower_boundary_first_underflowing_hijri_year():
    with pytest.raises((OverflowError, ValueError)):
        HijriCalendar.hijri_to_gregorian(LOWER_FIRST_UNDERFLOWING_YEAR, 1, 1)


def test_extended_negative_range_between_epoch_and_lower_boundary_round_trips():
    """A coarse sweep of negative/zero Hijri years between the epoch and
    the lower boundary, confirming no crash and (for years whose Gregorian
    equivalent is on/after the real epoch) full round-trip consistency."""
    for year in range(0, LOWER_LAST_FULL_YEAR - 1, -37):
        g = HijriCalendar.hijri_to_gregorian(year, 1, 1)
        # Round trip holds unless the target predates the true epoch, in
        # which case gregorian_to_hijri raises ValueError.
        try:
            h_back = HijriCalendar.gregorian_to_hijri(*g)
            assert h_back == (year, 1, 1)
        except ValueError as e:
            assert "Date is before Hijri epoch" in str(e)
