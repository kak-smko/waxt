"""Nowruz and Jalali year-boundary tests (requirements #4 and #5).

For every Jalali year whose Nowruz falls within Gregorian years 1900-2500
(inclusive), this module checks:

* the day *before* Nowruz (last day of the previous Jalali year - Esfand
  29 or 30, depending on whether the previous year is a leap year),
* Nowruz itself (1 Farvardin),
* the day *after* Nowruz (2 Farvardin),

in both directions (Gregorian -> Jalali and Jalali -> Gregorian), ensuring
full internal consistency across the year boundary.
"""

from __future__ import annotations

import datetime

import pytest

from waxt.calendar_converters import JalaliCalendar

# Nowruz of Jalali year `jy` falls within Gregorian year `jy + 621` (March).
# Gregorian 1900 -> Jalali ~1278, Gregorian 2500 -> Jalali ~1879.
JALALI_YEARS_FOR_NOWRUZ = list(range(1279, 1880))


@pytest.mark.parametrize("jalali_year", JALALI_YEARS_FOR_NOWRUZ)
def test_nowruz_day_before_on_and_after(jalali_year):
    nowruz_g = JalaliCalendar.jalali_to_gregorian(jalali_year, 1, 1)
    nowruz_date = datetime.date(*nowruz_g)

    day_before = nowruz_date - datetime.timedelta(days=1)
    day_after = nowruz_date + datetime.timedelta(days=1)

    # Nowruz itself.
    assert JalaliCalendar.gregorian_to_jalali(*nowruz_g) == (jalali_year, 1, 1)

    # Day after Nowruz: 2 Farvardin of the same Jalali year.
    j_after = JalaliCalendar.gregorian_to_jalali(
        day_after.year, day_after.month, day_after.day
    )
    assert j_after == (jalali_year, 1, 2)
    assert JalaliCalendar.jalali_to_gregorian(*j_after) == (
        day_after.year,
        day_after.month,
        day_after.day,
    )

    # Day before Nowruz: last day of Esfand of the previous Jalali year.
    previous_year = jalali_year - 1
    expected_last_esfand_day = 30 if JalaliCalendar.is_leap(previous_year) else 29
    j_before = JalaliCalendar.gregorian_to_jalali(
        day_before.year, day_before.month, day_before.day
    )
    assert j_before == (previous_year, 12, expected_last_esfand_day)
    assert JalaliCalendar.jalali_to_gregorian(*j_before) == (
        day_before.year,
        day_before.month,
        day_before.day,
    )


@pytest.mark.parametrize("jalali_year", JALALI_YEARS_FOR_NOWRUZ)
def test_jalali_year_end_and_start_are_contiguous(jalali_year):
    """Esfand 29/30 of `jalali_year` must be immediately followed by
    Farvardin 1 of `jalali_year + 1`, with no gap or overlap."""
    last_day = 30 if JalaliCalendar.is_leap(jalali_year) else 29
    g_last_day = JalaliCalendar.jalali_to_gregorian(jalali_year, 12, last_day)
    g_next_nowruz = JalaliCalendar.jalali_to_gregorian(jalali_year + 1, 1, 1)

    expected_next_day = datetime.date(*g_last_day) + datetime.timedelta(days=1)
    assert g_next_nowruz == (
        expected_next_day.year,
        expected_next_day.month,
        expected_next_day.day,
    )


@pytest.mark.parametrize("jalali_year", [1279, 1300, 1400, 1403, 1500, 1700, 1879])
def test_farvardin_1_is_always_1_or_2_days_after_march_19(jalali_year):
    """Nowruz always falls on March 19th, 20th, 21st or 22nd (Gregorian)."""
    g_year, g_month, g_day = JalaliCalendar.jalali_to_gregorian(jalali_year, 1, 1)
    assert g_month == 3
    assert 19 <= g_day <= 22
