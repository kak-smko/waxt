"""Supplementary, lighter tests for ``HijriCalendar``.

The task that produced this suite specifically targeted the Jalali
(Persian) <-> Gregorian converter (see the other ``test_jalali_*`` files
for the thorough treatment). ``HijriCalendar`` lives in the same module,
so a light smoke-test layer is included here for completeness, but it is
intentionally much less exhaustive than the Jalali suite.
"""

from __future__ import annotations

import datetime

import pytest

from waxt.calendar_converters import HijriCalendar

pytestmark = pytest.mark.hijri


def test_hijri_epoch_round_trip():
    g = HijriCalendar.hijri_to_gregorian(1, 1, 1)
    assert g == (622, 7, 19)
    assert HijriCalendar.gregorian_to_hijri(*g) == (1, 1, 1)


@pytest.mark.parametrize("month", [0, -1, 13, 100])
def test_hijri_to_gregorian_rejects_invalid_month(month):
    with pytest.raises(ValueError, match="Invalid Hijri month"):
        HijriCalendar.hijri_to_gregorian(1445, month, 1)


@pytest.mark.parametrize("day", [0, -1, 31])
def test_hijri_to_gregorian_rejects_invalid_day(day):
    with pytest.raises(ValueError, match="Invalid Hijri day"):
        HijriCalendar.hijri_to_gregorian(1445, 1, day)


def test_gregorian_to_hijri_before_epoch_raises():
    """Documented current behaviour: dates before the Hijri epoch raise
    ValueError."""
    with pytest.raises(ValueError, match="Date is before Hijri epoch"):
        HijriCalendar.gregorian_to_hijri(600, 1, 1)


@pytest.mark.parametrize(
    "g_year, g_month, g_day",
    [
        (2024, 1, 1),
        (2000, 6, 15),
        (1990, 12, 31),
        (2500, 12, 31),
        (1600, 1, 1),
    ],
)
def test_hijri_round_trip_gregorian_to_hijri_to_gregorian(g_year, g_month, g_day):
    h = HijriCalendar.gregorian_to_hijri(g_year, g_month, g_day)
    g_back = HijriCalendar.hijri_to_gregorian(*h)
    assert g_back == (g_year, g_month, g_day)


def test_hijri_leap_year_has_30_days_in_dhul_hijjah():
    leap_years = [y for y in range(1400, 1500) if HijriCalendar.is_leap(y)]
    assert leap_years  # sanity: leap years exist in this range

    year = leap_years[0]
    g = HijriCalendar.hijri_to_gregorian(year, 12, 30)
    assert HijriCalendar.gregorian_to_hijri(*g) == (year, 12, 30)
